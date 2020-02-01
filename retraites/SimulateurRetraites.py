#!/usr/bin/python
# coding:utf-8

from copy import deepcopy
import json

class SimulateurRetraites:
    def __init__(self, json_filename):
        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        self.horizon=2070
        self.annees=range(2005, self.horizon+1)           # annees sur lesquelles on fait les calculs
        self.annees_futures=range(2020, self.horizon+1)   # annees sur lesquelles on peut changer qqch
        self.annees_EV=range(1930,2011)              # annees sur lesquelles on a l'espérance de vie
        self.scenarios=range(1,7)                    # scenarios consideres

        # Lit les hypothèses de calcul dans le fichier JSON
        json_file = open(json_filename)
        self.data = json.load(json_file)
        json_file.close()
        
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

    def get(self, var):
        # fonction pour récupérer les données du COR
        
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
    
    def calcule_Ts_Ps_As_fixant_As_RNV_S(self, Age=0, RNV=1.0, S=0.0):
    
        # Si Age==0 utilise l'age de la projection COR
        
        Ts,Ps,As = deepcopy(self.T), deepcopy(self.P), deepcopy(self.A)
    
        if Age!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    As[s][a] = Age
            
        for s in self.scenarios:
    
            for a in self.annees_futures:
                 
                GdA = self.G[s][a] * ( As[s][a] - self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5*GdA )
                Z = ( 1.0 - self.TCR[s][a] ) * self.CNV[s][a] / RNV 
                U = 1.0 - ( self.TCS[s][a] - self.T[s][a] )
                L = S / self.B[s][a]
    
                Ps[s][a] = ( U - L - K*self.dP[s][a] ) / ( Z + K )
                Ts[s][a] = U - Ps[s][a] * Z 
                
        return Ts,Ps,As
    
    def calcule_Ts_Ps_As_fixant_Ts_RNV_S(self, Tcible=0, RNV=1.0, S=0.0):
        
        # Si Tcible==0, utilise le taux fixé par le COR
    
        Ts = deepcopy(self.T)
        if Tcible!=0:
            if type(Tcible)==float:
                for s in self.scenarios:
                    for a in self.annees_futures:
                        Ts[s][a] = Tcible
            else:
                Ts=Tcible
            
        Ps, As = deepcopy(self.P), deepcopy(self.A)
    
        for s in self.scenarios:
    
            for a in self.annees_futures:
    
                Ps[s][a] = RNV * (1-(self.TCS[s][a] + Ts[s][a]-self.T[s][a])) / self.CNV[s][a] / (1-self.TCR[s][a])
                K = (Ts[s][a] - S / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts,Ps,As
    
    
    def calcule_Ts_Ps_As_fixant_Ps_Ts_S(self, Pcible=0, Tcible=0, S=0.0):
        
        # Si Pcible==0, utilise le taux du COR en 2020
        # Si Tcible==0, utilise le taux fixé par le COR
        
        Ps = deepcopy(self.P)
        for s in self.scenarios:
            if Pcible==0:
                p = self.P[s][2020]
            else:
                p = Pcible
            for a in self.annees_futures:
                Ps[s][a] = p
        
        Ts = deepcopy(self.T)
        if Tcible!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    Ts[s][a] = Tcible
    
        As = deepcopy(self.A)
    
        for s in self.scenarios:
    
            for a in self.annees_futures:
    
                K = (Ts[s][a] - S / self.B[s][a]) / (Ps[s][a]+self.dP[s][a])
                As[s][a] = self.A[s][a] + ( self.NR[s][a] - K*self.NC[s][a] ) / (0.5*K + 1.0) / self.G[s][a]
                
        return Ts,Ps,As
        
    def calcule_Ts_Ps_As_fixant_As_Ts_S(self, Acible=0, Tcible=0, S=0.0):
        
        # Si Pcible==0, utilise le taux du COR en 2020
        # Si Tcible==0, utilise le taux fixé par le COR
        
        As = deepcopy(self.A)
        for s in self.scenarios:
            if Acible==0:
                b = self.A[s][2020]
            else:
                b = Acible
            for a in self.annees_futures:
                As[s][a] = b
        
        Ts = deepcopy(self.T)
        if Tcible!=0:
            for s in self.scenarios:
                for a in self.annees_futures:
                    Ts[s][a] = Tcible
    
        Ps = deepcopy(self.P)
        
        for s in self.scenarios:
    
            for a in self.annees_futures:
    
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5 * GdA )
                Ps[s][a] = (self.T[s][a]-S/self.B[s][a])/K - self.dP[s][a]
                
        return Ts,Ps,As
        
    def calcule_S_RNV_REV(self, Ts,Ps,As):
    
        S,RNV,REV = dict(), dict(), dict()
    
        for s in self.scenarios:
    
            S[s], RNV[s], REV[s] = dict(), dict(), dict()
    
            for a in self.annees:
    
                GdA = self.G[s][a] * ( As[s][a]-self.A[s][a] )
                K = ( self.NR[s][a] - GdA ) / ( self.NC[s][a] + 0.5*GdA )
                U = 1.0 - ( self.TCS[s][a] - self.T[s][a] )
                S[s][a] = self.B[s][a] * ( Ts[s][a] -  K * ( Ps[s][a] + self.dP[s][a] ) ) 
                RNV[s][a] =  Ps[s][a] * ( 1.0 - self.TCR[s][a] ) / (U - Ts[s][a]) * self.CNV[s][a]
    
                tmp = 60.0 + self.EV[s][ int(a+.5-As[s][a]) ]
                REV[s][a] = ( tmp - As[s][a] ) / tmp
    
        return S, RNV, REV
