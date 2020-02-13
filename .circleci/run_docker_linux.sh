#!/bin/sh

set -xe

echo `pwd`

export PYTHONPATH="$PWD:$PYTHONPATH"

# Doc Latex 1
cd doc
pdflatex notice.tex
pdflatex notice.tex
cd ..

# Doc Latex 2
cd doc/Article4
pdflatex article4-analyse-impact.tex
pdflatex article4-analyse-impact.tex
cd ../..

# Demonstrations Python
python demo.py

# Tests unitaires
cd tests
python test_retraites.py
python test_etudeimpact.py
cd ..

# Notebooks in all subdirectories
python tests/find-ipynb-files.py


