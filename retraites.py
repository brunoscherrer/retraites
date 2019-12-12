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

def calcule_T_P_A(Age=62, RNV=1.0, S=0.0):

    T,P,A,G,NR,NC,TCR,TCS,CNV,dP,B = get('T'),get('P'),get('A'),get('G'),get('NR'),get('NC'),get('TCR'),get('TCS'),get('CNV'),get('dP'),get('B')

    As=deepcopy(A)
    
    for s in scenarios:

        for a in annees_futures:

            if Age!=0:
                As[s][a] = Age
            
            GdA = G[s][a] * ( As[s][a] - A[s][a] )
            K = ( NR[s][a] - GdA ) / ( NC[s][a] + 0.5*GdA )
            Z = ( 1.0 - TCR[s][a] ) * CNV[s][a] / RNV 
            U = 1.0 - ( TCS[s][a] - T[s][a] )
            L = S / B[s][a]

            P[s][a] = ( U - L - K*dP[s][a] ) / ( Z + K )
            T[s][a] = U - P[s][a] * Z 

    return T,P,As


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


