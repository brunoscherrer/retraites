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

if __name__=="__main__":
    unittest.main()
