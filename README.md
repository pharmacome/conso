<h1 align="center">
  <br>
  Terminology
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
  <a href="#contributing">Contributing</a>
</p>

## Contents

### terms.tsv

This tab-separated values file contains 4 columns describing 
entities in the HBP terminology:

1. Identifier
2. Label
3. References (comma separated)
4. Description

### synonyms.tsv

This tab-separated values contains two columns describing synonyms
for terms in the HBP terminology:

1. Identifier
2. Synonym

### xrefs.tsv

This tab-separated values file contains three columns describing
other databases that have listed this equivalent entity:

1. HBP Identifier
2. Database
3. Identifier

## Contributing

Contributions are welcome! Please submit all pull requests to https://github.com/pharmacome/terminology.

Tips:

- When adding a new term, make sure that the entry has a new and unique identifier that follows 
  the regular expression `^HBP\d{5}$`
- Only capitalize proper nouns in term labels (e.g., *Tau* is a named protein, so it is capitalized but *hyperphosphorylation* is not)
- References should follow the https://identifiers.org semantic web style (e.g., `pmid:1234`, `pmid:1245`, `pmc:PMC1234`, etc.)
