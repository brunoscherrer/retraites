#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openturns as ot
import scipy as sp

class FonctionPension(ot.OpenTURNSPythonFunction):
    def __init__(self, simulateur, annee, verbose = False):
        """
        Crée un modèle de pension.
        
        Paramètres :
            simulateur : un SimulateurRetraite
            annee : l'année de calcul de P
            verbose : si vrai, affiche des variables intermédiaires durant l'évaluation
        
        Description :
            Crée un modèle de pension permettant d'évaluer le 
            ratio (pension moyenne) / (salaire moyen) pour une année donnée.
        
            Les entrées de la fonction sont "S", "D", "As", "F", "TauC" 
            et la sortie est "P". 
            
            * S : le solde financier du système de retraites (% PIB)
            * D : le montant des dépenses (% PIB)
            * As : l'âge moyen de départ à la retraite défini par l'utilisateur
            * F  : facteur d'élasticité de report de l'âge de départ 
                (par exemple F=0.5)
            * TauC : le taux de chômage (par exemple TauC = 4.5)
            * P : le rapport entre le montant moyen des pensions et le 
                 montant moyen des salaires
        
            Les autres paramètres  sont ceux du simulateur, 
            dans le scénario central (i.e. s = 1) à l'année considérée. 
        
            Le modèle calcule NC, dP, B, G, A, NR en fonction du taux 
            de chômage TauC par interpolation dans les données 
            du COR. 
            
        Attributs :
            simulateur : 
                un SimulateurRetraites
            annee : 
                un entier. L'année de calcul.
            verbose : 
                un booléen. Si vrai, affiche les calculs intermédiaires.
            interpolateur_NC : 
                une fonction. 
                L'interpolateur du nombre de cotisants. 
            interpolateur_dP : 
                une fonction. 
                L'interpolateur des autres dépenses de retraite.
            interpolateur_B : 
                une fonction. 
                L'interpolateur de la part des revenus d'activités bruts dans le PIB. 
            interpolateur_NR : 
                une fonction. 
                L'interpolateur du nombre de retraités. 
            interpolateur_G : 
                une fonction. 
                L'interpolateur de l'effectif moyen d'une génération 
                arrivant aux âges de la retraite. 
            interpolateur_A : 
                une fonction. 
                L'interpolateur de l'âge effectif moyen de départ en retraite. 

        Exemple :
            modele = FonctionPension(simulateur, 2050)
            S = 0.0
            D = 0.14
            As = 63.0
            F = 0.5
            TauC = 7.0
            X = ot.Point([S, D, As, F, TauC])
            Y = modele(X)
        """
        super(FonctionPension, self).__init__(5, 1)
        # Attributs
        self.simulateur = simulateur
        self.annee = annee
        self.verbose = verbose
        # Configuration de la fonction
        self.setInputDescription(["S", "D", "As", "F", "TauC"])
        self.setOutputDescription(["P"])
        # Calcul des interpolateurs
        scenario_central = self.simulateur.scenario_central
        scenario_optimiste = self.simulateur.scenario_optimiste
        scenario_pessimiste = self.simulateur.scenario_pessimiste
        # Table des taux de chômages
        table_TauC = [self.simulateur.scenarios_chomage[scenario_optimiste], \
                      self.simulateur.scenarios_chomage[scenario_central], \
                      self.simulateur.scenarios_chomage[scenario_pessimiste]]
        # Table de NC
        table_NC = [self.simulateur.NC[scenario_optimiste][self.annee], \
                    self.simulateur.NC[scenario_central][self.annee], \
                    self.simulateur.NC[scenario_pessimiste][self.annee]]
        self.interpolateur_NC = sp.interpolate.interp1d(table_TauC, table_NC)
        # Table de dP
        table_dP = [self.simulateur.dP[scenario_optimiste][self.annee], \
                    self.simulateur.dP[scenario_central][self.annee], \
                    self.simulateur.dP[scenario_pessimiste][self.annee]]
        self.interpolateur_dP = sp.interpolate.interp1d(table_TauC, table_dP)
        # Table de B
        table_B = [self.simulateur.B[scenario_optimiste][self.annee], \
                   self.simulateur.B[scenario_central][self.annee], \
                   self.simulateur.B[scenario_pessimiste][self.annee]]
        self.interpolateur_B = sp.interpolate.interp1d(table_TauC, table_B)
        # Table de NR
        table_NR = [self.simulateur.NR[scenario_optimiste][self.annee], \
                    self.simulateur.NR[scenario_central][self.annee], \
                    self.simulateur.NR[scenario_pessimiste][self.annee]]
        self.interpolateur_NR = sp.interpolate.interp1d(table_TauC, table_NR)
        # Table de G
        table_G = [self.simulateur.G[scenario_optimiste][self.annee], \
                   self.simulateur.G[scenario_central][self.annee], \
                   self.simulateur.G[scenario_pessimiste][self.annee]]
        self.interpolateur_G = sp.interpolate.interp1d(table_TauC, table_G)
        # Table de A
        table_A = [self.simulateur.A[scenario_optimiste][self.annee], \
                   self.simulateur.A[scenario_central][self.annee], \
                   self.simulateur.A[scenario_pessimiste][self.annee]]
        self.interpolateur_A = sp.interpolate.interp1d(table_TauC, table_A)
        return

    def _exec(self, X):
        """
        Calcule la pension en fonction du solde S, 
        des dépenses D et de l'âge de départ en retraite As.
        
        Paramètres
        S : le solde financier
        D : le montant des dépenses de retraite en part de PIB
        As : l'âge de départ à la retraite de l'utilisateur
        F : facteur d'élasticité (par défaut, F = 0.5)
        TauC : taux de chômage (%)
        
        Description
        Retourne 
        P : niveau des pensions par rapport aux salaires
        
        Si l’utilisateur renseigne un âge effectif moyen de départ 
        à la retraite plus élevé que celui
        qui découle de l’évolution spontanée à législation inchangée 
        (c’est-à-dire si As > A), le nombre de
        retraités est donc diminué de G x (As – A) et le nombre 
        de cotisants augmenté de F x G x (As – A).
        
        Le calcul utilise la variable NC :
        NC : Nombre de personnes en emploi (ou nombre de cotisants)
    
        B : part des revenus d'activités bruts dans le PIB
        G : Effectif moyen d'une génération arrivant aux âges de la retraite
        A : âge moyen de départ à la retraite du COR
        NR : Nombre de retraités de droit direct (tous régimes confondus)
        dP : Autres dépenses de retraite rapportées au nombre de retraités 
             de droit direct en % du revenu d'activités brut moyen
        """
        S, D, As, F, TauC = X
        # Paramètres
        # Influence du taux de chômage
        G = self.interpolateur_G(TauC)
        A = self.interpolateur_A(TauC)
        NC = self.interpolateur_NC(TauC)
        dP = self.interpolateur_dP(TauC)
        B = self.interpolateur_B(TauC)
        NR = self.interpolateur_NR(TauC)
        # Coeur du modèle
        T = (S + D) / B
        g = G * (As - A)
        K = (NR - g) / (NC + F * g)
        P = (T - S / B) / K - dP
        # Affichage
        if self.verbose:
            print("G=", G)
            print("A=", A)
            print("NC =", NC)
            print("dP =", dP)
            print("B=", B)
            print("NR=", NR)
            print("T =", T)
            print("g =", g)
            print("K =", K)
            print("P =", P)
        # Sortie
        Y = [P]
        return Y
