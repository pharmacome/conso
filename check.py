# -*- coding: utf-8 -*-

"""A script to check the sanctity of the HBP resources."""

import csv
import os
import re
import sys
from typing import Iterable, Set

#: Path to this directory
HERE = os.path.abspath(os.path.dirname(__file__))

HBP_IDENTIFIER = re.compile('^HBP(?P<number>\d{5})$')


def get_terms(path: str) -> Iterable[str]:
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        yield from _get_terms_helper(path, reader)


def _get_terms_helper(path, reader):
    for i, line in enumerate(reader, start=1):
        if not line:
            continue

        if line[-1].endswith('\t') or line[-1].endswith(' '):
            raise Exception(f'{path}: Trailing whitespace on line {i}')

        term = line[0]
        match = HBP_IDENTIFIER.match(term)

        if match is None:
            raise Exception(f'{path}: Invalid identifier chosen on line {i}: {line}')

        current_number = int(match.groups()[0])
        if i != current_number:  # current_number <= last_number:
            raise Exception(f'{path}: Indexing scheme broken on line {i}: {term}')

        if len(line) < 4:
            raise Exception(f'{path}: Not enough fields (only found {len(line)}) on line {i}: {line}')

        if len(line) > 4:
            raise Exception(f'{path}: Too many fields (found {len(line)}) on line {i}: {line}')

        if line[1] == 'WITHDRAWN':
            print(f'{term} was withdrawn')
            if line[2] != '.' or line[3] != '.':
                raise Exception(f'{path}: Wrong formatting for withdrawn term line {i}: '
                                f'Use periods as placeholders.')
            continue

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        references = line[2].split(',')
        references_split = [reference.strip().split(':') for reference in references]

        if any(len(x) != 2 for x in references_split):
            raise Exception(f'{path}, line {i}: missing reference {references_split}')

        if any(source not in {'pmc', 'pmid', 'doi'} for source, reference in references_split):
            raise Exception(
                f'{path}, line {i} : invalid reference type '
                f'(note: always use lowercase pmid, pmc, etc.): {references_split}'
            )

        if '"' in line[3]:
            raise Exception(f'{path}, line {i}: can not use double quote in description column')

        yield term


def check_xrefs_file(path: str, terms: Set[str]):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        _check_xrefs_file_helper(path, reader, terms)


def _check_xrefs_file_helper(path, reader, terms: Set[str]):
    for i, line in enumerate(reader, start=2):
        if len(line) != 3:
            raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        term = line[0]

        if term not in terms:
            raise Exception(f'{path}: Invalid identifier on line {i}: {term}')


ALLOWED_SYNONYM_TYPES = {'EXACT', 'BROAD', 'NARROW', 'RELATED', '?'}


def check_synonyms_file(path: str, terms: Set[str]):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        _check_synonyms_helper(path, reader, terms)


def _check_synonyms_helper(path, reader, terms: Set[str]):
    for i, line in enumerate(reader, start=2):
        if len(line) != 4:
            raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        term = line[0]
        if term not in terms:
            raise Exception(f'{path}: Invalid identifier on line {i}: {term}')

        specificity = line[3]
        if specificity not in ALLOWED_SYNONYM_TYPES:
            raise Exception(f'{path}: Invalid specificity on line {i}: {specificity}')


def check_relations_file(path: str, terms: Set[str]):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        _check_relations_file_helper(path, reader, terms)


def _check_relations_file_helper(path, reader, terms: Set[str]):
    for i, line in enumerate(reader, start=2):
        if len(line) != 7:
            raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        source_namespace = line[0]
        source_identifier = line[1]
        if source_namespace == 'HBP' and source_identifier not in terms:
            raise Exception(f'{path}: Invalid source identifier on line {i}: {source_identifier}')

        target_namespace = line[4]
        target_identifier = line[5]
        if target_namespace == 'HBP' and target_identifier not in terms:
            raise Exception(f'{path}: Invalid target identifier on line {i}: {target_identifier}')


def main():
    """Run the check on the terms, synonyms, and xrefs."""
    terms = set(get_terms('terms.tsv'))

    check_synonyms_file('synonyms.tsv', terms)
    check_xrefs_file('xrefs.tsv', terms)
    check_relations_file('relations.tsv', terms)

    sys.exit(0)


if __name__ == '__main__':
    main()
