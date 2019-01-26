# -*- coding: utf-8 -*-

"""A script for enriching the HBP terminology with external information."""

import pandas as pd
import pubchempy as pcp
from tqdm import tqdm

synonym_header = ['Identifier', 'Synonym', 'Reference', 'Specificity']


def enrich_pubchem_synonyms():
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
            pd.DataFrame(new_synonyms, columns=synonym_header),
        ])
            .drop_duplicates()
            .sort_values(synonym_header)
            .to_csv('synonyms.tsv', sep='\t', index=False)
    )


if __name__ == '__main__':
    enrich_pubchem_synonyms()
