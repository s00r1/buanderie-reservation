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

## Déploiement

Pour déployer sur une plateforme compatible avec les fichiers `Procfile` (comme Heroku), renommez `Procfile.txt` en `Procfile` si nécessaire puis poussez le dépôt. Le contenu du `Procfile` indique à la plateforme de démarrer l'application avec :

```procfile
web: python app.py
```


