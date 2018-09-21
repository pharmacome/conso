Export
======
This folder contains scripts for exporting the Human Brain Pharmacome Terminology in
different formats, and the resulting exported files.

BEL Namespace
-------------
The latest BEL namespace can be found at https://raw.githubusercontent.com/pharmacome/terminology/master/export/hbp.belns.

Below are instructions on how to update the BEL namespace.

1. Change into the `/export` directory with `cd export`
2. Generate a new namespace with `python3 belns.py` 
3. Commit to GitHub and use the commit hash to build a new URL for BEL documents following the form of: https://raw.githubusercontent.com/pharmacome/terminology/{HASH GOES HERE}/export/hbp.belns
