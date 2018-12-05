# -*- coding: utf-8 -*-

"""A script to check the sanctity of the HBP resources."""

import csv
import os
import re
import sys
from collections import defaultdict
from typing import Iterable, Set, Tuple

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
    'Daniel',
}


def get_terms(*, classes: Set[str], path: str = 'terms.tsv') -> Iterable[str]:
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return list(_get_terms_helper(path, reader, classes))


def _get_terms_helper(path: str, reader, classes: Set[str]) -> Iterable[str]:
    errors = 0

    def print_fail(s):
        nonlocal errors
        errors += 1
        print(s)

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
            # print(f'note: {term} was withdrawn')
            if not all(entry == '.' for entry in line[WITHDRAWN_COLUMN + 1:]):
                print_fail(f'{path}: Wrong formatting for withdrawn term line {i}: '
                           f'Use periods as placeholders.')
            continue

        if any(not column for column in line):
            print_fail(f'{path}, line {i}: Missing entries: {line}')
            continue

        if line[TYPE_COLUMN] not in classes:
            print_fail(f'{path}, line {i}: Invalid class: {line[TYPE_COLUMN]}.')
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

    if errors:
        print(f'Found {errors} errors. Exiting with code: 1')
        sys.exit(1)


def get_classes(*, path: str = 'classes.tsv') -> Set[str]:
    with open(os.path.join(HERE, path)) as file:
        return {
            line.strip()
            for line in file
        }


def check_xrefs_file(*, terms: Set[str], path: str = 'xrefs.tsv'):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        yield from _check_xrefs_file_helper(path, reader, terms)


def _check_xrefs_file_helper(path, reader, terms: Set[str]):
    for i, line in enumerate(reader, start=2):
        if len(line) != 3:
            raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        term = line[0]

        if term not in terms:
            raise Exception(f'{path}: Invalid identifier on line {i}: {term}')

        yield line


ALLOWED_SYNONYM_TYPES = {'EXACT', 'BROAD', 'NARROW', 'RELATED', '?'}


def check_synonyms_file(*, terms: Set[str], path: str = 'synonyms.tsv'):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return list(_check_synonyms_helper(path, reader, terms))


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

        yield line


def check_relations_file(*, terms: Set[str], path: str = 'relations.tsv'):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return list(_check_relations_file_helper(path, reader, terms))


def _check_relations_file_helper(path, reader, terms: Set[str]) -> Tuple[str, ...]:
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

        yield line


def check_chemical_roles():
    with open(os.path.join(HERE, 'terms.tsv')) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        chemicals = {
            (hbp_id, name)
            for hbp_id, curator, name, cls, refs, definition in reader
            if cls == 'chemical'
        }

    with open(os.path.join(HERE, 'relations.tsv')) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        roles = defaultdict(list)
        for source_ns, source_id, source_name, rel, target_ns, target_id, target_name in reader:
            if rel != 'has_role' or (source_id, source_name) not in chemicals:
                roles[source_id, source_name].append((target_id, target_name))

    for source_id, source_name in sorted(chemicals):
        if (source_id, source_name) not in roles:
            print(f'Missing role: HBP:{source_id} "{source_name}"')


def main():
    """Run the check on the terms, synonyms, and xrefs."""
    classes = set(get_classes())
    terms = set(get_terms(classes=classes))

    check_synonyms_file(terms=terms)
    check_xrefs_file(terms=terms)
    check_relations_file(terms=terms)

    check_chemical_roles()

    sys.exit(0)


if __name__ == '__main__':
    main()
