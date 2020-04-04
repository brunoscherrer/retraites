#!/bin/sh

set -xe

echo `pwd`

export PYTHONPATH="$PWD:$PYTHONPATH"

# Doc Latex 2
cd doc/Article4
pdflatex article4-analyse-impact.tex
bibtex article4-analyse-impact
pdflatex article4-analyse-impact.tex
pdflatex article4-analyse-impact.tex
cd ../..

# Demonstrations Python
python demo.py

# Tests unitaires
python -m unittest discover tests

# Notebooks in all subdirectories
python tests/find-ipynb-files.py


