# -*- coding: utf-8 -*-

"""A script to check the sanctity of the HBP resources."""

import csv
import os
import re
import sys
from collections import defaultdict
from typing import Iterable, Mapping, Optional, Set, Tuple

#: Path to this directory
HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir)

CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

HBP_IDENTIFIER = re.compile(r'^HBP(?P<number>\d{5})$')
IDENTIFIER_COLUMN = 0
NUMBER_TERM_COLUMNS = 6
CURATOR_COLUMN = 1
WITHDRAWN_COLUMN = 2
NAME_COLUMN = 2
TYPE_COLUMN = 3
REFERENCES_COLUMN = 4
DESCRIPTION_COLUMN = 5
VALID_CURATORS = {
    'Charlie',
    'Rana',
    'Sandra',
    'Lingling',
    'Esther',
    'Kristian',
    'Daniel',
}
VALID_SOURCES = {'pmc', 'pmid', 'doi', 'pubchem.compound', 'ncit'}
VALID_SYNONYM_TYPES = {'EXACT', 'BROAD', 'NARROW', 'RELATED', '?'}


def is_ascii(s: str) -> bool:
    """Check if a string only has ASCII characters in it."""
    return all(ord(c) < 128 for c in s)


def get_identifier_to_name(*, classes: Set[str]) -> Mapping[str, str]:
    """Generate a mapping from terms' identifiers to their names."""
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return dict(_get_terms_helper(reader, classes))


def _get_terms_helper(reader, classes: Set[str]) -> Iterable[Tuple[str, str]]:
    errors = 0

    def _print_fail(s):
        nonlocal errors
        errors += 1
        print(s)

    for i, line in enumerate(reader, start=2):
        if not line:
            continue

        if line[-1].endswith('\t') or line[-1].endswith(' '):
            _print_fail(f'{TERMS_PATH}: Trailing whitespace on line {i}')

        for column_number, column in enumerate(line, start=1):
            if column != column.strip():
                _print_fail(f'{TERMS_PATH}, line {i}, column {column_number}: Extra white space: {column}')

        identifier = line[IDENTIFIER_COLUMN]
        match = HBP_IDENTIFIER.match(identifier)

        if match is None:
            _print_fail(f'{TERMS_PATH}, line {i}: Invalid identifier chosen: {line}')
            continue

        current_number = int(match.groups()[0])
        if i - 1 != current_number:  # current_number <= last_number:
            _print_fail(f'{TERMS_PATH}, line {i}: Indexing scheme broken: {identifier}')
            continue

        if i > 346 and not is_ascii(line[NAME_COLUMN]):  # introduced later
            _print_fail(f'{TERMS_PATH}, line {i}: Name contains non-ascii: {line[NAME_COLUMN]}')

        if line[CURATOR_COLUMN] not in VALID_CURATORS:
            _print_fail(f'{TERMS_PATH}, line {i}: Invalid curator: {line[CURATOR_COLUMN]}')

        if len(line) < NUMBER_TERM_COLUMNS:
            _print_fail(
                f'{TERMS_PATH}, line {i}: Not enough fields (only found {len(line)}/{NUMBER_TERM_COLUMNS}): {line}')
            continue

        if len(line) > NUMBER_TERM_COLUMNS:
            _print_fail(f'{TERMS_PATH}, line {i}: Too many fields '
                        f'(found {len(line)}/{NUMBER_TERM_COLUMNS}) on line {i}: {line}')
            continue

        if line[WITHDRAWN_COLUMN] == 'WITHDRAWN':
            print(f'note: {identifier} was withdrawn')
            if not all(entry == '.' for entry in line[WITHDRAWN_COLUMN + 1:]):
                _print_fail(f'{TERMS_PATH}: Wrong formatting for withdrawn term line {i}: '
                            f'Use periods as placeholders.')
            continue

        if any(not column for column in line):
            _print_fail(f'{TERMS_PATH}, line {i}: Missing entries: {line}')
            continue

        if line[TYPE_COLUMN] not in classes:
            _print_fail(f'{TERMS_PATH}, line {i}: Invalid class: {line[TYPE_COLUMN]}.')
            continue

        references = line[REFERENCES_COLUMN].split(',')
        references_split = [reference.strip().split(':') for reference in references]

        if not all(len(reference) == 2 for reference in references_split):
            _print_fail(f'{TERMS_PATH}, line {i}: problematic references: {references_split}')
            continue

        if any(len(x) != 2 for x in references_split):
            _print_fail(f'{TERMS_PATH}, line {i}: missing reference {references_split}')
            continue

        if any(source not in VALID_SOURCES for source, reference in references_split):
            _print_fail(
                f'{TERMS_PATH}, line {i} : invalid reference type '
                f'(note: always use lowercase pmid, pmc, etc.): {references_split}'
            )
            continue

        if '"' in line[DESCRIPTION_COLUMN]:
            _print_fail(f'{TERMS_PATH}, line {i}: can not use double quote in description column')
            continue

        yield identifier, line[NAME_COLUMN]

    if errors:
        print(f'Found {errors} errors. Exiting with code: 1')
        sys.exit(1)


