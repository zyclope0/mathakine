# Mathakine (anciennement Math Trainer)

## ⚠️ INFORMATION IMPORTANTE : RENOMMAGE DU PROJET ⚠️

**Ce dépôt est la nouvelle version du projet**. L'ancien projet "Math Trainer" a été renommé en "Mathakine" avec une organisation améliorée des tests et une meilleure cohérence du thème Star Wars.

### Structure actuelle du projet

Tous les fichiers ont été réorganisés dans cette nouvelle structure :
- **Code principal** : `/math-trainer-backend/`
- **Documentation principale** : `/math-trainer-backend/README.md`
- **Documentation des tests** : `/math-trainer-backend/tests/README.md`
- **Plan de test complet** : `/math-trainer-backend/tests/TEST_PLAN.md`
- **Documentation détaillée** : `/math-trainer-backend/docs/`

### Avantages de cette réorganisation

Cette restructuration a permis :
1. D'organiser les tests en 4 catégories distinctes (unitaires, API, intégration, fonctionnels)
2. D'intégrer plus profondément la thématique Star Wars dans le code et la documentation
3. De nettoyer les fichiers obsolètes et de clarifier la structure du projet
4. D'améliorer la maintenabilité et l'extensibilité du code

---

## Présentation

**Mathakine** est une application éducative backend pour un site d'entraînement mathématique interactif destiné aux enfants, spécialement adapté pour un enfant autiste de 9 ans, avec une thématique Star Wars.

Cette application permet un apprentissage des mathématiques adapté aux besoins spécifiques des enfants autistes. Elle aide les jeunes "Padawans des mathématiques" à maîtriser la "Force des nombres" à travers des exercices interactifs et personnalisés.

## Fonctionnalités

- Génération d'exercices mathématiques (addition, soustraction, multiplication, division)
- Interface adaptée aux enfants autistes avec thème Star Wars
- Différents niveaux de difficulté (Initié, Padawan, Chevalier, Maître)
- Mode adaptatif qui ajuste la difficulté selon les performances
- Tableau de bord pour suivre les progrès
- Génération d'exercices avec IA via l'API OpenAI
- Tests automatisés robustes
- Compatibilité avec Python 3.13
- Système de gestion des environnements (dev, test, prod)
- API REST complète
- Normalisation des données pour une meilleure cohérence et fiabilité
- Support de PostgreSQL pour les environnements de production
- Outils de migration et de gestion de base de données
- Déploiement facilité sur Render avec PostgreSQL

## Démarrage rapide

### Installation

```bash
# Menu principal d'accès à toutes les fonctionnalités
scripts/scripts.bat

# Version PowerShell
./Scripts-Menu.ps1

# Installation directe
scripts/setup.bat
```

### Initialisation de la base de données

```bash
# Initialiser la base de données
scripts/init_db.bat

# Version PowerShell
scripts/Initialize-Database.ps1
```

### Lancement du serveur

```bash
# Lancer le serveur avec interface graphique (par défaut)
python mathakine_cli.py run

# Lancer le serveur API uniquement (sans interface graphique)
python mathakine_cli.py run --api-only

# Avec options supplémentaires
python mathakine_cli.py run --port 8082 --debug
```

### Validation du Projet

```bash
# Configuration de l'environnement de validation
tests/setup_validation.bat

# Validation complète du projet
tests/auto_validate.bat

# Validation rapide (sans dépendances complexes)
python tests/simplified_validation.py

# Vérification de compatibilité
python tests/compatibility_check.py

# Génération d'un rapport complet
python tests/generate_report.py
```

### Migration vers PostgreSQL

```bash
# Pour le développement local
python scripts/migrate_to_postgres.py

# Pour Render
python scripts/migrate_to_render.py

# Basculer entre SQLite et PostgreSQL
python scripts/toggle_database.py [sqlite|postgres]

# Vérifier la connexion à la base de données
python check_db_connection.py
```

Pour des instructions détaillées, consultez [GETTING_STARTED.md](GETTING_STARTED.md) et [docs/validation/README.md](docs/validation/README.md).

## Structure du projet

