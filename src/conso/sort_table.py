# -*- coding: utf-8 -*-

"""A script form sorting all tables."""

import click
import pandas as pd


@click.command()
@click.argument('path')
def sort(path: str) -> None:
    """Sort the table."""
    df = pd.read_csv(path, sep='\t')
    df.drop_duplicates(inplace=True)
    df.sort_values(list(df.columns)).to_csv(path, sep='\t', index=False)


if __name__ == '__main__':
    sort()
