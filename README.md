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

## Configuration

Le chemin du fichier stockant les réservations peut être personnalisé via la variable d'environnement `RESERVATIONS_FILE`.
Si elle n'est pas définie, l'application utilisera `reservations.json` par défaut.

La valeur du code administrateur peut également être ajustée grâce à la variable d'environnement `ADMIN_CODE`. Elle vaut `s0r1` si elle n'est pas spécifiée.

## Déploiement

Pour déployer sur une plateforme compatible avec les fichiers `Procfile` (comme Heroku), renommez `Procfile.txt` en `Procfile` si nécessaire puis poussez le dépôt. Le contenu du `Procfile` indique à la plateforme de démarrer l'application avec :

```procfile
web: gunicorn app:app
```

## Tests

Une suite de tests unitaires est fournie pour vérifier les principales routes de l'application. Après installation des dépendances, lancez simplement :

```bash
pytest
```


