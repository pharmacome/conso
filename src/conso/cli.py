# -*- coding: utf-8 -*-

"""CLI for CONSO."""

import click

from .check import check


@click.group()
def main():
    """Run the CONSO CLI."""


main.add_command(check)

if __name__ == '__main__':
    main()
