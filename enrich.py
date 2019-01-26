# -*- coding: utf-8 -*-

"""A script for enriching the HBP terminology with external information."""

import pandas as pd
from tqdm import tqdm

SYNONYM_HEADER = ['Identifier', 'Synonym', 'Reference', 'Specificity']
XREFS_HEADER = ['HBP Identifier', 'Database', 'Database Identifier']


def enrich_pubchem_synonyms():
    """Enrich synonyms.tsv with information from PubChem."""
    import pubchempy as pcp

    xrefs = pd.read_csv('xrefs.tsv', sep='\t')
    xrefs = xrefs[xrefs['Database'] == 'pubchem.compound']
    cid_to_hbp = pd.Series(xrefs['HBP Identifier'].values, index=xrefs['Database Identifier']).to_dict()

    new_synonyms = [
        (
            cid_to_hbp[cid],
            synonym,
            f'pubchem.compound:{cid}',
            'EXACT',
        )
        for cid in tqdm(cid_to_hbp)
        for synonym in pcp.Compound.from_cid(cid).synonyms
    ]

    (
        pd.concat([
            pd.read_csv('synonyms.tsv', sep='\t'),
            pd.DataFrame(new_synonyms, columns=SYNONYM_HEADER),
        ])
            .drop_duplicates()
            .sort_values(SYNONYM_HEADER)
            .to_csv('synonyms.tsv', sep='\t', index=False)
    )
