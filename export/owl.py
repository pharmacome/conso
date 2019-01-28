# -*- coding: utf-8 -*-

"""Export the Human Brain Pharmacome terminology to OWL."""

import csv
import os
import types
from typing import Dict, Type

import pandas as pd
from owlready2 import AnnotationProperty, Ontology, Thing, get_namespace, get_ontology

HERE = os.path.dirname(os.path.abspath(__file__))

HBP = 'HBP'
URL = 'https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp.owl'
CLASSES_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'classes.tsv'))
TERMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'relations.tsv'))


# label = IRIS['http://www.w3.org/2000/01/rdf-schema#label']


def make_ontology() -> Ontology:
    """Get classes."""
    ontology = get_ontology(URL)
    skos = ontology.get_namespace('http://www.w3.org/2008/05/skos')

    with skos:
        class altLabel(AnnotationProperty):
            """Denotes a synonym using the SKOS vocabulary."""

        class related(AnnotationProperty):
            """Denotes a cross-reference using the SKOS vocabulary."""

    class curator(AnnotationProperty):
        """Denotes the curator of a given entry."""
        namespace = ontology

    class bel(AnnotationProperty):
        """Denotes the BEL term corresponding to a given entry."""
        namespace = ontology

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
        for hbp_identifier, curator, name, super_cls_name, references, definition in reader:
            if name == 'WITHDRAWN':
                continue

            cls: Type[Thing] = types.new_class(
                name=hbp_identifier,
                bases=(super_classes[super_cls_name],),
            )
            cls.label = name
            cls.comment = definition
            cls.curator = curator
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


def main():
    ontology = make_ontology()
    ontology.save(os.path.join(HERE, 'hbp.owl'))


if __name__ == '__main__':
    main()
