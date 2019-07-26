#!/usr/bin/env bash

# BEL Namespaces
python -m bio2bel.obo belns hp --foundry
python -m bio2bel.obo belns doid --foundry

python -m bio2bel.obo belns efo --url https://www.ebi.ac.uk/efo/efo.obo

# BEL Annotations

# NCBI Taxonomy
python -m bio2bel.obo belanno ncbitaxon -f ncbitaxon.belanno

# Cell Ontology 
python -m bio2bel.obo belanno cl -f cl.belanno

# Cell Line Ontology (doesn't yet exist)
# python -m bio2bel.obo belanno clo -f clo.belanno
