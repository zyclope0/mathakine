# Mathakine (anciennement Math Trainer)

## ⚠️ AVIS IMPORTANT : MIGRATION DU PROJET ⚠️

**Ce dépôt est maintenant obsolète**. Le projet a été migré vers la nouvelle structure "Mathakine" avec une organisation améliorée des tests et une meilleure cohérence du thème Star Wars.

### Où trouver la nouvelle version ?

Le code et la documentation à jour se trouvent maintenant dans les répertoires suivants :
- **Code principal** : `/math-trainer-backend/`
- **Documentation principale** : `/math-trainer-backend/README.md`
- **Documentation des tests** : `/math-trainer-backend/tests/README.md`
- **Plan de test complet** : `/math-trainer-backend/tests/TEST_PLAN.md`
- **Documentation détaillée** : `/math-trainer-backend/docs/`

### Pourquoi cette migration ?

Cette migration a permis :
1. D'organiser les tests en 4 catégories distinctes (unitaires, API, intégration, fonctionnels)
2. D'intégrer plus profondément la thématique Star Wars dans le code et la documentation
3. De nettoyer les fichiers obsolètes et de clarifier la structure du projet
4. D'améliorer la maintenabilité et l'extensibilité du code

## Documentation conservée à titre historique

Le reste de ce document est conservé à titre historique et pour référence. Pour les informations les plus récentes, veuillez consulter la documentation référencée ci-dessus.

---

Backend pour un site d'entraînement mathématique interactif destiné aux enfants, spécialement adapté pour un enfant autiste de 9 ans, avec une thématique Star Wars.

## Présentation

Mathakine est une application éducative conçue pour les enfants autistes, permettant un apprentissage des mathématiques adapté à leurs besoins spécifiques. L'application aide les jeunes "Padawans des mathématiques" à maîtriser la "Force des nombres" à travers des exercices interactifs et personnalisés.

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
# Démarrer le serveur (exemple)
scripts/start_render.sh
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

Pour des instructions détaillées, consultez [GETTING_STARTED.md](GETTING_STARTED.md) et [docs/validation/README.md](docs/validation/README.md).

## Structure du projet

```
math-trainer-backend/
├── app/                  # Code de l'application
├── docs/                 # Documentation détaillée
├── scripts/              # Scripts utilitaires (installation, serveur, config, etc.)
├── static/               # Fichiers statiques (CSS, JS)
├── templates/            # Templates HTML
├── tests/                # Tests unitaires et d'intégration
├── Dockerfile            # Image Docker
├── Procfile              # Commande de démarrage Render
├── README.md             # Documentation générale
├── GETTING_STARTED.md    # Guide de démarrage
├── STRUCTURE.md          # Structure du projet
├── requirements.txt      # Dépendances Python
├── .gitignore            # Fichiers ignorés par Git
├── .dockerignore         # Fichiers ignorés par Docker
├── LICENSE               # Licence
├── sample.env            # Exemple de configuration d'environnement
├── math_trainer.db       # Base de données SQLite (dev)
├── enhanced_server.py    # Serveur principal amélioré
├── fix_database.py       # Script de correction de la base de données
└── mathakine_cli.py      # Interface en ligne de commande
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

#### Documentation technique
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) : Architecture du système
- [docs/PROJECT_STATUS.md](docs/PROJECT_STATUS.md) : État du projet et planification
- [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) : Plan d'implémentation détaillé

#### Documentation de référence
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) : Guide de résolution des problèmes
- [docs/validation/README.md](docs/validation/README.md) : Documentation du système d'auto-validation
- [docs/validation/COMPATIBILITY.md](docs/validation/COMPATIBILITY.md) : Compatibilité avec Python 3.13

#### Documents spécifiques
- [tests/README.md](tests/README.md) : Documentation des tests
- [tests/TEST_PLAN.md](tests/TEST_PLAN.md) : Plan de test
- [scripts/README.md](scripts/README.md) : Documentation des scripts
- [docs/LOGIC_CHALLENGES_REQUIREMENTS.md](docs/LOGIC_CHALLENGES_REQUIREMENTS.md) : Exigences pour les défis logiques

## Améliorations récentes

### Juin-Juillet 2024

- ✅ Résolution du problème de non-mise à jour du tableau de bord après complétion d'exercices
- ✅ Normalisation des types d'exercices et niveaux de difficulté dans la base de données
- ✅ Création d'un script `fix_database.py` pour corriger les données existantes
- ✅ Ajout de tests pour vérifier la normalisation des données
- ✅ Mise à jour de la documentation avec un guide de résolution des problèmes

Pour plus de détails sur les corrections et améliorations, consultez [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

*Pour toute contribution ou question, consulte la documentation ou ouvre une issue sur GitHub.*

*Dernière mise à jour : 22/07/2024* 