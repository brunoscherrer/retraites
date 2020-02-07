#!/usr/bin/python
# coding:utf-8

from __future__ import print_function
import pylab as pl
from retraites.SimulateurRetraites import SimulateurRetraites

# Génération des graphes pour le statu quo (COR)

simulateur = SimulateurRetraites('retraites/fileProjection.json')
analyse = simulateur.pilotageCOR()

pl.figure(figsize=(10,8))
pl.suptitle(u"Projections du COR (hypothèses)",fontsize=16)
for c in range(9):
    pl.subplot(3,3,c+1)
    v,V = [ (simulateur.B,'B'), (simulateur.NR,'NR'), (simulateur.NC,'NC'), (simulateur.G,'G'), \
           (simulateur.dP,'dP'), (simulateur.TCR,'TPR'), (simulateur.TCS,'TPS'), \
           (simulateur.CNV,'CNV'), (simulateur.EV,'EV') ][c]
    analyse.graphique(v,V)
pl.tight_layout(rect=[0, 0.03, 1, 0.95])

#analyse.mysavefig("conjoncture")
