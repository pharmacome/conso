# -*- coding: utf-8 -*-

"""Export the Curation of Neurodegeneration Supporting Ontology (CONSO) to BELNS."""

import argparse
import csv
import os
from typing import List, Mapping, Optional

from bel_resources import write_namespace
from bel_resources.constants import NAMESPACE_DOMAIN_OTHER

#: Path to this directory
HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir, os.pardir)

TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))

OUTPUT_FILE_PATH = os.path.abspath(os.path.join(ROOT, 'export', 'hbp.belns'))
OUTPUT_NAME_FILE_PATH = os.path.abspath(os.path.join(ROOT, 'export', 'hbp-names.belns'))


def _get_classes() -> Mapping[str, str]:
    with open(CLASSES_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return {
            line[0].strip(): line[1].strip()
            for line in reader
        }


def _get_terms() -> Mapping[str, str]:
    classes = _get_classes()
    return {
        line[0]: classes[line[3]]
        for line in _get_lines()
    }


def _get_labels() -> Mapping[str, str]:
    classes = _get_classes()
    return {
        line[2]: classes[line[3]]
        for line in _get_lines()
    }


def _get_lines() -> List[str]:
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for line in reader:
            if not line or line[2] == 'WITHDRAWN':
                continue
            yield line


def _write_namespace(path, values: Mapping[str, str], namespace_version: Optional[str] = None):
    with open(path, 'w') as file:
        write_namespace(
            namespace_name='Human Brain Pharmacome Terminology',
            namespace_keyword='HBP',
            namespace_domain=NAMESPACE_DOMAIN_OTHER,
            namespace_version=namespace_version,
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


def main(identifiers_path: Optional[str] = None, names_path: Optional[str] = None) -> None:
    """Export CONSO as BELNS."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--version')
    args = parser.parse_args()

    _write_namespace(identifiers_path or OUTPUT_FILE_PATH, _get_terms(), namespace_version=args.version)
    _write_namespace(names_path or OUTPUT_NAME_FILE_PATH, _get_labels(), namespace_version=args.version)


if __name__ == '__main__':
    main()
