# -*- coding: utf-8 -*-

"""Functions for maintaining a healthy ontology."""

import json
from collections import defaultdict

import pandas as pd
import requests

from .resources import TERMS_PATH, XREFS_PATH

GILDA_URL = 'http://34.201.164.108:8001'


def post_gilda(text: str, url: str = GILDA_URL) -> requests.Response:
    """Send text to GILDA."""
    return requests.post(f'{url}/ground', json={'text': text})


def find_new_xrefs():
    """Look up entities without xrefs using GILDA and propose groundings."""
    xrefs = pd.read_csv(XREFS_PATH, sep='\t')
    d = defaultdict(list)
    for conso_id, db, db_id in xrefs.values:
        d[conso_id].append((db, db_id))

    terms = pd.read_csv(TERMS_PATH, sep='\t')
    for conso_id, author, name, *_ in terms.values:
        if conso_id not in d:

            res = post_gilda(name).json()
            if res:
                print(f'{conso_id} {name} curated by {author}')
                print(json.dumps(res, indent=2))


if __name__ == '__main__':
    find_new_xrefs()
