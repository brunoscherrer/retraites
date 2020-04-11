#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import openturns as ot
from retraites.FonctionPension import FonctionPension


class ModelePensionProbabiliste:
    def InterpoleAge(
        annee, annee_courante, annee_horizon, age_courant, age_horizon
    ):
        """
        Interpole l'âge de départ à la retraite.

        Retourne l'âge pour l'année "annee" par interpolation linéaire
        entre l'âge courant et l'âge à l'horizon.

        Utilise une interpolation linéaire entre les deux points suivants :

        * (annee_courante, age_courant)
        * (annee_horizon, age_horizon)

        Parameters
        ----------
        annee : float
            L'année où calculer l'âge
        annee_courante : float
            L'année d'aujourd'hui
        annee_horizon : float
            L'année finale de la simulation dans le futur
        age_courant : float
            L'âge de départ en retraite aujourd'hui
        age_horizon : float
            L'âge de départ en retraite à la fin de la simulation
        """
        age = (
            (annee - annee_courante)
            / (annee_horizon - annee_courante)
            * age_horizon
            + (annee_horizon - annee)
            / (annee_horizon - annee_courante)
            * age_courant
        )
        return age

    def __init__(
        self,
        simulateur,
        annee,
        S,
        D,
        ageMin=62.0,
        ageMax=66.0,
        FMin=0.25,
        FMax=0.75,
        tauxChomageMin=4.5,
        tauxChomageMax=10.0,
        bornesAgeConstant=True,
    ):
        """
        Crée un modèle de pension probabiliste.

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

        Les marginales du vecteur aléatoire sont indépendantes.

        * F = ot.Uniform(FMin, FMax)
        * TauC = ot.Uniform(tauxChomageMin, tauxChomageMax)

        Si bornesAgeConstant est vrai, alors
        As = ot.Uniform(ageMin, ageMax)

        Sinon, alors l'âge suit une distribution qui dépend de l'année
        et dont les bornes sont entre l'âge du COR et l'âge de l'étude
        d'impact.

        * Avant 2020, la distribution de l'âge est un Dirac centré
        sur l'âge du COR.

        * De 2020 à 2038, l'âge du COR et l'âge de l'étude d'impact
        sont les mêmes.
        La distribution est un Dirac.

        * De 2038 à 2044, l'âge de l'étude d'impact est inférieur à
        celui du COR.
        L'étude d'impact prévoit une avance de l'âge de départ à la
        retraite sur cette période.
        La distribution est uniforme.
        De 2044 à 2070, l'âge de l'étude d'impact est supérieur à
        celui du COR.
        L'étude d'impact prévoit un recul de l'âge de départ à la
        retraite sur cette période.
        La distribution est uniforme.

        Parameters
        ----------
        simulateur : SimulateurRetraite
            Le simulateur.
        annee : float
            L'année de calcul de P
        S : float
            Le solde financier en part de PIB
        D : float
            Le montant des dépenses de retraites en part de PIB
        ageMin : float
            L'âge minimum
        ageMax : float
            L'âge maximum
        FMin : float
            Dans [0, 1], le facteur de report
            de l'âge de départ en retraite minimum
        FMax : float
            Dans [0, 1], le facteur de report
            de l'âge de départ en retraite maximum
        tauxChomageMin : float
            Positif. Le taux de chômage minimum
        tauxChomageMax : float
            Positif. Le taux de chômage maximum
        bornesAgeConstant : bool
            Si True, alors utilise les bornes ageMin et ageMax quelque soit
            l'année.
            Sinon, utilise un âge situé entre l'âge du COR et l'âge de
            l'étude d'impact.

        Attributes
        ----------
        fonction : ot.Function.
            Le modèle.
        inputDistribution : ot.Distribution.
            La distribution des variables d'entrée.
        ageMin : float
            La borne inférieure de la distribution de l'âge moyen
            effectif de départ en retraite pour l'année.
        ageMax : float
            La borne supérieure de la distribution de l'âge moyen
            effectif de départ en retraite pour l'année.

        Examples
        --------
        >>> S = 0.0
        >>> D = 0.14
        >>> annee = 2050
        >>> modele = ModelePensionProbabiliste(simulateur, annee, S, D)
        >>> fonction = modele.getFonction()
        >>> inputDistribution = modele.getInputDistribution()
        """
        # Crée le modèle de pension complet : entrées = (S, D, As, F, TauC)
        modelePension = ot.Function(FonctionPension(simulateur, annee))
        # Crée le modèle réduit à partir du modèle complet :
        # entrées = (As, F, TauC)
        indices = ot.Indices([0, 1])
        referencePoint = ot.Point([S, D])
        self.fonction = ot.ParametricFunction(
            modelePension, indices, referencePoint
        )
        # Distribution
        self._calculeAge(simulateur, annee, ageMin, ageMax, bornesAgeConstant)
        if self.ageMin == self.ageMax:
            As = ot.Dirac(self.ageMin)
        else:
            As = ot.Uniform(self.ageMin, self.ageMax)
        F = ot.Uniform(FMin, FMax)
        TauC = ot.Uniform(tauxChomageMin, tauxChomageMax)
        self.inputDistribution = ot.ComposedDistribution([As, F, TauC])
        self.inputDistribution.setDescription(["As", "F", "TauC"])
        return

    def getFonction(self):
        """
        Retourne la fonction du modèle physique.

        Returns
        -------
        fonction : ot.Function
            La fonction du modèle physique.
        """
        return self.fonction

    def getInputDistribution(self):
        """
        Retourne la distribution du modèle.

        Returns
        -------
        inputDistribution : ot.Distribution
            La distribution du vecteur aléatoire en entrée du modèle.
        """
        return self.inputDistribution

    def _calculeAge(
        self, simulateur, annee, ageMin, ageMax, bornesAgeConstant
    ):
        """
        Calcule les bornes de l'âge en fonction de l'option bornesAgeConstant.

        Le but de cette méthode est de calculer les attributs ageMin
        et ageMax de l'objet.

        Si bornesAgeConstant est True, alors utilise les arguments d'entrée
        de la fonction  ageMin et ageMax.

        Sinon,

        * si l'année est inférieure à l'année courante, utilise l'âge du COR,
        * sinon, réalise une interpolation linéaire entre les paramètres
          de l'étude d'impact (borne supérieure) et les paramètres du COR
          (borne inférieure).

        Parameters
        ----------
        simulateur : SimulateurRetraites
            Le simulateur.
        annee : int
            L'année du calcul.
        ageMin : float
            L'âge minimum.
        ageMax : float
            L'âge maximum.
        bornesAgeConstant : bool
            Si True, alors utilise les bornes minimum et maximum d'âge
            quelque soit la valeur du paramètre "annne".
            Sinon, utilise une interpolation linéaire.
        """
        if bornesAgeConstant:
            self.ageMin = ageMin
            self.ageMax = ageMax
        else:
            # Pour l'âge de départ en retraite
            analyse_COR = simulateur.pilotageCOR()
            if annee <= simulateur.annee_courante:
                ageCOR = analyse_COR.A[simulateur.scenario_central][annee]
                self.ageMin = ageCOR
                self.ageMax = ageCOR
            else:
                ageCOR_courant = analyse_COR.A[simulateur.scenario_central][
                    simulateur.annee_courante
                ]
                ageMin_horizon = ageMin
                ageMax_horizon = ageMax
                self.ageMin = ModelePensionProbabiliste.InterpoleAge(
                    annee,
                    simulateur.annee_courante,
                    simulateur.horizon,
                    ageCOR_courant,
                    ageMin_horizon,
                )
                self.ageMax = ModelePensionProbabiliste.InterpoleAge(
                    annee,
                    simulateur.annee_courante,
                    simulateur.horizon,
                    ageCOR_courant,
                    ageMax_horizon,
                )
        return
