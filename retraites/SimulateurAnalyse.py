#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 21:37:59 2020

@author: osboxes
"""
import pylab as pl

class SimulateurAnalyse:
    ### fonctions pour générer des graphiques
    def __init__(self, simulateur, dir_image):
        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        self.simulateur = simulateur

        self.scenarios_labels=["Hausse des salaires: +1,8%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,5%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,3%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,8%/an, Taux de chômage: 4.5%",
                              "Hausse des salaires: +1%/an, Taux de chômage: 10%"]
        self.dir_image=dir_image        # répertoire pour les images

        return None
    
    def mysavefig(self, f):
        ext_image=["png","pdf"]   # types de fichier à générer
    
        for ext in ext_image:
            pl.savefig(self.dir_image + f + "." + ext)
        return None
    
    def graphique(self, v, nom, fs=8, rg=[], leg=False, sc=None):
        if sc==None:
            sc = self.simulateur.scenarios
            
        if nom=="EV":
            an=self.simulateur.annees_EV
        else:
            an=self.simulateur.annees
    
        for s in sc:
            pl.plot(an, [ v[s][a] for a in an ], label=self.scenarios_labels[s-1] )
    
        # titres des figures
        
        t=[u"Situation financière du système (part du PIB)",
           u"Niveau de vie des retraités p/r à celui des actifs",
           u"Proportion de la vie passée à la retraite",
           u"Taux de cotisation de retraite (part du PIB)",
           u"Age de départ effectif moyen à la retraite",
           u"Ratio (pension moyenne)/(salaire moyen)",
           u"B: Part des revenus d'activité bruts dans le PIB",
           u"NR: Nombre de retraités",
           u"NC: Nombre de cotisants",
           u"G: Effectif d'une generation arrivant à l'âge de la retraite",
           u"dP: Autres dépenses de retraites",
           u"TPR: Taux de prélèvement sur les retraites",
           u"TPS: Taux de prélèvement sur les salaires",
           u"CNV: (niveau de vie)/[(pension moy))/(salaire moy)]",
           u"EV: Espérance de vie à 60 ans"
        ][ ["S","RNV","REV","T","A","P","B","NR","NC","G","dP","TPR","TPS","CNV","EV"].index(nom) ]
           
        pl.title(t,fontsize=fs)
        if rg!=[]:
            pl.ylim(bottom=rg[0],top=rg[1])
        if leg:
            pl.legend(loc="best")
        return None
    
    def graphiques(self, T, P, A, S, RNV, REV, fs=8):
    
        for i in range(6):
            pl.subplot(3,2,i+1)
            v,V,r = [ (S,"S" ,[-0.02,0.02]),
                      (RNV,"RNV", [0.6,1.2]),
                      (REV,"REV", [0.2,0.4]),
                      (T,"T", [0.25,0.4] ),
                      (A,"A", [60,70]),
                      (P,"P", [.25,.55]) ][ i ]
            self.graphique(v, V, fs ,r)
        pl.tight_layout(rect=[0, 0.03, 1, 0.95])
        return None
        
    ##############################################################################
    
    def affiche_variable(self, v):
    
        ans=[2019, 2020, 2025, 2030, 2040, 2050, 2060, 2070]
        for s in self.simulateur.scenarios:
            print()
            print("Scenario",s,": ",self.scenarios_labels[s-1])
            for a in ans:
                print("%.2f"%(v[s][a]),)
            print("")
        return None
            
    def affiche_solutions_simulateur_COR(self, Ts,Ps,As):
    
        print("Valeur à rentrer sur le simulateur officiel du COR:")
        
        ans=[2020, 2025, 2030, 2040, 2050, 2060, 2070]
        for s in self.simulateur.scenarios:
            print("")
            print("Scenario",s,": ",self.scenarios_labels[s-1] )
            print("Age:        ",)
            for a in ans:
                print("%.1f"%(As[s][a]),)
            print("")
            print("Cotisation: ",)
            for a in ans:
                print("%.1f"%(100*Ts[s][a]),)
            print("")
            print("Pension:    ",)
            for a in ans:
                print("%.1f"%(100*Ps[s][a]),)
            print("")
            print("")
        return None
    