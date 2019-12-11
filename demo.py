#!/usr/bin/python
# coding:utf-8


from pylab import *
from retraites import *

### fonctions pour tracer des graphiques

def graphique(v,t,rg=[]):
    y=[ v[a] for a in annees ]
    title(t,fontsize=8)
    if rg!=[]:
        ylim(bottom=rg[0],top=rg[1])
    plot(annees,y)
    
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
    

### Partie principale

# génération des graphes sur la conjoncture
figure(figsize=(10,8))
suptitle("Conjoncture",fontsize=15)
for sc in range(1,7):
    (B,NR,NC,G,dP,TPR,TPS,CNV)=(get2('B',sc),get2('NR',sc),get2('NC',sc),get2('G',sc),get2('dP',sc),get2('TCR',sc),get2('TCS',sc),get2('CNV',sc))
    c=1
    for (v,t) in [(B,"B:Part des revenus d activite bruts dans le PIB"),
                  (NR,"NR:Nombre de retraites"),
                  (NC,"NC:Nombre de cotisants"),
                  (G,"G:Effectif d une generation arrivant a l age de la retraite"),
                  (dP,"dP:Autres depenses de retraites"),
                  (TPR,"TPR:Taux de prelevement sur les retraites"),
                  (TPS,"TPS:Taux de prelevement sur les salaires"),
                  (CNV,"CNV:(niveau de vie)/(pension/salaire)")
    ]:
        subplot(3,3,c)
        graphique(v,t)
        c+=1
    EV=[ get('EV',sc,a) for a in range(1930,2011) ]
    subplot(3,3,9)
    title("Esperance de vie a 60 ans",fontsize=8)
    plot(range(1930,2011),EV)
tight_layout(rect=[0, 0.03, 1, 0.95])
savefig("conjoncture.jpg")

# génération des graphes pour des réformes à prestation garantie
for d in [61,0]:
    figure(figsize=(6,8))
    if d!=0:
        suptitle('Depart a %d ans et cotisations adaptees'%(d),fontsize=15)
    else:
        suptitle('Cotisations adaptees',fontsize=15)
    for sc in range(1,7):
        T,P,A = reforme(sc,d)
        S,RNV,REV = simule(T,P,A,sc)
        graphiques(T,P,A,S,RNV,REV, get2('B',sc))
    tight_layout(rect=[0, 0.03, 1, 0.95])
    if d!=0:
        savefig("%dans.jpg"%(d))
    else:
        savefig("cotisations.jpg")

# génération des graphes pour le statu quo (COR)
figure(figsize=(6,8))
suptitle('Projection COR',fontsize=15)
for sc in range(1,7):
    T,P,A = recupere_TPA(sc)
    S,RNV,REV = simule(T,P,A,sc)
    graphiques(T,P,A,S,RNV,REV, get2('B',sc))
tight_layout(rect=[0, 0.03, 1, 0.95])
savefig("cor.jpg")
    
show()
