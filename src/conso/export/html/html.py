# -*- coding: utf-8 -*-

"""Export CONSO to HTML."""

import os
from collections import Counter, defaultdict
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

#: Path to this directory
HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir, os.pardir))

AUTHORS_PATH = os.path.join(ROOT, 'authors.tsv')
CLASSES_PATH = os.path.join(ROOT, 'classes.tsv')
TERMS_PATH = os.path.join(ROOT, 'terms.tsv')
SYNONYMS_PATH = os.path.join(ROOT, 'synonyms.tsv')
XREFS_PATH = os.path.join(ROOT, 'xrefs.tsv')
RELATIONS_PATH = os.path.join(ROOT, 'relations.tsv')

OUTPUT_DIRECTORY = os.path.join(ROOT, 'docs')

environment = Environment(autoescape=True, loader=FileSystemLoader(HERE), trim_blocks=False)
index_template = environment.get_template('index.html')
summary_template = environment.get_template('summary.html')
term_template = environment.get_template('term.html')

CONSO = 'CONSO'


def main(directory: Optional[str] = None, debug_links: bool = False) -> None:
    """Export CONSO as HTML.

    :param directory: The output directory where the html goes.
    :param debug_links: If true, uses links directly to index files instead of by folder.
    """
    authors_df = pd.read_csv(AUTHORS_PATH, sep='\t')
    authors = dict(authors_df[['ORCID', 'Name']].values)

    terms_df = pd.read_csv(TERMS_PATH, sep='\t')
    terms_df = terms_df[terms_df.Name != 'WITHDRAWN']

    terms_df['author_name'] = terms_df['Author'].map(authors.get)

    synonyms_df = pd.read_csv(SYNONYMS_PATH, sep='\t')
    synonyms = defaultdict(list)
    for _, row in synonyms_df.iterrows():
        synonyms[row.identifier].append((row.synonym, row.reference, row.specificity))

    xrefs_df = pd.read_csv(XREFS_PATH, sep='\t')
    xrefs = defaultdict(list)
    for _, row in xrefs_df.iterrows():
        xrefs[row.identifier].append((row.database, row.database_identifier))

    relations_df = pd.read_csv(RELATIONS_PATH, sep='\t')
    incoming_relations = defaultdict(list)
    outgoing_relations = defaultdict(list)
    for _, row in relations_df.iterrows():
        if row['Source Namespace'] == CONSO:
            outgoing_relations[row['Source Identifier']].append((
                row['Relation'],
                row['Target Namespace'],
                row['Target Identifier'],
                row['Target Name'],
            ))
        if row['Target Namespace'] == CONSO:
            incoming_relations[row['Target Identifier']].append((
                row['Source Namespace'],
                row['Source Identifier'],
                row['Source Name'],
                row['Relation'],
            ))

    if directory is None:
        directory = OUTPUT_DIRECTORY

    os.makedirs(directory, exist_ok=True)

    index_html = index_template.render(
        terms_df=terms_df,
        incoming_relations=incoming_relations,
        outgoing_relations=outgoing_relations,
        synonyms=synonyms,
        xrefs=xrefs,
        debug_links=debug_links,
    )
    with open(os.path.join(directory, 'index.html'), 'w') as file:
        print(index_html, file=file)

    summary_df = terms_df.groupby('Type').count().sort_values('Identifier', ascending=False)['Identifier'].reset_index()
    summary_df['Type'] = summary_df['Type'].map(str.title)
    summary_df = summary_df[summary_df['Type'] != '?']
    summary_html = summary_template.render(
        summary_df=summary_df,
    )
    with open(os.path.join(directory, 'summary.html'), 'w') as file:
        print(summary_html, file=file)

    for _, row in terms_df.iterrows():
        subdirectory = os.path.join(directory, row.Identifier)
        os.makedirs(subdirectory, exist_ok=True)
        html = term_template.render(
            row=row,
            synonyms=synonyms[row.Identifier],
            xrefs=xrefs[row.Identifier],
            incoming_relations=incoming_relations[row.Identifier],
            outgoing_relations=outgoing_relations[row.Identifier],
            debug_links=debug_links,
        )
        with open(os.path.join(subdirectory, 'index.html'), 'w') as file:
            print(html, file=file)

    # Make some plots
    fig, (lax, rax) = plt.subplots(ncols=2, figsize=(12, 5))
    sns.barplot(data=summary_df, y='Type', x='Identifier', ax=lax)
    lax.set_xlabel('Count')
    lax.set_ylabel('')
    lax.set_title(f'Entries ({len(terms_df.index)} in {summary_df["Type"].nunique()} classes)')

    relations = Counter(relations_df['Relation'].map(lambda s: s.replace('_', ' ').title()))
    relations['Has Synonym'] = len(synonyms_df.index)
    relations['Has Xref'] = len(xrefs_df.index)
    relations_summary_df = pd.DataFrame(relations.most_common(), columns=['Type', 'Count'])
    sns.barplot(data=relations_summary_df, x='Count', y='Type', ax=rax)
    rax.set_xscale('log')
    rax.set_ylabel('')
    rax.set_title(f'Relations ({sum(relations.values())})')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIRECTORY, 'summary.png'), dpi=300)


if __name__ == '__main__':
    main()
