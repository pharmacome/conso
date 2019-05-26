# -*- coding: utf-8 -*-

"""A script form sorting all tables."""

import sys

import pandas as pd


def pandas_sort(path: str) -> None:
    """Sort the table."""
    df = pd.read_csv(path, sep='\t')
    df.drop_duplicates(inplace=True)
    df.sort_values(list(df.columns)).to_csv(path, sep='\t', index=False)


def main() -> None:
    """Run the sort from the command line."""
    pandas_sort(sys.argv[1])


if __name__ == '__main__':
    main()
