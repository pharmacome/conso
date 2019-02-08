<h1 align="center">
  <br>
  HBP Terminology
  <a href="https://travis-ci.com/pharmacome/terminology">
    <img src="https://travis-ci.com/pharmacome/terminology.svg?branch=master"
         alt="Travis CI">
  </a>
  <br>
</h1>

<p align="center">
This is a terminology for the Human Brain Pharmacome (HBP) project, containing terms representing the molecular biology
relevant to neurodegenerative disease.
</p>

<p align="center">
  <a href="#contents">Contents</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#exports">Exports</a>
</p>

## Contents

### classes.tsv

This tab-separated values file contains a two columns describing
classes of entities in the HBP terminology:

1. Class
2. BEL Encodings

### terms.tsv

This tab-separated values file contains four columns describing
entities in the HBP terminology:

1. Identifier
2. Author
3. Label
4. Class
5. References (namespace prefixed, comma separated. Example: `pmid:1234, pmid:1245, pmc:PMC1234`)
6. Description (no double quote characters allowed)

### synonyms.tsv

This tab-separated values contains four columns describing synonyms
for terms in the HBP terminology:

1. Identifier
2. Synonym
3. References (namespace prefixed, comma separated. Example: `pmid:1234, pmid:1245, pmc:PMC1234`)
4. Specificity (one of ``EXACT``, ``BROAD``, ``NARROW``, or ``RELATED``.
   See: https://owlcollab.github.io/oboformat/doc/GO.format.obo-1_4.html)

### xrefs.tsv

This tab-separated values file contains three columns describing
other databases that have listed this equivalent entity:

1. HBP Identifier
2. Database (preferred using identifiers.org)
3. Identifier

### relations.tsv

This tab-separated values file describes
relations between terms in the HBP terminology:

1. Source Namespace
2. Source Identifier
3. Source Name
4. Relationship (e.g., ``is_a``, ``part_of``, etc.)
5. Target Namespace
6. Target Identifier
7. Target Name

## Contributing

Contributions are welcome! Please submit all pull requests to https://github.com/pharmacome/terminology.

Tips:

- When adding a new term, make sure that the entry has a new and unique identifier that follows
  the regular expression `^HBP\d{5}$`
- Only capitalize proper nouns in term labels (e.g., *Tau* is a named protein, so it is capitalized but *hyperphosphorylation* is not)
- Normalize greek letters to full english names, then add synonyms with the greek letter.
- References should follow the https://identifiers.org semantic web style (e.g., `pmid:1234`, `pmid:1245`, `pmc:PMC1234`, etc.)

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
