# Buanderie Reservation

Cette application permet de gérer la réservation en ligne des machines d'une buanderie. Elle est écrite en Python avec le microframework Flask. Une version en ligne est disponible à l'adresse [https://soury.pythonanywhere.com](https://soury.pythonanywhere.com/).

- [English version](README.en.md)
- [النسخة العربية](README.ar.md)

## Sommaire
- [Installation](#installation)
- [Lancement en local](#lancement-en-local)
- [Configuration](#configuration)
- [Gestion des données](#gestion-des-données)
- [Guide utilisateur](#guide-utilisateur)
- [Déploiement sur PythonAnywhere](#déploiement-sur-pythonanywhere)
- [Tests](#tests)
- [Contribuer](#contribuer)
- [Licence](#licence)

## Installation

Assurez-vous de disposer de **Python 3** et de l'outil `git` sur votre
ordinateur.

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

Ce fichier se situe sur le serveur hébergeant l'application (comme sur
[PythonAnywhere](https://www.pythonanywhere.com/)). Toutes les personnes
consultant le site partagent donc le même fichier : lorsqu'une réservation est
ajoutée ou supprimée, la modification est visible par tous les utilisateurs.

## Guide utilisateur

### Réaliser une réservation

1. Choisissez votre **chambre**.
2. Sélectionnez la **date** et l'**heure** de début.
3. Indiquez la **machine** désirée.
4. Précisez le **nombre de tournées** (1 à 3).
5. Entrez un **code à 4 chiffres** puis validez.

Règles :
- le code doit comporter exactement quatre chiffres ;
- une machine ne peut dépasser **3 tournées par jour** ;
- le créneau doit se terminer **avant 23h**.

### Annuler une réservation

Cliquez sur la réservation dans le calendrier puis saisissez le même code pour confirmer la suppression.

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

PythonAnywhere exécute l'application via **Gunicorn**. Le fichier `Procfile`
fourni lance la commande suivante :

```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-8080}
```

Le port est géré automatiquement par la plateforme. Vous pouvez utiliser la même
commande pour tester localement ou sur tout autre hébergeur compatible.

## Tests

Une suite de tests unitaires est fournie pour vérifier les principales routes de l'application. Après installation des dépendances, lancez simplement :

```bash
pytest
```

## Contribuer

Les contributions sont les bienvenues ! Ouvrez une issue pour discuter d'un changement ou proposez directement une pull request. Veillez à faire tourner `pytest` avant toute soumission.

---

Ce projet est distribué sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.


