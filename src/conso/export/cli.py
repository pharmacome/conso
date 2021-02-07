# -*- coding: utf-8 -*-

"""Command line interface for exporting the Curation of Neurodegeneration Supporting Ontology (CONSO)."""

import click

from .belns import belns
from .html import html
from .obo import obo
from .owl import owl


@click.group()
def export():
    """Export CONSO."""


export.add_command(belns)
export.add_command(html)
export.add_command(obo)
export.add_command(owl)

if __name__ == '__main__':
    export()
