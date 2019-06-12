Export
======
This folder contains scripts for exporting the Human Brain Pharmacome Terminology in
different formats, and the resulting exported files.

Biological Expression Language (BEL) Namespace
----------------------------------------------
This file can be regenerated with ``tox -e belns``, then commit to GitHub and use the commit hash to build a new URL
for BEL documents following the form of:
https://raw.githubusercontent.com/pharmacome/terminology/{HASH GOES HERE}/export/hbp.belns

The latest BEL namespace can be found at:

- Identifiers: https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp.belns.
- Names: https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp-names.belns.

Open Biomedical Ontology (OBO)
------------------------------
The latest OBO file can be found at https://raw.githubusercontent.com/pharmacome/terminology/master/export/conso.obo.

This file can be regenerated with ``tox -e obo``.


Web Ontology Language (OWL)
---------------------------
The latest OWL file can be found at https://raw.githubusercontent.com/pharmacome/terminology/master/export/conso.owl.

This file can be regenerated with ``tox -e owl``.
