#!/usr/bin/python
# coding:utf-8

from __future__ import print_function
from retraites.SimulateurRetraites import SimulateurRetraites

# Génération des graphes pour le statu quo (COR)

simulateur = SimulateurRetraites('retraites/fileProjection.json')
simulateur.dessineConjoncture()
#analyse.sauveFigure("conjoncture")
