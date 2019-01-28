# -*- coding: utf-8 -*-

"""Export the Human Brain Pharmacome terminology to OWL."""

import csv
import os
import types
from typing import Dict, Mapping, Type

from owlready2 import Ontology, Thing, get_ontology

HERE = os.path.dirname(os.path.abspath(__file__))

HBP = 'HBP'
URL = 'https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp.owl'
TERMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'terms.tsv'))
SYNONYMS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'synonyms.tsv'))
XREFS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'xrefs.tsv'))
RELATIONS_PATH = os.path.abspath(os.path.join(HERE, os.pardir, 'relations.tsv'))


def make_ontology() -> Ontology:
    """Make the HBP ontology."""
    ontology = get_ontology(URL)
    get_classes(ontology)
    return ontology


def get_classes(ontology: Ontology) -> Mapping[str, Type[Thing]]:
    """Get classes."""
    with open(TERMS_PATH) as file, ontology:
        reader = csv.reader(file, delimiter='\t')
        _ = next(reader)  # skip the header

        class HBPEntry(Thing):
            """An entry in the Human Brain Pharmacome ontology."""

        class has_label(HBPEntry >> str):  # TODO replace with proper RDFS or OWL
            """A label for an entry."""

        classes: Dict[str, Type[Thing]] = {}
        for hbp_identifier, _, name, _, references, description in reader:
            if name == 'WITHDRAWN':
                continue
            cls: Type[Thing] = types.new_class(hbp_identifier, (HBPEntry,))
            cls.has_label.append(name)
            classes[hbp_identifier] = cls

        return classes


def main():
    ontology = make_ontology()
    ontology.save(os.path.join(HERE, 'hbp.owl'))


if __name__ == '__main__':
    main()
