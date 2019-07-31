Export
======
This folder contains scripts for exporting CONSO in
different formats, and the resulting exported files.

Biological Expression Language (BEL) Namespace
----------------------------------------------
This file can be regenerated with ``tox -e belns``, then commit to GitHub and use the commit hash to build a new URL
for BEL documents following the form of:
https://raw.githubusercontent.com/pharmacome/conso/{HASH GOES HERE}/export/conso.belns

The latest BEL namespace can be found at:

- Identifiers: https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.belns.
- Names: https://raw.githubusercontent.com/pharmacome/conso/master/export/conso-names.belns.

Open Biomedical Ontology (OBO)
------------------------------
The latest OBO file can be found at https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.obo.

This file can be regenerated with ``tox -e obo``.


Web Ontology Language (OWL)
---------------------------
The latest OWL file can be found at https://raw.githubusercontent.com/pharmacome/conso/master/export/conso.owl.

This file can be regenerated with ``tox -e owl``.
