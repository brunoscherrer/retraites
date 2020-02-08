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

# Demonstrations Notebook
jupyter nbconvert --to notebook --execute index.ipynb

# Tests unitaires
cd tests
python test_retraites.py
python test_etudeimpact.py
cd ..

# Doc
cd doc
jupyter nbconvert --to notebook --execute Description-du-composant-retraites.ipynb
jupyter nbconvert --to notebook --execute simulation-COR-juin-2019.ipynb
jupyter nbconvert --to notebook --execute notes-bugs.ipynb
jupyter nbconvert --to notebook --execute simulation-Etude-Impact.ipynb
jupyter nbconvert --to notebook --execute reformes.ipynb
jupyter nbconvert --to notebook --execute reformes2.ipynb
cd ..


