# -*- coding: utf-8 -*-

"""Export the Curation of Neurodegeneration Supporting Ontology (CONSO) to OBO."""

import csv
import datetime
import os
from dataclasses import dataclass
from typing import List, Mapping, Optional, TextIO, Union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir, os.pardir)

HBP = 'HBP'

CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

OUTPUT_PATH = os.path.join(ROOT, 'export', 'hbp.obo')

INVERSE_RELATIONS = {
    'is_a': 'inverse_is_a',
    'part_of': 'has_part',
}


@dataclass
class Reference:
    """A namespace, identifier, and label."""

    namespace: str
    identifier: str
    name: Optional[str] = None

    def __str__(self):  # noqa: D105
        if self.name:
            return f'{self.namespace}:{self.identifier} ! {self.name}'
        return f'{self.namespace}:{self.identifier}'


@dataclass
class Synonym:
    """A synonym with optional specificity and references."""

    name: str
    specificity: str
    references: Optional[List[str]] = None


@dataclass
class Term:
    """A term in OBO."""

    reference: Reference
    description: str
    provenance: List[Reference]
    relationships: Optional[Mapping[str, List[Reference]]] = None
    synonyms: Optional[List[Synonym]] = None
    xrefs: Optional[List[Reference]] = None

    def to_obo(self) -> str:
        """Convert this term to an OBO entry."""
        obo_str = f'''[Term]
id: {self.reference.namespace}:{self.reference.identifier}
name: {self.reference.name}
def: "{self.description}" [{', '.join(map(str, self.provenance))}]
'''
        for synonym in self.synonyms or []:
            synonym_references_string = ', '.join(synonym.references)
            obo_str += f'synonym: "{synonym.name}" {synonym.specificity} [{synonym_references_string}]\n'

        for xref in self.xrefs or []:
            if xref.namespace == 'BEL':
                obo_str += f'bel: {xref.identifier}\n'
            else:
                obo_str += f'xref: {xref}\n'

        for relationship, references in (self.relationships or {}).items():
            for reference in references:
                obo_str += f'{relationship}: {reference}\n'

        return obo_str

    def __str__(self):  # noqa: D105
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
            for hbp_identifier, _, name, _, references, description in reader
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


def dump_obo_terms(terms: List[Term], file: Union[None, TextIO]) -> None:
    """Write all OBO terms to the file."""
    date = datetime.datetime.today()
    date_str = date.strftime('%d:%m:%Y %H:%M')

    print('format-version: 1.2', file=file)
    print(f'date: {date_str}', file=file)
    print('auto-generated-by: https://github.com/pharmacome/terminology/blob/master/export/obo.py', file=file)
    print('', file=file)

    print('''[Typedef]
name: bel
comment: A formulation for a term in Biological Expression language
''', file=file)

    for term in terms:
        obo_str = term.to_obo()
        print(obo_str, file=file)


def main(path: Optional[str] = None) -> None:
    """Export CONSO as OBO."""
    obo_terms = get_obo_terms()
    with open(path or OUTPUT_PATH, 'w') as output_file:
        dump_obo_terms(obo_terms, output_file)


if __name__ == '__main__':
    main()
