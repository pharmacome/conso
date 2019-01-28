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
    rdfs = get_namespace('http://www.w3.org/2000/01/rdf-schema#')

    class curator(AnnotationProperty):
        namespace = ontology

    class database_cross_reference(AnnotationProperty):
        namespace = ontology

    class has_exact_synonym(AnnotationProperty):
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
            cls.database_cross_reference = [reference.strip() for reference in references.split(',')]
            classes[hbp_identifier] = cls

    xrefs_df = pd.read_csv(XREFS_PATH, sep='\t')
    for _, (identifier, database, database_identifier) in xrefs_df.iterrows():
        cls = classes[identifier]
        cls.database_cross_reference.append(f'{database}:{database_identifier}')

    synonyms_df = pd.read_csv(SYNONYMS_PATH, sep='\t')
    for _, (identifier, synonym, reference, _) in synonyms_df.iterrows():
        cls = classes[identifier]
        cls.has_exact_synonym.append(synonym)
        database_cross_reference[cls, has_exact_synonym, synonym] = reference

    return ontology


def main():
    ontology = make_ontology()
    ontology.save(os.path.join(HERE, 'hbp.owl'))


if __name__ == '__main__':
    main()
