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

- ✅ Génération d'exercices mathématiques (addition, soustraction, multiplication, division)
- ✅ Interface adaptée aux enfants autistes avec thème Star Wars (animations douces, design inspiré de l'espace)
- ✅ Différents niveaux de difficulté (Initié, Padawan, Chevalier, Maître)
- ✅ Mode adaptatif qui ajuste la difficulté selon les performances
- ✅ Tableau de bord pour suivre les progrès du "Chemin vers la maîtrise"
- ✅ Génération d'exercices avec IA via l'API OpenAI
- ✅ Tests automatisés robustes pour garantir la non-régression
- ✅ Compatibilité avec Python 3.13
- ✅ Système de gestion des environnements (dev, test, prod)
- ✅ Scripts Windows (Batch et PowerShell) pour toutes les opérations
- ✅ API REST complète

## Démarrage rapide

### Installation

```bash
# Menu principal d'accès à toutes les fonctionnalités
scripts.bat

# Version PowerShell
.\Scripts-Menu.ps1

# Installation directe
scripts/setup.bat
```

### Initialisation de la base de données

```bash
# Initialiser la base de données avec les modèles et données de départ
scripts/init_db.bat

# Version PowerShell
.\scripts/Initialize-Database.ps1
```

### Lancement du serveur

```bash
# Via le menu principal
scripts.bat
# Puis sélectionnez l'option "Démarrer le serveur Mathakine"

# Ou directement
scripts/server/start_math_trainer.bat
```

Pour des instructions détaillées, consultez [GETTING_STARTED.md](GETTING_STARTED.md).

## Configuration pour la génération par IA

Pour utiliser la génération d'exercices par IA, vous devez configurer une clé API OpenAI:

1. Créez un compte sur [OpenAI Platform](https://platform.openai.com)
2. Créez une clé API dans la section API Keys
3. Utilisez l'option "Configurer la clé API OpenAI" dans le menu de configuration
   
   OU définissez la variable d'environnement:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY = "votre-clé-api"
   
   # Windows CMD
   set OPENAI_API_KEY=votre-clé-api
   
   # Linux/Mac
   export OPENAI_API_KEY=votre-clé-api
   ```

Alternativement, vous pouvez utiliser le menu de configuration :
```bash
# Menu de configuration des environnements
scripts/config_menu.bat
# Puis sélectionnez l'option "Configurer la clé API OpenAI"
```

## Structure du projet

Le projet est organisé selon une structure modulaire académique pour faciliter la maintenance :

```
math-trainer-backend/
├── scripts.bat                 # Menu principal en mode batch
├── Scripts-Menu.ps1            # Menu principal en PowerShell
├── run_ps1.bat                 # Exécuteur de scripts PowerShell sans restrictions
├── run_server.bat              # Script de lancement unifié
├── scripts/setup.bat           # Script d'installation unifié
├── scripts/init_db.bat         # Script d'initialisation de la base de données
├── scripts/Initialize-Database.ps1     # Script PowerShell d'initialisation de la base de données
├── GETTING_STARTED.md          # Guide de démarrage
├── README.md                   # Documentation générale
├── minimal_server.py           # Serveur minimal API
├── enhanced_server.py          # Serveur complet avec UI
├── requirements.txt            # Dépendances du projet
├── math_trainer.db             # Base de données SQLite
├── scripts/
│   ├── create_database.py      # Script d'initialisation de la base de données
│   ├── config_menu.bat         # Menu de configuration des environnements
│   ├── Config-Menu.ps1         # Menu de configuration PowerShell
│   ├── README.md               # Documentation des scripts
│   ├── server/                 # Scripts de démarrage du serveur
│   │   ├── start_math_trainer.bat  # Version batch 
│   │   ├── Start-MathTrainer.ps1   # Version PowerShell
│   │   ├── run_minimal_server.bat  # Serveur minimal
│   │   ├── run_enhanced_server.bat # Serveur amélioré
│   │   └── Run-MathTrainer.ps1     # Version PowerShell
│   └── ...
├── static/                     # Fichiers statiques (CSS, JS)
├── templates/                  # Templates HTML
├── tests/                      # Tests unitaires et d'intégration
└── app/                        # Code de l'application
    ├── core/                   # Configuration et utilitaires
    ├── db/                     # Base de données
    ├── models/                 # Modèles de données
    │   ├── user.py            # Modèle Utilisateur
    │   ├── exercise.py        # Modèle Exercice
    │   ├── attempt.py         # Modèle Tentative
    │   ├── progress.py        # Modèle Progression
    │   ├── setting.py         # Modèle Paramètres
    │   └── all_models.py      # Exportation de tous les modèles
    └── main.py                # Point d'entrée de l'application
```

## Modèles de données

Le projet utilise SQLAlchemy avec les modèles suivants:

### Utilisateurs

Les utilisateurs sont organisés selon les rangs de l'Ordre Jedi:
- **Padawan**: Élèves, accès standard
- **Maître**: Enseignants, création d'exercices
- **Gardien**: Modérateurs, gestion des utilisateurs
- **Archiviste**: Administrateurs, accès complet

### Exercices (Épreuves Jedi)

Niveaux de difficulté:
- **Initié**: Facile
- **Padawan**: Moyen
- **Chevalier**: Difficile
- **Maître**: Très difficile

Types d'exercices:
- Addition, Soustraction, Multiplication, Division
- Fractions, Géométrie et autres

### Système de progression (Chemin vers la Maîtrise)

Le système suit la progression des utilisateurs avec des niveaux de maîtrise:
1. **Novice**
2. **Initié**
3. **Padawan**
4. **Chevalier**
5. **Maître**

## Gestion des environnements

Le projet dispose d'un système complet de gestion des environnements avec trois profils prédéfinis :

| Profil | Description | Configuration |
|--------|-------------|--------------|
| **dev** | Développement | Debug activé, logs détaillés, port 8000 |
| **test** | Test | Debug activé, logs modérés, port 8080 |
| **prod** | Production | Debug désactivé, logs minimaux, port 80 |

Pour configurer ou changer d'environnement, utilisez :

```bash
# Menu de configuration des environnements
scripts/config_menu.bat

# Version PowerShell
.\scripts/Config-Menu.ps1
```

## Validation et correction automatique

Le système inclut une validation automatique des variables d'environnement :

```bash
# Valider les variables
scripts/utils/check_env_vars.bat

# Version PowerShell
.\scripts/utils/Check-EnvVars.ps1

# Gestionnaire d'environnement avancé
scripts/utils/env_manager.bat --validate --fix
```

## Tests et Assurance Qualité

```bash
# Menu principal
scripts.bat
# Puis sélectionnez les options de test

# Exécuter tous les tests
scripts/tests/run_tests.bat

# Version PowerShell
.\scripts/tests/Run-Tests.ps1
```

## Déploiement 

### Docker

Le projet inclut un Dockerfile pour faciliter le déploiement :

```bash
# Construire l'image
docker build -t math-trainer .

# Exécuter le conteneur
docker run -p 8080:8080 -e MATH_TRAINER_PROFILE=prod math-trainer
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 