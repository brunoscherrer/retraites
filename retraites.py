#!/usr/bin/python
# coding:utf-8

import json
from pylab import *


# initialisations diverses
# chargement des donnees du COR pour les 6 scenarios

annees=range(2005,2071)
annees2=range(2020,2071)   # annees sur lesquelles on peut changer qqch

json_file=open('fileProjection.json')
data = json.load(json_file)


def get(var,s,a): # variable, scenario, annee
    return data[var][str(s)][str(a)]

def get2(var,s): # variable scenario
    v=dict()
    for a in annees:
        v[a]=get(var,s,a)
    return v


def recupere_TPA(sc=1):
    
    T, P, A = dict(),dict(),dict()
    
    for a in annees:
        A[a] = get('A',sc,a) 
        P[a] = get('P',sc,a)
        T[a] = get('T',sc,a)

    return T, P, A


def reforme(sc=1, age=0, niveau=1.0, equil=0.0):

    Ts,Ps,As = recupere_TPA(sc)
    
    ###  Objectifs

    RNVs,Ss = dict(),dict()

    for a in annees2:

        if age!=0:
            As[a] = age    # année de départ effective
        RNVs[a] = niveau   # egalite du niveau de vie entre retraités et actifs
        Ss[a] = equil      # situation financière du système équilibrée


    ### Calcul des cotisations et des pensions relatives

    for a in annees2:

        var = dict()

        for s in ['G','A','B','NR','NC','dP','TCR','TCS','T','CNV']:
            var[s] = get(s,sc,a)

        GdA = var['G'] * ( As[a]- var['A'] )
        K = ( var['NR'] - GdA ) / ( var['NC'] + 0.5*GdA )
        Z = ( 1.0 - var['TCR'] ) * var['CNV'] / RNVs[a] 
        U = 1.0 - ( var['TCS'] - var['T'] )
        L = Ss[a] / var['B']

        Ps[a] = ( U - L - K*var['dP'] ) / ( Z + K )
        Ts[a] = U - Ps[a] * Z 

    return Ts,Ps,As
        

def simule(Ts,Ps,As,sc=1):

    S,RNV,REV = dict(), dict(), dict()

    for a in annees:

        var = dict()

        for s in ['G','A','B','NR','NC','dP','TCR','TCS','T','CNV']:
            var[s]=get(s,sc,a)

        GdA = var['G'] * ( As[a]-var['A'] )
        K = ( var['NR'] - GdA ) / ( var['NC'] + 0.5*GdA )
        U = 1.0 - ( var['TCS'] - var['T'] )
        S[a] = var['B'] * ( Ts[a] -  K * ( Ps[a] + var['dP'] ) ) 
        RNV[a] =  Ps[a] * ( 1.0 - var['TCR'] ) / (U - Ts[a]) * var['CNV']


        var['EV'] = get('EV',sc,int(a+.5-As[a]))
        tmp = 60.0 + var['EV']
        REV[a] = ( tmp - As[a] ) / tmp  

    return S, RNV, REV


