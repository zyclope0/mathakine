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

Pour des instructions détaillées, consultez [GETTING_STARTED.md](GETTING_STARTED.md).

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
└── math_trainer.db       # Base de données SQLite (dev)
```

## Documentation supplémentaire

- [GETTING_STARTED.md](GETTING_STARTED.md) : Guide de démarrage
- [STRUCTURE.md](STRUCTURE.md) : Structure du projet
- [docs/](docs/) : Documentation détaillée
- [tests/README.md](tests/README.md) : Documentation des tests
- [tests/TEST_PLAN.md](tests/TEST_PLAN.md) : Plan de test
- [scripts/README.md](scripts/README.md) : Documentation des scripts

---

*Pour toute contribution ou question, consulte la documentation ou ouvre une issue sur GitHub.* 