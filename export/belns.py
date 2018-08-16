# -*- coding: utf-8 -*-

import csv
import os
from typing import Iterable, List

from pybel.constants import NAMESPACE_DOMAIN_OTHER
from pybel.resources import write_namespace

#: Path to this directory
HERE = os.path.abspath(os.path.dirname(__file__))

TERMS_PATH = os.path.abspath(os.path.join(os.pardir, 'terms.tsv'))
OUTPUT_FILE_PATH = os.path.join(HERE, 'hbp.belns')


def _get_terms() -> List[str]:
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        return [line[0] for line in reader]


def _write_namespace(values: Iterable[str]):
    with open(OUTPUT_FILE_PATH, 'w') as file:
        write_namespace(
            namespace_name='HBP',
            namespace_keyword='HBP',
            namespace_domain=NAMESPACE_DOMAIN_OTHER,
            author_name='Charles Tapley Hoyt',
            citation_name='HBP',
            values=values,
            namespace_description='Human Brain Pharmacome Terminology.',
            author_copyright='CC0 1.0 Universal',
            case_sensitive=True,
            cacheable=True,
            file=file,
        )


if __name__ == '__main__':
    entities = _get_terms()
    _write_namespace(entities)
