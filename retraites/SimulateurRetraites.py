#!/usr/bin/python
# coding:utf-8

from copy import deepcopy
import json
from .SimulateurAnalyse import SimulateurAnalyse

class SimulateurRetraites:
    def __init__(self, json_filename):
        """
        Crée un simulateur à partir d'un fichier d'hypothèses JSON.
        
        Paramètres
        json_filename : une chaîne de caractère, le nom du fichier JSON contenant les hypothèses
        pilotage : un entier, la stratégie de pilotage (par défaut, celle du COR)
        
        Description
        Plusieurs stratégies de pilotage peuvent être utilisées. 
        Les pilotages 1 à 4 assurent l'équilibre financier. 
        * pilotage 0 : statu quo du COR (peut créer un déficit financier)
        * pilotage 1 : imposer l'âge de départ à la retraite et le niveau de vie,
        * pilotage 2 : imposer le taux de cotisations et le niveau pensions par rapport aux salaires,
        * pilotage 3 : imposer le niveau de vie par rapport à l'ensemble de la population et le taux de cotisations,
        * pilotage 4 : imposer le taux de cotisations et l'âge de départ à la retraite.

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
        self.TCR = self.get('TCR')
        self.TCS = self.get('TCS')
        self.CNV = self.get('CNV')
        self.dP = self.get('dP')
        self.B = self.get('B')
        self.EV = self.get('EV')
        
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
