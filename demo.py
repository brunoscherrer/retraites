#!/usr/bin/python
# coding:utf-8

from retraites.SimulateurRetraites import SimulateurRetraites

simulateur = SimulateurRetraites()
analyse = simulateur.pilotageCOR()
analyse.afficheSolutionsSimulateurCOR()

