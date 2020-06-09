<p align="center">
  <img style="width: 150px; height: 150px;" src="https://docs.google.com/drawings/d/e/2PACX-1vTXUpnVo_W6vJOv2nx894YkZ8XAra1SksAgsWDgg2gya9sIldRaZd7JrXNFamZp2kCWQhYEM8S5fBvS/pub?w=150&amp;h=150">
</p>

<h1 align="center">
  <br>
  Curation of Neurodegeneration Supporting Ontology (CONSO)
  <a href="https://travis-ci.com/pharmacome/conso">
    <img src="https://travis-ci.com/pharmacome/conso.svg?branch=master"
         alt="Travis CI">
  </a>
  <a href="https://zenodo.org/badge/latestdoi/142866236">
    <img src="https://zenodo.org/badge/142866236.svg" alt="DOI">
  </a>
  <br>
</h1>

<p align="center">
This ontology, developed during the <a href="https://pharmacome.github.io">Human Brain Pharmacome project</a>, 
contains terms representing chemistry, molecular biology, epidemiology, and pathology relevant to neurodegenerative 
disease.
</p>

<p align="center">
  <a href="#contents">Contents</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#build">Build</a> •
  <a href="#license">License</a>
</p>

## Contents

### [classes.tsv](classes.tsv)

This tab-separated values file contains a two columns describing
classes of entities in CONSO:

1. Class
2. BEL Encodings

### [typedefs.tsv](typedefs.tsv)

This tab-separated values file contains a six columns describing
relationships used in CONSO:

1. Identifier
2. Name
3. Namespace (optional)
4. Xrefs (namespace prefixed, comma separated)
5. Transitive (true or false)
6. Comment

### [terms.tsv](terms.tsv)

This tab-separated values file contains four columns describing
entities in CONSO:

1. Identifier
2. Author
3. Label
4. Class
5. References (namespace prefixed, comma separated. Example: `pmid:1234, pmid:1245, pmc:PMC1234`)
6. Description (no double quote characters allowed)

### [synonyms.tsv](synonyms.tsv)

This tab-separated values contains four columns describing synonyms
for terms in CONSO:

1. Identifier
2. Synonym
3. References (namespace prefixed, comma separated. Example: `pubmed:1234, pubmed:1245, pmc:PMC1234`)
4. Specificity (one of ``EXACT``, ``BROAD``, ``NARROW``, or ``RELATED``.
   See: https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html)

### [xrefs.tsv](xrefs.tsv)

This tab-separated values file contains three columns describing
other databases that have listed this equivalent entity:

1. CONSO Identifier
2. Database (preferred using identifiers.org)
3. Identifier

### [relations.tsv](relations.tsv)

This tab-separated values file describes
relations between terms in CONSO:

1. Source Namespace
2. Source Identifier
3. Source Name
4. Relationship (e.g., ``is_a``, ``part_of``, etc.)
5. Target Namespace
6. Target Identifier
7. Target Name

## [Exports](exports/)

CONSO is automatically exported to several formats on each build in the `exports/` directory:

### Open Biomedical Ontology (OBO)

The latest OBO file can be found at https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.obo.

This file can be regenerated with ``tox -e obo``.

### Web Ontology Language (OWL)

The latest OWL file can be found at https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.owl.

This file can be regenerated with ``tox -e owl``.

### Biological Expression Language

The [Biological Expression Language (BEL)](https://biological-expression-language.github.io) is a domain
specific language for encoding biomedical relations. It relies on controlled vocabularies like CONSO to
ensure semantic alignment.

A BEL namespace file for CONSO can be generated with ``tox -e belns``, then commit to GitHub and use
the commit hash to build a new URL for BEL documents following the form of:
https://raw.githubusercontent.com/pharmacome/conso/{HASH GOES HERE}/export/conso.belns

The latest BEL namespace can be found at:

- Identifiers: https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.belns.
- Names: https://raw.githubusercontent.com/pharmacome/conso/master/export/conso-names.belns.

## Contributing

Contributions are welcome! Please submit all pull requests to https://github.com/pharmacome/conso.

Tips:

- When adding a new term, make sure that the entry has a new and unique identifier that follows
  the regular expression `^CONSO\d{5}$`
- Only capitalize proper nouns in term labels (e.g., *Tau* is a named protein, so it is capitalized but 
  *hyperphosphorylation* is not)
- Normalize greek letters to full english names, then add synonyms with the greek letter.
- References should be written as compact URIs (CURIEs) (e.g., `pubmed:1234`, `pubmed:1245`, 
  `pmc:PMC1234`, etc.)

## Build

All build operations are handled by `tox`, which can be installed from the command line (just needed the first time) 
with:

```bash
$ pip install tox
```

First, `cd` into the folder for this repository, then `tox` can be directly run as a command. It takes care of 
checking the content and exporting it

```bash
$ tox
```

Finally, the results need to be `git push`ed back to GitHub.

## License

- BEL scripts in this repository are licensed under the CC BY 4.0 license.
- Python source code in this repository is licensed under the MIT license.

## Acknowledgements

### Logo

Logo designed by Daniel Domingo-Fernández
