#!/usr/bin/python
# coding:utf-8

from __future__ import print_function
import pylab as pl
import retraites



scenarios_labels=["Hausse des salaires: +1,8%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,5%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,3%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,8%/an, Taux de chômage: 4.5%",
                  "Hausse des salaires: +1%/an, Taux de chômage: 10%"]


### fonctions pour générer des graphiques


dir_image="./fig/"        # répertoire pour les images
ext_image=["png","pdf"]   # types de fichier à générer

def mysavefig(f):
    for ext in ext_image:
        pl.savefig(dir_image + f + "." + ext)

def graphique(v, nom, fs=8, rg=[], leg=False, sc=retraites.scenarios):

    if nom=="EV":
        an=retraites.annees_EV
    else:
        an=retraites.annees

    for s in sc:
        pl.plot(an, [ v[s][a] for a in an ], label=scenarios_labels[s-1] )

    # titres des figures
    
    t=[u"Situation financière du système (part du PIB)",
       u"Niveau de vie des retraités p/r à celui des actifs",
       u"Proportion de la vie passée à la retraite",
       u"Taux de cotisation de retraite (part du PIB)",
       u"Age de départ effectif moyen à la retraite",
       u"Ratio (pension moyenne)/(salaire moyen)",
       u"B: Part des revenus d'activité bruts dans le PIB",
       u"NR: Nombre de retraités",
       u"NC: Nombre de cotisants",
       u"G: Effectif d'une generation arrivant à l'âge de la retraite",
       u"dP: Autres dépenses de retraites",
       u"TPR: Taux de prélèvement sur les retraites",
       u"TPS: Taux de prélèvement sur les salaires",
       u"CNV: (niveau de vie)/[(pension moy))/(salaire moy)]",
       u"EV: Espérance de vie à 60 ans"
    ][ ["S","RNV","REV","T","A","P","B","NR","NC","G","dP","TPR","TPS","CNV","EV"].index(nom) ]
       
    pl.title(t,fontsize=fs)
    if rg!=[]:
        pl.ylim(bottom=rg[0],top=rg[1])
    if leg:
        pl.legend(loc="best")

def graphiques(T, P, A, S, RNV, REV, fs=8):

    for i in range(6):
        pl.subplot(3,2,i+1)
        v,V,r = [ (S,"S" ,[-0.02,0.02]),
                  (RNV,"RNV", [0.6,1.2]),
                  (REV,"REV", [0.2,0.4]),
                  (T,"T", [0.25,0.4] ),
                  (A,"A", [60,70]),
                  (P,"P", [.25,.55]) ][ i ]
        graphique(v, V, fs ,r)
    pl.tight_layout(rect=[0, 0.03, 1, 0.95])

    
##############################################################################

def affiche_variable(v):

    ans=[2019, 2020, 2025, 2030, 2040, 2050, 2060, 2070]
    for s in retraites.scenarios:
        print()
        print("Scenario",s,": ",scenarios_labels[s-1])
        for a in ans:
            print("%.2f"%(v[s][a]),)
        print("")
        
        
def affiche_solutions_simulateur_COR(Ts,Ps,As):

    print("Valeur à rentrer sur le simulateur officiel du COR:")
    
    ans=[2020, 2025, 2030, 2040, 2050, 2060, 2070]
    for s in retraites.scenarios:
        print("")
        print("Scenario",s,": ",scenarios_labels[s-1] )
        print("Age:        ",)
        for a in ans:
            print("%.1f"%(As[s][a]),)
        print("")
        print("Cotisation: ",)
        for a in ans:
            print("%.1f"%(100*Ts[s][a]),)
        print("")
        print("Pension:    ",)
        for a in ans:
            print("%.1f"%(100*Ps[s][a]),)
        print("")

        print("")


    
##############################################################################
# SIMULATION NUMERIQUES
    
# génération des graphes pour le statu quo (COR)

def simu0():

    pl.figure(figsize=(6,8))
    pl.suptitle('Projections du COR',fontsize=16)
    
    T,P,A = retraites.get('T'), retraites.retraites.get('P'), retraites.get('A')
    S,RNV,REV = retraites.calcule_S_RNV_REV(T,P,A)

    graphiques(T,P,A, S,RNV,REV)

    mysavefig("cor")


# génération des graphes sur la conjoncture

def simu1():

    B,NR,NC,G,dP,TPR,TPS,CNV,EV=retraites.get('B'),retraites.get('NR'),retraites.get('NC'),retraites.get('G'),retraites.get('dP'),retraites.get('TCR'),retraites.get('TCS'),retraites.get('CNV'),retraites.get('EV')
    
    pl.figure(figsize=(10,8))
    pl.suptitle(u"Projections du COR (hypothèses)",fontsize=16)
    for c in range(9):
        pl.subplot(3,3,c+1)
        v,V = [ (B,'B'), (NR,'NR'), (NC,'NC'), (G,'G'), (dP,'dP'), (TPR,'TPR'), (TPS,'TPS'), (CNV,'CNV'), (EV,'EV') ][c]
        graphique(v,V)
    pl.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    mysavefig("conjoncture")

    
