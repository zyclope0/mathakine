# Guide de Contribution - Mathakine

## Table des matières
- [Introduction](#introduction)
- [Prérequis](#prérequis)
- [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Processus de contribution](#processus-de-contribution)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Système CI/CD](#système-cicd)
- [Documentation](#documentation)
- [Soumission des modifications](#soumission-des-modifications)

## Introduction
Merci de votre intérêt pour contribuer à Mathakine ! Ce guide vous aidera à comprendre notre processus de contribution et nos standards.

## Prérequis
- Python 3.9+
- Git
- PostgreSQL 13+
- Un éditeur de code (VS Code recommandé)

## Configuration de l'environnement
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-username/mathakine.git
   cd mathakine
   ```

2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer l'environnement :
   ```bash
   cp .env.example .env
   # Modifier les variables dans .env selon votre configuration
   ```

5. Installer les hooks Git pour le CI/CD :
   ```bash
   python scripts/setup_git_hooks.py
   ```

## Processus de contribution
1. Créer une branche pour votre fonctionnalité :
   ```bash
   git checkout -b feature/nom-de-la-fonctionnalite
   ```

2. Développer et tester localement

3. Commiter vos changements :
   ```bash
   git add .
   git commit -m "Description claire des modifications"
   # Les tests critiques s'exécutent automatiquement via le hook pre-commit
   ```

4. Pousser vers votre fork :
   ```bash
   git push origin feature/nom-de-la-fonctionnalite
   ```

5. Créer une Pull Request

## Standards de code
- Suivre PEP 8
- Utiliser des noms explicites en français
- Commenter le code complexe
- Documenter les fonctions avec docstrings
- Maximum 80 caractères par ligne

## Tests
- Écrire des tests unitaires pour chaque nouvelle fonctionnalité
- Maintenir une couverture de code > 80%
- Exécuter les tests avant chaque commit :
  ```bash
  pytest
  ```

## Système CI/CD

### Classification des Tests

Le projet utilise un système de classification des tests en 3 niveaux :

#### 🔴 Tests Critiques (BLOQUANTS)
- **Impact** : Bloquent le commit et le déploiement
- **Timeout** : 3 minutes
- **Contenu** : Tests fonctionnels, services utilisateur, authentification
- **Commande** : `python scripts/pre_commit_check.py`

#### 🟡 Tests Importants (NON-BLOQUANTS)
- **Impact** : Avertissement, commit autorisé
- **Timeout** : 2 minutes  
- **Contenu** : Tests d'intégration, modèles, adaptateurs

#### 🟢 Tests Complémentaires (INFORMATIFS)
- **Impact** : Information seulement
- **Timeout** : 1 minute
- **Contenu** : CLI, initialisation, fonctionnalités secondaires

### Hooks Git Automatiques

Les hooks Git sont automatiquement installés et exécutent :
- **Pre-commit** : Tests critiques avant chaque commit
- **Post-merge** : Mise à jour des dépendances après merge

### Commandes Utiles

```bash
# Vérification manuelle pre-commit
python scripts/pre_commit_check.py

# Tests par catégorie
python -m pytest tests/functional/ -v  # Critiques
python -m pytest tests/integration/ -v  # Importants

# Mise à jour automatique des tests après modifications
python scripts/update_tests_after_changes.py --auto-create

# Bypass temporaire (non recommandé)
git commit --no-verify
```

### Pipeline GitHub Actions

Le pipeline CI/CD s'exécute automatiquement sur :
- Push vers `main` ou `develop`
- Pull Requests
- Workflow manuel

**Étapes du pipeline :**
1. Tests critiques (bloquants)
2. Tests importants (parallèles)
3. Tests complémentaires (informatifs)
4. Analyse de couverture
5. Vérifications qualité (Black, Flake8, Bandit)
6. Génération de rapports

### Bonnes Pratiques CI/CD

1. **Toujours corriger** les tests critiques qui échouent
2. **Surveiller** les avertissements des tests importants
3. **Utiliser** `--auto-create` pour générer les tests manquants
4. **Consulter** les rapports de couverture
5. **Documenter** les nouveaux tests ajoutés

Pour plus de détails, consultez le [Guide CI/CD complet](../CI_CD_GUIDE.md).

## Documentation
- Mettre à jour la documentation pour toute nouvelle fonctionnalité
- Suivre le format Markdown existant
- Inclure des exemples de code si nécessaire
- Mettre à jour le CHANGELOG.md

## Soumission des modifications
1. Vérifier que tous les tests passent
2. Mettre à jour la documentation
3. Créer une Pull Request détaillée
4. Attendre la review des mainteneurs

---

Pour toute question, n'hésitez pas à ouvrir une issue ou à contacter l'équipe de développement.

### Structure du projet
```
./
├── app/                  # Code principal FastAPI
├── docs/                 # Documentation
├── scripts/             # Scripts utilitaires
├── static/              # Fichiers statiques
├── templates/           # Templates HTML
├── tests/               # Tests
└── enhanced_server.py   # Serveur Starlette
```

### Workflow de développement

1. **Créer une branche**
   ```bash
   git checkout -b feature/nom-de-la-feature
   ```

2. **Développer**
   - Suivre les conventions de code Python (PEP 8)
   - Ajouter des tests unitaires
   - Documenter les changements

3. **Tester**
   ```bash
   # Exécuter tous les tests
   python -m tests.run_tests --all
   
   # Tests spécifiques
   python -m tests.run_tests --unit
   python -m tests.run_tests --api
   ```

4. **Mettre à jour la documentation**
   - Ajouter/modifier les documents dans docs/
   - Mettre à jour CHANGELOG.md
   - Vérifier les liens dans la documentation

5. **Soumettre une PR**
   - Description claire des changements
   - Références aux issues concernées
   - Liste des tests effectués

### Conventions

#### Code
- Utiliser des noms explicites en anglais
- Commenter le code complexe
- Documenter les fonctions avec docstrings
- Respecter la structure du projet

#### Documentation
- Utiliser le markdown
- Suivre la structure Core/Tech/Features
- Mettre à jour la table des matières
- Archiver les anciens documents

#### Tests
- Un test par fonctionnalité
- Nommer les tests clairement
- Utiliser les fixtures pytest
- Vérifier la couverture de code

### Thème Star Wars

Pour maintenir la cohérence du thème :
- Utiliser la terminologie Star Wars appropriée
- Suivre le guide de style dans UI_GUIDE.md
- Adapter les messages d'erreur au thème
- Utiliser les couleurs définies

### Points d'attention

1. **Sécurité**
   - Ne pas exposer de secrets
   - Valider toutes les entrées
   - Utiliser les middlewares de sécurité

2. **Performance**
   - Optimiser les requêtes SQL
   - Minimiser les appels API
   - Utiliser le cache quand possible

3. **Accessibilité**
   - Supporter les lecteurs d'écran
   - Fournir des alternatives textuelles
   - Respecter les contrastes WCAG

### Support

- Issues GitHub pour les bugs
- Discussions pour les questions
- Wiki pour la documentation étendue

---

*Dernière mise à jour : 15 juin 2025* 