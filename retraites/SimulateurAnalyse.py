#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 21:37:59 2020

@author: osboxes
"""
import pylab as pl
import os

class SimulateurAnalyse:
    ### fonctions pour générer des graphiques
    def __init__(self, T, P, A, S, RNV, REV, Depenses, \
                 scenarios, annees_EV, annees, dir_image="."):
        """
        Créée une analyse de simulateur de retraites.
        
        Paramètres
        T: un dictionnaire, niveau des cotisations sociales
        P: un dictionnaire, niveau des pensions par rapport aux salaires
        A: un dictionnaire, âge moyen de départ à la retraite
        S: un dictionnaire, Situation financière du système de retraite en \% du PIB
        RNV: un dictionnaire, Niveau de vie des retraités par rapport à l'ensemble de la population
        REV: un dictionnaire, Durée de la vie passée à la retraite
        Depenses: un dictionnaire, Dépenses de retraites en % PIB
        scenarios: une liste d'indices, les scénarios considérés
        annees_EV: une liste d'entiers, annees sur lesquelles on a l'espérance de vie
        annees: une liste d'entiers supérieurs ou égaux à 1, les scenarios consideres
        dir_image : le répertoire de sauvegarde des images 
                    (par défaut, le répertoire courant)
        
        Exemple
        simulateur = SimulateurRetraites('retraites/fileProjection.json')
        analyse = simulateur.pilotageCOR()
        analyse.graphiques()
        """
        self.scenarios = scenarios
        self.annees_EV = annees_EV
        self.annees = annees

        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        self.T = T
        self.P = P
        self.A = A
        self.S = S
        self.RNV = RNV
        self.REV = REV
        self.Depenses = Depenses

        self.scenarios_labels=["Hausse des salaires: +1,8%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,5%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,3%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1%/an, Taux de chômage: 7%",
                              "Hausse des salaires: +1,8%/an, Taux de chômage: 4.5%",
                              "Hausse des salaires: +1%/an, Taux de chômage: 10%"]
        self.scenarios_labels_courts=["+1,8%/an, Taux de chômage: 7%",
                              "+1,5%/an, Chômage: 7%",
                              "+1,3%/an, Chômage: 7%",
                              "+1%/an, Chômage: 7%",
                              "+1,8%/an, Chômage: 4.5%",
                              "+1%/an, Chômage: 10%"]

        self.labels_is_long = True # True, si on utilise les labels longs
        
        self.dir_image=dir_image # répertoire pour les images

        self.ext_image=["png","pdf"]   # types de fichier à générer
        
        # Configure les plages min et max pour l'axe des ordonnées 
        # des variables standard en sortie du simulateur
        self.yaxis_lim = dict()
        self.yaxis_lim["S"] = [-2.0,2.0]
        self.yaxis_lim["RNV"] = [60.0,120.0]
        self.yaxis_lim["REV"] = [20.0,40.0]
        self.yaxis_lim["T"] = [25.0,40.0]
        self.yaxis_lim["A"] = [60,72]
        self.yaxis_lim["P"] = [25.0,55.0]
        self.yaxis_lim["Depenses"] = [11.0,15.0]
        
        # Liste des années dans le simulateur du COR
        self.liste_annees=[2020, 2025, 2030, 2040, 2050, 2060, 2070]

        return None
    
    def setImageFormats(self, ext_image):
        """
        Configure le format de sauvegarde des images
        
        ext_image : une liste de chaînes de caractères (par defaut, ext_image=["png","pdf"])
        """
        self.ext_image = ext_image
        return None

    def getImageFormats(self):
        """
        Retourne le répertoire contenant les images
        """
        return self.ext_image 

    
    def setLabelLongs(self, labels_is_long):
        """
        Configure la longueur des étiquettes
        
        labels_is_long : un booléen, True si les labels longs sont utilisés (par défaut = True)
        """
        self.labels_is_long = labels_is_long
        return None

    def getLabelLongs(self):
        """
        Retourne le répertoire contenant les images
        """
        return self.labels_is_long 

    def setDirectoryImage(self, dir_image):
        """
        Configure le répertoire contenant les images
        
        dir_image : une chaîne de caractères, le répertoire contenant les images 
        (par défaut, dir_image="fig")
        exportées par mysavefig.
        """
        self.dir_image = dir_image
        return None

    def getDirectoryImage(self):
        """
        Retourne le répertoire contenant les images
        """
        return self.dir_image

    def mysavefig(self, f):
        """
        Sauvegarde l'image dans le répertoire
        
        Paramètres:
        f : une chaîne de caractères, le nom des fichiers à sauver
        
        Description
        Sauvegarde l'image dans les formats définis. 
        
        Exemple:
        analyse.mysavefig("conjoncture")
        """
    
        for ext in self.ext_image:
            basefilename = f + "." + ext
            filename = os.path.join(self.dir_image,basefilename)
            pl.savefig(filename)
        return None
    
    def graphique(self, v, nom, font_size=8, yaxis_lim=[], \
                  draw_legend=False, scenarios_indices=None):
        """
        Dessine un graphique associé à une variable donnée 
        pour tous les scénarios.
        
        Paramètres:
        v : variable à dessiner
        nom : chaîne de caractère, nom de la variable
        font_size : taille de la fonte (par défaut, fs=8)
        yaxis_lim : une liste de taille 2, les bornes inférieures et supérieures 
        de l'axe des ordonnées
        draw_legend : booleen, True si la légende doit être dessinée
        scenarios_indices : une liste d'entiers, la liste des indices des scénarios
        (par défaut, sc = range(1,7))
        
        Exemple:
        analyse.graphique(analyse.RNV,"RNV",14,[],True,range(1,6))
        """
        if scenarios_indices==None:
            scenarios_indices = self.scenarios
            
        if nom=="EV":
            an=self.annees_EV
        else:
            an=self.annees
    
        for s in scenarios_indices:
            if (nom=="S" or nom=="RNV" or nom=="T" or nom=="P" \
                or nom=="REV" or nom=="Depenses"):
                y = [ 100.0 * v[s][a] for a in an ]
            else:
                y = [ v[s][a] for a in an ]
            if (self.labels_is_long):
                label_variable = self.scenarios_labels[s-1]
            else:
                label_variable = self.scenarios_labels_courts[s-1]
            pl.plot(an, y, label=label_variable )
    
        # titres des figures
        liste_variables = ["S","RNV","REV","T","A","P","B","NR","NC","G","dP","TPR","TPS","CNV","EV","Depenses"]
        indice_variable = liste_variables.index(nom)
        t=[u"Situation financière du système (% PIB)",
           u"Niveau de vie des retraités p/r à l'ensemble (%)",
           u"Proportion de la vie passée à la retraite (%)",
           u"Taux de cotisation de retraite (% PIB)",
           u"Age de départ effectif moyen à la retraite",
           u"Ratio (pension moyenne)/(salaire moyen) (%)",
           u"B: Part des revenus d'activité bruts dans le PIB",
           u"NR: Nombre de retraités",
           u"NC: Nombre de cotisants",
           u"G: Effectif d'une generation arrivant à l'âge de la retraite",
           u"dP: Autres dépenses de retraites",
           u"TPR: Taux de prélèvement sur les retraites",
           u"TPS: Taux de prélèvement sur les salaires",
           u"CNV: (niveau de vie)/[(pension moy))/(salaire moy)]",
           u"EV: Espérance de vie à 60 ans",
           u"Dépenses de retraites (% PIB)"
        ][ indice_variable ]
           
        pl.title(t,fontsize=font_size)
        
        # Ajuste les limites de l'axe des ordonnées
        if yaxis_lim==[]:
            # If the use did not set the yaxis_lim
            if nom in self.yaxis_lim.keys():
                # If the variable name was found in the dictionnary
                yaxis_lim = self.yaxis_lim[nom]

        if yaxis_lim!=[]:
            pl.ylim(bottom=yaxis_lim[0],top=yaxis_lim[1])

        if draw_legend:
            pl.legend(loc="best")
        return None
    
    def graphiques(self, font_size=8):
        """
        Dessine les 6 graphiques "standards" 
        pour tous les scénarios.
        
        Paramètres:
        font_size : taille de la fonte (par défaut, fs=8)
        
        Description
        Dessine S, RNV, REV, T, A, P. 
        
        Exemple:
        analyse.graphique(analyse.RNV,"RNV",14,[],True,range(1,6))
        """
    
        for i in range(6):
            pl.subplot(3,2,i+1)
            v,V = [ (self.S,"S" ),
                      (self.RNV,"RNV"),
                      (self.REV,"REV"),
                      (self.T,"T" ),
                      (self.A,"A"),
                      (self.P,"P") ][ i ]
            self.graphique(v, V, font_size)
        pl.tight_layout(rect=[0, 0.03, 1, 0.95])
        return None
    
    def affiche_variable(self, v):
        """
        Affiche les valeurs d'une variable. 
        
        v : une variable
        
        Exemple
        analyse.affiche_variable(RNV)
        """
    
        for s in self.scenarios:
            print()
            print("Scenario",s,": ",self.scenarios_labels[s-1])
            for a in self.liste_annees:
                print("%d : %.3f"%(a, v[s][a]))
            print("")
        return None
            
    def affiche_solutions_simulateur_COR(self):
        """
        Affiche les paramètres du simulateur. 
        """
    
        print("Valeurs à rentrer sur le simulateur officiel du COR:")
        
        for s in self.scenarios:
            print("")
            print("Scenario",s,": ",self.scenarios_labels[s-1] )
            print("Annéee, Age,      Cotis., Pension:",)
            for a in self.liste_annees:
                print("%5d : %.1f ans, %.1f %%, %.1f %%"%(a, \
                                                         self.A[s][a], \
                                                         100*self.T[s][a], \
                                                         100*self.P[s][a]))
        return None
    
    def plot_legend(self):
        """
        Affiche les légendes des graphiques.
        """
        # Juste les légendes
        pl.figure(figsize=(6,2))
        nb_scenarios = len(self.scenarios_labels)
        for i in range(nb_scenarios):
            pl.plot(0.,0.,label=self.scenarios_labels[i])
        pl.legend(self.scenarios_labels, loc="center")
        pl.ylim(bottom=0.0,top=0.7)
        pl.axis('off')
        return None
