# -*- coding: utf-8 -*-

"""Command line interface for exporting the Curation of Neurodegeneration Supporting Ontology (CONSO)."""

from conso.export.belns import main as export_belns
from conso.export.html import main as export_html
from conso.export.obo import main as export_obo
from conso.export.owl import main as export_owl


def main() -> None:
    """Make all exports."""
    export_belns()
    export_obo()
    export_html()
    export_owl()


if __name__ == '__main__':
    main()
