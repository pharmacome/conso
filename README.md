<h1 align="center">
  <br>
  Curation of Neurodegeneration Supporting Ontology (CONSO)
  <a href="https://travis-ci.com/pharmacome/conso">
    <img src="https://travis-ci.com/pharmacome/conso.svg?branch=master"
         alt="Travis CI">
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

### classes.tsv

This tab-separated values file contains a two columns describing
classes of entities in CONSO:

1. Class
2. BEL Encodings

### typedefs.tsv

This tab-separated values file contains a six columns describing
relationships used in CONSO:

1. Identifier
2. Name
3. Namespace (optional)
4. Xrefs (namespace prefixed, comma separated)
5. Transitive (true or false)
6. Comment

### terms.tsv

This tab-separated values file contains four columns describing
entities in CONSO:

1. Identifier
2. Author
3. Label
4. Class
5. References (namespace prefixed, comma separated. Example: `pmid:1234, pmid:1245, pmc:PMC1234`)
6. Description (no double quote characters allowed)

### synonyms.tsv

This tab-separated values contains four columns describing synonyms
for terms in CONSO:

1. Identifier
2. Synonym
3. References (namespace prefixed, comma separated. Example: `pmid:1234, pmid:1245, pmc:PMC1234`)
4. Specificity (one of ``EXACT``, ``BROAD``, ``NARROW``, or ``RELATED``.
   See: https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html)

### xrefs.tsv

This tab-separated values file contains three columns describing
other databases that have listed this equivalent entity:

1. CONSO Identifier
2. Database (preferred using identifiers.org)
3. Identifier

### relations.tsv

This tab-separated values file describes
relations between terms in CONSO:

1. Source Namespace
2. Source Identifier
3. Source Name
4. Relationship (e.g., ``is_a``, ``part_of``, etc.)
5. Target Namespace
6. Target Identifier
7. Target Name

## Contributing

Contributions are welcome! Please submit all pull requests to https://github.com/pharmacome/conso.

Tips:

- When adding a new term, make sure that the entry has a new and unique identifier that follows
  the regular expression `^CONSO\d{5}$`
- Only capitalize proper nouns in term labels (e.g., *Tau* is a named protein, so it is capitalized but 
  *hyperphosphorylation* is not)
- Normalize greek letters to full english names, then add synonyms with the greek letter.
- References should follow the https://identifiers.org semantic web style (e.g., `pmid:1234`, `pmid:1245`, 
  `pmc:PMC1234`, etc.)

## Build

All build operations are handled by `tox`, which can be installed from the command line (just needed the first time) 
with:

```bash
$ pip3 install tox
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
