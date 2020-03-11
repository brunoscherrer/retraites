#!/usr/bin/python
# coding:utf-8
"""
Classe de gestion d'un simulateur de retraites.
"""

from copy import deepcopy
import json
from retraites.SimulateurAnalyse import SimulateurAnalyse
import pylab as pl
import os
import retraites
import scipy.optimize as spo

class SimulateurRetraites:

    def __init__(self, json_filename = None):
        """
        Crée un simulateur à partir d'un fichier d'hypothèses JSON.
        
        Paramètres :
            json_filename : une chaîne de caractère, le nom du fichier JSON 
            contenant les hypothèses
            (par défaut, charge le fichier "fileProjection.json" fournit par le 
            module)
            pilotage : un entier, la stratégie de pilotage (par défaut, celle du COR)
            
        Attributs :
            annee_courante : 
                Un entier. 
                L'année correspondant à la date d'aujourd'hui.

            horizon : 
                Un entier. 
                La dernière année du calcul. 
    
            annees : 
                Une liste d'entiers.
                La liste des années sur lesquelles on fait les calculs. 
                Chaque année de cette liste est inférieure à l'année de l'horizon.
    
            annees_futures :
                Une liste d'entiers.
                La liste des années sur lesquelles on peut changer 
                quelque chose.
    
            annees_standard :
                Une liste d'entiers.
                La liste d'une sélection des années futures standard dans les calculs simplifiés. 
    
            annees_EV :
                Une liste d'entiers.
                La liste des années de naissance pour lesquelles on a l'espérance de vie. 
    
            scenarios :
                Une liste d'entiers.
                la liste des scénarios considérés. 
                Ces scénarios sont des indices dans les tables de scénarios de 
                chomage, de croissance ainsi que les labels. 
    
            scenario_central :
                Un entier. 
                L'indice du scénario central, 
                +1,3%/an, Chômage: 7%. 
    
            scenario_pessimiste :
                L'indice du scénario pessimiste +1%/an, Chômage: 10%. 
        
            scenario_optimiste :
                L'indice du scénario optimiste : +1,8%/an, Chômage: 4.5%.
    
            scenarios_croissance :
                Une liste de flottants. 
                La liste des taux de croissance pour chaque scénario 
                de la liste retournée par getScenarios().
    
            scenarios_chomage :
                Une liste de flottants. 
                La liste des taux de chomage pour chaque scénario 
                de la liste retournée par getScenarios().
    
            scenarios_labels :
                La liste de chaîne de caractère décrivant les 
                scénarios pour chaque scénario 
                de la liste retournée par getScenarios().
    
            scenarios_labels_courts :
                La liste de chaîne de caractère courtes décrivant les 
                scénarios pour chaque scénario 
                de la liste retournée par getScenarios().
                
            T : 
                Un dictionnaire représentant une trajectoire. 
                Le taux de cotisations retraites
            
            P : 
                Un dictionnaire représentant une trajectoire. 
                Le niveau moyen brut des pensions par rapport au 
                niveau moyen brut des salaires
            
            A : 
                Un dictionnaire représentant une trajectoire. 
                l'âge effectif moyen de départ en retraite
                
            G : 
                Un dictionnaire représentant une trajectoire. 
                Effectif moyen d'une génération arrivant aux âges 
                de la retraite
                
            NR  : 
                Un dictionnaire représentant une trajectoire. 
                Nombre de retraités de droit direct (tous régimes confondus)
                
            NC :
                Un dictionnaire représentant une trajectoire. 
                Nombre de personnes en emploi (ou nombre de cotisants) 
        
            TCR :
                Un dictionnaire représentant une trajectoire. 
                Taux des prélèvements sociaux sur les pensions de retraite
                Son nom est TPR dans le composant, TCR dans le fichier json
        
            TCS :
                Un dictionnaire représentant une trajectoire. 
                Taux des prélèvements sociaux sur les salaires et 
                revenus d'activité ;
                Son nom est TPR dans le composant, TCR dans le fichier json
        
            CNV :
                Un dictionnaire représentant une trajectoire. 
                Coefficient pour passer du ratio "pensions/salaire moyen" 
                au ratio "niveau de vie/salaire moyen"
        
            dP :
                Un dictionnaire représentant une trajectoire. 
                Autres dépenses de retraite rapportées au nombre de 
                retraités de droit direct en % du revenu d'activités brut moyen
        
            B :
                Un dictionnaire représentant une trajectoire. 
                part des revenus d'activités bruts dans le PIB 
        
            EV :
                Un dictionnaire représentant une trajectoire. 
                Espérance de vie à 60 ans par génération

            liste_variables :
                Une liste de chaînes de caractères. 
                La liste des variables du modèle : B, NR, etc...
                
            liste_legendes
                Une liste de chaînes de caractères. 
                La liste des légendes pour chaque variable dans liste_variables

            labels_is_long :
                Un booléen. 
                True, si on utilise les labels longs dans les graphiques
        
            yaxis_lim :
                Un dictionnaire. 
                Les plages min et max pour l'axe des ordonnées 
                des variables en sortie du simulateur. 

            dir_image :
                Une chaîne de caractère. 
                Le répertoire de sauvegarde des images. 
                Par défaut, le répertoire courant. 

            ext_image :
                Une liste de chaînes de caractères. 
                Les types de fichier à générer par la méthode sauveFigure. 
                
            affiche_quand_ecrit :
                Un booléen.
                Si True, alors affiche un message quand la méthode sauveFigure 
                écrit un fichier.

            rechercheAgeBornes :
                Une liste de flottants.
                Les bornes de recherches pour l'inversion de l'âge 
                en fonction du ratio de durée de vie en retraite. 

            rechercheAgeRTol :
                Un flottant.
                La tolérance relative sur l'âge pour l'inversion de l'âge 
                en fonction du ratio de durée de vie en retraite. 
        
        Description :
            Plusieurs stratégies de pilotage peuvent être utilisées :
            1 pilotageCOR, avec les paramètres du COR
            1 pilotageParPensionAgeCotisations
            2 pilotageParSoldePensionAge
            3 pilotageParSoldePensionCotisations
            4 pilotageParSoldeAgeCotisations
            5 pilotageParSoldeAgeDepenses
            6 pilotageParSoldePensionDepenses
            7 pilotageParPensionCotisationsDepenses
            8 pilotageParAgeCotisationsDepenses
            9 pilotageParAgeEtNiveauDeVie (sous-entendu et par solde financier)
            10 pilotageParNiveauDeVieEtCotisations (sous-entendu et par solde financier)
            
            Les scénarios sont numérotés de 1 à 6 dans l'attribut "scenarios"
            (contrairement à l'usage Python ordinaire qui voudrait plutôt que 
            l'indice aille de 0 à 5). 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.dessineConjoncture()
            simulateur.dessineLegende()
            
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.dessineSimulation()
            analyse.dessineLegende()
        """
        
        if (json_filename is None):
            # Loading default JSON data
            json_filename = os.path.join(retraites.__path__[0], "fileProjection.json")
            
        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        # Lit les hypothèses de calcul dans le fichier JSON
        json_file = open(json_filename)
        self.data = json.load(json_file)
        json_file.close()
        
        # Paramètres constants
        self.annee_courante = 2020  # Annee correspondant à la date d'aujourd'hui
        self.horizon = 2070         # Dernière année du calcul
        self.annees_futures=range(self.annee_courante, self.horizon+1) # annees sur lesquelles on peut changer qqch
        self.annees=range(2005, self.horizon+1)         # annees sur lesquelles on fait les calculs
        self.annees_standard=[2020, 2025, 2030, 2040, 2050, 2060, 2070] # Années standard dans les calculs simplifiés
        self.annees_EV=range(1930,2011)                 # annees sur lesquelles on a l'espérance de vie

        # Scénarios
        self.scenarios = range(1,7)  # Scenarios considérés
        self.scenario_central = 3    # central    : +1,3%/an, Chômage: 7%
        self.scenario_pessimiste = 6 # pessimiste :   +1%/an, Chômage: 10%
        self.scenario_optimiste = 5  # optimiste  : +1,8%/an, Chômage: 4.5%
        # Taux de croissance pour chaque scénario
        self.scenarios_croissance = [0.0, 1.8, 1.5, 1.3, 1.0, 1.8, 1.0]
        # Taux de chomage pour chaque scénario
        self.scenarios_chomage = [0.0, 7.0, 7.0, 7.0, 7.0, 4.5, 10.0]
        # Graphiques
        self.scenarios_labels=["Scénario inexistant", 
                               "Hausse des salaires: +1,8%/an, Taux de chômage: 7%",
                               "Hausse des salaires: +1,5%/an, Taux de chômage: 7%",
                               "Hausse des salaires: +1,3%/an, Taux de chômage: 7%",
                               "Hausse des salaires: +1%/an, Taux de chômage: 7%",
                               "Hausse des salaires: +1,8%/an, Taux de chômage: 4.5%",
                               "Hausse des salaires: +1%/an, Taux de chômage: 10%"]
        self.scenarios_labels_courts=["Scénario inexistant", 
                                      "+1,8%/an, Chômage: 7%",
                                      "+1,5%/an, Chômage: 7%",
                                      "+1,3%/an, Chômage: 7%",
                                      "+1%/an, Chômage: 7%",
                                      "+1,8%/an, Chômage: 4.5%",
                                      "+1%/an, Chômage: 10%"]

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
        
        # Le répertoire de sauvegarde des images
        self.dir_image = "."

        self.affiche_quand_ecrit = True # Affiche un message quand on écrit un fichier

        # Paramètres pour l'algorithme d'inversion de la durée de vie en retraite
        # Bornes de recherche de l'âge
        self.rechercheAgeBornes = [60.0, 70.0]
        # Tolérance relative sur l'âge
        self.rechercheAgeRTol = 1.e-3
        return None

    def pilotageCOR(self):
        """
        pilotage 1 : statu quo du COR
        
        Description :
            Retourne un objet de type SimulateurAnalyse.

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageCOR()
        """
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(self.T, self.P, self.A)
        resultat = self._creerAnalyse(self.T, self.P, self.A, S, RNV, REV, Depenses)
        return resultat
    
    def _creerAnalyse(self, Ts, Ps, As, Ss, RNVs, REVs, Depenses):
        """
        Retourne une analyse en fonction des objets essentiels. 
        """
        PIB = self._genereTrajectoirePIB()
        PensionBrut = self._calculePensionAnnuelleDroitDirect(PIB, As)
        resultat = SimulateurAnalyse(Ts, Ps, As, Ss, RNVs, REVs, Depenses, \
                                     PIB, PensionBrut, \
                                     self.scenarios, self.annees_EV, self.annees, self.annees_standard, \
                                     self.scenarios_labels, self.scenarios_labels_courts, 
                                     self.dir_image, self.ext_image)
        return resultat
    
    def pilotageParPensionAgeCotisations(self, Pcible=None, Acible=None, Tcible=None):
        """
        pilotage 1 : imposer 1) le niveau des pensions par rapport aux salaires
        2) l'âge de départ à la retraite
        3) le taux de cotisations
            
        Paramètres :
            Pcible : le niveau de pension des retraites par rapport aux actifs
            Acible : l'âge de départ à la retraite
            Tcible : le taux de cotisations

        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParPensionAgeCotisations(Pcible = 0.5)
            simulateur.pilotageParPensionAgeCotisations(Acible = 62.0)
            simulateur.pilotageParPensionAgeCotisations(Tcible = 0.28)
            simulateur.pilotageParPensionAgeCotisations(Pcible = 0.5, Acible = 62.0)
            simulateur.pilotageParPensionAgeCotisations(Pcible = 0.5, Acible = 62.0, Tcible = 0.28)
            
            # Conserve le niveau de pension actuel
            s = 3 # Scénario central
            Pcible = simulateur.P[s][2020]
            simulateur.pilotageParPensionAgeCotisations(Pcible = Pcible)
        """
        # Génère les trajectoires en fonction des paramètres
        Ps = self.genereTrajectoire("P", Pcible)
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat

    def pilotageParSoldePensionAge(self, Scible=None, Pcible=None, Acible=None):
        """
        pilotage 2 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) l'âge de départ à la retraite
            
        Paramètres :
            Scible : la situation financière en % de PIB
            Pcible : le niveau de pension des retraites par rapport aux actifs
            Acible : l'âge de départ à la retraite
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParSoldePensionAge(Scible = 0.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        As = self.genereTrajectoire("A", Acible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_As(Ss, Ps, As)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat

    def pilotageParSoldePensionCotisations(self, Scible=None, Pcible=None, Tcible=None):
        """
        pilotage 3 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) le taux de cotisations
            
        Paramètres :
            Scible : la situation financière en % de PIB
            Pcible : le niveau de pension des retraites par rapport aux actifs
            Tcible : le taux de cotisations
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParSoldePensionCotisations(Scible = 0.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        Ts = self.genereTrajectoire("T", Tcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_Ts(Ss, Ps, Ts)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 

    def pilotageParSoldeAgeCotisations(self, Scible=None, Acible=None, Tcible=None):
        """
        pilotage 4 : imposer 1) le bilan financer
        2) l'âge de départ à la retraite
        3) le taux de cotisations
            
        Paramètres :
            Scible : la situation financière en % de PIB
            Acible : l'âge de départ à la retraite
            Tcible : le taux de cotisations
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParSoldeAgeCotisations(Scible = 0.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_As_Ts(Ss, As, Ts)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 

    def pilotageParSoldeAgeDepenses(self, Scible=None, Acible=None, Dcible=None):
        """
        pilotage 5 : imposer 1) le bilan financer
        2) l'âge de départ à la retraite
        3) le niveau de dépenses
            
        Paramètres :
            Scible : la situation financière en % de PIB
            Acible : l'âge de départ à la retraite
            Dcible : le niveau de dépenses
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParSoldeAgeDepenses(Scible = 0.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        As = self.genereTrajectoire("A", Acible)
        Ds = self.genereTrajectoire("Depenses", Dcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_As_Ds(Ss, As, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 
    
    def pilotageParSoldePensionDepenses(self, Scible=None, Pcible=None, Dcible=None):
        """
        pilotage 6 : imposer 1) le bilan financer
        2) le niveau des pensions par rapport aux salaires
        3) le niveau de dépenses
            
        Paramètres :
            Scible : la situation financière en % de PIB
            Pcible : le niveau de pension des retraites par rapport aux actifs
            Dcible : le niveau de dépenses
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParSoldePensionDepenses(Scible = 0.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ss = self.genereTrajectoire("S", Scible)
        Ps = self.genereTrajectoire("P", Pcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ss_Ps_Ds(Ss, Ps, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 

    def pilotageParPensionCotisationsDepenses(self, Pcible=None, Tcible=None, Dcible=None):
        """
        pilotage 7 : imposer 1) le niveau des pensions par rapport aux salaires
        2) le taux de cotisations
        3) le niveau de dépenses
            
        Paramètres :
            Pcible : le niveau de pension des retraites par rapport aux actifs
            Tcible : le taux de cotisations
            Dcible : le niveau de dépenses
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParPensionCotisationsDepenses(Pcible = 0.5)
        """
        # Génère les trajectoires en fonction des paramètres
        Ps = self.genereTrajectoire("P", Pcible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ps_Ts_Ds(Ps, Ts, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 

    def pilotageParAgeCotisationsDepenses(self, Acible=None, Tcible=None, Dcible=None):
        """
        pilotage 8 : imposer 1) l'âge de départ à la retraite
        2) le taux de cotisations
        3) le niveau de dépenses
            
        Paramètres :
            Acible : l'âge de départ à la retraite
            Tcible : le taux de cotisations
            Dcible : le niveau de dépenses
            
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParAgeCotisationsDepenses(Acible = 62.0)
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        Ts = self.genereTrajectoire("T", Tcible)
        Ds = self.genereTrajectoire("Depenses", Dcible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_Ts_Ds(As, Ts, Ds)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat 
    
    def pilotageParAgeEtNiveauDeVie(self, Acible=None, RNVcible=None, Scible=None):
        """
        pilotage 9 : imposer 1) l'âge de départ à la retraite,  
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres :
            Acible : un flottant, l'âge de départ imposé
            RNVcible : un flottant positif, le niveau de vie des retraités par 
                rapport à l’ensemble de la population
            Scible : la situation financière en % de PIB
        
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParAgeEtNiveauDeVie(RNVcible = 1.0)
        """
        # Génère les trajectoires en fonction des paramètres
        As = self.genereTrajectoire("A", Acible)
        RNVs = self.genereTrajectoire("RNV", RNVcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_As_RNV_S(As, RNVs, Ss)
        # Simule 
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat
    
    def pilotageParNiveauDeVieEtCotisations(self, Tcible=None, RNVcible=None, Scible=None):
        """
        pilotage 10 : imposer 1) le taux de cotisations, 
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres :
            Tcible : le taux de cotisations
            RNVcible : le niveau de vie des retraités par rapport à 
                l’ensemble de la population
            Scible : la situation financière en % de PIB
        
        Description :
            Retourne un objet de type SimulateurAnalyse.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire.

        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.pilotageParNiveauDeVieEtCotisations(RNVcible = 1.0)
        """
        # Génère les trajectoires en fonction des paramètres
        Ts = self.genereTrajectoire("T", Tcible)
        RNVs = self.genereTrajectoire("RNV", RNVcible)
        Ss = self.genereTrajectoire("S", Scible)
        # Calcule le pilotage
        Ts, Ps, As = self._calcule_fixant_Ts_RNV_S(Ts, RNVs, Ss)
        # Simule
        S, RNV, REV, Depenses = self._calcule_S_RNV_REV(Ts,Ps,As)
        resultat = self._creerAnalyse(Ts, Ps, As, S, RNV, REV, Depenses)
        return resultat
    
    def get(self, var):
        """
        Retourne une donnée du COR correspondant à un nom donné.
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
        
        Paramètres :
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
    
        
    def _calcule_fixant_Ts_RNV_S(self, Ts, RNVs, Ss):
        """
        Pilotage 3 : calcul à cotisations et niveau de vie défini
        
        Paramètres :
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
        
        Paramètres :
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
        
    def _calcule_S_RNV_REV(self, Ts, Ps, As):
        """
        pilotage 0 : statu quo du COR
        Calcule les sorties du modèle de retraite en fonction des leviers.
        
        Paramètres :
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
    
                annee_naissance = round(a + 0.5 - As[s][a])
                age_mort = 60.0 + self.EV[s][annee_naissance]
                REV[s][a] = ( age_mort - As[s][a] ) / age_mort
    
        return S, RNV, REV, Depenses

    def genereTrajectoire(self, nom, valeur=None):
        """
        Crée une nouvelle trajectoire à partir de la valeur constante. 
        
        Paramètres :
            nom : une chaîne de caratères, le nom de la variable
            valeur : un flottant, la valeur numérique constante
        
        Description :        
            Retourne un dictionnaire contenant une trajectoire 
            dans tous les scénarios et pour toutes les années : 
            trajectoire[s][a] est la valeur numérique du scénario s à l'année a
            
            * Si la valeur n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire.         
        
        Exemples        
            simulateur = SimulateurRetraites()
            simulateur.genereTrajectoire(simulateur, "A") # Départ à l'âge du COR
            simulateur.genereTrajectoire(simulateur, "A", 62.0) # Départ à 62.0 ans
            simulateur.genereTrajectoire(simulateur, "A", simulateur.A[1][2020]) # Départ à l'âge du COR en 2020
        """

        if type(valeur) is dict:
            # Si la valeur est un dictionnaire, on suppose que c'est une trajectoire 
            # et on le copie
            trajectoire = deepcopy(valeur)
        else:
            # Sinon, on suppose que c'est un flottant 
            # et on calcule la trajectoire du COR
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
            elif (nom=="REV"):
                S_COR, RNV_COR, REV_COR, Depenses_COR = self._calcule_S_RNV_REV(self.T, self.P, self.A)
                trajectoire = REV_COR
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
        
        Paramètres :
            taille_fonte_titre : taille de la fonte du titre (par défaut, fs=8)
            dessine_legende : booleen, True si la légende doit être dessinée
            scenarios_indices : une liste d'entiers, la liste des indices des scénarios
            (par défaut, sc = range(1,7))
            dessine_annees : la liste des années à dessiner
        
        Exemple:
            simulateur = SimulateurRetraites()
            simulateur.dessineConjoncture()
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
    
    def graphique(self, nom, v = None, taille_fonte_titre = 8, yaxis_lim = None, \
                  dessine_legende = False, scenarios_indices = None, 
                  dessine_annees = None):
        """
        Dessine un graphique associé à une variable donnée 
        pour tous les scénarios.
        
        Paramètres :
            nom : chaîne de caractère, nom de la variable
            v : variable à dessiner (par défaut, en fonction du nom)
            taille_fonte_titre : taille de la fonte du titre (par défaut, fs=8)
            yaxis_lim : une liste de taille 2, les bornes inférieures et supérieures 
            de l'axe des ordonnées (par défaut, utilise les paramètres de 
            l'objet)
            dessine_legende : booleen, True si la légende doit être dessinée
            scenarios_indices : une liste d'entiers, la liste des indices des scénarios
            (par défaut, sc = range(1,7))
            dessine_annees : la liste des années à dessiner
        
        Description :
            Le nom peut être une égal à une des chaînes de caractères parmi 
            les chaînes suivantes : "B", "NR", "NR", "G", "dP", "TPR", 
            "TPS", "CNV", "EV".
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.graphique("B")
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

        if scenarios_indices is None:
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
                label_variable = self.scenarios_labels[s]
            else:
                label_variable = self.scenarios_labels_courts[s]
            pl.plot(list_annees_dessin, y, label=label_variable )
    
        # titres des figures
        indice_variable = self.liste_variables.index(nom)
        titre_figure=self.liste_legendes[ indice_variable ]
           
        pl.title(titre_figure,fontsize=taille_fonte_titre)
        
        # Ajuste les limites de l'axe des ordonnées
        if yaxis_lim is None:
            # If the use did not set the yaxis_lim
            if nom in self.yaxis_lim.keys():
                # If the variable name was found in the dictionnary
                yaxis_lim = self.yaxis_lim[nom]
        else:
            pl.ylim(bottom=yaxis_lim[0],top=yaxis_lim[1])

        if dessine_legende:
            pl.legend(loc="best")
        return None
    
    def setAfficheMessageEcriture(self, affiche_quand_ecrit):
        """
        Configure l'affichage d'un message quand on écrit un fichier
        
        Paramètres :
            affiche_quand_ecrit : un booléen (par défaut = True)
        
        Exemple
            simulateur = SimulateurRetraites()
            simulateur.setAfficheMessageEcriture(False)
        """
        self.affiche_quand_ecrit = affiche_quand_ecrit
        return None
    
    def setImageFormats(self, ext_image):
        """
        Configure le format de sauvegarde des images
        
        Paramètres :
            ext_image : une liste de chaînes de caractères (par defaut, ext_image=["png","pdf"])
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.setImageFormats(["jpg"])
        """
        self.ext_image = ext_image
        return None

    def getImageFormats(self):
        """
        Retourne la liste des formats de sauvegarde des images.
        
        Exemple :
            simulateur = SimulateurRetraites()
            ext_image = simulateur.getImageFormats()
        """
        return self.ext_image 

    
    def setLabelLongs(self, labels_is_long):
        """
        Configure si la longueur des étiquettes est longue ou courte.
        
        Paramètres :
            labels_is_long : un booléen, True si les labels longs sont utilisés (par défaut = True)
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.setLabelLongs(False)
        """
        self.labels_is_long = labels_is_long
        return None

    def getLabelLongs(self):
        """
        Retourne le booléen associé à la longueur des étiquette. 
        
        Exemple :
            simulateur = SimulateurRetraites()
            labels_is_long = simulateur.getLabelLongs()
        """
        return self.labels_is_long 

    def setDirectoryImage(self, dir_image):
        """
        Configure le répertoire contenant les images
        
        Paramètres :
            dir_image : une chaîne de caractères, le répertoire contenant les images 
            (par défaut, dir_image="fig")
            exportées par sauveFigure.
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.setDirectoryImage("/tmp")
        """
        self.dir_image = dir_image
        return None

    def getDirectoryImage(self):
        """
        Retourne le répertoire contenant les images
        
        Exemple :
            simulateur = SimulateurRetraites()
            dir_image = simulateur.getDirectoryImage()
        """
        return self.dir_image

    def sauveFigure(self, f):
        """
        Sauvegarde l'image dans le répertoire
        
        Paramètres :
            f : une chaîne de caractères, le nom de base des fichiers à sauver
        
        Description :
            Sauvegarde l'image dans les formats définis. 
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.sauveFigure("conjoncture")
        """
    
        for ext in self.ext_image:
            basefilename = f + "." + ext
            filename = os.path.join(self.dir_image,basefilename)
            if self.affiche_quand_ecrit:
                print("Ecriture du fichier %s" % (filename))
            pl.savefig(filename)
        return None
    
    def dessineLegende(self):
        """
        Crée un graphique présentant les légendes des graphiques.
        
        Exemple :
            simulateur = SimulateurRetraites()
            simulateur.dessineLegende()
        """
        # Juste les légendes
        pl.figure(figsize=(6,2))
        for s in self.scenarios:
            pl.plot(0., 0., label = self.scenarios_labels[s])
        pl.legend(loc="center")
        pl.ylim(bottom=0.0, top=0.7)
        pl.axis('off')
        return None

    def _genereTrajectoirePIB(self):
        """
        Calcule le PIB dans les différents scénarios. 
        Source : https://fr.wikipedia.org/wiki/Produit_int%C3%A9rieur_brut_de_la_France
        """
        # Historique de PIBs (Milliards EUR)
        PIB_constate = {
        2005 : 1772.0, 
        2006 : 1853.3, 
        2007 : 1945.7, 
        2008 : 1995.8, 
        2009 : 1939.0, 
        2010 : 1998.5, 
        2011 : 2059.3, 
        2012 : 2091.1, 
        2013 : 2115.7, 
        2014 : 2141.1, 
        2015 : 2181.1, 
        2016 : 2228.9, 
        2017 : 2291.7, 
        2018 : 2353.1
        }
        # Croissance en fonction du scénario
        annee_dernier_PIB = 2018
        # Génère la trajectoire
        PIB = dict()
        for s in self.scenarios:
            PIB[s] = dict()
            croissance = self.scenarios_croissance[s]
            for a in self.annees:
                if (a<= annee_dernier_PIB):
                    PIB[s][a] = PIB_constate[a]
                else:
                    PIB[s][a] = (1.0 + croissance/100.0) * PIB[s][a - 1]
        return PIB

    def _calculePensionAnnuelleDroitDirect(self, PIB, As):
        """
        Calcule la pension annuelle de droit direct (brut) en kEUR.
        
        Paramètres :
            PIB : la trajectoire de PIB
            As : l'âge de départ à la retraite modifié par l'utilisateur
        """
        pensionBrut = dict()
        for s in self.scenarios:
            pensionBrut[s] = dict()
            for a in self.annees:
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                pensionBrut[s][a] = self.B[s][a] * self.P[s][a] * \
                    PIB[s][a] * 1000.0 / (self.NC[s][a] + 0.5 * GdA)
        return pensionBrut

    def calculeAge(self, REVcible):
        """
        Calcul de l'âge en fonction de la durée de vie à la retraite
        
        Paramètres :
            REVcible : la durée de vie à la retraite

        Description :
            Retourne un dictionnaire représentant une trajectoire d'âge de 
            départ en retraite.
            * Si la valeur cible n'est pas donnée, utilise par défaut la trajectoire du COR.
            * Si la valeur cible donnée est un flottant, utilise la trajectoire du 
            COR pour les années passées et cette valeur pour les années futures. 
            * Si la valeur cible donnée est un dictionnaire, considère que c'est 
            une trajectoire et utilise cette trajectoire. 
            
            Le calcul est réalisé par inversion numérique du ratio de durée  
            de vie en retraite. 
            Pour cela, nous utilisons le module scipy.optimize. 
            
            La trajectoire d'âge est uniquement déterminée par le ratio de durée 
            de vie en retraite. 
            C'est pourquoi on peut combiner la méthode calculeAge avec tout 
            pilotage prenant en entrée une trajectoire d'âge. 
            Par exemple, on peut combiner la méthode calculeAge avec la méthode 
            pilotageParPensionAgeCotisations. 

        Exemple :
            simulateur = SimulateurRetraites()
            REVcible = 0.30
            Acible = simulateur.calculeAge(REVcible = REVcible)
            analyse = simulateur.pilotageParSoldePensionAge(Acible = Acible)
        """

        def _EcartDeREV(As, args):
            """
            Pour un âge de départ à la retraite donné, 
            calcule la différence entre la durée de vie à la retraite pour 
            une année donnée et la durée de vie à la retraite 
            cible REVcible. 
            
            Paramètres :
                As : un flottant, l'âge de départ à la retraite
                args : une liste de quatre éléments [simulateur, annee, anneeReference, scenarioReference]
                simulateur : un SimulateurRetraite
                annee : un flottant, l'année du calcul de la durée de vie à la retraite
                anneeReference : un flottant, l'année de référence du calcul de la durée de vie à la retraite
                scenarioReference : un entier, le scénario de référence
                deltaREV : un flottant, la différence entre les deux durées de vie à la retraite
            
            Description :
                Utilise implicitement les variables simulateur et annee.
            """
            simulateur, scenario, annee, REVcible = args
            annee_naissance = round(annee + 0.5 - As)
            age_mort = 60.0 + simulateur.EV[scenario][annee_naissance]
            REV = ( age_mort - As ) / age_mort
            deltaREV = REVcible - REV
            return deltaREV

        REVs = self.genereTrajectoire("REV", REVcible)
        #
        As = deepcopy(self.A)
        for s in self.scenarios:
            for a in self.annees_futures:
                # Calcul l'âge
                args = [self, s, a, REVs[s][a]]
                result = spo.root_scalar(_EcartDeREV, \
                                         bracket= self.rechercheAgeBornes, \
                                         args = args, \
                                         rtol = self.rechercheAgeRTol)
                As[s][a] = result.root
        return As
