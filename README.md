# Buanderie Reservation

Cette application permet de gérer la réservation en ligne des machines d'une buanderie. Elle est écrite en Python avec le microframework Flask. Une version en ligne est disponible à l'adresse [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [English version](README.en.md)
- [النسخة العربية](README.ar.md)

## Sommaire
- [Installation](#installation)
- [Lancement en local](#lancement-en-local)
- [Configuration](#configuration)
- [Gestion des données](#gestion-des-données)
- [Déploiement sur PythonAnywhere](#déploiement-sur-pythonanywhere)
- [Tests](#tests)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Installation

1. Téléchargez ou clonez ce dépôt sur votre machine.
2. *(Optionnel)* créez un environnement virtuel :

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Lors de la première installation, créez un fichier `reservations.json` vide à la racine du projet :

   ```bash
   echo "[]" > reservations.json
   ```

## Lancement en local

Exécutez directement le fichier `app.py` pour lancer le serveur local :

```bash
python app.py
```

L'application sera alors disponible sur [http://localhost:5000](http://localhost:5000).

## Configuration

Deux variables d'environnement permettent d'ajuster le comportement de l'application :

- `RESERVATIONS_FILE` : chemin vers le fichier JSON utilisé pour stocker les réservations. Par défaut, `reservations.json` est employé à la racine du projet.
- `ADMIN_CODE` : code secret donnant l'autorisation de supprimer n'importe quelle réservation. Sa valeur par défaut est `s00r1`.

## Gestion des données

Toutes les réservations sont enregistrées dans le fichier désigné par `RESERVATIONS_FILE`. Pour repartir d'une base vide, créez simplement ce fichier avec le contenu suivant :

```json
[]
```

L'application verrouille automatiquement ce fichier pour éviter les accès concurrents.

## Déploiement sur PythonAnywhere

1. Créez un compte sur [pythonanywhere.com](https://www.pythonanywhere.com/) et ouvrez une console Bash.
2. Chargez le projet (par `git clone` ou par téléversement) puis placez-vous dans le dossier :

   ```bash
   git clone https://github.com/votre-utilisateur/buanderie-reservation.git
   cd buanderie-reservation
   ```

3. Créez un environnement virtuel et installez les dépendances :

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Dans l'onglet **Web**, créez une nouvelle application *Manual configuration* et indiquez le chemin vers ce dépôt.
5. Éditez le fichier WSGI pour exposer l'application :

   ```python
   import sys
   sys.path.insert(0, '/home/<user>/buanderie-reservation')
   from app import app as application
   ```

6. Définissez les variables `RESERVATIONS_FILE` et `ADMIN_CODE` dans la section *Environment Variables* (ex :`RESERVATIONS_FILE=/home/<user>/buanderie-reservation/reservations.json`).
7. Cliquez sur **Reload** pour démarrer l'application.

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

---

Ce projet est distribué sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.


