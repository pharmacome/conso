# -*- coding: utf-8 -*-

"""Export the Curation of Neurodegeneration Supporting Ontology (CONSO) to OBO."""

import csv
import datetime
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, List, Mapping, Optional, TextIO, Union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir, os.pardir)

HBP = 'HBP'

CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

OUTPUT_PATH = os.path.join(ROOT, 'export', 'hbp.obo')

BEL_RELATION_ID = 'bel'

typedefs = {
    'bel': f"""[Typedef]
id: {BEL_RELATION_ID}
name: BEL term
comment: A formulation for a term in Biological Expression language""",
    'part_of': """[Typedef]
id: part_of
name: part of
namespace: external
xref: BFO:0000050
is_transitive: true""",
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
    references: List[str] = field(default_factory=list)


@dataclass
class Term:
    """A term in OBO."""

    reference: Reference
    namespace: str
    description: str
    provenance: List[Reference]
    parents: List[Reference] = field(default_factory=list)
    relationships: Mapping[str, List[Reference]] = field(default_factory=lambda: defaultdict(list))
    synonyms: List[Synonym] = field(default_factory=list)
    xrefs: List[Reference] = field(default_factory=list)

    @property
    def _namespace_normalized(self) -> str:
        return self.namespace \
            .replace(' ', '_') \
            .replace('-', '_') \
            .replace('(', '') \
            .replace(')', '')

    def _yield_obo_lines(self) -> Iterable[str]:
        yield '[Term]'
        yield f'id: {self.reference.namespace}:{self.reference.identifier}'
        yield f'name: {self.reference.name}'
        if self.namespace != '?':
            yield f'namespace: {self._namespace_normalized}'
        yield f'''def: "{self.description}" [{', '.join(map(str, self.provenance))}]'''

        for synonym in self.synonyms:
            synonym_references_string = ', '.join(synonym.references)
            yield f'synonym: "{synonym.name}" {synonym.specificity} [{synonym_references_string}]'

        for xref in self.xrefs:
            yield f'xref: {xref}'

        for parent_reference in self.parents:
            yield f'is_a: {parent_reference}'

        for relationship, relationship_references in self.relationships.items():
            for relationship_reference in relationship_references:
                yield f'relationship: {relationship} {relationship_reference}'

    def to_obo(self) -> str:
        """Convert this term to an OBO entry."""
        return '\n'.join(self._yield_obo_lines()) + '\n'

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
                provenance=[
                    Reference(*pmid.strip().split(':'))
                    for pmid in references.split(',')
                ],
                namespace=namespace,
                description=description,
            )
            for hbp_identifier, _, name, namespace, references, description in reader
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
            if database.lower() == 'bel':
                terms[hbp_id].relationships['bel'] = [identifier]
            else:
                terms[hbp_id].xrefs.append(Reference(database, identifier))

    with open(RELATIONS_PATH) as file:
        reader = enumerate(csv.reader(file, delimiter='\t'), start=1)
        _ = next(reader)  # skip the header
        handled_relations = {'is_a'} | set(typedefs)
        for line, (source_ns, source_id, source_name, relation, target_ns, target_id, target_name) in reader:
            if relation not in handled_relations:
                print(f'{RELATIONS_PATH} can not handle line {line} because unhandled relation: {relation}')
                continue

            if source_ns != HBP and target_ns != HBP:
                print(f'{RELATIONS_PATH}: skipping line {line} because neither entity is from HBP')
                continue

            if source_ns != HBP:
                print(f'{RELATIONS_PATH} can not handle line {line} because of'
                      f' inverse relation definition to external identifier')
                continue

            target = Reference(target_ns, target_id, target_name)
            if relation == 'is_a':
                terms[source_id].parents.append(target)
            else:
                terms[source_id].relationships[relation].append(target)

    return list(terms.values())


def dump_obo_terms(terms: List[Term], file: Union[None, TextIO]) -> None:
    """Write all OBO terms to the file."""
    date = datetime.datetime.today()
    date_str = date.strftime('%d:%m:%Y %H:%M')

    print('format-version: 1.2', file=file)
    print(f'date: {date_str}', file=file)
    print('auto-generated-by: https://github.com/pharmacome/terminology/blob/master/src/conso/export/obo.py', file=file)
    print('ontology: conso', file=file)
    print('', file=file)

    for typedef in typedefs.values():
        print(f'{typedef}\n', file=file)

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