```
./
├── app/                  # Code de l'application
├── docs/                 # Documentation détaillée
│   ├── ARCHITECTURE.md   # Architecture du système
│   ├── CHANGELOG.md      # Historique des modifications
│   ├── CLEANUP_REPORT.md # Rapport détaillé de nettoyage
│   ├── CLEANUP_SUMMARY.md # Résumé des opérations de nettoyage
│   ├── CONTEXT.md        # Contexte du projet
│   ├── DASHBOARD_FIX_REPORT.md # Corrections du tableau de bord
│   └── ...               # Autres documents
├── scripts/              # Scripts utilitaires
│   ├── check_project.py  # Vérification de la santé du projet
│   ├── fix_style.py      # Correction des problèmes de style courants
│   ├── fix_advanced_style.py # Correction des problèmes de style avancés
│   ├── migrate_to_postgres.py # Migration vers PostgreSQL
│   ├── toggle_database.py # Basculement entre SQLite et PostgreSQL
│   └── ...               # Autres scripts
├── static/               # Fichiers statiques (CSS, JS)
├── templates/            # Templates HTML
├── tests/                # Tests unitaires et d'intégration
├── archive/              # Fichiers récemment archivés
├── archives/             # Archives historiques
│   ├── obsolete/         # Fichiers obsolètes
│   └── sqlite/           # Anciennes sauvegardes SQLite
├── Dockerfile            # Image Docker
├── Procfile              # Commande de démarrage Render
├── README.md             # Documentation générale
├── GETTING_STARTED.md    # Guide de démarrage
├── STRUCTURE.md          # Structure du projet
├── requirements.txt      # Dépendances Python
├── ai_context_summary.md # Résumé du contexte du projet
├── .gitignore            # Fichiers ignorés par Git
├── .dockerignore         # Fichiers ignorés par Docker
├── .flake8               # Configuration de Flake8
├── setup.cfg             # Configuration des outils de développement
├── LICENSE               # Licence
├── sample.env            # Exemple de configuration d'environnement
├── enhanced_server.py    # Serveur principal amélioré
├── mathakine_cli.py      # Interface en ligne de commande
└── math-trainer-backend/ # Dossier hérité (en cours de migration)
```

## Glossaire et Index de la documentation

### Glossaire des termes

| Terme | Description |
|-------|-------------|
| **Mathakine** | Nom du projet, anciennement Math Trainer. Inspiré de Star Wars |
| **Padawan** | Niveau intermédiaire de difficulté (équivalent à "medium") |
| **Initié** | Niveau facile de difficulté (équivalent à "easy") |
| **Chevalier** | Niveau difficile de difficulté (équivalent à "hard") |
| **Maître** | Niveau expert de difficulté (non implémenté) |
| **La Force des nombres** | Métaphore pour les compétences mathématiques |
| **API Rebelle** | Nom de l'API REST du projet |
| **Les Archives** | Métaphore pour la base de données |
| **Épreuves d'Initié** | Tests unitaires |
| **Épreuves de Chevalier** | Tests d'intégration |
| **Épreuves de Maître** | Tests de performance |
| **Épreuves du Conseil Jedi** | Défis logiques pour les 10-15 ans |
| **Les Cristaux d'Identité** | Système d'authentification JWT |
| **Boucliers Déflecteurs** | Middleware de sécurité |
| **Holocrons** | Documentation API (Swagger/OpenAPI) |
| **Normalisation** | Processus d'uniformisation des données pour assurer la cohérence |

### Index de la documentation

#### Guide utilisateur et administrateur
- [GETTING_STARTED.md](GETTING_STARTED.md) : Guide de démarrage
- [STRUCTURE.md](STRUCTURE.md) : Structure du projet
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) : Guide de déploiement
- [docs/GLOSSARY.md](docs/GLOSSARY.md) : Glossaire complet des termes du projet
- [docs/UI_GUIDE.md](docs/UI_GUIDE.md) : Guide de l'interface graphique

#### Documentation technique
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) : Architecture du système
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) : État du projet et planification
- [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) : Plan d'implémentation détaillé
- [docs/POSTGRESQL_MIGRATION.md](docs/POSTGRESQL_MIGRATION.md) : Guide de migration vers PostgreSQL
- [docs/PYDANTIC_V2_MIGRATION.md](docs/PYDANTIC_V2_MIGRATION.md) : Migration vers Pydantic v2
- [docs/CHANGELOG.md](docs/CHANGELOG.md) : Résumé des modifications récentes et historique
- [docs/CLEANUP_REPORT.md](docs/CLEANUP_REPORT.md) : Rapport de nettoyage des fichiers obsolètes
- [docs/CLEANUP_SUMMARY.md](docs/CLEANUP_SUMMARY.md) : Résumé des améliorations de code

#### Documentation de référence
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) : Guide de résolution des problèmes
- [docs/validation/README.md](docs/validation/README.md) : Documentation du système d'auto-validation
- [docs/validation/COMPATIBILITY.md](docs/validation/COMPATIBILITY.md) : Compatibilité avec Python 3.13
- [docs/DASHBOARD_FIX_REPORT.md](docs/DASHBOARD_FIX_REPORT.md) : Corrections du tableau de bord

