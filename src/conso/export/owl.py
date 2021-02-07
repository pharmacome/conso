# -*- coding: utf-8 -*-

"""Export CONSO to OWL."""

import csv
import types
from typing import Dict, Type

import click
import pandas as pd
from owlready2 import AnnotationProperty, Namespace, Ontology, Thing, get_ontology

from ..resources import CLASSES_PATH, SYNONYMS_PATH, TERMS_PATH, XREFS_PATH

CONSO = 'CONSO'
URL = 'https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.owl'


# DC_NAME = 'Curation of Neurodegeneration Supporting Ontology'
# DC_SHORT = 'CONSO'


def get_owl() -> Ontology:
    """Get classes."""
    ontology = get_ontology(URL)

    skos: Namespace = ontology.get_namespace('http://www.w3.org/2008/05/skos', 'skos')

    # dc: Namespace = ontology.get_namespace('http://dublincore.org/2012/06/14/dcterms', 'dc')
    # ontology.metadata.append(dc)

    with skos:
        class altLabel(AnnotationProperty):  # noqa: N801
            """Denotes a synonym using the SKOS vocabulary."""

        class related(AnnotationProperty):  # noqa: N801
            """Denotes a cross-reference using the SKOS vocabulary."""

    with ontology:
        class author(AnnotationProperty):  # noqa: N801
            """Denotes the author of a given entry."""

        class bel(AnnotationProperty):  # noqa: N801
            """Denotes the BEL term corresponding to a given entry."""

    classes_df = pd.read_csv(CLASSES_PATH, sep='\t')
    super_classes = {}
    with ontology:
        for i, (name, _encoding) in classes_df.iterrows():
            super_classes[name] = cls = types.new_class(
                name=f'{CONSO}C{i}',
                bases=(Thing,),
            )
            cls.label = name

    # authors_df = pd.read_csv(AUTHORS_PATH, sep='\t')
    # authors = dict(authors_df[['ORCID', 'Name']].values)

    with open(TERMS_PATH) as file, ontology:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        classes: Dict[str, Type[Thing]] = {}
        for conso_id, orcid, name, super_cls_name, references, definition in reader:
            if name == 'WITHDRAWN':
                continue

            cls: Type[Thing] = types.new_class(
                name=conso_id,
                bases=(super_classes[super_cls_name],),
            )
            cls.label = name
            cls.comment = definition
            cls.author = f'orcid:{orcid}'
            cls.related = [reference.strip() for reference in references.split(',')]
            classes[conso_id] = cls

    xrefs_df = pd.read_csv(XREFS_PATH, sep='\t')
    for _, (identifier, database, database_identifier) in xrefs_df.iterrows():
        cls = classes[identifier]
        if database == 'BEL':
            cls.bel = database_identifier
        else:
            cls.related.append(f'{database}:{database_identifier}')

    synonyms_df = pd.read_csv(SYNONYMS_PATH, sep='\t')
    for _, (identifier, synonym, reference, _) in synonyms_df.iterrows():
        cls = classes[identifier]
        cls.altLabel.append(synonym)
        related[cls, altLabel, synonym] = reference

    return ontology


@click.command()
@click.argument('path')
def owl(path: str):
    """Export CONSO as OWL."""
    get_owl().save(path)


if __name__ == '__main__':
    owl()
