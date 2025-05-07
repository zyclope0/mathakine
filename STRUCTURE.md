# Structure du Projet Mathakine

Ce document clarifie la structure du projet Mathakine (anciennement Math Trainer) pour éviter toute confusion lors du développement.

## Nom du Projet

- **Nom original** : Math Trainer
- **Nom actuel** : Mathakine (avec thématique Star Wars)

## Organisation des Répertoires

```
math-trainer-backend/
├── app/                # Code de l'application
├── docs/               # Documentation détaillée
├── scripts/            # Scripts utilitaires (installation, serveur, config, etc.)
├── static/             # Fichiers statiques (CSS, JS)
├── templates/          # Templates HTML
├── tests/              # Tests unitaires et d'intégration
├── Dockerfile          # Image Docker
├── Procfile            # Commande de démarrage Render
├── README.md           # Documentation principale
├── GETTING_STARTED.md  # Guide de démarrage
├── STRUCTURE.md        # Structure du projet
├── requirements.txt    # Dépendances Python
├── .gitignore          # Fichiers ignorés par Git
├── .dockerignore       # Fichiers ignorés par Docker
├── LICENSE             # Licence
├── sample.env          # Exemple de configuration d'environnement
└── math_trainer.db     # Base de données SQLite (dev)
```

## Points Importants

1. **Répertoire Principal** : Tout le code source et la documentation se trouvent dans le dossier `math-trainer-backend`.
2. **Terminologie Star Wars** : Le projet utilise la terminologie Star Wars dans tout le code et la documentation.
3. **Tests** : Les tests se trouvent dans le répertoire `tests/` et sont organisés en quatre catégories.
4. **Documentation** : La documentation détaillée se trouve dans `docs/`.

## Évolution Future

Si le projet doit être restructuré à l'avenir, il est recommandé de :
1. Renommer le dossier principal en `mathakine` pour refléter le nouveau nom du projet
2. Mettre à jour toutes les références et chemins dans le code et la documentation
3. Mettre à jour ce document STRUCTURE.md pour refléter les changements

## Documentation Principale

- **README.md** : Documentation principale du projet
- **tests/README.md** : Documentation des tests
- **tests/TEST_PLAN.md** : Plan de test détaillé
- **docs/** : Documentation détaillée sur divers aspects du projet 