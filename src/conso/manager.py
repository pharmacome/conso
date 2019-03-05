"""Manager for normalizing BEL graphs."""

# from bio2bel import AbstractManager

from typing import Iterable, Optional, Tuple

import networkx as nx
import pandas as pd

from pybel import BELGraph
from pybel.constants import IDENTIFIER, NAME, NAMESPACE
from pybel.dsl import BaseEntity
from .check import IDENTIFIER_COLUMN, NAME_COLUMN, TERMS_PATH, TYPE_COLUMN


class Manager:
    """Manage the terms in CONSO."""

    def __init__(self):
        self.term_df = pd.read_csv(TERMS_PATH, sep='\t')
        self.identifier_to_label = {}
        self.label_to_identifier = {}
        self.identifier_to_type = {}
        for _, (identifier, cls, label) in self.term_df[[IDENTIFIER_COLUMN, TYPE_COLUMN, NAME_COLUMN]].iterrows():
            self.identifier_to_label[identifier] = label
            self.label_to_identifier[label] = identifier
            self.identifier_to_type[identifier] = cls

    def normalize_terms(self, graph: BELGraph) -> None:
        """Normalize terms in a BEL Graph."""
        mapping = dict(self.iter_nodes(graph))
        nx.relabel_nodes(graph, mapping, copy=False)

    def iter_nodes(self, graph: BELGraph) -> Iterable[Tuple[BaseEntity, BaseEntity]]:
        """Iterate over pairs of BEL nodes and Rat genes."""
        for node in graph:
            new_node = self.normalize_node(node)
            if new_node is not None:
                yield node, new_node

    def normalize_node(self, node: BaseEntity) -> Optional[BaseEntity]:
        """Normalize a node if possible, otherwise return None."""
        namespace = node.get(NAMESPACE)

        if not namespace or namespace.lower() not in {'hbp', 'conso'}:
            return

        identifier = node.get(IDENTIFIER)
        name = node.get(NAME)

        if identifier is None and name is None:
            raise ValueError

        if identifier is not None:
            name = self.identifier_to_label.get(identifier)
            if name is not None:
                return node.__class__(namespace=namespace, name=name, identifier=identifier)

        identifier = self.label_to_identifier.get(name)
        if identifier is not None:
            return node.__class__(namespace=namespace, name=name, identifier=identifier)
