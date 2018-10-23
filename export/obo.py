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
RELATIONS_PATH = os.path.join(HERE, os.pardir, 'relations.tsv')


@dataclass
class Reference:
    ns: str
    id: str
    name: Optional[str] = None

    def __str__(self):
        if self.name:
            return f'{self.ns}:{self.id} ! {self.name}'
        return f'{self.ns}:{self.id}'


@dataclass
class Synonym:
    name: str
    status: str
    references: Optional[List[str]] = None


class Term:
    """Represents a term in OBO."""

    def __init__(self,
                 term_id: Reference,
                 name: str,
                 description: str,
                 references: List[Reference],
                 relationships: Optional[Mapping[str, List[Reference]]] = None,
                 synonyms: Optional[List[Synonym]] = None,
                 xrefs: Optional[List[Reference]] = None
                 ) -> None:
        self.term_id = term_id
        self.name = name
        self.description = description
        self.references = references

        self.synonyms = synonyms or []
        self.xrefs = xrefs or []
        self.relationships = relationships or {}

    def to_obo(self) -> str:
        """Convert this term to an OBO entry."""
        obo_str = f'''[Term]
id: {self.term_id.ns}:{self.term_id.id}
name: {self.name}
def: "{self.description}" [{', '.join(map(str,self.references))}]
'''
        for synonym in self.synonyms:
            synonym_references_string = ', '.join(synonym.references)
            obo_str += f'synonym: "{synonym.name}" {synonym.status} [{synonym_references_string}]\n'

        for xref in self.xrefs:
            if xref.ns == 'BEL':
                entry = f'BEL:"{xref.id}"'
            else:
                entry = f'{xref.ns}:{xref.id}'

            obo_str += f'xref: {entry}\n'

        for relationship, references in self.relationships.items():
            for reference in references:
                obo_str += f'{relationship}: {reference}\n'

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
                term_id=Reference(HBP, hbp_id, label),
                name=label,
                references=[Reference(*pmid.strip().split(':')) for pmid in references.split(',')],
                description=description
            )
            for hbp_id, label, references, description in reader
            if label != 'WITHDRAWN'
        }

    with open(SYNONYMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for hbp_id, synonym, references, specificity in reader:
            references = (
                [r.strip() for r in references.split(',')]
                if references and references != '?' else
                []
            )
            specificity = (
                'EXACT' if specificity == '?' else specificity
            )
            terms[hbp_id].synonyms.append(Synonym(synonym, specificity, references))

    with open(XREFS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for hbp_id, database, identifier in reader:
            terms[hbp_id].xrefs.append(Reference(database, identifier))

    with open(RELATIONS_PATH) as file:
        reader = enumerate(csv.reader(file, delimiter='\t'), start=1)
        _ = next(reader)  # skip the header
        for line, (source_ns, source_id, source_label, relation, target_ns, target_id, target_label) in reader:
            if relation not in {'is_a', }:
                print(f'can not handle line {line}')
                continue

            if source_ns != HBP or target_ns != HBP:
                print(f'can not currently handle line {line} becuase not using HBP namespace')
                continue

            if relation not in terms[source_id].relationships:
                terms[source_id].relationships[relation] = []
            terms[source_id].relationships[relation].append(Reference(target_ns, target_id, target_label))

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
