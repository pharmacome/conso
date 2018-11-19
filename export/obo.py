# -*- coding: utf-8 -*-

"""Export the Human Brain Pharmacome terminology to OBO."""

import csv
import datetime
import os
from dataclasses import dataclass
from typing import List, Mapping, Optional, TextIO

HERE = os.path.dirname(os.path.abspath(__file__))

HBP = 'HBP'

TERMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'relations.tsv'))

INVERSE_RELATIONS = {
    'is_a': 'inverse_is_a',
    'part_of': 'has_part',
}


@dataclass
class Reference:
    namespace: str
    identifier: str
    name: Optional[str] = None

    def __str__(self):
        if self.name:
            return f'{self.namespace}:{self.identifier} ! {self.name}'
        return f'{self.namespace}:{self.identifier}'


@dataclass
class Synonym:
    name: str
    specificity: str
    references: Optional[List[str]] = None


class Term:
    """Represents a term in OBO."""

    def __init__(self,
                 reference: Reference,
                 description: str,
                 provenance: List[Reference],
                 relationships: Optional[Mapping[str, List[Reference]]] = None,
                 synonyms: Optional[List[Synonym]] = None,
                 xrefs: Optional[List[Reference]] = None
                 ) -> None:
        self.reference = reference
        self.description = description
        self.provenance = provenance

        self.synonyms = synonyms or []
        self.xrefs = xrefs or []
        self.relationships = relationships or {}

    def to_obo(self) -> str:
        """Convert this term to an OBO entry."""
        obo_str = f'''[Term]
id: {self.reference.namespace}:{self.reference.identifier}
name: {self.reference.name}
def: "{self.description}" [{', '.join(map(str,self.provenance))}]
'''
        for synonym in self.synonyms:
            synonym_references_string = ', '.join(synonym.references)
            obo_str += f'synonym: "{synonym.name}" {synonym.specificity} [{synonym_references_string}]\n'

        for xref in self.xrefs:
            if xref.namespace == 'BEL':
                entry = f'BEL:"{xref.identifier}"'
            else:
                entry = str(xref)

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
            hbp_identifier: Term(
                reference=Reference(namespace=HBP, identifier=hbp_identifier, name=name),
                provenance=[Reference(*pmid.strip().split(':')) for pmid in references.split(',')],
                description=description,
            )
            for hbp_identifier, name, references, description in reader
            if name != 'WITHDRAWN'
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
        for line, (source_ns, source_id, source_name, relation, target_ns, target_id, target_name) in reader:
            if relation not in {'is_a', 'part_of'}:
                print(f'{RELATIONS_PATH} can not handle line {line} because unhandled relation: {relation}')
                continue

            if source_ns != HBP and target_ns != HBP:
                print(f'{RELATIONS_PATH}: skipping line {line} because neither entity is from HBP')
                continue

            if source_ns != HBP:
                relation = INVERSE_RELATIONS[relation]
                source_ns, source_id, source_name, target_ns, target_id, target_name = target_ns, target_id, target_name, source_ns, source_id, source_name

            if relation not in terms[source_id].relationships:
                terms[source_id].relationships[relation] = []
            terms[source_id].relationships[relation].append(Reference(target_ns, target_id, target_name))

    return list(terms.values())


def dump_obo_terms(terms: List[Term], file: TextIO):
    date = datetime.datetime.today()
    date_str = date.strftime('%d:%m:%Y %H:%M')

    print('format-version: 1.2', file=file)
    print(f'date: {date_str}', file=file)
    print('auto-generated-by: https://github.com/pharmacome/terminology/blob/master/export/obo.py', file=file)
    print('', file=file)

    for term in terms:
        obo_str = term.to_obo()
        print(obo_str, file=file)


if __name__ == '__main__':
    output_path = os.path.join(HERE, 'hbp.obo')
    obo_terms = get_obo_terms()
    with open(output_path, 'w') as output_file:
        dump_obo_terms(obo_terms, output_file)
