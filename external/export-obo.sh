# BEL Namespaces
python -m bio2bel.obo belns hp -f hp.belns
python -m bio2bel.obo belns hp -f hp-names.belns -n

python -m bio2bel.obo belns doid -f doid.belns
python -m bio2bel.obo belns doid -f doid-names.belns -n

# BEL Annotations

# NCBI Taxonomy
python -m bio2bel.obo belanno ncbitaxon -f ncbitaxon.belanno

# Cell Ontology 
python -m bio2bel.obo belanno cl -f cl.belanno

# Cell Line Ontology (doesn't yet exist)
# python -m bio2bel.obo belanno clo -f clo.belanno
