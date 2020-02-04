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
jupyter nbconvert --to notebook --execute simulation-COR-juin-2019.ipynb
jupyter nbconvert --to notebook --execute notes-bugs.ipynb
jupyter nbconvert --to notebook --execute simulation-Etude-Impact.ipynb
jupyter nbconvert --to notebook --execute reformes.ipynb
jupyter nbconvert --to notebook --execute reformes2.ipynb
cd ..

