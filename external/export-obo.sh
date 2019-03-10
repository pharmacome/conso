# BEL Namespaces
python -m bio2bel.obo belns hp -f hp.belanno
python -m bio2bel.obo belns hp -f hp-names.belanno -n

python -m bio2bel.obo belns doid -f doid.belanno
python -m bio2bel.obo belns doid -f doid-names.belanno -n

# BEL Annotations

# NCBI Taxonomy
python -m bio2bel.obo belanno ncbitaxon -f ncbitaxon.belanno

# Cell Ontology 
python -m bio2bel.obo belanno cl -f cl.belanno

# Cell Line Ontology (doesn't yet exist)
# python -m bio2bel.obo belanno clo -f clo.belanno
