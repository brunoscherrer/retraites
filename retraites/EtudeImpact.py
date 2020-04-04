#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe pour simuler l'étude d'impact de Janvier 2020.
"""
from scipy import interpolate
from copy import deepcopy

class EtudeImpact:
    def __init__(self, simulateur):
        """
        Créée un simulateur reproduisant l'étude d'impact.
        
        Paramètres :
            simulateur: un SimulateurRetraites.
        
        Exemple :
            from retraites.SimulateurRetraites import SimulateurRetraites
            from retraites.EtudeImpact import EtudeImpact
            simulateur = SimulateurRetraites()
            etudeImpact = EtudeImpact(simulateur)
            etudeImpact.calcule()
            Ds = etudeImpact.getDepenses()
            Ss = etudeImpact.getSolde()
            As = etudeImpact.getAge()
            
        Attributs :
            simulateur : 
                un SimulateurRetraites
            depenses_annee_transition :
                un entier. 
                L'année de transition de l'étude d'impact.
            depenses_annee_extrapolation :
                un entier.
                La première année d'extrapolation au delà des données 
                de l'étude d'imact. 
            depenses_annees : 
                une liste d'entiers. 
                La liste des années où le montant des dépenses est connu 
                dans l'étude d'impact. 
            depenses_valeurs : 
                une liste de flottants.
                La liste des montants des dépenses d'après le tableau 39 
                de l'étude d'impact. 
            analyse : 
                un SimulateurAnalyse. 
                L'analyse du pilotage du COR. 
            Ds :
                un dictionnaire. 
                Le montant des dépenses dans chaque scénario, 
                pour chaque année. 
            Ss :
                un dictionnaire. 
                Le solde financier dans chaque scénario, 
                pour chaque année.
            As :
                un dictionnaire. 
                L'âge effectif moyen de départ en retraite dans chaque scénario, 
                pour chaque année. 
            premiere_generation : 
                Un entier. 
                L'année de naissance de la première génération affectée 
                par la transition. 
            age_premiere_generation :
                Un flottant. 
                L'âge moyen de départ à la retraite de la première 
                génération affectée par la transition. 
            derniere_generation :
                Un entier. 
                L'année de naissance la plus grande détaillée dans l'étude 
                d'impact relatif à l'âge effectif moyen de départ en retraite. 
            age_derniere_generation :
                Un flottant. 
                L'âge effectif moyen de départ en retraite de la dernière 
                génération évoquée dans l'étude d'impact.
            age_annee_transition : 
                un entier. 
                L'année où la première génération de la transition 
                part en retraite. 
            age_annee_extrapolation : 
                un entier. 
                L'année où la dernière génération évoquée dans l'étude d'impact 
                part en retraite. 
            solde_annee_transition : 
                Un entier. 
                La première année de transition pour le solde.
            solde_annee_equilibre : 
                Un entier. 
                La première année d'équilibre pour le solde.
            epaisseur_ligne : 
                Un entier. 
                L'épaisseur de la ligne pour reproduire graphiquement 
                l'étude d'impact.
            couleur_HR : 
                Une chaîne de caractère. 
                La couleur d'une courbe "Hors réforme" ou "Avant réforme".
            couleur_SUR : 
                Une chaîne de caractère. 
                La couleur d'une courbe "SUR" ou "Après réforme".
            
        """
        # Liste des années dans le simulateur du COR
        self.simulateur = simulateur
        
        # Paramètres pour le calcul des dépenses
        self.depenses_annee_transition = 2020
        self.depenses_annee_extrapolation = 2050
        self.depenses_annees =  [2025,  2030,  2040,  2050,  2060,  2070]
        self.depenses_valeurs = [0.136, 0.135, 0.133, 0.129, 0.1275, 0.126]
        
        self.analyse = self.simulateur.pilotageCOR()
        self.Ds = deepcopy(self.analyse.Depenses)
        self.Ss = deepcopy(self.analyse.S)
        self.As = deepcopy(self.analyse.A)
        
        # Paramètres pour le calcul des âges
        # Paramètres de l'interpolation linéaire
        self.premiere_generation = 1975
        self.age_premiere_generation = 63.6
        self.derniere_generation = 2000 # Graphique 49 : 1990
        self.age_derniere_generation = 65.2 # Graphique 49 : 64.83
        self.age_annee_transition = int(self.premiere_generation + self.age_premiere_generation) # 2038
        self.age_annee_extrapolation = int(self.derniere_generation + self.age_derniere_generation) # 2065
        
        # Paramètre pour le calcul du solde
        self.solde_annee_transition = 2020
        self.solde_annee_equilibre = 2027 # Première année d'équilibre strict
        
        # Préférences graphiques de l'étude d'impact
        self.epaisseur_ligne= 3
        self.couleur_HR = "cornflowerblue"
        self.couleur_SUR = "orange"

        return None

    def calcule(self):
        """
        Calcule la trajectoire dans l'étude d'impact.
        Le pilotage est réalisé à partir de l'âge moyen de départ en retraite, 
        des dépenses et du solde financier. 
        """
        self.calculeDepenses()
        self.calculeAgeDepartRetraite()
        self.calculeSolde()
        
        analyse = self.simulateur.pilotageParSoldeAgeDepenses(Scible=self.Ss, Acible=self.As, Dcible=self.Ds)
        return analyse
    
    def calculeDepenses(self):
        """
        Calcule la trajectoire des dépenses dans l'étude d'impact.
        Source : Tableau 39 de l'étude d'impact, page 176. 
        Méthode interpolation quadratique dans les 
        données de la table. 
        """        

        # Crée une liste d'années et une liste de dépenses
        # Crée une liste initiale : la première valeur sera remplacée pour chaque 
        # scénario par la suite.
        annees =   [self.depenses_annee_transition]
        for a in self.depenses_annees:
            annees.append(a)
        valeur_factice = -1.0
        depenses = [valeur_factice]
        for d in self.depenses_valeurs:
            depenses.append(d)            
        # Boucle sur les scénarios
        for s in self.simulateur.scenarios:
            # Affecte la dernière dépense constatée dans le scénario
            depenses[0] = self.analyse.Depenses[s][self.depenses_annee_transition]
            
            # Crée l'interpolateur
            depenses_interpolateur = interpolate.interp1d(annees, depenses, kind="quadratic")
            
            # Corrige les dépenses
            for a in self.simulateur.annees_futures:
                if (a>=self.depenses_annee_transition):
                    self.Ds[s][a] = depenses_interpolateur(a)

        return None

    def ageDepartParAnnee(self, a):
        """
        Calcule l'âge de départ pour une année de départ en retraite donnée.

        Paramètres
            a : année de départ en retraite
        
        Description :
            Retourne l'âge de départ en retraite.
        """
        # Interpolation linéaire inverse
        Age1 = self.age_premiere_generation
        Age2 = self.age_derniere_generation
        an1 = self.premiere_generation
        an2 = self.derniere_generation
        As = (Age2 * (a - an1) + Age1 * (an2 - a)) / ((an2 - an1) + (Age2 - Age1))
        return As

    def ageDepartParGeneration(self, an):
        """
        Calcule l'âge de départ pour une année de naissance donnée. 
        
        Paramètres :
            an : année de naissance
        
        Description :
            Retourne l'âge de départ en retraite
        """
        # Interpolation linéaire inverse
        Age1 = self.age_premiere_generation
        Age2 = self.age_derniere_generation
        an1 = self.premiere_generation
        an2 = self.derniere_generation
        As = Age1 * (an2 - an) / (an2 - an1) + Age2 * (an - an1) / (an2 - an1)
        return As

    def calculeAgeDepartRetraite(self):
        """
        Calcule l'âge de départ en retraite de l'étude d'impact (Janvier 2020).
        Source : graphique 73 page 139 de l'étude d'impact de Janvier 2020. 
        Méthode : interpolation linéaire, puis inversion formelle des équations 
        pour obtenir l'âge de départ en retraite en fonction de l'année 
        de départ en retraite. 
        
        Note : dans la première version, nous utilisions le 
        graphique 49 page 139 de l'étude d'impact de Janvier 2020. 
        Mais le graphique 49 s'arrête en 1990 alors que le graphique 73 
        présente jusqu'à 2000.
        """
    
        for s in self.simulateur.scenarios:
            for a in self.simulateur.annees_futures:
                if (a>=self.age_annee_transition):
                    self.As[s][a] = self.ageDepartParAnnee(a)
                    
        return None
    
    def calculeSolde(self):
        """
        Calcul le solde de l'étude d'impact (Janvier 2020).
        Source : graphique 63, page 180 "Solde du système de retraites, avant et après réforme"
        Données : courbe pointillé orange jusqu'à 2027, puis 
        courbe orange en trait plein.
        Method : interpolation linéaire
        """
        annees = [self.solde_annee_transition, 2027, 2070]
        
        # Met à jour le solde
        for s in self.simulateur.scenarios:
            dernier_solde_constate = self.analyse.S[s][self.solde_annee_transition]
            soldes = [dernier_solde_constate, 0.0, 0.0]
    
            # Crée l'interpolateur de solde financier   
            soldes_interpolateur = interpolate.interp1d(annees, soldes)
            for a in self.simulateur.annees_futures:
                if (a>=self.solde_annee_transition):
                    self.Ss[s][a] = soldes_interpolateur(a)
        
        return None
    
