#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe de gestion d'une analyse d'un système de retraites.
"""
import pylab as pl
import os

class SimulateurAnalyse:
    def __init__(self, T, P, A, S, RNV, REV, Depenses, \
                 PIB, PensionBrut, \
                 scenarios, annees_EV, annees, annees_standard, \
                 scenarios_labels, scenarios_labels_courts, \
                 dir_image, ext_image):
        """
        Crée une analyse de simulateur de retraites.
        
        Paramètres :
            T: un dictionnaire, niveau des cotisations sociales
            P: un dictionnaire, niveau des pensions par rapport aux salaires
            A: un dictionnaire, âge moyen de départ à la retraite
            S: un dictionnaire, Situation financière du système de retraite en \% du PIB
            RNV: un dictionnaire, Niveau de vie des retraités par rapport à l'ensemble de la population
            REV: un dictionnaire, Durée de la vie passée à la retraite
            Depenses: un dictionnaire, Dépenses de retraites en % PIB
            PIB : le montant absolu du PIB (Milliard EUR)
            PensionBrut : la pension annuelle (brut) de droit direct moyenne (kEUR) 
            scenarios: une liste d'indices, les scénarios considérés
            annees_EV: une liste d'entiers, annees sur lesquelles on a l'espérance de vie
            annees: une liste d'entiers supérieurs ou égaux à 1, les scenarios consideres
            annees_standard: une liste d'entiers supérieurs ou égaux à 1, les années futures standard
            scenarios_labels : une liste de chaîne de caractères, les étiquettes 
                des scénarios économiques
            scenarios_labels_courts : une liste de chaîne de caractères, les étiquettes 
                courtes des scénarios économiques
            dir_image : le répertoire de sauvegarde des images
            ext_image : la liste des formats de sauvegarde des images
            
        Attributs :
            scenarios :
                Une liste d'entiers.
                la liste des scénarios considérés. 
                Ces scénarios sont des indices dans les tables de scénarios de 
                chomage, de croissance ainsi que les labels. 

            annees_EV :
                Une liste d'entiers.
                La liste des années de naissance pour lesquelles on a l'espérance de vie. 
    
            annees : 
                Une liste d'entiers.
                La liste des années sur lesquelles on fait les calculs. 
                Chaque année de cette liste est inférieure à l'année de l'horizon.
    
            annees_standard :
                Une liste d'entiers.
                La liste d'une sélection des années futures standard dans les calculs simplifiés. 
    
            T : 
                Un dictionnaire représentant une trajectoire. 
                Le taux de cotisations retraites.
            
            P : 
                Un dictionnaire représentant une trajectoire. 
                Le niveau moyen brut des pensions par rapport au 
                niveau moyen brut des salaires.
            
            A : 
                Un dictionnaire représentant une trajectoire. 
                L'âge effectif moyen de départ en retraite.
            
            S : 
                Un dictionnaire représentant une trajectoire. 
                Le solde financier du système de retraites en part de PIB. 

            RNV :
                Un dictionnaire représentant une trajectoire. 
                Niveau de vie des retraités par rapport à l'ensemble de la population. 

            REV :
                Un dictionnaire représentant une trajectoire. 
                Durée de la vie passée à la retraite.

            Depenses : 
                Un dictionnaire représentant une trajectoire. 
                Le montant des dépenses de retraites en part de PIB. 

            PIB : 
                Un dictionnaire représentant une trajectoire. 
                Le produit intérieur brut. 

            PensionBrut : 
                Un dictionnaire représentant une trajectoire. 
                Le montant annuel moyen brut de pension de droit direct. 
    
            scenarios_labels :
                La liste de chaîne de caractère décrivant les 
                scénarios pour chaque scénario 
                de la liste retournée par getScenarios().
    
            scenarios_labels_courts :
                La liste de chaîne de caractère courtes décrivant les 
                scénarios pour chaque scénario 
                de la liste retournée par getScenarios().

            labels_is_long :
                Un booléen. 
                True, si on utilise les labels longs dans les graphiques
        
            dir_image :
                Une chaîne de caractère. 
                Le répertoire de sauvegarde des images. 
                Par défaut, la chaîne de caractère vide. 

            ext_image :
                Une liste de chaînes de caractères. 
                Les types de fichier à générer par la méthode sauveFigure. 
                
            affiche_quand_ecrit :
                Un booléen.
                Si True, alors affiche un message quand la méthode sauveFigure 
                écrit un fichier.
        
            yaxis_lim :
                Un dictionnaire. 
                Les plages min et max pour l'axe des ordonnées 
                des variables en sortie de l'analyse. 
        

            liste_variables :
                Une liste de chaînes de caractère. 
                La liste des variables de l'analyse. 
                
            liste_legendes :
                Une liste de chaînes de caractère. 
                La liste des légendes des variables de l'analyse. 
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.dessineSimulation()
        """
        self.scenarios = scenarios
        self.annees_EV = annees_EV
        self.annees = annees
        
        # Liste des années dans le simulateur du COR
        self.annees_standard = annees_standard

        # initialisations diverses
        # chargement des donnees du COR pour les 6 scenarios
        
        self.T = T
        self.P = P
        self.A = A
        self.S = S
        self.RNV = RNV
        self.REV = REV
        self.Depenses = Depenses
        self.PIB = PIB
        self.PensionBrut = PensionBrut

        # Graphiques
        self.scenarios_labels = scenarios_labels
        self.scenarios_labels_courts = scenarios_labels_courts

        self.labels_is_long = True # True, si on utilise les labels longs
        
        self.dir_image = dir_image # répertoire pour les images

        self.ext_image = ext_image   # types de fichier à générer
        
        # Configure les plages min et max pour l'axe des ordonnées 
        # des variables standard en sortie du simulateur
        self.yaxis_lim = dict()
        self.yaxis_lim["S"] = [-2.0,2.0]
        self.yaxis_lim["RNV"] = [60.0,120.0]
        self.yaxis_lim["REV"] = [20.0,40.0]
        self.yaxis_lim["T"] = [25.0,40.0]
        self.yaxis_lim["A"] = [60,72]
        self.yaxis_lim["P"] = [25.0,55.0]
        self.yaxis_lim["Depenses"] = [11.0,15.0]

        self.affiche_quand_ecrit = True # Affiche un message quand on écrit un fichier
        
        self.liste_variables = ["S","RNV","REV","T","A","P","Depenses", "PIB", "PensionBrut"]
        self.liste_legendes=[u"Situation financière du système (% PIB)",
           u"Niveau de vie des retraités p/r à l'ensemble (%)",
           u"Proportion de la vie passée à la retraite (%)",
           u"Taux de cotisation de retraite (% PIB)",
           u"Age de départ effectif moyen à la retraite",
           u"Ratio (pension moyenne)/(salaire moyen) (%)",
           u"Dépenses de retraites (% PIB)", 
           u"Produit Intérieur Brut (Milliards EUR)", 
           u"Pension annuelle (brut) de droit direct (kEUR)"
        ]
        return None

    def setAfficheMessageEcriture(self, affiche_quand_ecrit):
        """
        Configure l'affichage d'un message quand on écrit un fichier
        
        Paramètres
            affiche_quand_ecrit : un booléen (par défaut = True)
        
        Exemple
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.setAfficheMessageEcriture(False)
        """
        self.affiche_quand_ecrit = affiche_quand_ecrit
        return None
    
    def setImageFormats(self, ext_image):
        """
        Configure le format de sauvegarde des images
        
        Paramètres
            ext_image : une liste de chaînes de caractères (par defaut, ext_image=["png","pdf"])
        
        Exemple
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.setImageFormats(["jpg"])
        """
        self.ext_image = ext_image
        return None

    def getImageFormats(self):
        """
        Retourne la liste des formats de sauvegarde des images.
        """
        return self.ext_image 

    
    def setLabelLongs(self, labels_is_long):
        """
        Configure la longueur des étiquettes
        
        Paramètres
            labels_is_long : un booléen, True si les labels longs sont utilisés (par défaut = True)
        
        Exemple
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.setLabelLongs(False)
        """
        self.labels_is_long = labels_is_long
        return None

    def getLabelLongs(self):
        """
        Retourne le booléen de longueur des étiquettes
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            labels_is_long = analyse.getLabelLongs()
        """
        return self.labels_is_long 

    def setDirectoryImage(self, dir_image):
        """
        Configure le répertoire contenant les images
        
        Paramètres :
            dir_image : une chaîne de caractères, le répertoire contenant les images 
            (par défaut, dir_image="fig")
            exportées par sauveFigure.
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.setDirectoryImage("/tmp")
        """
        self.dir_image = dir_image
        return None

    def getDirectoryImage(self):
        """
        Retourne le répertoire contenant les images
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            dir_image = analyse.getDirectoryImage()
        """
        return self.dir_image

    def sauveFigure(self, f):
        """
        Sauvegarde l'image dans le répertoire
        
        Paramètres:
            f : une chaîne de caractères, le nom des fichiers à sauver
        
        Description :
            Sauvegarde l'image dans les formats définis. 
        
        Exemple:
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.graphique("Depenses")
            analyse.sauveFigure("depenses")
        """
    
        for ext in self.ext_image:
            basefilename = f + "." + ext
            filename = os.path.join(self.dir_image,basefilename)
            if self.affiche_quand_ecrit:
                print("Ecriture du fichier %s" % (filename))
            pl.savefig(filename)
        return None
    
    def graphique(self, nom, v = None, taille_fonte_titre = 8, yaxis_lim = [], \
                  dessine_legende = False, scenarios_indices = None, 
                  dessine_annees = None):
        """
        Dessine un graphique associé à une variable donnée 
        pour tous les scénarios.
        
        Paramètres:
            nom : chaîne de caractère, nom de la variable
            v : variable à dessiner (par défaut, en fonction du nom)
            taille_fonte_titre : taille de la fonte du titre (par défaut, fs=8)
            yaxis_lim : une liste de taille 2, les bornes inférieures et supérieures 
            de l'axe des ordonnées
            dessine_legende : booleen, True si la légende doit être dessinée
            scenarios_indices : une liste d'entiers, la liste des indices des scénarios
            (par défaut, sc = range(1,7))
            dessine_annees : la liste des années à dessiner
        
        Description :
            Le nom peut être une égal à une des chaînes de caractères parmi 
            les chaînes suivantes : "T", "P", "A", "S", "RNV", "REV", 
            "Depenses", "PIB", "PensionBrut".
        
        Exemple:
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.graphique("RNV")
            analyse.graphique("RNV", dessine_legende = True, scenarios_indices = range(1,5))
            analyse.graphique("RNV", dessine_annees = range(2020,2041))
            analyse.graphique("RNV", taille_fonte_titre = 14)
            analyse.graphique("B", simulateur.B)
        """
        
        if v is None:
            if nom=="T":
                v = self.T
            elif nom=="P":
                v = self.P
            elif nom=="A":
                v = self.A
            elif nom=="S":
                v = self.S
            elif nom=="RNV":
                v = self.RNV
            elif nom=="REV":
                v = self.REV
            elif nom=="Depenses":
                v = self.Depenses
            elif nom=="PIB":
                v = self.PIB
            elif nom=="PensionBrut":
                v = self.PensionBrut
            else:
                raise TypeError('Mauvaise valeur pour le nom : %s' % (nom))

        if scenarios_indices==None:
            scenarios_indices = self.scenarios
        
        if dessine_annees is not None:
            list_annees_dessin = dessine_annees
        else:
            if nom=="EV":
                list_annees_dessin=self.annees_EV
            else:
                list_annees_dessin=self.annees
    
        for s in scenarios_indices:
            if (nom=="S" or nom=="RNV" or nom=="T" or nom=="P" \
                or nom=="REV" or nom=="Depenses"):
                # Ce sont des % : multiplie par 100.0
                y = [ 100.0 * v[s][a] for a in list_annees_dessin ]
            else:
                y = [ v[s][a] for a in list_annees_dessin ]
            if (self.labels_is_long):
                label_variable = self.scenarios_labels[s]
            else:
                label_variable = self.scenarios_labels_courts[s]
            pl.plot(list_annees_dessin, y, label=label_variable )
    
        # titres des figures
        indice_variable = self.liste_variables.index(nom)
        titre_figure = self.liste_legendes[ indice_variable ]
           
        pl.title(titre_figure,fontsize=taille_fonte_titre)
        
        # Ajuste les limites de l'axe des ordonnées
        if yaxis_lim==[]:
            # If the use did not set the yaxis_lim
            if nom in self.yaxis_lim.keys():
                # If the variable name was found in the dictionnary
                yaxis_lim = self.yaxis_lim[nom]

        if yaxis_lim!=[]:
            pl.ylim(bottom=yaxis_lim[0],top=yaxis_lim[1])

        if dessine_legende:
            pl.legend(loc="best")
        return None
    
    def dessineSimulation(self, taille_fonte_titre=8):
        """
        Dessine les 9 graphiques "standards" 
        de la conjoncture pour tous les scénarios.
        
        Paramètres:
            taille_fonte_titre : taille de la fonte (par défaut, fs=8)
        
        Description :
            Dessine S, RNV, REV, T, A, P. 
        
        Exemple:
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.dessineSimulation()
            analyse.dessineSimulation(taille_fonte_titre = 4)
        """
    
        for i in range(6):
            pl.subplot(3,2,i+1)
            nom= self.liste_variables[ i ]
            self.graphique(nom, taille_fonte_titre = taille_fonte_titre)
        pl.tight_layout(rect=[0, 0.03, 1, 0.95])
        return None
    
    def afficheVariable(self, v):
        """
        Affiche les valeurs d'une variable. 
        
        Paramètres :
            v : un dictionnaire, une trajectoire d'une des variables
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.afficheVariable(analyse.RNV)
        """
    
        for s in self.scenarios:
            print("Scenario",s,": ",self.scenarios_labels[s])
            for a in self.annees_standard:
                print("%d : %.3f"%(a, v[s][a]))
            print("")
        return None
            
    def afficheSolutionsSimulateurCOR(self):
        """
        Affiche les paramètres du simulateur. 
        
        Description :
            Les valeurs numériques affichées peuvent être utilisées 
            dans le simulateur du COR pour reproduire les simulations. 
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.afficheSolutionsSimulateurCOR()
        """
    
        print("Valeurs à rentrer sur le simulateur officiel du COR:")
        
        for s in self.scenarios:
            print("")
            print("Scenario",s,": ",self.scenarios_labels[s] )
            print("Annéee, Age,      Cotis., Pension:",)
            for a in self.annees_standard:
                print("%5d : %.1f ans, %.1f %%, %.1f %%"%(a, \
                                                         self.A[s][a], \
                                                         100*self.T[s][a], \
                                                         100*self.P[s][a]))
        return None
    
    def dessineLegende(self):
        """
        Crée un graphique présentant les légendes des graphiques.
        
        Exemple :
            simulateur = SimulateurRetraites()
            analyse = simulateur.pilotageCOR()
            analyse.dessineLegende()
        """
        # Juste les légendes
        pl.figure(figsize=(6,2))
        for s in self.scenarios:
            pl.plot(0., 0., label = self.scenarios_labels[s])
        pl.legend(loc="center")
        pl.ylim(bottom=0.0, top=0.7)
        pl.axis('off')
        return None
