# -*- coding: utf-8 -*-
# Copyright Michaël Baudin
"""
Test for SimulateurRetraites class.
"""
import unittest
from SimulateurRetraites import SimulateurRetraites
import pylab as pl

class CheckSimulateur(unittest.TestCase):

    def test_0(self):
        # génération des graphes pour le statu quo (COR)
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        
        pl.figure(figsize=(6,8))
        pl.suptitle('Projections du COR',fontsize=16)
                
        analyse = simulateur.pilotageCOR()
        analyse.graphiques()
    
        analyse.mysavefig("cor")

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
        age=61.0
        RNV = 1.0
        analyse = simulateur.pilotageParAgeEtNiveauDeVie(age, RNV, S)
    
        pl.figure(figsize=(6,8))
        if age!=0:
            pl.suptitle( (u"Cotisations adaptées (eq. financier, maintien du niveau de vie & départ à %d ans"%(age)),fontsize=10)
        else:
            pl.suptitle(u"Cotisations adaptées (équilibre financier & maintien du niveau de vie)",fontsize=10)
                
        
        analyse.graphiques()
        
        if age!=0:
            analyse.mysavefig( ("%dans"%(age)))
        else:
            analyse.mysavefig("cotisations")

        return None

    def test_3(self):
        # Pilotage 3 : calcul à cotisations et niveau de vie défini
        # génération des graphes pour la réforme Macron avec maintien du niveau de vie

        Ts=0
        RNV=1.0
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
                    
        analyse = simulateur.pilotageParNiveauDeVieEtCotisations(Ts,RNV)
        
        pl.figure(figsize=(6,8))
        pl.suptitle(u'Réforme Macron (équilibre financier & maintien du niveau de vie)',fontsize=12)
        analyse.graphiques()
        
        print("Maintien du niveau de vie")
        analyse.affiche_solutions_simulateur_COR()
        
        analyse.mysavefig("macron_niveau_de_vie")

        return None
    
    def test_4(self):
        # Pilotage 2 : calcul à cotisations et pensions définies
        # génération des graphes pour la réforme Macron avec point indexé sur 
        # le salaire moyen (rapport (pension moyenne/)(salaire moyen) constant égal à celui de 2020)
        
        Ps=0
        Ts=0
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        pl.figure(figsize=(6,8))
        pl.suptitle(u'Réforme Macron (équilibre financier & ratio pension/salaire fixe)',fontsize=12)
        
        analyse = simulateur.pilotageParCotisationsEtPensions(Ps,Ts)
            
        analyse.graphiques()
        analyse.mysavefig("macron_point_indexe")
        
        print("Maintien du rapport pension moyenne / salaire moyen")
        analyse.affiche_solutions_simulateur_COR()

        return None

    def test_article2(self):
        # Pilotage 3 : calcul à cotisations et niveau de vie défini
        print("Données et figure pour article 2")
        
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        Tcible = 0
        analyse = simulateur.pilotageParNiveauDeVieEtCotisations(Tcible)
            
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
        return None
    
    def test_article3(self):
        # Pilotage 4 : calcul à cotisations et âge définis
    
        print("Données et figures pour article 3")
        
        simulateur = SimulateurRetraites('../retraites/fileProjection.json')
        analyse = simulateur.pilotageParCotisationsEtAge(62) 
    
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
        return None

if __name__=="__main__":
    unittest.main()