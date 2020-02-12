#!/usr/bin/python
# coding:utf-8

from copy import deepcopy
import json
from retraites.SimulateurAnalyse import SimulateurAnalyse
import pylab as pl
import os

class SimulateurRetraites:
    def __init__(self, json_filename):
        """
        Crée un simulateur à partir d'un fichier d'hypothèses JSON.
        
        Paramètres
        json_filename : une chaîne de caractère, le nom du fichier JSON contenant les hypothèses
        pilotage : un entier, la stratégie de pilotage (par défaut, celle du COR)
        
        Description
        Plusieurs stratégies de pilotage peuvent être utilisées :
            pilotageParPensionAgeCotisations
            pilotageParSoldePensionAge
            pilotageParSoldePensionCotisations
            pilotageParSoldeAgeCotisations
            pilotageParSoldeAgeDepenses
            pilotageParSoldePensionDepenses
            pilotageParPensionCotisationsDepenses
            pilotageParAgeCotisationsDepenses
            pilotageParAgeEtNiveauDeVie (sous-entendu et par solde financier)
            pilotageParNiveauDeVieEtCotisations (sous-entendu et par solde financier)

        Exemple :
        simulateur = SimulateurRetraites('fileProjection.json')
        """
        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        # Lit les hypothèses de calcul dans le fichier JSON
        json_file = open(json_filename)
        self.data = json.load(json_file)
        json_file.close()
        
        # Paramètres constants
        self.horizon=2070
        self.annees=range(2005, self.horizon+1)           # annees sur lesquelles on fait les calculs
        self.annees_futures=range(2020, self.horizon+1)   # annees sur lesquelles on peut changer qqch
        self.annees_EV=range(1930,2011)              # annees sur lesquelles on a l'espérance de vie
        self.scenarios=range(1,7)                    # scenarios consideres

        # Extrait les variables depuis les données
        self.T = self.get('T')
        self.P = self.get('P')
        self.A = self.get('A')
        self.G = self.get('G')
        self.NR = self.get('NR')
        self.NC = self.get('NC')
        self.TCR = self.get('TCR') # Son nom est TPR dans le composant, TCR dans le fichier json
        self.TCS = self.get('TCS') # Son nom est TCS dans le composant, TCS dans le fichier json
        self.CNV = self.get('CNV')
        self.dP = self.get('dP')
        self.B = self.get('B')
        self.EV = self.get('EV')
        
        # Graphiques
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

        self.liste_variables = ["B","NR","NC","G","dP","TPR","TPS","CNV","EV"]
        self.liste_legendes=[u"B: Part des revenus d'activité bruts dans le PIB",
           u"NR: Nombre de retraités",
           u"NC: Nombre de cotisants",
           u"G: Effectif d'une generation arrivant à l'âge de la retraite",
           u"dP: Autres dépenses de retraites",
           u"TPR: Taux de prélèvement sur les retraites",
           u"TPS: Taux de prélèvement sur les salaires",
           u"CNV: (niveau de vie)/[(pension moy))/(salaire moy)]",
           u"EV: Espérance de vie à 60 ans"
        ]

        self.labels_is_long = True # True, si on utilise les labels longs
        
        # Configure les plages min et max pour l'axe des ordonnées 
        # des variables standard en sortie du simulateur
        self.yaxis_lim = dict()
        self.yaxis_lim["RNV"] = [60.0,120.0]
        self.yaxis_lim["REV"] = [20.0,40.0]

        self.ext_image=["png","pdf"]   # types de fichier à générer

        self.affiche_quand_ecrit = True # Affiche un message quand on écrit un fichier
        return None

    def pilotageCOR(self):
        """
        pilotage 0 : statu quo du COR
        Retourne un objet de type SimulateurAnalyse.
        """
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(self.T, self.P, self.A)
        resultat = SimulateurAnalyse(self.T, self.P, self.A, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParPensionAgeCotisations(self, Pcible=None, Acible=None, Tcible=None):
        """
        pilotage 1 : imposer 1) le niveau des pensions par rapport aux salaires
        2) l'âge de départ à la retraite
        3) le taux de cotisations
            
        Paramètres
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Acible : l'âge de départ à la retraite
        Tcible : le taux de cotisations

        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ps = self.genereTrajectoire("P", Pcible)
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)

        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParSoldePensionAge(self, Scible=None, Pcible=None, Acible=None):
        """
        pilotage 2 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) l'âge de départ à la retraite
            
        Paramètres
        Scible : la situation financière en % de PIB
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Acible : l'âge de départ à la retraite
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        As = self.genereTrajectoire("A", Acible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_As(Ss, Ps, As)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParSoldePensionCotisations(self, Scible=None, Pcible=None, Tcible=None):
        """
        pilotage 3 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) le taux de cotisations
            
        Paramètres
        Scible : la situation financière en % de PIB
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Tcible : le taux de cotisations
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        Ts = self.genereTrajectoire("T", Tcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_Ts(Ss, Ps, Ts)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 

    def pilotageParSoldeAgeCotisations(self, Scible=None, Acible=None, Tcible=None):
        """
        pilotage 4 : imposer 1) le bilan financer
        2) l'âge de départ à la retraite
        3) le taux de cotisations
            
        Paramètres
        Scible : la situation financière en % de PIB
        Acible : l'âge de départ à la retraite
        Tcible : le taux de cotisations
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_As_Ts(Ss, As, Ts)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 

    def pilotageParSoldeAgeDepenses(self, Scible=None, Acible=None, Dcible=None):
        """
        pilotage 5 : imposer 1) le bilan financer
        2) l'âge de départ à la retraite
        3) le niveau de dépenses
            
        Paramètres
        Scible : la situation financière en % de PIB
        Acible : l'âge de départ à la retraite
        Dcible : le niveau de dépenses
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        As = self.genereTrajectoire("A", Acible)
        Ds = self.genereTrajectoire("Depenses", Dcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_As_Ds(Ss, As, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 
    
    def pilotageParSoldePensionDepenses(self, Scible=None, Pcible=None, Dcible=None):
        """
        pilotage 6 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) le niveau de dépenses
            
        Paramètres
        Scible : la situation financière en % de PIB
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Dcible : le niveau de dépenses
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_Ds(Ss, Ps, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 

    def pilotageParPensionCotisationsDepenses(self, Pcible=None, Tcible=None, Dcible=None):
        """
        pilotage 7 : imposer 1) le niveau des pensions par rapport aux salaires
        2) le taux de cotisations
        3) le niveau de dépenses
            
        Paramètres
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Tcible : le taux de cotisations
        Dcible : le niveau de dépenses
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        Ps = self.genereTrajectoire("P", Pcible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ps_Ts_Ds(Ps, Ts, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 

    def pilotageParAgeCotisationsDepenses(self, Acible=None, Tcible=None, Dcible=None):
        """
        pilotage 8 : imposer 1) l'âge de départ à la retraite
        2) le taux de cotisations
        3) le niveau de dépenses
            
        Paramètres
        Acible : l'âge de départ à la retraite
        Tcible : le taux de cotisations
        Dcible : le niveau de dépenses
            
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)

        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_Ts_Ds(As, Ts, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat 
    
    def pilotageParAgeEtNiveauDeVie(self, Acible=None, RNVcible=None, Scible=None):
        """
        pilotage 1 : imposer 1) l'âge de départ à la retraite,  
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres
        Acible : un flottant, l'âge de départ imposé
        RNVcible : un flottant positif, le niveau de vie des retraités par 
        rapport à l’ensemble de la population
        Scible : la situation financière en % de PIB
        
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire. 
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        RNVs = self.genereTrajectoire("RNV", RNVcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_RNV_S(As, RNVs, Ss)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParCotisationsEtPensions(self, Pcible=None, Tcible=None, Scible=None):
        """
        pilotage 2 : imposer 1) le taux de cotisations,  
        2) le niveau de pensions par rapport aux salaires et 
        3) le bilan financier
        
        Paramètres
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Tcible : le taux de cotisations
        Scible : la situation financière en % de PIB
        
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire.         
        """
        # Génère les trajectoires en fonction des paramètres
        Ps = self.genereTrajectoire("P", Pcible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ps_Ts_S(Ps, Ts, Ss)
        # Simule
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParNiveauDeVieEtCotisations(self, Tcible=None, RNVcible=None, Scible=None):
        """
        pilotage 3 : imposer 1) le taux de cotisations, 
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres
        Tcible : le taux de cotisations
        RNVcible : le niveau de vie des retraités par rapport à 
        l’ensemble de la population
        Scible : la situation financière en % de PIB
        
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire.         
        """
        # Génère les trajectoires en fonction des paramètres
        Ts = self.genereTrajectoire("T", Tcible)
        RNVs = self.genereTrajectoire("RNV", RNVcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ts_RNV_S(Ts, RNVs, Ss)
        # Simule
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParCotisationsEtAge(self, Acible=None, Tcible=None, Scible=None):
        """
        pilotage 4 : imposer 1) le taux de cotisations, 
        2) l'âge de départ à la retraite et 
        3) le bilan financier. 
        
        Paramètres
        Acible : l'âge de départ à la retraite
        Tcible : le taux de cotisations
        Scible : la situation financière en % de PIB
        
        Description
        Retourne un objet de type SimulateurAnalyse.
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire.         
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_Ts_S(As, Ts, Ss) 
        # Simule
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParAgeEtDepenses(self, Acible=None, Dcible=None, Scible=None):
        """
        pilotage 5 : imposer 1) l'âge de départ à la retraite, 
        2) le niveau de dépenses Ds et 
        3) le bilan financier. 
        
        Paramètres
        Acible : l'âge de départ à la retraite
        Dcible : le niveau de dépenses
        Scible : la situation financière en % de PIB
        
        Description
        Retourne un objet de type SimulateurAnalyse.
        Si la valeur n'est pas donnée, conserve la valeur du COR.
        Si une valeur est donnée, utilise cette valeur pour les années 
        futures. 
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        Ds = self.genereTrajectoire("Depenses", Dcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_Ds_S(As, Ds, Ss)
        # Simule
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def get(self, var):
        """
        Retourne une donnée du COR correspondant à un nom donné.
        
        var : une chaîne de caractère, la variable à extraire
        v : un dictionnaire, v[s][a] est la valeur de la variable 
        pour le scénario s à l'année a
        
        Exemple :
        T = simulateur.get("T")
        """
        if var=='EV':
            an=self.annees_EV
        else:
            an=self.annees

        v=dict()
        
        for s in self.scenarios:
            v[s]=dict()
            for a in an:
                v[s][a]=self.data[var][str(s)][str(a)]
                
        return v

    def _calcule_fixant_Ss_Ps_As(self, Ss, Ps, As):
        """
        Calcul à solde, pension et âge définis
        
        Paramètres
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        Ps : un dictionnaire, Ps[s][a] est le montant de la pension 
        par rapport aux salaires du scénario s à l'année a
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        """
    
        # Calcule Ts
        Ts = deepcopy(self.T)    
        for s in self.scenarios:    
            for a in self.annees_futures:
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = (self.NR[s][a] - GdA) / (self.NC[s][a] + 0.5*GdA)
                Ts[s][a] = Ss[s][a] / self.B[s][a] + K * (Ps[s][a] + self.dP[s][a])
                
        return Ts, Ps, As

    def _calcule_fixant_Ss_Ps_Ts(self, Ss, Ps, Ts):
        """
        Calcul à solde, pension et cotisations définis
        
        Paramètres
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        Ps : un dictionnaire, Ps[s][a] est le montant de la pension 
        par rapport aux salaires du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations 
        du scénario s à l'année a
        """
    
        # Calcule As
        As = deepcopy(self.A)    
        for s in self.scenarios:    
            for a in self.annees_futures:
                K = (Ts[s][a] - Ss[s][a] / self.B[s][a]) / (Ps[s][a] + self.dP[s][a])
                As[s][a] = self.A[s][a] + (self.NR[s][a] - K * self.NC[s][a]) / (0.5*K + 1) / self.G[s][a]
                
        return Ts, Ps, As

    def _calcule_fixant_Ss_As_Ts(self, Ss, As, Ts):
        """
        Calcul à solde, âge et cotisations définis
        
        Paramètres
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations 
        du scénario s à l'année a
        """
    
        # Calcule Ps
        Ps = deepcopy(self.P)
        for s in self.scenarios:    
            for a in self.annees_futures:
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = (self.NR[s][a] - GdA) / (self.NC[s][a] + 0.5*GdA)
                Ps[s][a] = (Ts[s][a] - Ss[s][a] / self.B[s][a]) / K - self.dP[s][a]
                
        return Ts, Ps, As

    def _calcule_fixant_Ss_As_Ds(self, Ss, As, Ds):
        """
        Calcul à solde, âge et dépenses définis
        
        Paramètres
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        Ds : un dictionnaire, Ds[s][a] est le niveau de dépenses 
        du scénario s à l'année a
        """
    
        # Calcule Ps et Ts
        Ps, Ts = deepcopy(self.P), deepcopy(self.T)
        for s in self.scenarios:    
            for a in self.annees_futures:
                Ts[s][a] = (Ss[s][a] + Ds[s][a]) / self.B[s][a]
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = (self.NR[s][a] - GdA) / (self.NC[s][a] + 0.5*GdA)
                Ps[s][a] = (Ts[s][a] - Ss[s][a] / self.B[s][a]) / K - self.dP[s][a]
                
        return Ts, Ps, As

    def _calcule_fixant_Ss_Ps_Ds(self, Ss, Ps, Ds):
        """
        Calcul à solde, pension et dépenses définis
        
        Paramètres
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        Ps : un dictionnaire, Ps[s][a] est le montant de la pension 
        par rapport aux salaires du scénario s à l'année a
        Ds : un dictionnaire, Ds[s][a] est le niveau de dépenses 
        du scénario s à l'année a
        """
    
        # Calcule As et Ts
        As, Ts = deepcopy(self.A), deepcopy(self.T)
        for s in self.scenarios:    
            for a in self.annees_futures:
                K = Ds[s][a] / self.B[s][a] / (Ps[s][a] + self.dP[s][a])
                As[s][a] = self.A[s][a] + (self.NR[s][a] - K * self.NC[s][a]) / (0.5*K + 1) / self.G[s][a]
                Ts[s][a] = (Ss[s][a] + Ds[s][a]) / self.B[s][a]
                
        return Ts, Ps, As
    
    def _calcule_fixant_Ps_Ts_Ds(self, Ps, Ts, Ds):
        """
        Calcul à pension, cotisations et dépenses définis
        
        Paramètres
        Ps : un dictionnaire, Ps[s][a] est le montant de la pension 
        par rapport aux salaires du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations 
        du scénario s à l'année a
        Ds : un dictionnaire, Ds[s][a] est le niveau de dépenses 
        du scénario s à l'année a
        """
    
        # Calcule As
        As = deepcopy(self.A)
        for s in self.scenarios:    
            for a in self.annees_futures:
                K = Ds[s][a] / self.B[s][a] / (Ps[s][a] + self.dP[s][a])
                As[s][a] = self.A[s][a] + (self.NR[s][a] - K * self.NC[s][a]) / (0.5*K + 1) / self.G[s][a]
                
        return Ts, Ps, As

    def _calcule_fixant_As_Ts_Ds(self, As, Ts, Ds):
        """
        Calcul à âge, cotisations et dépenses définis
        
        Paramètres
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations 
        du scénario s à l'année a
        Ds : un dictionnaire, Ds[s][a] est le niveau de dépenses 
        du scénario s à l'année a
        """
    
        # Calcule Ps
        Ps = deepcopy(self.P)
        for s in self.scenarios:    
            for a in self.annees_futures:
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = (self.NR[s][a] - GdA) / (self.NC[s][a] + 0.5*GdA)
                Ps[s][a] = Ds[s][a] / self.B[s][a] / K - self.dP[s][a]
                
        return Ts, Ps, As
    
    def _calcule_fixant_As_RNV_S(self, As, RNVs, Ss):
        """
        Pilotage 1 : calcul à âge et niveau de vie défini
        
        Paramètres
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        RNVs : un dictionnaire, RNVs[s][a] est le niveau de vie 
        par rapport à l'ensemble de la population 
        du scénario s à l'année a
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        """
        
        # Calcule Ps et Ts
        Ts, Ps = deepcopy(self.T), deepcopy(self.P)
        for s in self.scenarios:    
            for a in self.annees_futures:                 
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5*GdA )
                Z = ( 1.0 - self.TCR[s][a] ) * self.CNV[s][a] / RNVs[s][a]
                U = 1.0 - ( self.TCS[s][a] - self.T[s][a] )
                L = Ss[s][a] / self.B[s][a]    
                Ps[s][a] = ( U - L - K*self.dP[s][a] ) / ( Z + K )
                Ts[s][a] = U - Ps[s][a] * Z 
                
        return Ts, Ps, As
    
    def _calcule_fixant_Ps_Ts_S(self, Ps, Ts, Ss):
        """
        Pilotage 2 : calcul à cotisations et pensions définies
        
        Paramètres
        Ps : un dictionnaire, Ps[s][a] est le montant de la pension 
        par rapport aux salaires du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations
        du scénario s à l'année a
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        """
    
        # Calcule l'âge 
        As = deepcopy(self.A)    
        for s in self.scenarios:    
            for a in self.annees_futures:    
                K = (Ts[s][a] - Ss[s][a] / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts, Ps, As
        
    def _calcule_fixant_Ts_RNV_S(self, Ts, RNVs, Ss):
        """
        Pilotage 3 : calcul à cotisations et niveau de vie défini
        
        Paramètres
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations
        du scénario s à l'année a
        RNVs : un dictionnaire, RNVs[s][a] est le niveau de vie 
        par rapport à l'ensemble de la population 
        du scénario s à l'année a
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        """
        
        # Calcule Ps et As
        Ps, As = deepcopy(self.P), deepcopy(self.A)    
        for s in self.scenarios:    
            for a in self.annees_futures:
                Ps[s][a] = RNVs[s][a] * (1-(self.TCS[s][a] + Ts[s][a]-self.T[s][a])) / self.CNV[s][a] / (1-self.TCR[s][a])
                K = (Ts[s][a] - Ss[s][a] / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts, Ps, As
    
    
    def _calcule_fixant_As_Ts_S(self, As, Ts, Ss):
        """
        Pilotage 4 : calcul à cotisations et âge définis
        
        Paramètres
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        Ts : un dictionnaire, Ts[s][a] est le taux de cotisations
        du scénario s à l'année a
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        """

        # Calcule Ps
        Ps = deepcopy(self.P)        
        for s in self.scenarios:    
            for a in self.annees_futures:
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5 * GdA )
                Ps[s][a] = (Ts[s][a]-Ss[s][a]/self.B[s][a])/K - self.dP[s][a]
                
        return Ts, Ps, As
        
    def _calcule_fixant_As_Ds_S(self, As, Ds, Ss):
        """
        Pilotage 5 : calcul à âge et dépenses définis
        
        Paramètres
        As : un dictionnaire, As[s][a] est l'âge de départ à la retraite 
        du scénario s à l'année a
        Ds : un dictionnaire, Ds[s][a] est le niveau de dépenses 
        du scénario s à l'année a
        Ss : un dictionnaire, Ss[s][a] est le solde financier 
        du scénario s à l'année a
        """
        
        # Calcule Ps et Ts
        Ps = deepcopy(self.P)
        Ts = deepcopy(self.T)
        for s in self.scenarios:
            for a in self.annees_futures:
                Ts[s][a] = (Ss[s][a] + Ds[s][a])/self.B[s][a]
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5 * GdA )
                Ps[s][a] = (Ts[s][a]-Ss[s][a]/self.B[s][a])/K - self.dP[s][a]
                
        return Ts, Ps, As

    def _calcule_S_RNV_REV(self, Ts, Ps, As):
        """
        pilotage 0 : statu quo du COR
        Calcule les sorties du modèle de retraite en fonction des leviers.
        
        Ts : le taux de cotisations
        P : le niveau des pensions par rapport aux salaires
        A : âge moyen de départ à la retraite
        """
    
        S,RNV,REV, Depenses = dict(), dict(), dict(), dict()
    
        for s in self.scenarios:
    
            S[s], RNV[s], REV[s], Depenses[s] = dict(), dict(), dict(), dict()
    
            for a in self.annees:
    
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5*GdA )
                U = 1.0 - ( self.TCS[s][a] - self.T[s][a] )
                Depenses[s][a] = self.B[s][a] * K * ( Ps[s][a] + self.dP[s][a] )
                S[s][a] = self.B[s][a] * ( Ts[s][a] -  K * ( Ps[s][a] + self.dP[s][a] ) ) 
                RNV[s][a] =  Ps[s][a] * ( 1.0 - self.TCR[s][a] ) / (U - Ts[s][a]) * self.CNV[s][a]
    
                tmp = 60.0 + self.EV[s][ int(a+.5-As[s][a]) ]
                REV[s][a] = ( tmp - As[s][a] ) / tmp
    
        return S, RNV, REV, Depenses

    def genereTrajectoire(self, nom, valeur=None):
        """
        Crée une nouvelle trajectoire à partir de la valeur constante. 
        
        Paramètres
        nom : une chaîne de caratères, le nom de la variable
        valeur : un flottant, la valeur numérique constante
        
        Description        
        Retourne un dictionnaire contenant une trajectoire 
        dans tous les scénarios et pour toutes les années : 
        trajectoire[s][a] est la valeur numérique du scénario s à l'année a
        
        * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
        * Si la valeur donnée est un flottant, utilise la trajectoire du 
        COR pour les années passées et cette valeur pour les années futures. 
        * Si la valeur donnée est un dictionnaire, considère que c'est 
        une trajectoire et utilise cette trajectoire.         
        
        Exemples        
        simulateur.genereTrajectoire(simulateur, "A") # Départ à l'âge du COR
        simulateur.genereTrajectoire(simulateur, "A", 62.0) # Départ à 62.0 ans
        simulateur.genereTrajectoire(simulateur, "A", simulateur.A[1][2020]) # Départ à l'âge du COR en 2020
        """

        if type(valeur) is dict:
            trajectoire = deepcopy(valeur)
        else:
            if (nom=="A"):
                trajectoire = deepcopy(self.A)
            elif (nom=="S"):
                S_COR, RNV_COR, REV_COR, Depenses_COR = self._calcule_S_RNV_REV(self.T, self.P, self.A)
                trajectoire = S_COR
            elif (nom=="P"):
                trajectoire = deepcopy(self.P)
            elif (nom=="T"):
                trajectoire = deepcopy(self.T)
            elif (nom=="RNV"):
                S_COR, RNV_COR, REV_COR, Depenses_COR = self._calcule_S_RNV_REV(self.T, self.P, self.A)
                trajectoire = RNV_COR
            elif (nom=="Depenses"):
                S_COR, RNV_COR, REV_COR, Depenses_COR = self._calcule_S_RNV_REV(self.T, self.P, self.A)
                trajectoire = Depenses_COR
            else:
                raise TypeError('Mauvaise valeur pour le nom : %s' % (nom))
            
            if valeur is not None:
                # Propage la valeur constante dans la trajectoire
                # pour les années futures
                for s in self.scenarios:
                    for a in self.annees_futures:
                        trajectoire[s][a] = valeur

        return trajectoire

    def dessineConjoncture(self, taille_fonte_titre = 8, \
                  dessine_legende = False, scenarios_indices = None, 
                  dessine_annees = None):
        """
        Dessine les hypothèses de conjoncture.
        
        Paramètres:
        taille_fonte_titre : taille de la fonte du titre (par défaut, fs=8)
        dessine_legende : booleen, True si la légende doit être dessinée
        scenarios_indices : une liste d'entiers, la liste des indices des scénarios
        (par défaut, sc = range(1,7))
        dessine_annees : la liste des années à dessiner
        
        Exemple:
        simulateur.dessine_conjoncture()
        """
        pl.figure(figsize=(10,8))
        pl.suptitle(u"Projections du COR (hypothèses)",fontsize=16)
        for c in range(9):
            pl.subplot(3,3,c+1)
            nom = self.liste_variables[c]
            self.graphique(nom, taille_fonte_titre = taille_fonte_titre, \
                            dessine_legende = dessine_legende, \
                            scenarios_indices = scenarios_indices, \
                            dessine_annees = dessine_annees)
        pl.tight_layout(rect=[0, 0.03, 1, 0.95])
        return None
    
    def graphique(self, nom, v = None, taille_fonte_titre = 8, yaxis_lim = [], \
                  dessine_legende = False, scenarios_indices = None, 
                  dessine_annees = None):
        """
        Dessine un graphique associé à une variable donnée 
        pour tous les scénarios.
        
        Paramètres:
        nom : chaîne de caractère, nom de la variable
        v : variable à dessiner (par défaut, en fonction du nom)
        taille_fonte_titre : taille de la fonte du titre (par défaut, fs=8)
        yaxis_lim : une liste de taille 2, les bornes inférieures et supérieures 
        de l'axe des ordonnées
        dessine_legende : booleen, True si la légende doit être dessinée
        scenarios_indices : une liste d'entiers, la liste des indices des scénarios
        (par défaut, sc = range(1,7))
        dessine_annees : la liste des années à dessiner
        
        """
        if v is None:
            if nom=="B":
                v = self.B
            elif nom=="NR":
                v = self.NR
            elif nom=="NC":
                v = self.NC
            elif nom=="G":
                v = self.G
            elif nom=="dP":
                v = self.dP
            elif nom=="TPR":
                v = self.TCR
            elif nom=="TPS":
                v = self.TCS
            elif nom=="CNV":
                v = self.CNV
            elif nom=="EV":
                v = self.EV
            else:
                raise TypeError('Mauvaise valeur pour le nom : %s' % (nom))

        if scenarios_indices==None:
            scenarios_indices = self.scenarios
        
        if dessine_annees is not None:
            list_annees_dessin = dessine_annees
        else:
            if nom=="EV":
                list_annees_dessin=self.annees_EV
            else:
                list_annees_dessin=self.annees
    
        for s in scenarios_indices:
            if (nom=="RNV"):
                # Ce sont des % : multiplie par 100.0
                y = [ 100.0 * v[s][a] for a in list_annees_dessin ]
            else:
                y = [ v[s][a] for a in list_annees_dessin ]

            if (self.labels_is_long):
                label_variable = self.scenarios_labels[s-1]
            else:
                label_variable = self.scenarios_labels_courts[s-1]
            pl.plot(list_annees_dessin, y, label=label_variable )
    
        # titres des figures
        indice_variable = self.liste_variables.index(nom)
        titre_figure=self.liste_legendes[ indice_variable ]
           
        pl.title(titre_figure,fontsize=taille_fonte_titre)
        
        # Ajuste les limites de l'axe des ordonnées
        if yaxis_lim==[]:
            # If the use did not set the yaxis_lim
            if nom in self.yaxis_lim.keys():
                # If the variable name was found in the dictionnary
                yaxis_lim = self.yaxis_lim[nom]

        if yaxis_lim!=[]:
            pl.ylim(bottom=yaxis_lim[0],top=yaxis_lim[1])

        if dessine_legende:
            pl.legend(loc="best")
        return None
    
    def setAfficheMessageEcriture(self, affiche_quand_ecrit):
        """
        Configure l'affichage d'un message quand on écrit un fichier
        
        Paramètres
        affiche_quand_ecrit : un booléen (par défaut = True)
        
        Exemple
        analyse.setAfficheMessageEcriture(False)
        """
        self.affiche_quand_ecrit = affiche_quand_ecrit
        return None
    
    def setImageFormats(self, ext_image):
        """
        Configure le format de sauvegarde des images
        
        Paramètres
        ext_image : une liste de chaînes de caractères (par defaut, ext_image=["png","pdf"])
        
        Exemple
        analyse.setImageFormats(["jpg"])
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
        
        Paramètres
        labels_is_long : un booléen, True si les labels longs sont utilisés (par défaut = True)
        
        Exemple
        analyse.setLabelLongs(False)
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
        exportées par sauveFigure.
        """
        self.dir_image = dir_image
        return None

    def getDirectoryImage(self):
        """
        Retourne le répertoire contenant les images
        """
        return self.dir_image

    def sauveFigure(self, f):
        """
        Sauvegarde l'image dans le répertoire
        
        Paramètres:
        f : une chaîne de caractères, le nom des fichiers à sauver
        
        Description
        Sauvegarde l'image dans les formats définis. 
        
        Exemple:
        analyse.sauveFigure("conjoncture")
        """
    
        for ext in self.ext_image:
            basefilename = f + "." + ext
            filename = os.path.join(self.dir_image,basefilename)
            if self.affiche_quand_ecrit:
                print("Ecriture du fichier %s" % (filename))
            pl.savefig(filename)
        return None
    
