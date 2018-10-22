# -*- coding: utf-8 -*-

"""Export the Human Brain Pharmacome terminology to OBO."""

import csv
import datetime
import os
from dataclasses import dataclass
from typing import List, Mapping, Optional, TextIO

HERE = os.path.dirname(os.path.abspath(__file__))

HBP = 'HBP'

TERMS_PATH = os.path.join(HERE, os.pardir, 'terms.tsv')
SYNONYMS_PATH = os.path.join(HERE, os.pardir, 'synonyms.tsv')
XREFS_PATH = os.path.join(HERE, os.pardir, 'xrefs.tsv')


@dataclass
class Reference:
    ns: str
    id: str


@dataclass
class Synonym:
    name: str
    status: str


class Term:
    """Represents a term in OBO."""

    def __init__(self,
                 term_id: Reference,
                 name: str,
                 description: str,
                 relationships: Optional[Mapping] = None,
                 synonyms: Optional[List[Synonym]] = None,
                 xrefs: Optional[List[Reference]] = None
                 ) -> None:
        self.term_id = term_id
        self.name = name
        self.description = description

        self.synonyms = synonyms or []
        self.xrefs = xrefs or []
        self.relationships = relationships or {}

    def to_obo(self) -> str:
        """Convert this term to an OBO entry."""
        obo_str = f'''[Term]
id: {self.term_id.ns}:{self.term_id.id}
name: {self.name}
'''

        for synonym in self.synonyms:
            obo_str += f'synonym: "{synonym.name}" {synonym.status} []\n'

        for xref in self.xrefs:
            if xref.ns == 'BEL':
                entry = f'BEL:"{xref.id}"'
            else:
                entry = f'{xref.ns}:{xref.id}'

            obo_str += f'xref: {entry}\n'

        for relationship_type, rel_entries in self.relationships.items():
            for ref in rel_entries:
                obo_str += '%s: %s:%s\n' % (relationship_type, ref.ns, ref.id)

        return obo_str

    def __str__(self):
        return self.to_obo()


def get_obo_terms() -> List[Term]:
    """Get OBO terms."""
    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        terms = {
            hbp_id: Term(
                term_id=Reference(HBP, hbp_id),
                name=label,
                xrefs=[Reference(*pmid.strip().split(':')) for pmid in references.split(',')],
                description=description
            )

            for hbp_id, label, references, description in reader
            if label != 'WITHDRAWN'
        }

    with open(SYNONYMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for hbp_id, synonym, reference in reader:
            terms[hbp_id].synonyms.append(Synonym(synonym, 'EXACT'))

    with open(XREFS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for hbp_id, database, identifier in reader:
            terms[hbp_id].xrefs.append(Reference(database, identifier))

    return list(terms.values())


def dump_obo_terms(terms: List[Term], file: TextIO):
    date = datetime.datetime.today()
    date_str = date.strftime('%d:%m:%Y %H:%M')

    print('format-version: 1.2', file=file)
    print(f'date: {date_str}', file=file)
    print('', file=file)

    for term in terms:
        obo_str = term.to_obo()
        print(obo_str, file=file)


if __name__ == '__main__':
    output_path = os.path.join(HERE, 'hbp.obo')
    obo_terms = get_obo_terms()
    with open(output_path, 'w') as output_file:
        dump_obo_terms(obo_terms, output_file)
