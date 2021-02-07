# -*- coding: utf-8 -*-

"""A script for enriching the CONSO with external information."""

import json
from typing import Mapping, Optional

import click
import pandas as pd
from tqdm import tqdm

from .resources import SYNONYMS_PATH, XREFS_PATH

SYNONYM_HEADER = ['identifier', 'synonym', 'reference', 'specificity']
XREFS_HEADER = ['identifier', 'database', 'database_identifier']


def enrich_pubchem_synonyms():
    """Enrich synonyms file with information from PubChem."""
    import pubchempy as pcp

    xrefs = pd.read_csv(XREFS_PATH, sep='\t')
    xrefs = xrefs[xrefs['database'] == 'pubchem.compound']
    cid_to_conso = pd.Series(xrefs['identifier'].values, index=xrefs['database_identifier']).to_dict()

    new_synonyms = [
        (
            cid_to_conso[cid],
            synonym,
            f'pubchem.compound:{cid}',
            'EXACT',
        )
        for cid in tqdm(cid_to_conso, desc='PubChem lookup')
        for synonym in pcp.Compound.from_cid(cid).synonyms
    ]

    (
        pd.concat([
            pd.read_csv(SYNONYMS_PATH, sep='\t'),
            pd.DataFrame(new_synonyms, columns=SYNONYM_HEADER),
        ])
        .drop_duplicates()
        .sort_values(SYNONYM_HEADER)
        .to_csv(SYNONYMS_PATH, sep='\t', index=False)
    )


def enrich_chebi_xrefs():
    """Enrich xrefs file with information from ChEBI."""
    import zeep
    wsdl = 'https://www.ebi.ac.uk/webservices/chebi/2.0/webservice?wsdl'
    client = zeep.Client(wsdl)

    def get_chebi_by_smiles(_smiles: str) -> Optional[Mapping]:
        """Look up a molecule in ChEBI using an exact match for smiles."""
        results = client.service.getStructureSearch(
            _smiles,
            client.get_type('ns0:StructureType')('SMILES'),
            client.get_type('ns0:StructureSearchCategory')('IDENTITY'),
            10,
            0.5,
        )
        if results is None or len(results) == 0:
            return

        if len(results) > 1:
            results = [
                {
                    key: result[key]
                    for key in result
                }
                for result in results
            ]

            three_star_results = [
                result
                for result in results
                if result['entityStar'] == 3
            ]
            if len(three_star_results) == 1:
                return three_star_results[0]

            raise ValueError(f'too many results when looking up {smiles}:\n{json.dumps(results, indent=2)}')

        if len(results) == 1:
            return results[0]

    xrefs = pd.read_csv(XREFS_PATH, sep='\t')
    xrefs = xrefs[xrefs['database'] == 'smiles']
    smiles_to_conso_id = pd.Series(xrefs['identifier'].values, index=xrefs['database_identifier']).to_dict()

    new_xrefs = []
    for smiles, conso_id in tqdm(smiles_to_conso_id.items(), desc='ChEBI lookup'):
        try:
            result = get_chebi_by_smiles(smiles)
        except zeep.exceptions.Fault:
            continue
        if result is None:
            continue

        new_xrefs.append((
            conso_id,
            'chebi',
            result['chebiId'],
        ))

    (
        pd.concat([
            pd.read_csv(XREFS_PATH, sep='\t'),
            pd.DataFrame(new_xrefs, columns=XREFS_HEADER),
        ])
        .drop_duplicates()
        .sort_values(XREFS_HEADER)
        .to_csv(XREFS_PATH, sep='\t', index=False)
    )


@click.command()
def enrich():
    """Enrich the ontology."""
    enrich_pubchem_synonyms()
    enrich_chebi_xrefs()


if __name__ == '__main__':
    enrich()
