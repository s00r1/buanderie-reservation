# Buanderie Reservation

Cette application permet de gérer la réservation en ligne des machines d'une buanderie. Elle est écrite en Python avec le microframework Flask.

## Installation

Assurez-vous d'avoir Python installé, puis installez les dépendances :

```bash
pip install -r requirements.txt
```

## Lancement en local

Exécutez directement le fichier `app.py` pour lancer le serveur local :

```bash
python app.py
```

L'application sera alors disponible sur [http://localhost:5000](http://localhost:5000).

## Variables de configuration

Deux variables d'environnement permettent d'ajuster le comportement de l'application :

- `RESERVATIONS_FILE` : chemin vers le fichier JSON utilisé pour stocker les réservations. Par défaut, `reservations.json` est employé à la racine du projet.
 - `ADMIN_CODE` : code secret donnant l'autorisation de supprimer n'importe quelle réservation. Sa valeur par défaut est `s00r1`.

## Exécution en production

Pour un environnement de production, il est recommandé d'utiliser Gunicorn et de lier l'application au port fourni par la plateforme. Cela permet un fonctionnement identique sur Fly.io, Railway ou tout autre hébergeur définissant la variable `PORT` :

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

Le `Procfile` inclus utilise cette commande afin de faciliter le déploiement sur différentes plateformes.

## Tests

Une suite de tests unitaires est fournie pour vérifier les principales routes de l'application. Après installation des dépendances, lancez simplement :

```bash
pytest
```

## Contribuer

Les contributions sont les bienvenues ! Ouvrez une issue pour discuter d'un changement ou proposez directement une pull request. Veillez à faire tourner `pytest` avant toute soumission.


