# Simulateur macroscopique du système de retraites

Le COR (conseil d'orientation des retraites) a mis en ligne un simulateur pour permettre aux citoyens de simuler les effets macroscopiques des grandes lignes d'une réforme des retraites.
Ce projet vise a reproduire les résultats et à ajouter un certain nombre de fonctionnalités utiles, comme celui de proposer de concevoir une réforme à prestation définie (ex: calcul automatique des cotisations sociales pour avoir un système équilibré financièrement avec un certain niveau de vie pour les retraités et un age de départ fixé a priori).

On utilise les [données de projection du COR](https://www.cor-retraites.fr/simulateur/fileProjection.json) et on se base sur la [documentation technique fournie par le COR](https://www.cor-retraites.fr/simulateur/img/pdf/Documentation_technique_vf.pdf).

Les calculs sont faits dans le fichier [retraites.py](https://github.com/brunoscherrer/retraites/blob/master/retraites.py).

Le script [demo.py](https://github.com/brunoscherrer/retraites/blob/master/demo.py) est un script qui utilise [retraites.py](https://github.com/brunoscherrer/retraites/blob/master/retraites.py) pour générer un certain nombre de figures, qu'on trouve dans le répertoire [fig](https://github.com/brunoscherrer/retraites/blob/master/retraites.py).

---

## Exemples de simulations

Ci-dessous, nous suivons une suggestion de Michaël Zemmour (Université de Lille) faite lors d'une [intervention d'une vingtaine de minutes](https://www.youtube.com/watch?v=f0EZ9KJmeLA&t=346s), c'est-à-dire d'expérimenter dans le même cadre macro-éconmique que le COR. 

On peut utiliser le code pour reproduire exactement les prévisions macroscopiques du simulateur du COR avec notamment les valeurs par défaut (celles d'un statu quo du système).
Cela permet de plus de calculer automatiquement les effets macroscopiques de réformes dont les cotisations seraient ajustées de sorte à équilibrer la situation financière du système. Ci-dessous, voici les prévisions du COR (sans aucune intervention) et deux exemples qui ont en commun de fixer comme objectif un niveau de vie des retraités égal à celui des actifs, le premier gardant les projections du COR en termes de départ à la retraite, le deuxième fixant un départ effectif à 61 ans. Les différentes courbes de couleurs à partir de 2020 correspondent aux différents scenarios conjoncturels (croissance/chômage) considérés par le COR à horizon 2070.

### Simulation 1: Projections du COR avec le réglage initial

![Projections du COR](./fig/cor.jpg) 

Dans cette première simulation, on observe une baisse légère des cotisations jusque 2070. Le système est globalement (en moyenne sur les différents scénarios conjoncturels) équilibré financièrement. Cet équilibre est possible via la baisse des pensions, de 0.5 fois le salaire moyen (2019) à une fourchette [0.25, 0.45] fois le salaire moyen selon la conjoncture. Le niveau de vie des retraités pourrait en être fortement affecté (jusqu'à une baisse de 30% dans le pire cas).

### Simulation 2: Adaptation automatique des cotisations

![Projection 1](./fig/cotisations.jpg)

On voit qu'il suffit de prévoir une hausse légère de cotisations, précisément de 31% (aujourd'hui) à 35% (en 2070), c'est-à-dire en moyene +0.25% par an (vu que 1.0025^(2070-2020)=35/31) alors on peut dans le pire scenario assurer un niveau de vie aux retraités équivalent à celui des actifs et le système est équilibré.

### Simulation 3: Adaptation automatique des cotisations avec départ à 61 ans

![Projection 2](./fig/61ans.jpg)

Dans la troisième figure "Départ à 61 ans et cotisations adaptées", on peut mesurer ce que coûterait collectivement le fait de permettre aux français de partir (effectivement) à la retraite à 61 ans (ce qui correspond à une hypothèse d'un départ possible à 60%). Il faudrait alors porter l'effort de cotisations de 31% à 39% dans le pire cas conjoncturel, soit une augmentation moyenne par an de +0.46% des cotisations.


## Hypothèses macroéconomiques du COR

Les projections ci-dessus sont basées sur celles d'un certain nombre d'indicateurs macroscopiques fournis par le COR (voir la [documentation technique fournie par le COR](https://www.cor-retraites.fr/simulateur/img/pdf/Documentation_technique_vf.pdf) pour plus de détails), par exemple sur le fait qu'en 2070, un retraité moyen qui aurait une pension d'environ la moitié du salarié moyen aurait sensiblement le même niveau de vie.

![conjoncture](./fig/conjoncture.jpg)