def get_types() -> Set[str]:
    """Get the set of all types used in CONSO."""
    with open(CLASSES_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return {
            line[0]
            for line in _get_types_helper(reader)
        }


def _get_types_helper(lines: Iterable[Tuple[str, ...]]):
    last_line = next(lines)
    yield last_line[0].strip()

    for i, line in enumerate(lines, start=3):
        if line[0].strip() != line[0]:
            raise ValueError(f'{CLASSES_PATH}: Extra spacing around first entry in line {i}: {line}')

        if line[0] < last_line[0]:
            raise ValueError(f'{CLASSES_PATH}: Not sorted properly on line {i}: {line}')

        yield line
        last_line = line


def check_xrefs_file(*, identifier_to_name: Mapping[str, str]):
    """Validate the cross-references file."""
    with open(XREFS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        yield from _check_xrefs_file_helper(reader, identifier_to_name)


def _check_xrefs_file_helper(reader, identifier_to_name: Mapping[str, str]):
    current_identifier = 0
    for i, line in enumerate(reader, start=2):
        if len(line) != 3:
            raise Exception(f'{XREFS_PATH}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{XREFS_PATH}: Missing entries on line {i}: {line}')

        term = line[0]

        if term not in identifier_to_name:
            raise Exception(f'{XREFS_PATH}: Invalid identifier on line {i}: {term}')

        new_identifier = int(HBP_IDENTIFIER.match(term).groups()[0])
        if new_identifier < current_identifier:
            raise Exception(f'{XREFS_PATH}: Not monotonic increasing on line {i}: {term}')
        current_identifier = new_identifier

        yield line


def check_synonyms_file(*, identifier_to_name: Mapping[str, str]):
    """Validate the synonyms file."""
    with open(SYNONYMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return list(_check_synonyms_helper(reader, identifier_to_name))


def _check_synonyms_helper(reader, identifier_to_name: Mapping[str, str]):
    current_identifier = 0
    for i, line in enumerate(reader, start=2):
        if line[-1].rstrip() != line[-1]:
            raise Exception(f'{SYNONYMS_PATH}: Trailing whitespace on line {i}')

        if len(line) != 4:
            raise Exception(f'{SYNONYMS_PATH}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{SYNONYMS_PATH}: Missing entries on line {i}: {line}')

        term = line[0]

        if term not in identifier_to_name:
            raise Exception(f'{SYNONYMS_PATH}: Invalid identifier on line {i}: {term}')

        new_identifier = int(HBP_IDENTIFIER.match(term).groups()[0])
        if new_identifier < current_identifier:
            raise Exception(f'{SYNONYMS_PATH}: Not monotonic increasing on line {i}: {term}')
        current_identifier = new_identifier

        specificity = line[3]
        if specificity not in VALID_SYNONYM_TYPES:
            raise Exception(f'{SYNONYMS_PATH}: Invalid specificity on line {i}: {specificity}')

        yield line


def check_relations_file(*, identifier_to_name: Mapping[str, str]):
    """Validate the relations file."""
    with open(RELATIONS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        return list(_check_relations_file_helper(RELATIONS_PATH, reader, identifier_to_name))


def _check_relations_file_helper(path, reader, identifier_to_name: Mapping[str, str]) -> Tuple[str, ...]:
    for i, line in enumerate(reader, start=2):
        if len(line) != 7:
            raise Exception(f'{path}: Not the right number fields (found {len(line)}) on line {i}: {line}')

        if any(not column for column in line):
            raise Exception(f'{path}: Missing entries on line {i}: {line}')

        source_namespace = line[0]
        source_identifier = line[1]
        if source_namespace == 'HBP' and source_identifier not in identifier_to_name:
            raise Exception(f'{path}: Invalid source identifier on line {i}: {source_identifier}')

        target_namespace = line[4]
        target_identifier = line[5]
        if target_namespace == 'HBP' and target_identifier not in identifier_to_name:
            raise Exception(f'{path}: Invalid target identifier on line {i}: {target_identifier}')

        yield line


def check_class_has_xref(cls, xrefs) -> None:
    """Check that members of a given class have certain cross-references."""
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        entries = {
            hbp_id: ('HBP', hbp_id, name)
            for hbp_id, curator, name, _cls, refs, definition in reader
            if _cls == cls
        }

    db_map = defaultdict(dict)
    with open(XREFS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for hbp_id, db, db_id in reader:
            if db_id in {'?', '', 'N/A', 'n/a'}:
                continue

            db_map[db][hbp_id] = db_id

    if isinstance(xrefs, str):
        xrefs = [xrefs]
    for xref in xrefs:
        _check_missing_xref(cls, entries, db_map, xref)


def check_class_has_relation(cls: str,
                             relation: str,
                             object_namespace: Optional[str] = None
                             ) -> None:
    """Check that members of the given class have a given relation with a cardinality of 1."""
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        entries = {
            ('HBP', hbp_id, name)
            for hbp_id, curator, name, cls_, refs, definition in reader
            if cls_ == cls
        }

    with open(RELATIONS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        rd = defaultdict(lambda: defaultdict(list))
        for source_ns, source_id, source_name, rel, target_ns, target_id, target_name in reader:
            rd[rel][source_ns, source_id, source_name].append((target_ns, target_id, target_name))

    missing_role = {
        entry
        for entry in entries
        if entry not in rd[relation]
    }
    if missing_role:
        s = 29 + len(relation) + len(cls)
        print('', '#' * s, f'# {cls} missing relation {relation} ({len(missing_role)}/{len(entries)}) #', '#' * s,
              sep='\n')
        for entry in sorted(missing_role):
            print(*entry, relation, object_namespace or '?', '?', '?', sep='\t')


def check_chemical_roles():
    """Check that all chemicals have at least one role."""
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        chemicals = {
            ('HBP', hbp_id, name)
            for hbp_id, curator, name, cls, refs, definition in reader
            if cls == 'chemical'
        }

    with open(RELATIONS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        roles = defaultdict(list)
        inhibitors = defaultdict(list)
        agonists = defaultdict(list)
        antagonists = defaultdict(list)
        for source_ns, source_id, source_name, rel, target_ns, target_id, target_name in reader:
            if rel == 'has_role':
                roles[source_ns, source_id, source_name].append((target_ns, target_id, target_name))
            elif rel == 'inhibitor_of':
                inhibitors[source_ns, source_id, source_name].append((target_ns, target_id, target_name))
            elif rel == 'agonist_of':
                agonists[source_ns, source_id, source_name].append((target_ns, target_id, target_name))
            elif rel == 'antagonist_of':
                antagonists[source_ns, source_id, source_name].append((target_ns, target_id, target_name))

    missing_role = {
        chemical
        for chemical in chemicals
        if all(chemical not in d for d in (roles, inhibitors, agonists, antagonists))
    }
    if missing_role:
        print('', '#' * 25, f'# Missing roles ({len(missing_role)}/{len(chemicals)}) #', '#' * 25, sep='\n')
        for chemical in sorted(missing_role):
            print(f'{":".join(chemical[1:])}')


def check_chemical_structures() -> None:
    """Check that all chemicals have an InChI and SMILES structure."""
    xrefs = [
        'inchi',
        'smiles',
        # 'chebi',
        # 'cas',
    ]
    check_class_has_xref('chemical', xrefs)


def _check_missing_xref(cls: str,
                        entries: Mapping[str, Tuple[str, str, str]],
                        db_map: Mapping[str, Mapping[str, str]],
                        db: str,
                        ) -> None:
    missing_entries = {
        entry
        for entry in entries
        if entry not in db_map[db]
    }
    if missing_entries:
        ratio = f'{len(missing_entries)}/{len(entries)}'
        n_spacers = 24 + len(ratio) + len(db) + len(cls)
        print('', '#' * n_spacers, f'# {cls} missing xref to {db} ({ratio}) #', '#' * n_spacers, sep='\n')
        for entry in sorted(missing_entries):
            print(*entries[entry][1:], db, '?', sep='\t')


def main():
    """Run the check on the terms, synonyms, and xrefs."""
    classes = get_types()
    identifier_to_name = get_identifier_to_name(classes=classes)

    check_synonyms_file(identifier_to_name=identifier_to_name)
    check_xrefs_file(identifier_to_name=identifier_to_name)
    check_relations_file(identifier_to_name=identifier_to_name)

    check_class_has_xref('isoform', 'uniprot.isoform')
    check_class_has_relation('isoform', 'has_reference_protein', object_namespace='uniprot')
    check_class_has_relation('protein isoform family', 'has_reference_protein', object_namespace='uniprot')
    check_chemical_structures()
    check_chemical_roles()
    check_class_has_relation('antibody', 'has_antibody_target')

    sys.exit(0)


if __name__ == '__main__':
    main()
