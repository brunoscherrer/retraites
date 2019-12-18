#!/usr/bin/python
# coding:utf-8

from pylab import *
from retraites import *

ext_image=".jpg"

scenarios_labels=["Hausse des salaires: +1,8%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,5%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,3%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1%/an, Taux de chômage: 7%",
                  "Hausse des salaires: +1,8%/an, Taux de chômage: 4.5%",
                  "Hausse des salaires: +1%/an, Taux de chômage: 10%"]

### fonctions pour tracer des graphiques

def graphique(v, nom, fs=8, rg=[], leg=False):

    if nom=="EV":
        an=annees_EV
    else:
        an=annees

    for s in scenarios:
        plot(an, [ v[s][a] for a in an ], label=scenarios_labels[s-1].decode("utf-8") )

    # titres des figures
    
    t=["Situation financière du système (part du PIB)",
       "Niveau de vie des retraités p/r aux actifs",
       "Proportion de la vie passée à la retraite",
       "Taux de cotisation de retraite (part du PIB)",
       "Age de départ effectif moyen à la retraite",
       "Ratio (pension moyenne)/(salaire moyen)",
       "B: Part des revenus d'activité bruts dans le PIB",
       "NR: Nombre de retraités",
       "NC: Nombre de cotisants",
       "G: Effectif d'une generation arrivant à l'âge de la retraite",
       "dP: Autres dépenses de retraites",
       "TPR: Taux de prélèvement sur les retraites",
       "TPS: Taux de prélèvement sur les salaires",
       "CNV: (niveau de vie)/[(pension moy))/(salaire moy)]",
       "EV: Espérance de vie à 60 ans"][ ["S","RNV","REV","T","A","P","B","NR","NC","G","dP","TPR","TPS","CNV","EV"].index(nom) ]
       
    title(t.decode("utf-8"),fontsize=fs)
    if rg!=[]:
        ylim(bottom=rg[0],top=rg[1])
    if leg:
        legend(loc="best")
    
def graphiques(T, P, A, S, RNV, REV, fs=8):

    subplot(3,2,1)
    graphique(S,"S",fs ,[-0.02,0.02])
    subplot(3,2,2)
    graphique(RNV,"RNV",fs, [0.6,1.2])
    subplot(3,2,3)
    graphique(REV,"REV",fs, [0.2,0.4])
    subplot(3,2,4)
    graphique(T,"T",fs, [0.25,0.4] )
    subplot(3,2,5)
    graphique(A,"A",fs, [60,70])
    subplot(3,2,6)
    graphique(P,"P",fs, [.25,.55] )
    tight_layout(rect=[0, 0.03, 1, 0.95])

    
##############################################################################

def affiche_solutions_simulateur_COR(Ts,Ps,As):

    print "Valeur à rentrer sur le simulateur officiel du COR:"
    
    ans=[2020, 2025, 2030, 2040, 2050, 2060, 2070]
    for s in scenarios:
        print
        print "Scenario",s,": ",scenarios_labels[s-1] 
        print "Age:        ",
        for a in ans:
            print "%.1f"%(As[s][a]),
        print
        print "Cotisation: ",
        for a in ans:
            print "%.1f"%(100*Ts[s][a]),
        print
        print "Pension:    ",
        for a in ans:
            print "%.1f"%(100*Ps[s][a]),
        print

    print

##############################################################################
# SIMULATION NUMERIQUES
    
# génération des graphes pour le statu quo (COR)

def simu0():

    figure(figsize=(6,8))
    suptitle('Projections du COR',fontsize=16)
    
    T,P,A = get('T'), get('P'), get('A')
    S,RNV,REV = calcule_S_RNV_REV(T,P,A)

    graphiques(T,P,A, S,RNV,REV)

    savefig("cor"+ext_image)


# génération des graphes sur la conjoncture

