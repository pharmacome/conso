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
OUTPUT_NAME_FILE_PATH = os.path.join(HERE, 'hbp-names.belns')


def _get_terms() -> List[str]:
    return [line[0] for line in _get_lines() if line]


def _get_labels() -> List[str]:
    return [line[1] for line in _get_lines() if line]


def _get_lines() -> List[str]:
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        yield from reader


def _write_namespace(path, values: Iterable[str]):
    with open(path, 'w') as file:
        write_namespace(
            namespace_name='Human Brain Pharmacome Terminology',
            namespace_keyword='HBP',
            namespace_domain=NAMESPACE_DOMAIN_OTHER,
            author_name='Charles Tapley Hoyt',
            citation_name='HBP',
            values=values,
            namespace_description='The Human Brain Pharmacome Terminology contains terms related to neurodegenerative '
                                  'disease and curation of related material. It is not disease-specific, but at least'
                                  'has a focus on Alzheimer\'s disease.',
            author_copyright='CC0 1.0 Universal',
            case_sensitive=True,
            cacheable=True,
            file=file,
        )


if __name__ == '__main__':
    _write_namespace(OUTPUT_FILE_PATH, _get_terms())
    _write_namespace(OUTPUT_NAME_FILE_PATH, _get_labels())
