# -*- coding: utf-8 -*-

"""Export the Curation of Neurodegeneration Supporting Ontology (CONSO) to OBO."""

import csv
import os
from typing import Mapping, Optional

from pyobo import Obo, Reference, Synonym, Term, TypeDef

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir, os.pardir)

TYPEDEF_PATH = os.path.abspath(os.path.join(ROOT, 'typedefs.tsv'))
AUTHORS_PATH = os.path.abspath(os.path.join(ROOT, 'authors.tsv'))
CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

OUTPUT_PATH = os.path.join(ROOT, 'export', 'conso.obo')

CONSO = 'CONSO'


def get_obo() -> Obo:
    """Get OBO object."""
    terms, typedefs = get_content()
    return Obo(
        format_version='1.2',
        auto_generated_by='https://github.com/pharmacome/conso/blob/master/src/conso/export/obo.py',
        ontology='conso',
        name='Curation of Neurodegeneration Supporting Ontology',
        iter_terms=lambda: iter(terms),
        typedefs=typedefs,
    )


def get_content():
    """Iterate CONSO terms."""
    with open(TYPEDEF_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        typedefs: Dict[str, TypeDef] = {
            identifier: TypeDef(
                reference=Reference(prefix=CONSO, identifier=identifier, name=name),
                namespace=namespace,
                xrefs=Reference.from_curies(xrefs),
                is_transitive=transitive == 'true',
                comment=comment,
            )
            for identifier, name, namespace, xrefs, transitive, comment in reader
        }

    with open(AUTHORS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        authors: Mapping[str, Reference] = {
            orcid_identifier: Reference(
                prefix='orcid',
                identifier=orcid_identifier,
                name=author,
            )
            for orcid_identifier, author in reader
        }

    with open(TERMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        terms: Dict[str, Term] = {}
        for conso_id, author_key, name, namespace, references, description in reader:
            if name == 'WITHDRAWN':
                continue
            terms[conso_id] = Term(
                reference=Reference(
                    prefix=CONSO,
                    identifier=conso_id,
                    name=name,
                ),
                provenance=[
                    Reference.from_curie(pmid_curie)
                    for pmid_curie in references.split(',')
                ],
                namespace=namespace,
                definition=description,
            )
            terms[conso_id].relationships[typedefs['author']].append(authors[author_key])

    with open(SYNONYMS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for conso_id, synonym, references, specificity in reader:
            references = (
                [r.strip() for r in references.split(',')]
                if references and references != '?' else
                []
            )
            specificity = (
                'EXACT' if specificity == '?' else specificity
            )
            terms[conso_id].synonyms.append(Synonym(synonym, specificity, provenance=references))

    with open(XREFS_PATH) as file:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header
        for conso_id, database, identifier in reader:
            if database.lower() == 'bel':
                terms[conso_id].relationships[typedefs['bel']] = [Reference(prefix='bel', identifier=identifier)]
            else:
                terms[conso_id].xrefs.append(Reference(prefix=database, identifier=identifier))

    with open(RELATIONS_PATH) as file:
        reader = enumerate(csv.reader(file, delimiter='\t'), start=1)
        _ = next(reader)  # skip the header
        handled_relations = {'is_a'} | set(typedefs)
        for line, (source_ns, source_id, _source_name, relation, target_ns, target_id, target_name) in reader:
            if relation not in handled_relations:
                print(f'{RELATIONS_PATH} can not handle line {line} because unhandled relation: {relation}')
                continue

            if source_ns != CONSO and target_ns != CONSO:
                print(f'{RELATIONS_PATH}: skipping line {line} because neither entity is from {CONSO}')
                continue

            if source_ns != CONSO:
                print(f'{RELATIONS_PATH} can not handle line {line} because of'
                      f' inverse relation definition to external identifier')
                continue

            target = Reference(prefix=target_ns, identifier=target_id, name=target_name)
            if relation == 'is_a':
                terms[source_id].parents.append(target)
            else:
                terms[source_id].relationships[typedefs[relation]].append(target)

    return terms.values(), typedefs.values()


def main(path: Optional[str] = None) -> None:
    """Export CONSO as OBO."""
    obo = get_obo()
    with open(path or OUTPUT_PATH, 'w') as file:
        obo.write(file)


if __name__ == '__main__':
    main()
