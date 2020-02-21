#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openturns as ot
from retraites.FonctionPension import FonctionPension

class ModelePensionProbabiliste():
    def __init__(self, simulateur, annee, S, D):
        """
        Crée un modèle de pension probabiliste.
        
        Paramètres :
            simulateur : un SimulateurRetraite
            annee : un flottant, l'année de calcul de P
            S : un flottant, le solde financier en part de PIB
            D : un flottant positif, le montant des dépenses de retraites 
            en part de PIB
        
        Description :
            Crée un modèle de pension probabiliste pour le 
            ratio (pension moyenne) / (salaire moyen).
            
            Les entrées du modèle sont "As", "E", "TauC" 
            et la sortie est "P". 
            
            Les paramètres S et D sont fixés par le constructeur 
            de la classe. 
            
            Les distributions des variables sont ot.Uniform 
            et indépendantes.

        Exemple :
            S = 0.0
            D = 0.14
            annee = 2050
            modele = ModelePensionProbabiliste(simulateur, annee, S, D)
            fonction = modele.getFonction()
            inputDistribution = modele.getInputDistribution()
        """
        # Crée le modèle de pension complet : entrées = (S, D, As, E, TauC)
        modelePension = ot.Function(FonctionPension(simulateur, annee))
        # Crée le modèle réduit à partir du modèle complet : entrées = (As, E, TauC)
        indices = ot.Indices([0, 1])
        referencePoint = ot.Point([S, D])
        self.fonction = ot.ParametricFunction(modelePension, indices, referencePoint)
        # Distribution
        As = ot.Uniform(62.0, 66.0)
        E = ot.Uniform(0.25, 0.75)
        TauC = ot.Uniform(4.5, 10.0)
        self.inputDistribution = ot.ComposedDistribution([As, E, TauC])
        self.inputDistribution.setDescription(["As", "E", "TauC"])
        return

    def getFonction(self):
        """
        Retourne la fonction du modèle physique.
        """
        return self.fonction
    
    def getInputDistribution(self):
        """
        Retourne la distribution du modèle.
        """
        return self.inputDistribution
