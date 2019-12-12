#!/usr/bin/python
# coding:utf-8

from pylab import *
from retraites import *

### fonctions pour tracer des graphiques

def graphique(v,t,rg=[],an=annees):
    for s in scenarios:
        plot(an, [ v[s][a] for a in an ])
    title(t,fontsize=8)
    if rg!=[]:
        ylim(bottom=rg[0],top=rg[1])
    
def graphiques(T, P, A, S, RNV, REV, B):
    subplot(3,2,1)
    graphique(S,"Situation financiere du systeme de retraites",[-0.02,0.02] )
    subplot(3,2,2)
    graphique(RNV,"Niveau de vie relatif des retraites", [0.6,1.1])
    subplot(3,2,3)
    graphique(REV,"Proportion de la vie passee a la retraite", [0.28,0.4])
    subplot(3,2,4)
    graphique(T,"Taux de cotisation de retraite", [0.25,0.4] )
    subplot(3,2,5)
    graphique(A,"Age de depart effectif a la retraite", [60,65])
    subplot(3,2,6)
    graphique(P,"Pension moyenne / salaire moyen", [.25,.55] )

    
##############################################################################


# génération des graphes pour le statu quo (COR)

def simu0():

    figure(figsize=(6,8))
    suptitle('Projection COR',fontsize=15)
    
    T,P,A = get('T'), get('P'), get('A')
    S,RNV,REV = calcule_S_RNV_REV(T,P,A)

    graphiques(T,P,A, S,RNV,REV, get('B'))

    tight_layout(rect=[0, 0.03, 1, 0.95])
    savefig("cor.jpg")


# génération des graphes sur la conjoncture

def simu1():

    B,NR,NC,G,dP,TPR,TPS,CNV,EV=get('B'),get('NR'),get('NC'),get('G'),get('dP'),get('TCR'),get('TCS'),get('CNV'),get('EV')
    
    figure(figsize=(10,8))
    suptitle("Conjoncture",fontsize=15)
    subplot(3,3,1)
    graphique(B,"B:Part des revenus d activite bruts dans le PIB")
    subplot(3,3,2)
    graphique(NR,"NR:Nombre de retraites")
    subplot(3,3,3)
    graphique(NC,"NC:Nombre de cotisants")
    subplot(3,3,4)
    graphique(G,"G:Effectif d une generation arrivant a l age de la retraite")
    subplot(3,3,5)
    graphique(dP,"dP:Autres depenses de retraites")
    subplot(3,3,6)
    graphique(TPR,"TPR:Taux de prelevement sur les retraites")
    subplot(3,3,7)
    graphique(TPS,"TPS:Taux de prelevement sur les salaires")
    subplot(3,3,8)
    graphique(CNV,"CNV:(niveau de vie)/(pension/salaire)")        
    subplot(3,3,9)
    graphique(EV, "Esperance de vie a 60 ans",[],annees_EV)
    
    tight_layout(rect=[0, 0.03, 1, 0.95])
    savefig("conjoncture.jpg")

    
# génération des graphes pour des réformes à prestation garantie

def simu2(ages=[61,0]):
    
    for d in ages:

        figure(figsize=(6,8))
        if d!=0:
            suptitle('Depart a %d ans et cotisations adaptees'%(d),fontsize=15)
        else:
            suptitle('Cotisations adaptees',fontsize=15)
                
        T,P,A = calcule_T_P_A(d)
        S,RNV,REV = calcule_S_RNV_REV(T,P,A)
        
        graphiques(T,P,A, S,RNV,REV, get('B'))
        
        tight_layout(rect=[0, 0.03, 1, 0.95])
        if d!=0:
            savefig("%dans.jpg"%(d))
        else:
            savefig("cotisations.jpg")


simu0()
simu1()
simu2()
show()
