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


def get_terms() -> Iterable[str]:
    with open(os.path.join(HERE, 'terms.tsv')) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        last_number = 0

        for i, line in enumerate(reader, start=1):
            if not line:
                continue

            if line[-1].endswith('\t') or line[-1].endswith(' '):
                raise Exception(f'terms.csv: Trailing whitespace on line {i}')

            if len(line) < 4:
                raise Exception(f'terms.csv: Not enough fields (only found {len(line)}) on line {i}: {line}')

            if len(line) > 4:
                raise Exception(f'terms.csv: Too many fields (found {len(line)}) on line {i}: {line}')

            if any(not column for column in line):
                raise Exception(f'terms.csv: Missing entries on line {i}: {line}')

            term = line[0]

            match = HBP_IDENTIFIER.match(term)

            if match is None:
                raise Exception(f'terms.csv: Invalid identifier chosen on line {i}: {line}')

            current_number = int(match.groups()[0])
            if i != current_number:  # current_number <= last_number:
                raise Exception(f'terms.csv: Indexing scheme broken on line {i}: {term}')

            # last_number = current_number

            references = line[2].split(',')
            references_split = [reference.strip().split(':') for reference in references]

            if any(len(x) != 2 for x in references_split):
                raise Exception(f'terms.csv, line {i}: missing reference {references_split}')

            if any(source not in {'pmc', 'pmid', 'doi'} for source, reference in references_split):
                raise Exception(f'terms.csv, line {i} : invalid reference type (note: always use lowercase pmid, pmc, etc.): {references_split}')

            yield term


def check_cross_referenced_file(path: str, expected_size: int, terms: Set[str]):
    with open(os.path.join(HERE, path)) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        for i, line in enumerate(reader):
            if len(line) != expected_size:
                raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

            if any(not column for column in line):
                raise Exception(f'{path}: Missing entries on line {i}: {line}')

            term = line[0]

            if term not in terms:
                raise Exception(f'{path}: Invalid identifier on line {i}: {term}')


def main():
    """Run the check on the terms, synonyms, and xrefs."""
    terms = set(get_terms())

    check_cross_referenced_file('synonyms.tsv', 3, terms)
    check_cross_referenced_file('xrefs.tsv', 3, terms)

    sys.exit(0)


if __name__ == '__main__':
    main()
