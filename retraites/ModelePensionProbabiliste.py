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
            
            Les entrées du modèle sont "As", "F", "TauC" 
            et la sortie est "P". 
            
            Les paramètres S et D sont fixés par le constructeur 
            de la classe au moment de la création de l'objet. 
            
            * S : le solde financier du système de retraites (% PIB)
            * D : le montant des dépenses (% PIB)
            * As : l'âge moyen de départ à la retraite défini par l'utilisateur
            * F  : facteur d'élasticité de report de l'âge de départ 
                (par exemple F=0.5)
            * TauC : le taux de chômage (par exemple TauC = 4.5)

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
        # Crée le modèle de pension complet : entrées = (S, D, As, F, TauC)
        modelePension = ot.Function(FonctionPension(simulateur, annee))
        # Crée le modèle réduit à partir du modèle complet : entrées = (As, F, TauC)
        indices = ot.Indices([0, 1])
        referencePoint = ot.Point([S, D])
        self.fonction = ot.ParametricFunction(modelePension, indices, referencePoint)
        # Distribution
        As = ot.Uniform(62.0, 66.0)
        F = ot.Uniform(0.25, 0.75)
        TauC = ot.Uniform(4.5, 10.0)
        self.inputDistribution = ot.ComposedDistribution([As, F, TauC])
        self.inputDistribution.setDescription(["As", "F", "TauC"])
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
