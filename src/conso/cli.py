# -*- coding: utf-8 -*-

"""CLI for CONSO."""

import click

from .check import check
from .enrich import enrich
from .export.cli import export
from .sort_table import sort


@click.group()
def main():
    """Run the CONSO CLI."""


main.add_command(check)
main.add_command(sort)
main.add_command(export)
main.add_command(enrich)

if __name__ == '__main__':
    main()
