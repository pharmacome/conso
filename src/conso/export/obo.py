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

AUTHORS_PATH = os.path.abspath(os.path.join(ROOT, 'authors.tsv'))
CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

OUTPUT_PATH = os.path.join(ROOT, 'export', 'conso.obo')

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
    'author': """[Typedef]
id: author
name: Author ORCID Identifier
namespace: external
""",
    'has_reference_protein': f"""[Typedef]
id: has_reference_protein
name: Isoform has Reference Protein
comment: A link between a protein isoform and its reference protein""",
    'has_role': f"""[Typedef]
id: has_role
name: Chemical Has Role
is_transitive: true
comment: Same as from ChEBI""",
}

OBO_ESCAPE = {
    c: f'\\{c}'
    for c in ':,"\\()[]{}'
}
OBO_ESCAPE[' '] = '\\W'


def obo_escape(string: str) -> str:
    """Escape all funny characters for OBO."""
    return ''.join(
        OBO_ESCAPE.get(character, character)
        for character in string
    )


@dataclass
class Reference:
    """A namespace, identifier, and label."""

    namespace: str
    identifier: str
    name: Optional[str] = None

    @property
    def _escaped_identifier(self):
        return obo_escape(self.identifier)

    def __str__(self):  # noqa: D105
        if self.name:
            return f'{self.namespace}:{self._escaped_identifier} ! {self.name}'
        return f'{self.namespace}:{self._escaped_identifier}'


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
    author: Reference
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

    def _yield_obo_lines(self, simple: bool = True) -> Iterable[str]:
        yield '[Term]'
        yield f'id: {self.reference.namespace}:{self.reference.identifier}'
        yield f'name: {self.reference.name}'
        if self.namespace != '?':
            yield f'namespace: {self._namespace_normalized}'
        yield f'''def: "{self.description}" [{', '.join(map(str, self.provenance))}]'''
        yield f'relationship: author {self.author}'

        for xref in self.xrefs:
            yield f'xref: {xref}'

        for parent_reference in self.parents:
            yield f'is_a: {parent_reference}'

        for relationship, relationship_references in self.relationships.items():
            if simple and relationship == 'bel':
                continue
            for relationship_reference in relationship_references:
                yield f'relationship: {relationship} {relationship_reference}'

        for synonym in self.synonyms:
            synonym_references_string = ', '.join(synonym.references)
            yield f'synonym: "{synonym.name}" {synonym.specificity} [{synonym_references_string}]'

    def to_obo(self, simple: bool = True) -> str:
        """Convert this term to an OBO entry."""
        return '\n'.join(self._yield_obo_lines(simple=simple)) + '\n'

    def __str__(self):  # noqa: D105
        return self.to_obo()


def get_obo_terms() -> List[Term]:
    """Get OBO terms."""
    with open(AUTHORS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        authors = {
            key: Reference(
                namespace='orcid',
                identifier=orcid_identifier,
                name=author,
            )
            for key, author, orcid_identifier in reader
        }

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
                author=authors[author_key],
            )
            for hbp_identifier, author_key, name, namespace, references, description in reader
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
                terms[hbp_id].relationships['bel'] = [Reference(namespace='bel', identifier=identifier)]
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


def dump_obo_terms(terms: List[Term], file: Union[None, TextIO], simple: bool = True) -> None:
    """Write all OBO terms to the file."""
    date = datetime.datetime.today()
    date_str = date.strftime('%d:%m:%Y %H:%M')

    print('format-version: 1.2', file=file)
    print(f'date: {date_str}', file=file)
    print('auto-generated-by: https://github.com/pharmacome/terminology/blob/master/src/conso/export/obo.py', file=file)
    print('ontology: conso', file=file)
    print('', file=file)

    for name, typedef in typedefs.items():
        if simple and name == 'bel':
            continue
        print(f'{typedef}\n', file=file)

    for term in terms:
        obo_str = term.to_obo(simple=simple)
        print(obo_str, file=file)


def main(path: Optional[str] = None, simple: bool = False) -> None:
    """Export CONSO as OBO."""
    terms = get_obo_terms()
    with open(path or OUTPUT_PATH, 'w') as file:
        dump_obo_terms(terms=terms, file=file, simple=simple)


if __name__ == '__main__':
    main()