#### Documents spécifiques
- [tests/README.md](tests/README.md) : Documentation des tests
- [tests/TEST_PLAN.md](tests/TEST_PLAN.md) : Plan de test
- [scripts/README.md](scripts/README.md) : Documentation des scripts
- [docs/LOGIC_CHALLENGES_REQUIREMENTS.md](docs/LOGIC_CHALLENGES_REQUIREMENTS.md) : Exigences pour les défis logiques

## Améliorations récentes

### Mai 2023

- ✅ Migration complète vers PostgreSQL et correction des problèmes liés aux types énumérés
- ✅ Résolution des problèmes de relation entre exercices et tentatives (cascade delete)
- ✅ Amélioration des endpoints d'API avec une meilleure gestion des erreurs
- ✅ Mise à jour de l'interface utilisateur des exercices avec bouton de suppression
- ✅ Optimisation des requêtes SQL pour les opérations critiques
- ✅ Nouveau système de maintien du contexte avec fichier centralisé et script de génération

Pour plus de détails sur ces améliorations, consultez [docs/CHANGELOG.md](docs/CHANGELOG.md).

### Système de maintien du contexte

Pour faciliter la compréhension rapide de l'état actuel du projet :

```bash
# Générer un rapport sur l'état actuel du projet
python scripts/generate_context.py

# Mettre à jour automatiquement le fichier de contexte
python scripts/generate_context.py --update

# Générer le rapport au format JSON (pour intégration avec d'autres outils)
python scripts/generate_context.py --json
```

Le fichier [docs/CONTEXT.md](docs/CONTEXT.md) sert de point d'entrée central pour comprendre l'état actuel du projet, son architecture et ses fonctionnalités clés.

#### Documentation consolidée

Le projet utilise un système de documentation simplifié et consolidé :

```bash
# Consolider les documents qui se chevauchent (crée des sauvegardes .bak)
python scripts/consolidate_docs.py

# Vérifier quels fichiers redondants seraient supprimés
python scripts/cleanup_redundant_docs.py check

# Supprimer les fichiers redondants après consolidation
python scripts/cleanup_redundant_docs.py remove

# Restaurer les fichiers à partir des sauvegardes (si nécessaire)
python scripts/cleanup_redundant_docs.py restore
```

Le système de documentation maintient :
- **CHANGELOG.md** : Historique complet des versions et modifications
- **CONTEXT.md** : État actuel du projet, mis à jour automatiquement
- **CLEANUP_REPORT.md** : Rapport consolidé sur les opérations de nettoyage
- **POSTGRESQL_MIGRATION.md** : Guide complet de migration vers PostgreSQL

Les fichiers obsolètes et sauvegardes (.bak) peuvent être archivés :
```bash
# Déplacer les fichiers de sauvegarde (.bak) vers le dossier d'archives
python scripts/move_obsolete_files.py
```

Cette approche garantit une documentation complète mais non redondante, facilitant la maintenance et la compréhension du projet.

### Août-Septembre 2023

- ✅ Migration des modèles de données vers Pydantic v2 pour améliorer les performances et la compatibilité
- ✅ Résolution des problèmes de déploiement sur Render avec PostgreSQL
- ✅ Centralisation du système de journalisation pour une meilleure gestion des logs
- ✅ Système de détection des fichiers obsolètes pour maintenir la propreté du code
- ✅ Restructuration du projet avec une meilleure organisation des services

### Système de logs centralisé

Le projet intègre désormais un système de logs centralisé avec :

```bash
# Migration des logs existants
python -m scripts.migrate_logs

# Nettoyage des anciens fichiers logs (après vérification)
python -m scripts.cleanup_logs
```

Consultez [docs/LOGGING.md](docs/LOGGING.md) pour plus de détails sur le système de journalisation.

### Maintenance et nettoyage

```bash
# Détecter les fichiers obsolètes
python -m scripts.detect_obsolete_files --verbose

# Déplacer les fichiers obsolètes vers un répertoire d'archives
python -m scripts.detect_obsolete_files --move-to archives/obsolete

# Supprimer les fichiers obsolètes avec une confiance très élevée (>95%)
python -m scripts.detect_obsolete_files --delete

# Générer un rapport de nettoyage
python -m scripts.detect_obsolete_files --cleanup-report docs/CLEANUP_REPORT.md --confidence 40
```

Pour plus de détails sur les procédures de nettoyage et de maintenance, consultez [docs/MAINTENANCE.md](docs/MAINTENANCE.md).

---

*Pour toute contribution ou question, consulte la documentation ou ouvre une issue sur GitHub.*

*Dernière mise à jour : 08/05/2023* 