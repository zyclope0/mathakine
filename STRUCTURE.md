# Structure du Projet Mathakine

Ce document clarifie la structure du projet Mathakine (anciennement Math Trainer) pour éviter toute confusion lors du développement.

## Nom du Projet

- **Nom original** : Math Trainer
- **Nom actuel** : Mathakine (avec thématique Star Wars)

## Organisation des Répertoires

```
/
├── math-trainer-backend/    # Répertoire principal du projet
│   ├── app/                # Code de l'application
│   ├── docs/               # Documentation détaillée
│   │   ├── IMPLEMENTATION_PLAN.md
│   │   ├── PROJECT_STATUS.md
│   │   └── LOGIC_CHALLENGES_REQUIREMENTS.md
│   ├── tests/              # Tests organisés par catégorie
│   │   ├── unit/          # Tests unitaires
│   │   ├── integration/   # Tests d'intégration
│   │   ├── api/           # Tests API
│   │   ├── functional/    # Tests fonctionnels
│   │   ├── README.md      # Documentation des tests
│   │   └── TEST_PLAN.md   # Plan de test détaillé
│   ├── scripts/            # Scripts utilitaires
│   ├── static/             # Fichiers statiques (CSS, JS)
│   ├── templates/          # Templates HTML
│   └── README.md           # Documentation principale
└── app/                    # Code de l'application front-end (si applicable)
```

## Points Importants

1. **Répertoire Principal** : Tout le code source et la documentation se trouvent dans le dossier `math-trainer-backend`, malgré le changement de nom du projet en "Mathakine".

2. **Terminologie Star Wars** : Bien que le nom du dossier reste `math-trainer-backend`, le projet utilise désormais la terminologie Star Wars dans tout le code et la documentation :
   - **Padawan** : Utilisateur apprenant
   - **Maître** : Enseignant
   - **Gardien** : Parent/Tuteur
   - **Archiviste** : Administrateur
   - **API Rebelle** : L'API REST Mathakine
   - **Épreuves du Conseil Jedi** : Défis logiques

3. **Tests** : Les tests se trouvent dans le répertoire `math-trainer-backend/tests/` et sont organisés en quatre catégories.

4. **Documentation** : La documentation détaillée se trouve dans `math-trainer-backend/docs/`.

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