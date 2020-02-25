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
        
            Les autres paramètres B, G, A, NR sont ceux du simulateur, 
            dans le scénario central (i.e. s = 1) à l'année considérée. 
        
            Le modèle calcule le nombre de cotisants NC et les autres dépenses 
            de retraites dP en fonction du taux de chômage TauC par 
            évalution de la méthode calculeNCetDP. 

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
        scenario_central = 1
        B = self.simulateur.B[scenario_central][self.annee]
        G = self.simulateur.G[scenario_central][self.annee]
        A = self.simulateur.A[scenario_central][self.annee]
        NR = self.simulateur.NR[scenario_central][self.annee]
        # Influence du taux de chômage
        NC, dP = self.calculeNCetDP(TauC)
        # Coeur du modèle
        T = (S + D) / B
        g = G * (As - A)
        K = (NR - g) / (NC + F * g)
        P = (T - S / B) / K - dP
        # Affichage
        if self.verbose:
            print("NC =", NC)
            print("T =", T)
            print("g =", g)
            print("K =", K)
            print("P =", P)
        # Sortie
        Y = [P]
        return Y

    def calculeNCetDP(self, TauC):
        """
        Calcule le nombre de cotisants et 
        des autres dépenses de retraites en fonction du taux 
        de chômage et de l'année. 
        
        Paramètres:
            TauC : taux de chômage
        
        Description:
            Le calcul repose sur une interpolation linéaire par morceaux 
            entre les scénarios optimiste (TauC = 4.5), 
            central (TauC = 7.0) et pessimiste (TauC = 10.0). 
            Les valeurs numériques du simulateur correspondant à 
            ces taux de chômage sont utilisées. 
        """
        scenario_central = 1
        scenario_optimiste = 5
        scenario_pessimiste = 6
        # Table des taux de chômages
        table_TauC = [self.simulateur.scenarios_chomage[scenario_optimiste], \
                      self.simulateur.scenarios_chomage[scenario_central], \
                      self.simulateur.scenarios_chomage[scenario_pessimiste]]
        #
        premiereAnneeFuture = self.simulateur.annees_futures[0]
        if (self.annee <= premiereAnneeFuture):
            NC = self.simulateur.NC[scenario_central][self.annee]
            dP = self.simulateur.dP[scenario_central][self.annee]
        else:
            # Table des taux de nombres de cotisants
            table_NC = [self.simulateur.NC[scenario_optimiste][self.annee], \
                        self.simulateur.NC[scenario_central][self.annee], \
                        self.simulateur.NC[scenario_pessimiste][self.annee]]
            interpolateur = sp.interpolate.interp1d(table_TauC, table_NC)
            NC = interpolateur(TauC)
            # Table des autres dépenses
            table_dP = [self.simulateur.dP[scenario_optimiste][self.annee], \
                        self.simulateur.dP[scenario_central][self.annee], \
                        self.simulateur.dP[scenario_pessimiste][self.annee]]
            interpolateur = sp.interpolate.interp1d(table_TauC, table_dP)
            dP = interpolateur(TauC)
        return [NC, dP]

