# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for SimulateurRetraites class.
"""

import unittest
from retraites.SimulateurRetraites import SimulateurRetraites
from retraites.FonctionPension import FonctionPension
import numpy as np
import openturns as ot

def CalculePAvecModelePension(annee, scenario):
    """
    Pour une annéee et un scenario, calcule P avec les paramètres 
    du COR. 
    """
    simulateur = SimulateurRetraites()
    modele = FonctionPension(simulateur, annee)
    analyse = simulateur.pilotageCOR()
    # Evaluation
    S = analyse.S[scenario][annee]
    D = analyse.Depenses[scenario][annee]
    As = analyse.A[scenario][annee]
    F = 0.5
    TauC = simulateur.scenarios_chomage[scenario]
    X = ot.Point([S, D, As, F, TauC])
    Y = modele(X)
    return Y

def LRE10(computed, exact):
    """
    Calcule la Log-Relative Error en base 10.
    """
    re = abs(computed - exact) / abs(exact)
    lre = -np.log10(re)
    lre = min(15.0, lre)
    return lre


class CheckFonctionPension(unittest.TestCase):

    def test_Init(self):
        simulateur = SimulateurRetraites()
        # Initialisation
        annee = 2020
        modele = FonctionPension(simulateur, annee)
        # Evaluation
        S = 0.0
        D = 0.14
        As = 63.0
        F = 0.5
        TauC = 7.00
        X = ot.Point([S, D, As, F, TauC])
        Y = modele(X)
        Y_exact = [0.547295]
        np.testing.assert_allclose(Y, Y_exact)
        # Description
        description = modele.getInputDescription()
        self.assertEqual(description, ["S", "D", "As", "F", "TauC"])
        description = modele.getOutputDescription()
        self.assertEqual(description, ["P"])
        return None

    def test_PensionParAnnee(self):
        """
        Vérifie P par comparaison avec les calculs du COR
        """
        simulateur = SimulateurRetraites()
        analyse = simulateur.pilotageCOR()
        for annee in simulateur.annees:
            for scenario in [simulateur.scenario_central, 
                             simulateur.scenario_optimiste, 
                             simulateur.scenario_pessimiste]:
                Y = CalculePAvecModelePension(annee, scenario)[0]
                Y_exact = analyse.P[scenario][annee]
                np.testing.assert_allclose(Y, Y_exact)
        return None

if __name__=="__main__":
    unittest.main()
