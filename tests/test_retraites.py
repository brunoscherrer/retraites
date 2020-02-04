# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for SimulateurRetraites class.
"""

import unittest
from SimulateurRetraites import SimulateurRetraites
import pylab as pl
import numpy as np

class CheckSimulateur(unittest.TestCase):

    def test_0(self):
        # génération des graphes pour le statu quo (COR)
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        pl.figure(figsize=(6,8))
        pl.suptitle('Projections du COR',fontsize=16)
        
        analyse = simulateur.pilotageCOR()
        analyse.graphiques()
    
        analyse.mysavefig("cor")
        
        analyse.affiche_solutions_simulateur_COR()

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
    
    def test_1(self):
        # génération des graphes sur la conjoncture
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
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
        
        analyse.mysavefig("conjoncture")
        return None

    def test_2(self):
        # Pilotage 1 : calcul à âge et niveau de vie défini
        # génération des graphes pour des réformes à prestation garantie

        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        S=0.0
        Age=61.0
        RNV = 1.0
        analyse = simulateur.pilotageParAgeEtNiveauDeVie(Acible=Age, RNVcible=RNV, Scible=S)
    
        pl.figure(figsize=(6,8))
        if Age!=0:
            pl.suptitle( (u"Eq. financier, maintien du niveau de vie & départ à %d ans"%(Age)),fontsize=10)
        else:
            pl.suptitle(u"Equilibre financier & maintien du niveau de vie",fontsize=10)
                
        
        analyse.graphiques()
        
        if Age!=0:
            analyse.mysavefig( ("%dans"%(Age)))
        else:
            analyse.mysavefig("cotisations")
            
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
        
        pl.figure(figsize=(6,8))
        pl.suptitle(u'Equilibre financier & maintien du niveau de vie',fontsize=12)
        analyse.graphiques()
        
        print("Maintien du niveau de vie")
        analyse.affiche_solutions_simulateur_COR()
        
        analyse.mysavefig("macron_niveau_de_vie")
        
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
            
        analyse.graphiques()
        analyse.mysavefig("macron_point_indexe")
        
        print("Maintien du rapport pension moyenne / salaire moyen")
        analyse.affiche_solutions_simulateur_COR()

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
            
        pl.figure(figsize=(9,6))
        analyse.graphique(analyse.A,"A",14,[],True,range(1,5))
        pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
        pl.legend(loc="best")
        analyse.mysavefig("macron_68_ans")
    
        pl.figure(figsize=(9,6))
        analyse.graphique(analyse.A,"A",14,[],True)
        pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
        pl.legend(loc="best")
        analyse.mysavefig("macron_68_ans_tout")
        
        print("Réforme Macron, Maintien du niveau de vie")
        analyse.affiche_solutions_simulateur_COR()
        
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
    
        pl.figure(figsize=(6,8))
        pl.suptitle(u"Equilibre financier, cotisations et âge définis")
        analyse.graphiques()

        titre=u"Modèle du COR: Réforme Macron (éq. financier & départ à 62 ans)"
        
        pl.figure(figsize=(9,6))
        analyse.graphique(analyse.RNV,"RNV",14,[],True,range(1,5))
        pl.suptitle(titre,fontsize=14)
        pl.legend(loc="best")
        analyse.mysavefig("macron_62_ans_nv")
        
        pl.figure(figsize=(9,6))
        analyse.graphique(analyse.P,"P",14,[],True,range(1,5))
        pl.suptitle(titre,fontsize=14)
        pl.legend(loc="best")
        analyse.mysavefig("macron_62_ans_p")
        
        print("Réforme Macron, Départ à 62 ans")
        analyse.affiche_solutions_simulateur_COR()
        print("\nEvolution du niveau de vie:")
        analyse.affiche_variable(analyse.RNV)
        print("\nEvolution du ratio pension/salaire:")
        analyse.affiche_variable(analyse.P)
        
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
    
        pl.figure(figsize=(8,10))
        pl.suptitle(u"Equilibre financier, age et dépenses définies")
        analyse.graphiques()
        
        pl.figure()
        analyse.setLabelLongs(False)
        analyse.graphique(analyse.Depenses,"Depenses")
        
        analyse.plot_legend()
            
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
    
        pl.figure(figsize=(8,10))
        pl.suptitle(u"Equilibre financier, age et dépenses définies")
        analyse.graphiques()
        
        pl.figure()
        analyse.setLabelLongs(False)
        analyse.graphique(analyse.Depenses,"Depenses")
        
        analyse.plot_legend()
            
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


if __name__=="__main__":
    unittest.main()
