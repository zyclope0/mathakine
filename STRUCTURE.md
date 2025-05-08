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
│   ├── validation/     # Documentation du système d'auto-validation
│   └── ...             # Autres documents spécifiques
├── scripts/            # Scripts utilitaires (installation, serveur, config, etc.)
├── static/             # Fichiers statiques (CSS, JS)
├── templates/          # Templates HTML
├── tests/              # Tests et validation
│   ├── unit/           # Tests unitaires
│   ├── api/            # Tests API
│   ├── integration/    # Tests d'intégration
│   ├── functional/     # Tests fonctionnels
│   ├── auto_validation.py    # Script principal d'auto-validation
│   ├── simple_validation.py  # Validation sans dépendances complexes
│   ├── compatibility_check.py # Vérification de compatibilité
│   ├── setup_validation.py   # Configuration de l'environnement de validation
│   └── ...             # Autres scripts de test et validation
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
3. **Tests et Validation** : 
   - Les tests se trouvent dans le répertoire `tests/` et sont organisés en quatre catégories (unitaires, API, intégration, fonctionnels).
   - Le système d'**auto-validation** permet de vérifier l'intégrité et la compatibilité du projet avec différents scripts adaptés à divers besoins.
4. **Documentation** : 
   - La documentation détaillée se trouve dans `docs/`.
   - La documentation du système d'auto-validation se trouve dans `docs/validation/`.

## Système d'Auto-Validation

Le projet intègre un système complet d'auto-validation avec différents niveaux de vérification :

1. **Validation complète** : Exécute tous les tests et vérifie la syntaxe Python (`auto_validation.py`).
2. **Validation légère** : Vérifie la structure du projet sans dépendances complexes (`simple_validation.py`, `simplified_validation.py`).
3. **Vérification de compatibilité** : Vérifie la compatibilité avec Python 3.13 (`compatibility_check.py`).
4. **Rapports** : Génère des rapports détaillés sur l'état du projet (`generate_report.py`).

Voir `docs/validation/README.md` pour plus de détails sur le système d'auto-validation.

## Évolution Future

Si le projet doit être restructuré à l'avenir, il est recommandé de :
1. Renommer le dossier principal en `mathakine` pour refléter le nouveau nom du projet
2. Mettre à jour toutes les références et chemins dans le code et la documentation
3. Mettre à jour ce document STRUCTURE.md pour refléter les changements

## Documentation Principale

- **README.md** : Documentation principale du projet
- **tests/README.md** : Documentation des tests
- **tests/TEST_PLAN.md** : Plan de test détaillé
- **docs/validation/README.md** : Documentation du système d'auto-validation
- **docs/** : Documentation détaillée sur divers aspects du projet 