#!/usr/bin/python
# coding:utf-8

from __future__ import print_function
import pylab as pl
import SimulateurRetraites
import SimulateurAnalyse

##############################################################################
# SIMULATION NUMERIQUES
    
# génération des graphes pour le statu quo (COR)

def simu0():

    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    pl.figure(figsize=(6,8))
    pl.suptitle('Projections du COR',fontsize=16)
    
    S,RNV,REV = simulateur.calcule_S_RNV_REV(simulateur.T,simulateur.P,simulateur.A)

    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    analyse.graphiques(simulateur.T,simulateur.P,simulateur.A, S, RNV,REV)

    analyse.mysavefig("cor")
    return None


# génération des graphes sur la conjoncture

def simu1():

    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    
    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    pl.figure(figsize=(10,8))
    pl.suptitle(u"Projections du COR (hypothèses)",fontsize=16)
    for c in range(9):
        pl.subplot(3,3,c+1)
        v,V = [ (simulateur.B,'B'), (simulateur.NR,'NR'), (simulateur.NC,'NC'), \
               (simulateur.G,'G'), (simulateur.dP,'dP'), (simulateur.TCR,'TPR'), 
               (simulateur.TCS,'TPS'), (simulateur.CNV,'CNV'), (simulateur.EV,'EV') ][c]
        analyse.graphique(v,V)
    pl.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    analyse.mysavefig("conjoncture")
    return None

    
# génération des graphes pour des réformes à prestation garantie

def simu2(ages=61.0,S=0.0):
    
    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    d = ages

    pl.figure(figsize=(6,8))
    if d!=0:
        pl.suptitle( (u"Cotisations adaptées (eq. financier, maintien du niveau de vie & départ à %d ans"%(d)),fontsize=10)
    else:
        pl.suptitle(u"Cotisations adaptées (équilibre financier & maintien du niveau de vie)",fontsize=10)
            
    Ts,Ps,As = simulateur.calcule_Ts_Ps_As_fixant_As_RNV_S(d, 1.0, S)
    S,RNV,REV = simulateur.calcule_S_RNV_REV(Ts,Ps,As)
    
    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    analyse.graphiques(Ts,Ps,As, S,RNV,REV)
    
    if d!=0:
        analyse.mysavefig( ("%dans"%(d)))
    else:
        analyse.mysavefig("cotisations")
    return None

            
# génération des graphes pour la réforme Macron avec maintien du niveau de vie

def simu3(Ts=0,RNV=1.0):
    
    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    pl.figure(figsize=(6,8))
    pl.suptitle(u'Réforme Macron (équilibre financier & maintien du niveau de vie)',fontsize=12)
                
    Ts,Ps,As = simulateur.calcule_Ts_Ps_As_fixant_Ts_RNV_S(Ts,RNV)
    S,RNV,REV = simulateur.calcule_S_RNV_REV(Ts,Ps,As)
        
    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    analyse.graphiques(Ts,Ps,As, S,RNV,REV)
    
    print("Maintien du niveau de vie")
    analyse.affiche_solutions_simulateur_COR(Ts,Ps,As)
    
    analyse.mysavefig("macron_niveau_de_vie")
    return None

# génération des graphes pour la réforme Macron avec point indexé sur le salaire moyen (rapport (pension moyenne/)(salaire moyen) constant égal à celui de 2020)

def simu4(Ps=0,Ts=0):

    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    pl.figure(figsize=(6,8))
    pl.suptitle(u'Réforme Macron (équilibre financier & ratio pension/salaire fixe)',fontsize=12)
                
    Ts,Ps,As = simulateur.calcule_Ts_Ps_As_fixant_Ps_Ts_S(Ps,Ts)
    S,RNV,REV = simulateur.calcule_S_RNV_REV(Ts,Ps,As)
        
    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    analyse.graphiques(Ts,Ps,As, S,RNV,REV)
    analyse.mysavefig("macron_point_indexe")
    
    print("Maintien du rapport pension moyenne / salaire moyen")
    analyse.affiche_solutions_simulateur_COR(Ts,Ps,As)
    return None

############################################################################
# génération des figures pour les articles mediapart

def pour_article_2():

    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    print("Données et figure pour article 2")
    
    Ts,Ps,As = simulateur.calcule_Ts_Ps_As_fixant_Ts_RNV_S(0)
    S,RNV,REV = simulateur.calcule_S_RNV_REV(Ts,Ps,As)
        
    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    pl.figure(figsize=(9,6))
    analyse.graphique(As,"A",14,[],True,range(1,5))
    pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
    pl.legend(loc="best")
    analyse.mysavefig("macron_68_ans")

    pl.figure(figsize=(9,6))
    analyse.graphique(As,"A",14,[],True)
    pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
    pl.legend(loc="best")
    analyse.mysavefig("macron_68_ans_tout")
    
    print("Réforme Macron, Maintien du niveau de vie")
    analyse.affiche_solutions_simulateur_COR(Ts,Ps,As)
    return None

def pour_article_3():

    simulateur = SimulateurRetraites.SimulateurRetraites('retraites/fileProjection.json')
    print("Données et figures pour article 3")
    
    Ts,Ps,As = simulateur.calcule_Ts_Ps_As_fixant_As_Ts_S(62) 
    S,RNV,REV = simulateur.calcule_S_RNV_REV(Ts,Ps,As)

    analyse = SimulateurAnalyse.SimulateurAnalyse(simulateur, "fig/")
    titre=u"Modèle du COR: Réforme Macron (éq. financier & départ à 62 ans)"
    
    pl.figure(figsize=(9,6))
    analyse.graphique(RNV,"RNV",14,[],True,range(1,5))
    pl.suptitle(titre,fontsize=14)
    pl.legend(loc="best")
    analyse.mysavefig("macron_62_ans_nv")
    
    pl.figure(figsize=(9,6))
    analyse.graphique(Ps,"P",14,[],True,range(1,5))
    pl.suptitle(titre,fontsize=14)
    pl.legend(loc="best")
    analyse.mysavefig("macron_62_ans_p")
    
    print("Réforme Macron, Départ à 62 ans")
    analyse.affiche_solutions_simulateur_COR(Ts,Ps,As)
    print("\nEvolution du niveau de vie:")
    analyse.affiche_variable(RNV)
    print("\nEvolution du ratio pension/salaire:")
    analyse.affiche_variable(Ps)
    return None

#####################

simu0()
#simu1()
#simu2()
#simu3()
#simu4(0,0.311)

#pour_article_2()
#pour_article_3()

#simu2(62.0,-0.01)