def simu1():

    B,NR,NC,G,dP,TPR,TPS,CNV,EV=get('B'),get('NR'),get('NC'),get('G'),get('dP'),get('TCR'),get('TCS'),get('CNV'),get('EV')
    
    figure(figsize=(10,8))
    suptitle("Projections du COR (hypothèses)".decode("utf-8"),fontsize=16)
    subplot(3,3,1)
    graphique(B,"B")
    subplot(3,3,2)
    graphique(NR,"NR")
    subplot(3,3,3)
    graphique(NC,"NC")
    subplot(3,3,4)
    graphique(G,"G")
    subplot(3,3,5)
    graphique(dP,"dP")
    subplot(3,3,6)
    graphique(TPR,"TPR")
    subplot(3,3,7)
    graphique(TPS,"TPS")
    subplot(3,3,8)
    graphique(CNV,"CNV")        
    subplot(3,3,9)
    graphique(EV, "EV")
    tight_layout(rect=[0, 0.03, 1, 0.95])
    
    savefig("conjoncture"+ext_image)

    
# génération des graphes pour des réformes à prestation garantie

def simu2(ages=[61,0]):
    
    for d in ages:

        figure(figsize=(6,8))
        if d!=0:
            suptitle( ("Cotisations adaptées (eq. financier, maintien du niveau de vie & départ à %d ans"%(d)).decode("utf-8"),fontsize=10)
        else:
            suptitle("Cotisations adaptées (équilibre financier & maintien du niveau de vie)".decode("utf-8"),fontsize=10)
                
        Ts,Ps,As = calcule_Ts_Ps_As_fixant_As_RNV_S(d)
        S,RNV,REV = calcule_S_RNV_REV(Ts,Ps,As)
        
        graphiques(Ts,Ps,As, S,RNV,REV)
        
        if d!=0:
            savefig( ("%dans"%(d))+ext_image)
        else:
            savefig("cotisations"+ext_image)

            
# génération des graphes pour la réforme Macron avec maintien du niveau de vie

def simu3(Ts=0):
    
    figure(figsize=(6,8))
    suptitle('Réforme Macron (équilibre financier & maintien du niveau de vie)'.decode("utf-8"),fontsize=12)
                
    Ts,Ps,As = calcule_Ts_Ps_As_fixant_Ts_RNV_S(Ts)
    S,RNV,REV = calcule_S_RNV_REV(Ts,Ps,As)
        
    graphiques(Ts,Ps,As, S,RNV,REV)
    
    print "Maintien du niveau de vie"
    affiche_solutions_simulateur_COR(Ts,Ps,As)
    
    #savefig("macron_niveau_de_vie"+ext_image)

        
# génération des graphes pour la réforme Macron avec point indexé sur le salaire moyen (rapport (pension moyenne/)(salaire moyen) constant égal à celui de 2020)

def simu4(Ps=0,Ts=0):

    figure(figsize=(6,8))
    suptitle('Réforme Macron (équilibre financier & ratio pension/salaire fixe)'.decode("utf-8"),fontsize=12)
                
    Ts,Ps,As = calcule_Ts_Ps_As_fixant_Ps_Ts_S(Ps,Ts)
    S,RNV,REV = calcule_S_RNV_REV(Ts,Ps,As)
        
    graphiques(Ts,Ps,As, S,RNV,REV)
    
    print "Maintien du rapport pension moyenne / salaire moyen"
    affiche_solutions_simulateur_COR(Ts,Ps,As)
    
    savefig("macron_point_indexe"+ext_image)


############################################################################
# génération des figures pour les articles mediapart

def figure_pour_article_2():
    
    Ts,Ps,As = calcule_Ts_Ps_As_fixant_Ts_RNV_S(0)
    S,RNV,REV = calcule_S_RNV_REV(Ts,Ps,As)
        
    figure(figsize=(9,6))
    graphique(As,"A",14,[],True)
    suptitle("Modèle du COR: Réforme Macron (éq. financier & niveau de vie maintenu)".decode("utf-8"),fontsize=14)
    legend(loc="best")

    savefig("macron_68_ans"+ext_image)

    print "Maintien du niveau de vie (article 2)"
    affiche_solutions_simulateur_COR(Ts,Ps,As)


#####################

    
simu0()
simu1()
simu2()
simu3()
simu4()

figure_pour_article_2()

show()