# génération des graphes pour des réformes à prestation garantie

def simu2(ages=61.0,S=0.0):
    
    d = ages

    pl.figure(figsize=(6,8))
    if d!=0:
        pl.suptitle( (u"Cotisations adaptées (eq. financier, maintien du niveau de vie & départ à %d ans"%(d)),fontsize=10)
    else:
        pl.suptitle(u"Cotisations adaptées (équilibre financier & maintien du niveau de vie)",fontsize=10)
            
    Ts,Ps,As = retraites.calcule_Ts_Ps_As_fixant_As_RNV_S(d, 1.0, S)
    S,RNV,REV = retraites.calcule_S_RNV_REV(Ts,Ps,As)
    
    graphiques(Ts,Ps,As, S,RNV,REV)
    
    if d!=0:
        mysavefig( ("%dans"%(d)))
    else:
        mysavefig("cotisations")

            
# génération des graphes pour la réforme Macron avec maintien du niveau de vie

def simu3(Ts=0,RNV=1.0):
    
    pl.figure(figsize=(6,8))
    pl.suptitle(u'Réforme Macron (équilibre financier & maintien du niveau de vie)',fontsize=12)
                
    Ts,Ps,As = retraites.calcule_Ts_Ps_As_fixant_Ts_RNV_S(Ts,RNV)
    S,RNV,REV = retraites.calcule_S_RNV_REV(Ts,Ps,As)
        
    graphiques(Ts,Ps,As, S,RNV,REV)
    
    print("Maintien du niveau de vie")
    affiche_solutions_simulateur_COR(Ts,Ps,As)
    
    #mysavefig("macron_niveau_de_vie")

        
# génération des graphes pour la réforme Macron avec point indexé sur le salaire moyen (rapport (pension moyenne/)(salaire moyen) constant égal à celui de 2020)

def simu4(Ps=0,Ts=0):

    pl.figure(figsize=(6,8))
    pl.suptitle(u'Réforme Macron (équilibre financier & ratio pension/salaire fixe)',fontsize=12)
                
    Ts,Ps,As = retraites.calcule_Ts_Ps_As_fixant_Ps_Ts_S(Ps,Ts)
    S,RNV,REV = retraites.calcule_S_RNV_REV(Ts,Ps,As)
        
    graphiques(Ts,Ps,As, S,RNV,REV)
    mysavefig("macron_point_indexe")
    
    print("Maintien du rapport pension moyenne / salaire moyen")
    affiche_solutions_simulateur_COR(Ts,Ps,As)

    


############################################################################
# génération des figures pour les articles mediapart

def pour_article_2():

    print("Données et figure pour article 2")
    
    Ts,Ps,As = retraites.calcule_Ts_Ps_As_fixant_Ts_RNV_S(0)
    S,RNV,REV = retraites.calcule_S_RNV_REV(Ts,Ps,As)
        
    pl.figure(figsize=(9,6))
    graphique(As,"A",14,[],True,range(1,5))
    pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
    pl.legend(loc="best")
    mysavefig("macron_68_ans")

    pl.figure(figsize=(9,6))
    graphique(As,"A",14,[],True)
    pl.suptitle(u"Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)",fontsize=14)
    pl.legend(loc="best")
    mysavefig("macron_68_ans_tout")
    
    print("Réforme Macron, Maintien du niveau de vie")
    affiche_solutions_simulateur_COR(Ts,Ps,As)



def pour_article_3():

    print("Données et figures pour article 3")
    
    Ts,Ps,As = retraites.calcule_Ts_Ps_As_fixant_As_Ts_S(62) 
    S,RNV,REV = retraites.calcule_S_RNV_REV(Ts,Ps,As)

    titre=u"Modèle du COR: Réforme Macron (éq. financier & départ à 62 ans)"
    
    pl.figure(figsize=(9,6))
    graphique(RNV,"RNV",14,[],True,range(1,5))
    pl.suptitle(titre,fontsize=14)
    pl.legend(loc="best")
    mysavefig("macron_62_ans_nv")
    
    pl.figure(figsize=(9,6))
    graphique(Ps,"P",14,[],True,range(1,5))
    pl.suptitle(titre,fontsize=14)
    pl.legend(loc="best")
    mysavefig("macron_62_ans_p")
    
    print("Réforme Macron, Départ à 62 ans")
    affiche_solutions_simulateur_COR(Ts,Ps,As)
    print("\nEvolution du niveau de vie:")
    affiche_variable(RNV)
    print("\nEvolution du ratio pension/salaire:")
    affiche_variable(Ps)
    
#####################

#simu0()
#simu1()
#simu2()
#simu3()
#simu4(0,0.311)

#pour_article_2()
#pour_article_3()

simu2(62.0,-0.01)

pl.show()
