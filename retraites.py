#!/usr/bin/python
# coding:utf-8

import json
from pylab import *
from copy import deepcopy


# initialisations diverses
# chargement des donnees du COR pour les 6 scenarios

horizon=2070
annees=range(2005, horizon+1)    # annees sur lesquelles on fait les calculs
annees_futures=range(2020, horizon+1)   # annees sur lesquelles on peut changer qqch
annees_EV=range(1930,2011)         # annees sur lesquelles on a l'espérance de vie
scenarios=range(1,7)             # scenarios consideres

json_file=open('fileProjection.json')
data = json.load(json_file)

# fonction pour récupérer les données du COR

def get(var):
    
    if var=='EV':
        an=annees_EV
    else:
        an=annees
    v=dict()
    
    for s in scenarios:
        v[s]=dict()
        for a in an:
            v[s][a]=data[var][str(s)][str(a)]
            
    return v

#############################################################################

# Calculs

def calcule_Ts_Ps_As_fixant_As_RNV_S(Age=0, RNV=1.0, S=0.0):
    # Si Age==0 utilise l'age de la projection COR

    T,P,A,G,NR,NC,TCR,TCS,CNV,dP,B = get('T'),get('P'),get('A'),get('G'),get('NR'),get('NC'),get('TCR'),get('TCS'),get('CNV'),get('dP'),get('B')

    Ts,Ps,As = deepcopy(T), deepcopy(P), deepcopy(A)

    if Age!=0:
        for s in scenarios:
            for a in annees_futures:
                As[s][a] = Age
        
    for s in scenarios:

        for a in annees_futures:
             
            GdA = G[s][a] * ( As[s][a] - A[s][a] )
            K = ( NR[s][a] - GdA ) / ( NC[s][a] + 0.5*GdA )
            Z = ( 1.0 - TCR[s][a] ) * CNV[s][a] / RNV 
            U = 1.0 - ( TCS[s][a] - T[s][a] )
            L = S / B[s][a]

            Ps[s][a] = ( U - L - K*dP[s][a] ) / ( Z + K )
            Ts[s][a] = U - Ps[s][a] * Z 
            
    return Ts,Ps,As




def calcule_Ts_Ps_As_fixant_Ts_RNV_S(Tcible=0, RNV=1.0, S=0.0):
    
    # Si Tcible==0, utilise le taux fixé par le COR
    
    T,P,A,G,NR,NC,TCR,TCS,CNV,dP,B = get('T'),get('P'),get('A'),get('G'),get('NR'),get('NC'),get('TCR'),get('TCS'),get('CNV'),get('dP'),get('B')

    Ts = deepcopy(T)
    if Tcible!=0:
        for s in scenarios:
            for a in annees_futures:
                Ts[s][a] = Tcible
        
    Ps, As = deepcopy(P), deepcopy(A)

    for s in scenarios:

        for a in annees_futures:

            Ps[s][a] = RNV * (1-(TCS[s][a] + Ts[s][a]-T[s][a])) / CNV[s][a] / (1-TCR[s][a])
            K = (Ts[s][a] - S / B[s][a]) / (Ps[s][a]+dP[s][a])
            As[s][a] = A[s][a] + ( NR[s][a] - K*NC[s][a] ) / (0.5*K + 1.0) / G[s][a]
            
    return Ts,Ps,As


def calcule_Ts_Ps_As_fixant_Ps_S(Pcible=0, S=0.0):
    
    # Si Pcible==0, utilise le taux du COR en 2020
    
    T,P,A,G,NR,NC,TCR,TCS,CNV,dP,B = get('T'),get('P'),get('A'),get('G'),get('NR'),get('NC'),get('TCR'),get('TCS'),get('CNV'),get('dP'),get('B')

        
    Ps = deepcopy(P)
    for s in scenarios:
        if Pcible==0:
            p = P[s][2020]
        else:
            p = Pcible
        for a in annees_futures:
            Ps[s][a] = p
    
    Ts, As = deepcopy(T), deepcopy(A)

    for s in scenarios:

        for a in annees_futures:

            K = (Ts[s][a] - S / B[s][a]) / (Ps[s][a]+dP[s][a])
            As[s][a] = A[s][a] + ( NR[s][a] - K*NC[s][a] ) / (0.5*K + 1.0) / G[s][a]
            
    return Ts,Ps,As
    


def calcule_S_RNV_REV(Ts,Ps,As):

    T,P,A,G,NR,NC,TCR,TCS,CNV,dP,B,EV = get('T'),get('P'),get('A'),get('G'),get('NR'),get('NC'),get('TCR'),get('TCS'),get('CNV'),get('dP'),get('B'),get('EV')
    
    S,RNV,REV = dict(), dict(), dict()

    for s in scenarios:

        S[s], RNV[s], REV[s] = dict(), dict(), dict()

        for a in annees:

            GdA = G[s][a] * ( As[s][a]-A[s][a] )
            K = ( NR[s][a] - GdA ) / ( NC[s][a] + 0.5*GdA )
            U = 1.0 - ( TCS[s][a] - T[s][a] )

            S[s][a] = B[s][a] * ( Ts[s][a] -  K * ( Ps[s][a] + dP[s][a] ) ) 
            RNV[s][a] =  Ps[s][a] * ( 1.0 - TCR[s][a] ) / (U - Ts[s][a]) * CNV[s][a]

            tmp = 60.0 + EV[s][ int(a+.5-As[s][a]) ]
            REV[s][a] = ( tmp - As[s][a] ) / tmp

    return S, RNV, REV


