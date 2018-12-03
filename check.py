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
NUMBER_TERM_COLUMNS = 6
CURATOR_COLUMN = 1
WITHDRAWN_COLUMN = 2
NAME_COLUMN = 2
TYPE_COLUMN = 3
REFERENCES_COLUMN = 4
DESCRIPTION_COLUMN = 5
CURATORS = {
    'Charlie',
    'Rana',
    'Sandra',
    'Lingling',
    'Esther',
    'Kristian',
    'Daniel'
}


def get_terms(path: str, classes: Set[str]) -> Iterable[str]:
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        yield from _get_terms_helper(path, reader, classes)


def _get_terms_helper(path: str, reader, classes: Set[str]) -> Iterable[str]:
    error = False

    def print_fail(*args, **kwargs):
        nonlocal error
        error = True
        print(*args, **kwargs)

    for i, line in enumerate(reader, start=1):
        if not line:
            continue

        if line[-1].endswith('\t') or line[-1].endswith(' '):
            print_fail(f'{path}: Trailing whitespace on line {i}')

        term = line[0]
        match = HBP_IDENTIFIER.match(term)

        if match is None:
            print_fail(f'{path}, line {i}: Invalid identifier chosen: {line}')
            continue

        current_number = int(match.groups()[0])
        if i != current_number:  # current_number <= last_number:
            print_fail(f'{path}, line {i}: Indexing scheme broken: {term}')
            continue

        if line[CURATOR_COLUMN] not in CURATORS:
            print_fail(f'{path}, line {i}: Invalid curator: {line[0]}')

        if len(line) < NUMBER_TERM_COLUMNS:
            print_fail(f'{path}, line {i}: Not enough fields (only found {len(line)}/{NUMBER_TERM_COLUMNS}): {line}')
            continue

        if len(line) > NUMBER_TERM_COLUMNS:
            print_fail(f'{path}, line {i}: Too many fields '
                       f'(found {len(line)}/{NUMBER_TERM_COLUMNS}) on line {i}: {line}')
            continue

        if line[WITHDRAWN_COLUMN] == 'WITHDRAWN':
            print_fail(f'{term} was withdrawn')
            if not all(entry == '.' for entry in line[WITHDRAWN_COLUMN + 1:]):
                print_fail(f'{path}: Wrong formatting for withdrawn term line {i}: '
                           f'Use periods as placeholders.')
            continue

        if any(not column for column in line):
            print_fail(f'{path}, line {i}: Missing entries: {line}')
            continue

        if line[TYPE_COLUMN] not in classes:
            print_fail(f'{path}, line {i}: Invalid class: {line[2]}')
            continue

        references = line[REFERENCES_COLUMN].split(',')
        references_split = [reference.strip().split(':') for reference in references]

        if not all(len(reference) == 2 for reference in references_split):
            print_fail(f'{path}, line {i}: problematic references: {references_split}')
            continue

        if any(len(x) != 2 for x in references_split):
            print_fail(f'{path}, line {i}: missing reference {references_split}')
            continue

        if any(source not in {'pmc', 'pmid', 'doi'} for source, reference in references_split):
            print_fail(
                f'{path}, line {i} : invalid reference type '
                f'(note: always use lowercase pmid, pmc, etc.): {references_split}'
            )
            continue

        if '"' in line[DESCRIPTION_COLUMN]:
            print_fail(f'{path}, line {i}: can not use double quote in description column')
            continue

        yield term

    if error:
        sys.exit(1)


def get_classes(path: str) -> Set[str]:
    with open(os.path.join(HERE, path)) as file:
        return {
            line.strip()
            for line in file
        }


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
    classes = set(get_classes('classes.tsv'))
    terms = set(get_terms('terms.tsv', classes))

    check_synonyms_file('synonyms.tsv', terms)
    check_xrefs_file('xrefs.tsv', terms)
    check_relations_file('relations.tsv', terms)

    sys.exit(0)


if __name__ == '__main__':
    main()
