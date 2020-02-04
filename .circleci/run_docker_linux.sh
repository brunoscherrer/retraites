#!/bin/sh

set -xe

echo `pwd`

export PYTHONPATH="$PWD/retraites:$PYTHONPATH"

# Demonstrations Python
python demo.py

# Demonstrations Notebook
jupyter nbconvert --to notebook --execute index.ipynb

# Tests unitaires
cd tests
python test_retraites.py
cd ..

# Doc
cd doc
jupyter nbconvert --to notebook --execute Description-du-composant-retraites.ipynb
cd ..

# Doc Latex 1
cd doc
pdflatex notice.tex
pdflatex notice.tex
cd ..

# Doc Latex 2
cd doc/Article4
pdflatex article4-analyse-impact.tex
pdflatex article4-analyse-impact.tex
cd ..

