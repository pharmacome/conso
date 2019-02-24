# -*- coding: utf-8 -*-

"""Export the Curation of Neurodegeneration Supporting Ontology (CONSO) to OWL."""

import csv
import os
import types
from typing import Dict, Optional, Type

import pandas as pd
from owlready2 import AnnotationProperty, Namespace, Ontology, Thing, get_ontology

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, os.pardir, os.pardir, os.pardir)

CLASSES_PATH = os.path.abspath(os.path.join(ROOT, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(ROOT, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(ROOT, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(ROOT, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(ROOT, 'relations.tsv'))

OUTPUT_PATH = os.path.join(ROOT, 'export', 'hbp.owl')

HBP = 'HBP'
URL = 'https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp.owl'


# DC_NAME = 'Curation of Neurodegeneration Supporting Ontology'
# DC_SHORT = 'CONSO'


def make_ontology() -> Ontology:
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
        class curator(AnnotationProperty):  # noqa: N801
            """Denotes the curator of a given entry."""

        class bel(AnnotationProperty):  # noqa: N801
            """Denotes the BEL term corresponding to a given entry."""

    classes_df = pd.read_csv(CLASSES_PATH, sep='\t')
    super_classes = {}
    with ontology:
        for i, (name, encoding) in classes_df.iterrows():
            super_classes[name] = cls = types.new_class(
                name=f'HBPC{i}',
                bases=(Thing,),
            )
            cls.label = name

    with open(TERMS_PATH) as file, ontology:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        classes: Dict[str, Type[Thing]] = {}
        for hbp_identifier, curator_name, name, super_cls_name, references, definition in reader:
            if name == 'WITHDRAWN':
                continue

            cls: Type[Thing] = types.new_class(
                name=hbp_identifier,
                bases=(super_classes[super_cls_name],),
            )
            cls.label = name
            cls.comment = definition
            cls.curator = curator_name
            cls.related = [reference.strip() for reference in references.split(',')]
            classes[hbp_identifier] = cls

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


def main(path: Optional[str] = None) -> None:
    """Export CONSO as OWL."""
    ontology = make_ontology()
    ontology.save(path or OUTPUT_PATH)


if __name__ == '__main__':
    main()
