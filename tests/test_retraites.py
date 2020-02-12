# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for SimulateurRetraites class.
"""

import unittest
from retraites.SimulateurRetraites import SimulateurRetraites
import pylab as pl
import numpy as np
import tempfile

class CheckSimulateur(unittest.TestCase):

    def test_0(self):
        # génération des graphes pour le statu quo (COR)
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        pl.figure(figsize=(6,8))
        pl.suptitle('Projections du COR',fontsize=16)
        
        analyse = simulateur.pilotageCOR()

        # Vérifie les ordres de grandeurs des calculs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                np.testing.assert_allclose(analyse.A[s][a], 64.0, atol=4.0)
                np.testing.assert_allclose(analyse.RNV[s][a], 0.8, atol=0.3)
                np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=0.02)
                np.testing.assert_allclose(analyse.REV[s][a], 0.3, atol=0.2)
                np.testing.assert_allclose(analyse.T[s][a], 0.3, atol=0.3)
                np.testing.assert_allclose(analyse.P[s][a], 0.5, atol=0.3)
        return None
    
    def test_graphiques(self):
        # génération des graphes pour le statu quo (COR)
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        
        analyse = simulateur.pilotageCOR()
        analyse.setDirectoryImage(tempfile.gettempdir())

        pl.figure(figsize=(6,8))
        pl.suptitle('Projections du COR',fontsize=16)
        analyse.dessineSimulation()
        pl.close()
        
        # Teste les options des graphiques
        pl.figure()
        analyse.graphique("P", analyse.P)
        pl.close()

        pl.figure()
        analyse.graphique("P")
        pl.close()

        pl.figure()
        analyse.graphique("P", dessine_legende = True)
        pl.close()

        pl.figure()
        analyse.graphique("P", scenarios_indices = range(1,5))
        pl.close()

        pl.figure()
        analyse.graphique("P", dessine_annees = range(2020,2041))
        pl.close()

        pl.figure()
        analyse.graphique("P", taille_fonte_titre = 14)
        pl.close()

        pl.figure()
        analyse.graphique("A")
        pl.close()

        pl.figure()
        analyse.graphique("S")
        pl.close()

        pl.figure()
        analyse.graphique("T")
        pl.close()

        pl.figure()
        analyse.graphique("RNV")
        pl.close()

        pl.figure()
        analyse.graphique("REV")
        pl.close()

        pl.figure()
        analyse.graphique("Depenses")
        analyse.sauveFigure("Depenses")
        pl.close()

        # Configure des longs titres
        analyse.setLabelLongs(True)
        analyse.graphique("P", analyse.P)
        pl.close()
        
        # Dessine la légende
        analyse.dessineLegende()
        analyse.sauveFigure("Legende")    
        pl.close()

        analyse.afficheSolutionsSimulateurCOR()

        return None
    
    def test_simulateur_retraites(self):
        # génération des graphes sur la conjoncture
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        simulateur.setDirectoryImage(tempfile.gettempdir())

        pl.figure(figsize=(10,8))
        pl.suptitle(u"Projections du COR (hypothèses)",fontsize=16)
        simulateur.dessineConjoncture()
        
        simulateur.sauveFigure("conjoncture")
        return None

    def test_2(self):
        # Pilotage 1 : calcul à âge et niveau de vie défini
        # génération des graphes pour des réformes à prestation garantie

        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        S=0.0
        Age=61.0
        RNV = 1.0
        analyse = simulateur.pilotageParAgeEtNiveauDeVie(Acible=Age, RNVcible=RNV, Scible=S)
        analyse.setDirectoryImage(tempfile.gettempdir())
    
        pl.figure(figsize=(6,8))
        if Age!=0:
            pl.suptitle( (u"Eq. financier, maintien du niveau de vie & départ à %d ans"%(Age)),fontsize=10)
        else:
            pl.suptitle(u"Equilibre financier & maintien du niveau de vie",fontsize=10)
                
        
        analyse.dessineSimulation()
        
        if Age!=0:
            analyse.sauveFigure( ("%dans"%(Age)))
        else:
            analyse.sauveFigure("cotisations")
            
        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.A[s][a], Age)
                    np.testing.assert_allclose(analyse.RNV[s][a], RNV)
                    np.testing.assert_allclose(analyse.S[s][a], S, atol=1.e-15)

        return None

    def test_3(self):
        # Pilotage 3 : calcul à cotisations et niveau de vie défini
        # génération des graphes pour la réforme Macron avec maintien du niveau de vie

        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
                    
        RNV=1.0
        analyse = simulateur.pilotageParNiveauDeVieEtCotisations(RNVcible=RNV, Scible=0.0)
        analyse.setDirectoryImage(tempfile.gettempdir())
        
        pl.figure(figsize=(6,8))
        pl.suptitle(u'Equilibre financier & maintien du niveau de vie',fontsize=12)
        analyse.dessineSimulation()
        
        print("Maintien du niveau de vie")
        analyse.afficheSolutionsSimulateurCOR()
        
        analyse.sauveFigure("macron_niveau_de_vie")
        
        # Vérifie les valeurs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.T[s][a], 0.3, atol=0.3)
                    np.testing.assert_allclose(analyse.RNV[s][a], RNV)
                    np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=1.e-15)

        return None
    
    def test_4(self):
        # Pilotage 2 : calcul à cotisations et pensions définies
        # génération des graphes pour la réforme Macron avec point indexé sur 
        # le salaire moyen (rapport (pension moyenne/)(salaire moyen) constant égal à celui de 2020)
        
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        pl.figure(figsize=(6,8))
        pl.suptitle(u'Equilibre financier & ratio pension/salaire fixe',fontsize=12)
        
        Pcible=simulateur.P[1][2020]
        analyse = simulateur.pilotageParCotisationsEtPensions(Pcible=Pcible, Scible=0.0)
        analyse.setDirectoryImage(tempfile.gettempdir())
            
        analyse.dessineSimulation()
        analyse.sauveFigure("macron_point_indexe")
        
        print("Maintien du rapport pension moyenne / salaire moyen")
        analyse.afficheSolutionsSimulateurCOR()

        # Vérifie les valeurs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][2020])
                    np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=1.e-15)
        return None

    def test_article2(self):
        # Pilotage 3 : calcul à cotisations et niveau de vie défini
        print("Données et figure pour article 2")
        
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        analyse = simulateur.pilotageParNiveauDeVieEtCotisations(RNVcible=1.0, Scible=0.0)
        analyse.setDirectoryImage(tempfile.gettempdir())
            
        pl.figure(figsize=(9,6))
        analyse.graphique("A")
        pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
        pl.legend(loc="best")
        analyse.sauveFigure("macron_68_ans")
    
        pl.figure(figsize=(9,6))
        analyse.graphique("A")
        pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
        pl.legend(loc="best")
        analyse.sauveFigure("macron_68_ans_tout")
        
        print("Réforme Macron, Maintien du niveau de vie")
        analyse.afficheSolutionsSimulateurCOR()
        
        # Vérifie les valeurs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.RNV[s][a], 1.0)
                    np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=1.e-15)
        return None
    
    def test_article3(self):
        # Pilotage 4 : calcul à cotisations et âge définis
    
        print("Données et figures pour article 3")
        
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        Age = 62.0
        analyse = simulateur.pilotageParCotisationsEtAge(Acible=Age, Scible=0.0) 
        analyse.setDirectoryImage(tempfile.gettempdir())
    
        pl.figure(figsize=(6,8))
        pl.suptitle(u"Equilibre financier, cotisations et âge définis")
        analyse.dessineSimulation()

        titre=u"Modèle du COR: Réforme Macron (éq. financier & départ à 62 ans)"
        
        pl.figure(figsize=(9,6))
        analyse.graphique("RNV")
        pl.suptitle(titre,fontsize=14)
        pl.legend(loc="best")
        analyse.sauveFigure("macron_62_ans_nv")
        
        pl.figure(figsize=(9,6))
        analyse.graphique("P")
        pl.suptitle(titre,fontsize=14)
        pl.legend(loc="best")
        analyse.sauveFigure("macron_62_ans_p")
        
        print("Réforme Macron, Départ à 62 ans")
        analyse.afficheSolutionsSimulateurCOR()
        print("\nEvolution du niveau de vie:")
        analyse.afficheVariable(analyse.RNV)
        print("\nEvolution du ratio pension/salaire:")
        analyse.afficheVariable(analyse.P)
        
        # Vérifie les valeurs
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], Age)
                    np.testing.assert_allclose(analyse.S[s][a], 0.0, atol=1.e-15)
        return None

    def test_pilotage5(self):
        # Pilotage 5 : calcul à âge et dépenses définis

        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        analyse = simulateur.pilotageParAgeEtDepenses(Scible=0.0)
        analyse.setDirectoryImage(tempfile.gettempdir())
    
        pl.figure(figsize=(8,10))
        pl.suptitle(u"Equilibre financier, age et dépenses définies")
        analyse.dessineSimulation()
        
        pl.figure()
        analyse.setLabelLongs(False)
        analyse.graphique("Depenses")
        
        analyse.dessineLegende()
            
        # Vérifie les valeurs imposées à partir de 2020
        analyse_COR = simulateur.pilotageCOR()
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                    np.testing.assert_allclose(analyse.Depenses[s][a], analyse_COR.Depenses[s][a])
                    np.testing.assert_allclose(analyse.S[s][a], 0., atol=1.e-15)

        return None

    def test_pilotage5_FixeAge(self):
        # Pilotage 5 : calcul à âge et dépenses définis
        # Fixe l'âge à une valeur non nulle

        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        analyse = simulateur.pilotageParAgeEtDepenses(Acible = 62.0, Scible = 0.0)
        analyse.setDirectoryImage(tempfile.gettempdir())
    
        pl.figure(figsize=(8,10))
        pl.suptitle(u"Equilibre financier, age et dépenses définies")
        analyse.dessineSimulation()
        
        pl.figure()
        analyse.setLabelLongs(False)
        analyse.graphique("Depenses")
        
        analyse.dessineLegende()
            
        # Vérifie les valeurs imposées à partir de 2020
        analyse_COR = simulateur.pilotageCOR()
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.A[s][a], 62.0)
                    np.testing.assert_allclose(analyse.Depenses[s][a], analyse_COR.Depenses[s][a])
                    np.testing.assert_allclose(analyse.S[s][a], 0., atol=1.e-15)

        return None
    
    def test_pilotageParPensionAgeCotisations(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ps = 0.5
        As = 62.0
        Ts = 0.28
        analyse = simulateur.pilotageParPensionAgeCotisations(Pcible=Ps, Acible=As, Tcible = Ts)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.P[s][a], Ps)
                    np.testing.assert_allclose(analyse.A[s][a], As)
                    np.testing.assert_allclose(analyse.T[s][a], Ts)

        return None

    def test_pilotageParSoldePensionAge(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ss = 0.0
        Ps = 0.5
        As = 62.0
        analyse = simulateur.pilotageParSoldePensionAge(Scible = Ss, Pcible=Ps, Acible=As)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.S[s][a], Ss)
                    np.testing.assert_allclose(analyse.P[s][a], Ps)
                    np.testing.assert_allclose(analyse.A[s][a], As)

        return None

    def test_pilotageParSoldePensionCotisations(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ss = 0.0
        Ps = 0.5
        Ts = 0.28
        analyse = simulateur.pilotageParSoldePensionCotisations(Scible=Ss, Pcible=Ps, Tcible = Ts)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.S[s][a], Ss, atol=1e-15)
                    np.testing.assert_allclose(analyse.P[s][a], Ps)
                    np.testing.assert_allclose(analyse.T[s][a], Ts)

        return None

    def test_pilotageParSoldeAgeCotisations(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ss = 0.0
        As = 62.0
        Ts = 0.28
        analyse = simulateur.pilotageParSoldeAgeCotisations(Scible=Ss, Acible=As, Tcible = Ts)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.S[s][a], Ss, atol=1e-15)
                    np.testing.assert_allclose(analyse.A[s][a], As)
                    np.testing.assert_allclose(analyse.T[s][a], Ts)

        return None

    def test_pilotageParSoldeAgeDepenses(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ss = 0.0
        As = 62.0
        Ds = 0.13
        analyse = simulateur.pilotageParSoldeAgeDepenses(Scible=Ss, Acible=As, Dcible = Ds)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.S[s][a], Ss, atol=1e-15)
                    np.testing.assert_allclose(analyse.A[s][a], As)
                    np.testing.assert_allclose(analyse.Depenses[s][a], Ds)

        return None

    def test_pilotageParSoldePensionDepenses(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ss = 0.0
        Ps = 0.5
        Ds = 0.13
        analyse = simulateur.pilotageParSoldePensionDepenses(Scible=Ss, Pcible=Ps, Dcible = Ds)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.S[s][a], Ss, atol=1e-15)
                    np.testing.assert_allclose(analyse.P[s][a], Ps)
                    np.testing.assert_allclose(analyse.Depenses[s][a], Ds)

        return None

    def test_pilotageParPensionCotisationsDepenses(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        Ps = 0.5
        Ts = 0.28
        Ds = 0.13
        analyse = simulateur.pilotageParPensionCotisationsDepenses(Pcible=Ps, Tcible=Ts, Dcible = Ds)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.P[s][a], Ps)
                    np.testing.assert_allclose(analyse.T[s][a], Ts)
                    np.testing.assert_allclose(analyse.Depenses[s][a], Ds)

        return None

    def test_pilotageParAgeCotisationsDepenses(self):
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        As = 62.0
        Ts = 0.28
        Ds = 0.13
        analyse = simulateur.pilotageParAgeCotisationsDepenses(Acible=As, Tcible=Ts, Dcible = Ds)

        # Vérifie les valeurs imposées à partir de 2020
        for s in simulateur.scenarios:
            for a in simulateur.annees:
                if (a<2020):
                    np.testing.assert_allclose(analyse.T[s][a], simulateur.T[s][a])
                    np.testing.assert_allclose(analyse.P[s][a], simulateur.P[s][a])
                    np.testing.assert_allclose(analyse.A[s][a], simulateur.A[s][a])
                else:
                    #print("s=%s, a=%s, S=%s" % (s, a, analyse.S[s][a]))
                    np.testing.assert_allclose(analyse.A[s][a], As)
                    np.testing.assert_allclose(analyse.T[s][a], Ts)
                    np.testing.assert_allclose(analyse.Depenses[s][a], Ds)

        return None

if __name__=="__main__":
    unittest.main()
