# Simulateur macroscopique du système de retraites

Le COR (conseil d'orientation des retraites) a mis en ligne un simulateur pour permettre aux citoyens de simuler les effets macroscopiques des grandes lignes d'une réforme des retraites.
Ce projet vise a reproduire les résultats et à ajouter un certain nombre de fonctionnalités utiles, comme celui de proposer de concevoir une réforme à prestation définie (ex: calcul automatique des cotisations sociales pour avoir un système équilibré financièrement avec un certain niveau de vie pour les retraités et un age de départ fixé a priori).

On utilise les [données de projection du COR](https://www.cor-retraites.fr/simulateur/fileProjection.json) et on se base sur la [documentation technique fournie par le COR](https://www.cor-retraites.fr/simulateur/img/pdf/Documentation_technique_vf.pdf).

Les calculs sont faits dans le fichier retraites.py.

Le fichier demo.py est un script qui utilise retraites.py pour générer un certain nombre de figures, qu'on trouve dans le répertoire fig.
