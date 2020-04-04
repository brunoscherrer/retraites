# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for EtudeImpact class.
"""

import unittest
from retraites.SimulateurRetraites import SimulateurRetraites
from retraites.EtudeImpact import EtudeImpact
import numpy as np


class CheckEtudeImpact(unittest.TestCase):
    def test_0(self):
        simulateur = SimulateurRetraites()
        etudeImpact = EtudeImpact(simulateur)
        analyse = etudeImpact.calcule()

        # Vérifie les ordres de grandeurs des calculs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                np.testing.assert_allclose(analyse.A[s][a], 64.0, atol=4.0)
                np.testing.assert_allclose(analyse.RNV[s][a], 0.8, atol=0.3)
                np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=0.02)
                np.testing.assert_allclose(analyse.REV[s][a], 0.3, atol=0.2)
                np.testing.assert_allclose(analyse.T[s][a], 0.3, atol=0.3)
                np.testing.assert_allclose(analyse.P[s][a], 0.5, atol=0.3)

        # Vérifie la cohérence interne de l'objet
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                np.testing.assert_allclose(analyse.A[s][a],
                                           etudeImpact.As[s][a])
                np.testing.assert_allclose(analyse.S[s][a],
                                           etudeImpact.Ss[s][a], atol=1.e-7)
                np.testing.assert_allclose(analyse.Depenses[s][a],
                                           etudeImpact.Ds[s][a])

        # Vérifie précisément certaines valeurs numériques
        s = 2  # on se concentre sur le scenario 1,3% croissance
        a = 2030
        np.testing.assert_allclose(etudeImpact.As[s][a], 63.0, atol=0.1)
        np.testing.assert_allclose(etudeImpact.Ss[s][a], 0.0, atol=1.e-7)
        np.testing.assert_allclose(etudeImpact.Ds[s][a], 0.135, atol=0.001)
        a = 2050
        np.testing.assert_allclose(etudeImpact.As[s][a], 64.3, atol=0.1)
        np.testing.assert_allclose(etudeImpact.Ss[s][a], 0.0, atol=1.e-7)
        np.testing.assert_allclose(etudeImpact.Ds[s][a], 0.129, atol=0.001)
        a = 2070
        np.testing.assert_allclose(etudeImpact.As[s][a], 65.5, atol=0.1)
        np.testing.assert_allclose(etudeImpact.Ss[s][a], 0.0, atol=1.e-7)
        np.testing.assert_allclose(etudeImpact.Ds[s][a], 0.126, atol=0.001)
        return None

    def test_AgeParAnnee(self):
        simulateur = SimulateurRetraites()
        etudeImpact = EtudeImpact(simulateur)

        # Vérifie l'age par année et par génération
        # Génération 1975
        an = 1975.0
        ageDepart_reference = 63.6
        ageDepart = etudeImpact.ageDepartParGeneration(an)
        print("Generation", an, ", ageDepart", ageDepart)
        np.testing.assert_allclose(ageDepart, ageDepart_reference, atol=0.1)
        anneeDepart = 2038.6  # 1975.0 + 63.6
        ageDepart = etudeImpact.ageDepartParAnnee(anneeDepart)
        print("Annee", anneeDepart, ", ageDepart", ageDepart)
        np.testing.assert_allclose(ageDepart, ageDepart_reference, atol=0.1)

        # Génération 2000
        an = 2000.0
        ageDepart_reference = 65.2
        ageDepart = etudeImpact.ageDepartParGeneration(an)
        print("Generation", an, ", ageDepart", ageDepart)
        np.testing.assert_allclose(ageDepart, ageDepart_reference, atol=0.1)
        anneeDepart = 2065.2  # 2000.0 + 65.2
        ageDepart = etudeImpact.ageDepartParAnnee(anneeDepart)
        print("Annee", anneeDepart, ", ageDepart", ageDepart)
        np.testing.assert_allclose(ageDepart, ageDepart_reference, atol=0.1)
        return None


if __name__ == "__main__":
    unittest.main()
