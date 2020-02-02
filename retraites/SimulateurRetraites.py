#!/usr/bin/python
# coding:utf-8

from copy import deepcopy
import json
from SimulateurAnalyse import SimulateurAnalyse

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
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(self.T, self.P, self.A)
        resultat = SimulateurAnalyse(self.T, self.P, self.A, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParAgeEtNiveauDeVie(self, Age=0, RNV=1.0, Ss=0.0):
        """
        pilotage 1 : imposer 1) l'âge de départ à la retraite,  
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres
        Age : un flottant, l'âge de départ imposé
        RNV : un flottant positif, le niveau de vie des retraités par rapport à l’ensemble de la population
        Ss : la situation financière en % de PIB
        Retourne un objet de type SimulateurAnalyse.
        
        Description
        Si Age==0 utilise l'age de la projection COR
        """
        Ts, Ps, As = self.calcule_fixant_As_RNV_S(Age, RNV, Ss)
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParCotisationsEtPensions(self, Pcible=0, Tcible=0, Ss=0.0):
        """
        pilotage 2 : imposer 1) le taux de cotisations,  
        2) le niveau de pensions par rapport aux salaires et 
        3) le bilan financier
        
        Paramètres
        Pcible : le niveau de pension des retraites par rapport aux actifs
        Tcible : le taux de cotisations
        Ss : la situation financière en % de PIB
        Retourne un objet de type SimulateurAnalyse.
        
        
        Description
        Si Pcible==0, utilise le taux du COR en 2020
        Si Tcible==0, utilise le taux fixé par le COR
        """
        Ts, Ps, As = self.calcule_fixant_Ps_Ts_S(Pcible, Tcible, Ss)
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParNiveauDeVieEtCotisations(self, Tcible=0, RNV=1.0, Ss=0.0):
        """
        pilotage 3 : imposer 1) le taux de cotisations, 
        2) le niveau de vie par rapport à l'ensemble de la population et 
        3) le bilan financier
        
        Paramètres
        Tcible : le taux de cotisations
        RNV : un flottant positif, le niveau de vie des retraités par rapport à l’ensemble de la population
        Ss : la situation financière en % de PIB
        Retourne un objet de type SimulateurAnalyse.
        
        Description
        Si Tcible==0, utilise le taux fixé par le COR
        """
        Ts, Ps, As = self.calcule_fixant_Ts_RNV_S(Tcible, RNV, Ss)
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat
    
    def pilotageParCotisationsEtAge(self, Acible=0, Tcible=0, Ss=0.0):
        """
        pilotage 4 : imposer 1) le taux de cotisations, 
        2) l'âge de départ à la retraite et 
        3) le bilan financier. 
        
        Paramètres
        Acible : l'âge de départ à la retraite
        Tcible : le taux de cotisations
        Ss : la situation financière en % de PIB
        
        Retourne un objet de type SimulateurAnalyse.

        Description
        Si Acible==0, utilise l'âge du COR en 2020
        Si Tcible==0, utilise le taux fixé par le COR
        """
        Ts, Ps, As = self.calcule_fixant_As_Ts_S(Acible, Tcible, Ss) 
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(Ts,Ps,As)
        resultat = SimulateurAnalyse(Ts, Ps, As, S, RNV, REV, Depenses, \
                                     self.scenarios, self.annees_EV, self.annees)
        return resultat

    def pilotageParAgeEtDepenses(self, Acible=0, Dcible=0.0, Ss=0.0):
        """
        pilotage 5 : imposer 1) l'âge de départ à la retraite, 
        2) le niveau de dépenses Ds et 
        3) le bilan financier. 
        
        Paramètres
        Acible : l'âge de départ à la retraite
        Dcible : le niveau de dépenses
        Ss : la situation financière en % de PIB
        
        Retourne un objet de type SimulateurAnalyse.

        Description
        Si Acible==0, utilise l'âge du COR
        Si Ds==0, utilise les dépenses du COR
        """
        Ts, Ps, As = self.calcule_fixant_As_Ds_S(Acible, Dcible, Ss)
        S, RNV, REV, Depenses = self.calcule_S_RNV_REV(Ts,Ps,As)
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
    
    def calcule_fixant_As_RNV_S(self, Age_s=0, RNVs=1.0, Ss=0.0):
        """
        Pilotage 1 : calcul à âge et niveau de vie défini
    
        Si Age_s==0 utilise l'age de la projection COR
        """
        
        Ts, Ps, As = deepcopy(self.T), deepcopy(self.P), deepcopy(self.A)
        
        # Définit l'âge
        if Age_s!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    As[s][a] = Age_s
        
        # Calcule Ps et Ts
        for s in self.scenarios:    
            for a in self.annees_futures:                 
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5*GdA )
                Z = ( 1.0 - self.TCR[s][a] ) * self.CNV[s][a] / RNVs
                U = 1.0 - ( self.TCS[s][a] - self.T[s][a] )
                L = Ss / self.B[s][a]    
                Ps[s][a] = ( U - L - K*self.dP[s][a] ) / ( Z + K )
                Ts[s][a] = U - Ps[s][a] * Z 
                
        return Ts, Ps, As
    
    def calcule_fixant_Ps_Ts_S(self, Pcible=0, Tcible=0, Ss=0.0):
        """
        Pilotage 2 : calcul à cotisations et pensions définies
        
        Si Pcible==0, utilise le taux du COR en 2020
        Si Tcible==0, utilise le taux fixé par le COR
        """
        
        # Définit Ps
        Ps = deepcopy(self.P)
        for s in self.scenarios:
            if Pcible==0:
                p = self.P[s][2020]
            else:
                p = Pcible
            for a in self.annees_futures:
                Ps[s][a] = p
        
        # Définit Ts
        Ts = deepcopy(self.T)
        if Tcible!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    Ts[s][a] = Tcible
    
        # Calcule l'âge 
        As = deepcopy(self.A)    
        for s in self.scenarios:    
            for a in self.annees_futures:    
                K = (Ts[s][a] - Ss / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts, Ps, As
        
    def calcule_fixant_Ts_RNV_S(self, Tcible=0, RNV=1.0, Ss=0.0):
        """
        Pilotage 3 : calcul à cotisations et niveau de vie défini
        
        Si Tcible==0, utilise le taux fixé par le COR
        """
        
        # Définit Ts
        Ts = deepcopy(self.T)
        if Tcible!=0:
            if type(Tcible)==float:
                for s in self.scenarios:
                    for a in self.annees_futures:
                        Ts[s][a] = Tcible
            else:
                Ts=Tcible
            
        # Calcule Ps et As
        Ps, As = deepcopy(self.P), deepcopy(self.A)    
        for s in self.scenarios:    
            for a in self.annees_futures:    
                Ps[s][a] = RNV * (1-(self.TCS[s][a] + Ts[s][a]-self.T[s][a])) / self.CNV[s][a] / (1-self.TCR[s][a])
                K = (Ts[s][a] - Ss / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts, Ps, As
    
    
    def calcule_fixant_As_Ts_S(self, Acible=0, Tcible=0, Ss=0.0):
        """
        Pilotage 4 : calcul à cotisations et âge définis
        
        Si Acible==0, utilise l'âge du COR en 2020
        Si Tcible==0, utilise le taux fixé par le COR
        """
        
        # Définit As
        As = deepcopy(self.A)
        for s in self.scenarios:
            if Acible==0:
                b = self.A[s][2020]
            else:
                b = Acible
            for a in self.annees_futures:
                As[s][a] = b
        
        # Définit Ts
        Ts = deepcopy(self.T)
        if Tcible!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    Ts[s][a] = Tcible
                    
        # Calcule Ps
        Ps = deepcopy(self.P)        
        for s in self.scenarios:    
            for a in self.annees_futures:    
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5 * GdA )
                Ps[s][a] = (Ts[s][a]-Ss/self.B[s][a])/K - self.dP[s][a]
                
        return Ts, Ps, As
        
    def calcule_fixant_As_Ds_S(self, Acible=0, Dcible=0.0, Ss=0.0):
        """
        Pilotage 5 : calcul à âge et dépenses définis
        Ds : un dictionnaire, Ds[a] est le niveau de dépenses à l'année a
        
        Si Acible==None, utilise l'âge du COR
        Si Ds==None, utilise les dépenses du COR
        """
        
        # Définit l'âge
        As = deepcopy(self.A)
        if Acible==0:
            print("Utilise l'âge du COR")
        else:
            for s in self.scenarios:
                for a in self.annees_futures:
                    As[s][a] = Acible[a]
        
        # Définit les dépenses
        if Dcible==0.0:
            # Utilise les dépenses du COR
            print("Utilise les dépenses du COR")
            S_COR, RNV_COR, REV_COR, Ds = self.calcule_S_RNV_REV(self.T, self.P, self.A)
        else:
            # Utilise les dépenses données à chaque année
            Ds = dict()
            for s in self.scenarios:
                Ds[s] = dict()
                for a in self.annees_futures:
                    Ds[s][a] = Dcible[a]
    
        # Calcule Ps et Ts
        Ps = deepcopy(self.P)
        Ts = deepcopy(self.T)
        for s in self.scenarios:
            for a in self.annees_futures:
                Ts[s][a] = (Ss + Ds[s][a])/self.B[s][a]
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5 * GdA )
                Ps[s][a] = (Ts[s][a]-Ss/self.B[s][a])/K - self.dP[s][a]
                
        return Ts, Ps, As

    def calcule_S_RNV_REV(self, Ts, Ps, As):
        """
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
