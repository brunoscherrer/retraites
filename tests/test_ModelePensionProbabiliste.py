# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for SimulateurRetraites class.
"""

import unittest
from retraites.SimulateurRetraites import SimulateurRetraites
from retraites.ModelePensionProbabiliste import ModelePensionProbabiliste
import openturns as ot

class CheckModelePensionProbabiliste(unittest.TestCase):

    def test_Init(self):
        """
        Teste la création de l'objet ModelePensionProbabiliste.
        """
        simulateur = SimulateurRetraites()
        S = 0.0
        D = 0.14
        annee = 2050
        modele = ModelePensionProbabiliste(simulateur, annee, S, D)
        # Vérifie la fonction
        fonction = modele.getFonction()
        dim = fonction.getInputDimension()
        self.assertEqual(dim, 3)
        # Vérifie la distribution
        inputDistribution = modele.getInputDistribution()
        dim = inputDistribution.getDimension()
        self.assertEqual(dim, 3)
        return None

    def test_GetSample(self):
        """
        Teste l'utilisation de l'objet ModelePensionProbabiliste.
        """
        simulateur = SimulateurRetraites()
        S = 0.0
        D = 0.14
        annee = 2050
        modele = ModelePensionProbabiliste(simulateur, annee, S, D)
        fonction = modele.getFonction()
        inputDistribution = modele.getInputDistribution()
        # Crée un vecteur aléatoire
        inputRandomVector = ot.RandomVector(inputDistribution)
        outputRandomVector = ot.CompositeRandomVector(fonction, inputRandomVector)
        sampleSize = 100
        sample = outputRandomVector.getSample(sampleSize)
        # Vérifie l'échantillon
        dim = sample.getDimension()
        self.assertEqual(dim, 1)
        size = sample.getSize()
        self.assertEqual(size, sampleSize)
        return None

if __name__=="__main__":
    unittest.main()
