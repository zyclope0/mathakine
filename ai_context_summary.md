# Compréhension du projet Mathakine (anciennement Math Trainer)

# AIDE-MÉMOIRE POUR LE MODÈLE

## 📌 Points clés du projet
- Mathakine = application éducative mathématique pour enfants autistes
- Thème Star Wars (Padawans des mathématiques)
- Double backend: FastAPI (API pure) + Starlette (interface web)
- Base de données: PostgreSQL (prod) / SQLite (dev)
- Migrations avec Alembic
- Tests structurés en 4 niveaux

## 🔀 Relations entre composants clés
```
enhanced_server.py (Starlette) ────► templates/ (UI)
                              ────► static/ (CSS/JS)
                              ────► app/models/ (DB)
                              
app/main.py (FastAPI) ─────────────► app/api/endpoints/
                      ─────────────► app/services/
                                        ▲
                                        │
                                        ▼
app/models/ ◄───────────────────────► app/schemas/
     ▲
     │ SQLAlchemy
     ▼
Base de données ◄────► migrations/ (Alembic)
```

## 💻 Exemples de code critiques

### Relations avec cascade (SQLAlchemy)
```python
# Exemple dans app/models/user.py
class User(Base):
    # ...
    exercises = relationship(
        "Exercise",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    attempts = relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    progress = relationship(
        "Progress",
        back_populates="user",
        cascade="all, delete-orphan"
    )
```

### Endpoint de suppression (FastAPI)
```python
# Exemple dans app/api/endpoints/exercises.py
@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    if exercise.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # La suppression en cascade est gérée automatiquement
    db.delete(exercise)
    db.commit()
    return None
```

### Test de cascade (pytest)
```python
# Exemple dans tests/integration/test_cascade_deletion.py
def test_user_deletion_cascades_to_exercises(db_session):
    # Créer un utilisateur avec des exercices
    user = User(username="test_cascade", email="test@cascade.com", hashed_password="test")
    db_session.add(user)
    db_session.commit()
    
    exercise = Exercise(title="Test Exercise", creator_id=user.id, 
                       exercise_type="Addition", difficulty="Initié",
                       question="1+1=?", correct_answer="2")
    db_session.add(exercise)
    db_session.commit()
    
    # Vérifier que l'exercice existe
    assert db_session.query(Exercise).filter_by(id=exercise.id).first() is not None
    
    # Supprimer l'utilisateur
    db_session.delete(user)
    db_session.commit()
    
    # Vérifier que l'exercice a été supprimé en cascade
    assert db_session.query(Exercise).filter_by(id=exercise.id).first() is None
```

## ⚙️ Processus de développement et test
```
Nouvelle implémentation/modification  ───┐
            │                            │
            ▼                            │
    Vérification locale                  │
            │                            │
            ▼                            │
    Exécution des tests ◄────────────────┘
            │
            ▼
Analyse des résultats de test
            │
            ▼
    Correction si besoin
            │
            ▼
  Documentation des changements
```

## 🧪 Exécution systématique des tests
Après chaque implémentation importante, modification majeure ou optimisation du code, **TOUJOURS** exécuter la suite de tests pour s'assurer de la non-régression et de la qualité du code.

### Exécution complète des tests
```bash
# Exécution de tous les tests
python -m tests.run_tests --all
# OU
tests/run_tests.bat --all
```

### Exécution par catégorie
En fonction des modifications apportées, exécuter les catégories de tests pertinentes :
```bash
# Tests unitaires (pour modifications de modèles, services, etc.)
python -m tests.run_tests --unit
# Tests API (pour modifications d'endpoints API)
python -m tests.run_tests --api
# Tests d'intégration (pour modifications impliquant plusieurs composants)
python -m tests.run_tests --integration
# Tests fonctionnels (pour modifications de l'interface ou workflows complets)
python -m tests.run_tests --functional
```

### Exécution d'un test spécifique
Pour tester uniquement une fonctionnalité modifiée :
```bash
# Test d'un fichier spécifique
pytest tests/unit/test_models.py -v
# Test d'une fonction spécifique
pytest tests/unit/test_models.py::test_exercise_cascade -v
```

### Vérification des résultats
1. S'assurer qu'il n'y a pas de tests échoués ou d'erreurs
2. Vérifier la couverture de code pour les parties modifiées
3. Si des tests échouent, corriger immédiatement avant de continuer
4. Documenter tous les problèmes rencontrés et leurs solutions

### Automatisation
Pour les modifications importantes, toujours utiliser cette séquence d'actions :
1. Implémenter les changements
2. Exécuter les tests pertinents
3. Analyser et corriger les problèmes
4. Documenter les modifications et les résultats

## ⚠️ Problèmes potentiels et solutions

| Problème | Symptôme | Solution |
|----------|----------|----------|
| Échec de suppression en cascade | Erreur d'intégrité référentielle | Vérifier la configuration `cascade` dans les modèles |
| Données orphelines | Tables avec références à des objets supprimés | Exécuter script de nettoyage `clean_orphans.py` |
| Conflit de migration Alembic | Erreur "Target database is not up to date" | Utiliser `alembic stamp head` puis générer nouvelle migration |
| Tests SQLite vs PostgreSQL | Tests échouant en prod mais pas en dev | Utiliser les fixtures spécifiques au moteur de base de données |
| Timeout des requêtes complexes | Erreur 504 en production | Optimiser les requêtes avec indexes ou pagination |

## 🔍 Comment trouver rapidement
- Configuration base de données: `app/core/config.py`
- Constantes & messages: `app/core/constants.py` et `app/core/messages.py`
- Modèles principaux: `app/models/{user,exercise,attempt,progress}.py`
- API REST: `app/api/endpoints/`
- Interface web: `enhanced_server.py` et `templates/`
- Tests: `tests/{unit,api,integration,functional}/`
- Documentation: `docs/` (voir TABLE_DES_MATIERES.md)

## ✅ Résultats actuels des tests
- 58 tests réussis
- 1 test ignoré (PostgreSQL spécifique)
- 0 échecs
- Couverture code: 64%
- Temps d'exécution moyen: ~25 secondes

## Vue d'ensemble
Mathakine est une application éducative backend pour un site d'entraînement mathématique interactif destiné aux enfants, spécialement adapté pour les enfants autistes, avec une thématique Star Wars. Anciennement nommée "Math Trainer", elle a été entièrement renommée et restructurée pour offrir une expérience cohérente et immersive où les enfants sont des "Padawans des mathématiques" apprenant à maîtriser la "Force des nombres".

## Historique et renommage
- Le projet était originellement nommé "Math Trainer"
- Un renommage complet vers "Mathakine" a été effectué
- La thématique Star Wars a été renforcée et profondément intégrée dans le code, les interfaces et la documentation
- Une restructuration complète a été réalisée pour améliorer la maintenabilité, avec réorganisation des tests et nettoyage des fichiers obsolètes

## Architecture technique
- **Double architecture backend**:
  - **FastAPI (app/main.py)** - API REST pure pour applications externes et futures frontends
  - **Starlette (enhanced_server.py)** - Version avec interface utilisateur web intégrée
- **Base de données**: 
  - PostgreSQL pour production (sur Render)
  - SQLite pour développement local (avec scripts de migration)
- **Migrations de schéma**:
  - **Alembic** pour la gestion professionnelle des migrations de base de données
  - Configuration spéciale pour préserver les tables héritées
  - Scripts utilitaires pour faciliter les opérations de migration
- **Structure du code**:
  - Architecture MVC moderne avec séparation claire entre modèles/schémas/services/API
  - API REST documentée via Swagger/OpenAPI (appelée "Les Holocrons" dans la terminologie du projet)
  - Tests répartis en 4 catégories: unitaires, API, intégration, fonctionnels
  - **Centralisation des constantes et messages** pour améliorer la maintenabilité
  - **Système de variables CSS** pour une apparence cohérente
  - **Requêtes SQL centralisées** pour faciliter la maintenance et éviter la duplication
- **Outils de gestion**:
  - Interface CLI complète (mathakine_cli.py) avec 6 commandes principales
  - Scripts de migration et de gestion de base de données
  - Outils de validation automatisée
- **Déploiement**:
  - Support Docker avec Dockerfile optimisé
  - Configuration pour déploiement sur Render
  - Compatibilité avec Python 3.13
  - Exemple de fichier .env pour la configuration des environnements

## Composants clés

### 1. enhanced_server.py
Le serveur principal combinant l'interface utilisateur web et l'API, construit avec Starlette pour une meilleure compatibilité Python 3.13.

**Fonctionnalités principales**:
- Interface web complète avec templates HTML et CSS
- API REST simple avec endpoints JSON
- Génération d'exercices (simple et IA)
- Soumission de réponses et feedback
- Tableau de bord avec statistiques
- Gestion des exercices (liste, détails, suppression)

**Routes principales**:
- Pages HTML: "/", "/exercises", "/dashboard", "/exercise/{id}"
- API: "/api/exercises/", "/api/exercises/{id}", "/api/exercises/generate", "/api/exercises/{id}/submit", "/api/users/stats"

**Mécanismes clés**:
- Normalisation des types d'exercices et difficultés
- Génération pseudo-IA d'exercices (avec tag TEST-ZAXXON)
- Gestion des choix en format JSON
- Statistiques par type d'exercice et niveau
- Suivi de progression via des graphiques de performance

### 2. app/ (Application FastAPI)
Contient l'implémentation API REST pure utilisant FastAPI, organisée selon les meilleures pratiques.

**Structure**:
- **api/endpoints/**: Endpoints REST (exercises.py, users.py, challenges.py, auth.py)
- **models/**: Modèles SQLAlchemy 2.0 (exercise.py, user.py, attempt.py, progress.py, logic_challenge.py)
  - **legacy_tables.py**: Modèles des tables héritées pour la compatibilité avec Alembic
- **schemas/**: Schémas Pydantic 2.0 pour validation (exercise.py, progress.py, etc.)
- **services/**: Logique métier (exercise_service.py, auth_service.py, etc.)
   - **core/**: Configuration et utilitaires
  - **config.py**: Configuration principale de l'application
  - **constants.py**: Toutes les constantes centralisées (types, niveaux, limites)
  - **messages.py**: Messages et textes centralisés pour l'interface et les API
  - **logging_config.py**: Configuration du système de journalisation centralisée
    
    **Système de journalisation**:
    - **Architecture**: Système centralisé basé sur loguru avec rotation et compression automatiques
    - **Niveaux**: DEBUG, INFO, WARNING, ERROR, CRITICAL dans des fichiers séparés
    - **Utilisation**: Via `from app.core.logging_config import get_logger`
    - **Format standardisé**: Horodatage, niveau, module, ligne, message
    - **Rotation**: Fichiers divisés à 10-20 Mo et compressés en ZIP
    - **Conservation**: 30-60 jours selon l'importance des logs
    - **Contexte**: Support pour l'ajout de métadonnées via `logger.bind()`
    - **Capture d'exceptions**: Enregistrement automatique des stack traces
    - **Importance**: Essentiel pour le débogage, la surveillance et l'analyse des performances
   - **db/**: Accès et initialisation de base de données
  - **init_db.py**: Initialisation de la base de données
  - **base.py**: Configuration de base
  - **queries.py**: Requêtes SQL centralisées

**Fonctionnalités avancées**:
- Support complet CRUD pour toutes les entités
- Pagination, filtrage et tri avancés
- Gestion des erreurs standardisée
- Modèles pour défis logiques avancés (10-15 ans)
- Validation des données avec Pydantic 2.0

### 3. templates/ et static/
Dossiers contenant les templates HTML et les fichiers statiques (CSS, JS) pour l'interface utilisateur web.

**Templates principaux**:
- **base.html**: Template de base avec layout, navigation et thème Star Wars
- **home.html**: Page d'accueil avec hero section optimisée suivant les best practices UI:
  - Layout horizontal avec contenu à gauche et visuel à droite
  - Affichage de statistiques clés (nombre d'exercices, niveaux, possibilités)
  - Unique CTA principal pour réduire les redondances avec la navigation
  - Design responsive adaptatif pour desktop et mobile
  - Animation spatiale avec objet céleste animé par CSS
- **exercise.html**: Interface pour résoudre un exercice spécifique
- **exercises.html**: Liste et gestion des exercices avec filtres
- **dashboard.html**: Interface du tableau de bord avec statistiques et graphiques
- **error.html**: Page d'erreur standardisée
- **exercise_detail.html**: Détails d'un exercice spécifique

**Structure CSS normalisée**:
- **normalize.css**: Réinitialisation CSS standardisée pour une cohérence entre navigateurs
- **variables.css**: Variables CSS centralisées (couleurs, espacements, typographie)
- **utils.css**: Classes utilitaires pour les mises en page et ajustements courants
- **style.css**: Styles globaux qui importent les autres fichiers CSS
- **space-theme.css**: Éléments de thème spatial Star Wars
- **home-styles.css**: Styles spécifiques à la page d'accueil

**Système de normalisation CSS**:
- Architecture inspirée des méthodologies CSS modernes (Utility-First, BEM)
- Remplacement systématique des styles en ligne par des classes utilitaires
- Script de normalisation (`scripts/normalize_css.py`) qui automatise la conversion
- Documentation détaillée dans `static/README.md` et `docs/UI_GUIDE.md`
- Ordre d'importation standardisé: normalize → variables → utils → style → theme

**Exemples de classes utilitaires**:
- Marges: `mt-3`, `mb-4`, `ml-2`, `mr-3` (top, bottom, left, right avec différentes tailles)
- Display: `d-flex`, `d-block`, `d-none`, `d-grid`
- Flexbox: `justify-between`, `align-center`, `flex-column`, `flex-wrap`
- Text: `text-center`, `text-primary`, `fw-bold`
- Colors: `bg-primary`, `text-sw-gold`, `border`

**Avantages de la normalisation**:
- Réduction de la duplication de code CSS
- Maintenance simplifiée grâce à la centralisation des styles
- Cohérence visuelle sur l'ensemble de l'application
- Performance améliorée par la réduction du poids total du CSS
- Facilité d'extension sans créer de conflits de style

### 4. mathakine_cli.py
Interface en ligne de commande complète pour administrer et gérer l'application.

**Commandes disponibles**:
- **run**: Démarrer l'application (avec/sans interface graphique)
- **init**: Initialiser/réinitialiser la base de données
- **test**: Exécuter différents types de tests
- **validate**: Valider l'application
- **shell**: Démarrer un shell Python avec contexte d'application
- **setup**: Configurer l'environnement de développement

### 5. Documentation
Ensemble complet de documents détaillant tous les aspects du projet.

**Documentation principale**:
- **README.md**: Documentation générale
- **STRUCTURE.md**: Structure détaillée du projet
- **ARCHITECTURE.md**: Architecture détaillée du système
- **PROJECT_STATUS.md**: État actuel et planification
- **IMPLEMENTATION_PLAN.md**: Plan d'implémentation détaillé
- **UI_GUIDE.md**: Guide de l'interface graphique
- **POSTGRESQL_MIGRATION.md**: Guide de migration vers PostgreSQL
- **CHANGELOG.md**: Historique des modifications
- **ALEMBIC.md**: Guide d'utilisation d'Alembic pour les migrations
- **CORRECTIONS_ET_MAINTENANCE.md**: Documentation des corrections et problèmes résolus
- **MAINTENANCE_ET_NETTOYAGE.md**: Résumé des opérations de nettoyage
- **LOGGING.md**: Guide du système de journalisation centralisé
- **PYDANTIC_V2_MIGRATION.md**: Documentation de la migration vers Pydantic v2

**Rôle de la documentation de migration**:
- **Valeur historique**: Documentation des décisions techniques importantes
- **Référence pour les développeurs**: Aide les nouveaux développeurs à comprendre les choix d'architecture
- **Guide de maintenance**: Facilite la compréhension de patterns utilisés dans le code actuel
- **Résolution de problèmes**: Source d'information pour diagnostiquer les problèmes liés aux migrations
- **Configuration des environnements**: Instructions pour configurer différents environnements (développement/production)

La documentation complète est organisée dans la **TABLE_DES_MATIERES.md** qui sert de point d'entrée vers tous les documents.

### 6. Scripts d'utilitaires
Le dossier scripts/ contient des outils essentiels pour la maintenance et le développement du projet.

**Scripts principaux**:
- **check_project.py**: Vérification de la santé du projet (style, syntaxe, imports)
- **fix_style.py**: Correction automatique des problèmes de style courants
- **fix_advanced_style.py**: Correction des problèmes de style avancés
- **toggle_database.py**: Basculement entre SQLite et PostgreSQL
- **migrate_to_postgres.py**: Migration des données vers PostgreSQL
- **generate_context.py**: Génération du contexte du projet
- **init_alembic.py**: Initialisation d'Alembic dans une base de données existante
- **generate_migration.py**: Génération sécurisée d'une nouvelle migration Alembic
- **alembic_demo.py**: Démonstration du processus complet de migration Alembic

### 7. Système de migrations Alembic
Configuration mise en place pour gérer l'évolution du schéma de la base de données de manière professionnelle.

**Structure des migrations**:
- **migrations/env.py**: Configuration personnalisée pour préserver les tables héritées
- **migrations/versions/**: Versions successives des migrations
  - **initial_snapshot.py**: Migration initiale documentant l'état actuel
  - **20250513_baseline_migration.py**: Migration de base comme point de départ

**Tables héritées préservées**:
- **results**: Résultats d'exercices
- **statistics**: Statistiques par session
- **user_stats**: Statistiques utilisateur
- **schema_version**: Version du schéma

**Fonctionnalités clés**:
- Protection des tables héritées contre la suppression accidentelle
- Détection des conflits potentiels dans les migrations générées
- Création sécurisée de nouvelles migrations avec vérification automatique
- Interface de démo pour tester le processus complet

**Workflow de migration**:
1. Initialisation de la base de données avec `init_alembic.py`
2. Génération de migrations avec `generate_migration.py`
3. Vérification manuelle des migrations générées
4. Application des migrations avec `alembic upgrade head`
5. Suivi de l'état avec `alembic current` et `alembic history`

### 8. Système de gestion des suppressions en cascade

Le projet implémente un mécanisme robuste de suppression en cascade pour maintenir l'intégrité des données et simplifier les opérations de nettoyage.

**Principe et avantages**:
- **Intégrité des données**: Évite les références orphelines dans la base de données
- **Simplification du code**: Réduit la complexité des opérations de suppression
- **Performance**: Exécute les suppressions dans une seule transaction
- **Maintenance**: Facilite le nettoyage des données obsolètes
- **Cohérence**: Garantit une approche uniforme dans toute l'application

**Implémentation technique**:
- **Relations SQLAlchemy avec option cascade**: Configuration des relations entre modèles avec `cascade="all, delete-orphan"`
- **Endpoints de suppression uniformisés**: Structure standardisée pour tous les endpoints de suppression
- **Gestion des erreurs**: Protection contre les échecs de transaction avec try/except et rollback

**Relations en cascade par modèle**:
- **User**: Supprime automatiquement les exercices créés, tentatives, défis logiques et statistiques
- **Exercise**: Supprime automatiquement les tentatives et statistiques associées
- **LogicChallenge**: Supprime automatiquement les tentatives et statistiques associées

**Documentation**:
- Documentation complète dans `docs/CASCADE_DELETION.md`
- Exemples de code pour l'implémentation
- Bonnes pratiques pour la gestion des suppressions

**Tests de validation**:
- Tests unitaires: `tests/unit/test_cascade_relationships.py`
- Tests d'intégration: `tests/integration/test_cascade_deletion.py`
- Tests API: `tests/api/test_deletion_endpoints.py`
- Tests fonctionnels: `tests/functional/test_starlette_cascade_deletion.py`

**Bénéfices pour le projet**:
- Réduction du code boilerplate dans les endpoints
- Prévention des problèmes d'intégrité référentielle
- Simplification des opérations de maintenance
- Performance améliorée des opérations de suppression

### 9. Tests

Le dossier tests/ contient des tests organisés par catégories avec une structure optimisée.

**Structure des tests**:
- **unit/**: Tests unitaires des composants individuels
  - **test_models.py**: Validation des modèles de données
  - **test_services.py**: Tests des services métier 
  - **test_cli.py**: Tests de l'interface CLI
  - **test_db_init_service.py**: Tests d'initialisation de la base de données
  - **test_cascade_relationships.py**: Vérification des relations avec cascade
- **api/**: Tests des endpoints API
  - **test_base_endpoints.py**: Tests des endpoints de base
  - **test_exercise_endpoints.py**: Tests des endpoints d'exercices
  - **test_challenge_endpoints.py**: Tests des endpoints de défis logiques
  - **test_deletion_endpoints.py**: Tests des endpoints de suppression
- **integration/**: Tests d'intégration entre les composants
  - **test_user_exercise_flow.py**: Tests du flux utilisateur-exercice
  - **test_cascade_deletion.py**: Tests de suppression en cascade
- **functional/**: Tests fonctionnels de l'application complète
  - **test_logic_challenge.py**: Tests des défis logiques
  - **test_enhanced_server.py**: Tests du démarrage du serveur
  - **test_starlette_cascade_deletion.py**: Tests de suppression en cascade via Starlette
- **fixtures/**: Données de test partagées
- **conftest.py**: Configuration centralisée pour pytest
- **run_tests.py**: Script central d'exécution des tests
- **run_tests.bat**: Script Windows pour l'exécution facile des tests
- **TEST_PLAN.md**: Plan détaillé des tests
- **README.md**: Documentation des tests

**Avantages de l'architecture de test**:
- **Organisation claire**: Tests séparés par niveau (unitaire, API, intégration, fonctionnel)
- **Fixtures réutilisables**: Réduction de la duplication de code
- **Exécution flexible**: Possibilité d'exécuter des tests par catégorie
- **Documentation complète**: Plan de test détaillé (TEST_PLAN.md)
- **Scripts d'automatisation**: Exécution simplifiée des tests

**Support des suppressions en cascade**:
- Tests unitaires pour valider la configuration des relations
- Tests d'intégration pour vérifier le comportement cascade
- Tests API pour valider les endpoints de suppression
- Tests fonctionnels pour confirmer le comportement end-to-end

**Support des tests asynchrones**:
- Utilisation de pytest-asyncio pour tester les coroutines
- Tests de fonctions asynchrones du serveur enhanced_server.py
- Gestion appropriée des event loops

**Fixtures d'authentification**:
- Fixture auth_client pour les tests nécessitant un utilisateur authentifié
- Création automatique d'utilisateurs temporaires avec tokens
- Gestion des headers d'authentification pour les tests d'API

**Commandes d'exécution**:
```bash
# Exécuter tous les tests
tests/run_tests.bat --all

# Exécuter par catégorie
tests/run_tests.bat --unit
tests/run_tests.bat --api
tests/run_tests.bat --integration
tests/run_tests.bat --functional
```

**Rapports générés**:
- Journaux détaillés dans `test_results/`
- Rapports de couverture HTML dans `test_results/coverage/`
- Rapports JUnit XML dans `test_results/junit.xml`
- Rapports par catégorie de test dans les fichiers séparés

**Système d'auto-validation**:
- Scripts pour la validation automatisée du projet
- Vérification de l'intégrité et de la compatibilité
- Génération de rapports détaillés

**Tests de suppression en cascade**:
- **Tests unitaires**: Vérification des configurations de relation (cascade="all, delete-orphan")
- **Tests d'intégration**: Validation des suppressions en cascade à travers les modèles
- **Tests API**: Test des endpoints de suppression avec vérification des résultats
- **Tests fonctionnels**: Vérification du comportement end-to-end dans le serveur Starlette

**Critères de succès**:
- Couverture de code > 60%
- Tous les tests de suppression en cascade réussis
- Documentation complète des tests implémentés

**Améliorations récentes (Mai 2025)**:
- Correction de l'authentification dans les tests de défis logiques
- Amélioration de la gestion des transactions pour éviter les avertissements
- Support des fonctions asynchrones avec pytest-asyncio
- Nouveau test de vérification du démarrage du serveur
- Nouveaux endpoints pour les tentatives d'exercices et stats utilisateur

## Niveaux de difficulté (Thème Star Wars)
- **Initié**: Niveau facile pour débutants (nombres 1-10)
- **Padawan**: Niveau intermédiaire (nombres 10-50)
- **Chevalier**: Niveau difficile (nombres 50-100)
- **Maître**: Niveau expert (nombres 100-500)

## Types d'exercices
- **Addition**: Opérations d'addition adaptées au niveau
- **Subtraction** (Soustraction): Opérations de soustraction avec valeurs positives
- **Multiplication**: Tables de multiplication adaptées au niveau
- **Division**: Divisions sans reste adaptées au niveau
- **Mixed**: Combinaison de plusieurs types d'opérations

## Fonctionnalités majeures

### Génération d'exercices
- **Génération algorithmique**: Exercices générés avec paramètres prédéfinis selon le niveau
- **Génération pseudo-IA**: Exercices avec thème Star Wars et libellés plus élaborés
- **Personnalisation**: Filtres par type d'exercice et niveau de difficulté
- **Interface utilisateur**: Boutons distincts pour génération standard et IA

### Résolution d'exercices
- **Présentation claire**: Question en haut, choix de réponses en grille 2x2
- **Feedback immédiat**: Message de succès/échec et explication en cas d'erreur
- **Navigation fluide**: Passage facile à l'exercice suivant
- **Validation et enregistrement**: Stockage des résultats pour analyse

### Suivi de progression
- **Tableau de bord**: Vue d'ensemble des performances et statistiques
- **Statistiques par type**: Répartition des résultats par opération mathématique
- **Graphiques visuels**: Représentation visuelle des performances
- **Activité récente**: Historique des dernières interactions
- **Évolution temporelle**: Graphique montrant la progression au fil du temps

### API REST complète
- **Documentation OpenAPI**: Interface Swagger pour explorer et tester l'API
- **Endpoints CRUD**: Accès complet à toutes les entités
- **Validation robuste**: Sécurisation des entrées avec Pydantic
- **Gestion des erreurs**: Réponses standardisées et informatives
- **Suppression en cascade**: Gestion automatique des dépendances lors des suppressions

### Défis logiques
- **Types variés**: Défis visuels, abstraits, patterns, mots
- **Groupes d'âge**: Adaptation pour différentes tranches d'âge (10-11, 12-13, 14-15 ans)
- **Système d'indices**: 3 niveaux d'indices progressifs
- **Explication détaillée**: Solution expliquée en détail après résolution
- **Thématique Star Wars**: Défis enrichis par le thème de l'univers Star Wars

### Migration et compatibilité base de données
- **PostgreSQL pour production**: Haute performance et scalabilité
- **SQLite pour développement**: Facilité de développement local
- **Scripts de migration**: Transfert fluide entre les deux systèmes
- **Normalisation des données**: Cohérence des types et formats
- **Alembic pour les migrations**: Gestion professionnelle de l'évolution du schéma

### Système de tests
- **Architecture en 4 niveaux**: Tests unitaires, API, intégration, fonctionnels
- **Tests de suppression en cascade**: Validation du comportement à tous les niveaux
- **Couverture de code**: Analyses détaillées des parties couvertes et manquantes
- **Rapports automatisés**: Génération de rapports de test détaillés
- **Scripts d'exécution**: Interface simplifiée pour lancer les tests

## Modèle de données

### Schéma détaillé de la base de données

#### Table: exercises
```
[PK] id - SERIAL
[ ] title - VARCHAR(255) (NOT NULL)
[ ] creator_id - INTEGER (NULL)
[ ] exercise_type - VARCHAR(50) (NOT NULL)
[ ] difficulty - VARCHAR(50) (NOT NULL)
[ ] tags - VARCHAR(255)
[ ] question - TEXT (NOT NULL)
[ ] correct_answer - VARCHAR(255) (NOT NULL)
[ ] choices - JSON
[ ] explanation - TEXT
[ ] hint - TEXT
[ ] image_url - VARCHAR(255)
[ ] audio_url - VARCHAR(255)
[ ] is_active - BOOLEAN
[ ] is_archived - BOOLEAN
[ ] ai_generated - BOOLEAN
[ ] view_count - INTEGER
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
```

#### Table: results
```
[PK] id - SERIAL
[ ] exercise_id - INTEGER (NOT NULL)
[ ] user_id - INTEGER
[ ] session_id - VARCHAR(255)
[ ] is_correct - BOOLEAN (NOT NULL)
[ ] created_at - TIMESTAMP WITH TIME ZONE
```

#### Table: user_stats
```
[PK] id - SERIAL
[ ] exercise_type - VARCHAR(50) (NOT NULL)
[ ] difficulty - VARCHAR(50) (NOT NULL)
[ ] total_attempts - INTEGER
[ ] correct_attempts - INTEGER
[ ] last_updated - TIMESTAMP WITH TIME ZONE
```

#### Table: users
```
[PK] id - SERIAL
[ ] username - VARCHAR(255) (NOT NULL)
[ ] email - VARCHAR(255) (NOT NULL)
[ ] hashed_password - VARCHAR(255) (NOT NULL)
[ ] full_name - VARCHAR(255)
[ ] role - ENUM (user, admin, teacher)
[ ] is_active - BOOLEAN
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
[ ] grade_level - INTEGER
[ ] learning_style - VARCHAR(255)
[ ] preferred_difficulty - VARCHAR(255)
[ ] preferred_theme - VARCHAR(255)
[ ] accessibility_settings - VARCHAR(255)
```

#### Table: attempts
```
[PK] id - SERIAL
[ ] user_id - INTEGER (NOT NULL)
[ ] exercise_id - INTEGER (NOT NULL)
[ ] user_answer - VARCHAR(255) (NOT NULL)
[ ] is_correct - BOOLEAN (NOT NULL)
[ ] time_spent - REAL
[ ] attempt_number - INTEGER
[ ] hints_used - INTEGER
[ ] device_info - VARCHAR(255)
[ ] created_at - TIMESTAMP WITH TIME ZONE
```

#### Table: progress
```
[PK] id - SERIAL
[ ] user_id - INTEGER (NOT NULL)
[ ] exercise_type - VARCHAR(255) (NOT NULL)
[ ] difficulty - VARCHAR(255) (NOT NULL)
[ ] total_attempts - INTEGER
[ ] correct_attempts - INTEGER
[ ] average_time - REAL
[ ] completion_rate - REAL
[ ] streak - INTEGER
[ ] highest_streak - INTEGER
[ ] mastery_level - INTEGER
[ ] awards - JSON
[ ] strengths - VARCHAR(255)
[ ] areas_to_improve - VARCHAR(255)
[ ] recommendations - VARCHAR(255)
[ ] last_updated - TIMESTAMP WITH TIME ZONE
```

#### Table: logic_challenges
```
[PK] id - SERIAL
[ ] title - VARCHAR(255) (NOT NULL)
[ ] creator_id - INTEGER
[ ] challenge_type - ENUM (visual, abstract, pattern, word)
[ ] age_group - ENUM (10-11, 12-13, 14-15)
[ ] description - TEXT (NOT NULL)
[ ] visual_data - JSON
[ ] correct_answer - VARCHAR(255) (NOT NULL)
[ ] solution_explanation - TEXT (NOT NULL)
[ ] hint_level1 - TEXT
[ ] hint_level2 - TEXT
[ ] hint_level3 - TEXT
[ ] difficulty_rating - REAL
[ ] estimated_time_minutes - INTEGER
[ ] success_rate - REAL
[ ] image_url - VARCHAR(255)
[ ] source_reference - VARCHAR(255)
[ ] tags - VARCHAR(255)
[ ] is_template - BOOLEAN
[ ] generation_parameters - JSON
[ ] is_active - BOOLEAN
[ ] is_archived - BOOLEAN
[ ] view_count - INTEGER
[ ] created_at - TIMESTAMP WITH TIME ZONE
[ ] updated_at - TIMESTAMP WITH TIME ZONE
```

#### Table: schema_version
```
[PK] version - INTEGER
```

#### Table: alembic_version
```
[PK] version_num - VARCHAR(32) (NOT NULL)
```

## Mises à jour récentes

### Système unifié de gestion des transactions
- **TransactionManager** - Gestionnaire de contexte pour les transactions de base de données:
  - Commit et rollback automatiques pour les transactions
  - Méthodes sécurisées pour la suppression et l'archivage
  - Journalisation détaillée des opérations
- **DatabaseAdapter** - Interface unifiée pour les opérations de base de données:
  - Support pour SQLAlchemy et requêtes SQL brutes
  - Filtrage automatique des objets archivés
  - Méthodes standardisées pour les opérations CRUD
- **EnhancedServerAdapter** - Adaptateur pour l'intégration avec enhanced_server.py:
  - Conversion des requêtes SQL directes en appels aux services métier
  - Gestion coherente des sessions SQLAlchemy
  - Prise en charge des endpoints clés (delete_exercise, submit_answer, get_exercises_list)
  - Migration progressive du serveur Starlette vers le système de transaction unifié
- **Services métier** pour chaque domaine fonctionnel:
  - ExerciseService pour la gestion des exercices
  - LogicChallengeService pour les défis logiques
  - UserService pour la gestion des utilisateurs
- Tests complets pour le système de transaction et l'adaptateur

### Interface utilisateur holographique
- Implémentation d'une interface holographique style Star Wars pour les exercices
- Effet de texte doré avec halo bleu et animations adaptatives selon le niveau de difficulté
- Préparation du système de feedback sonore avec fichiers audio de sabre laser
- Correction des problèmes d'affichage des exercices archivés dans les listes
- Résolution du défilement automatique indésirable lors des changements de page et de vue

### Fonctionnalités d'accessibilité
- **Barre d'outils d'accessibilité** flottante disponible sur toutes les pages:
  - Mode contraste élevé (Alt+C) - Améliore le contraste pour meilleure lisibilité
  - Texte plus grand (Alt+T) - Augmente la taille du texte de 20%
  - Réduction des animations (Alt+M) - Pour utilisateurs photosensibles
  - Mode dyslexie (Alt+D) - Police adaptée et espacement des lettres amélioré
- **Persistance des préférences** via localStorage
- **Support des préférences système** (media queries `prefers-contrast`, `prefers-reduced-motion`)
- **Compatibilité avec technologies d'assistance** (lecteurs d'écran, navigation clavier)
- **Conformité WCAG 2.1 AA** pour toute l'interface

### Scripts de migration sécurisée
- **safe_migrate.py** - Script qui effectue les migrations Alembic avec mesures de sécurité:
  - Sauvegarde automatique de la base de données avant migration
  - Vérification post-migration de l'intégrité des tables protégées
  - Journal détaillé des opérations
  - Restauration automatique en cas d'échec

### Suppression en cascade
- Implémentation complète des relations avec `cascade="all, delete-orphan"` dans les modèles SQLAlchemy
- Documentation des suppressions en cascade dans `docs/CASCADE_DELETION.md`
- Création de tests à tous les niveaux pour valider le comportement
- Mise à jour des endpoints de suppression avec documentation OpenAPI
- Correction des problèmes dans `enhanced_server.py` pour la suppression d'exercices

### Améliorations des tests
- **Nouveaux tests de suppression en cascade**:
  - Tests unitaires: `test_cascade_relationships.py`
  - Tests d'intégration: `test_cascade_deletion.py`
  - Tests API: `test_deletion_endpoints.py`
  - Tests fonctionnels: `test_starlette_cascade_deletion.py`
- **Correction des tests existants**:
  - Adaptation aux changements de schéma
  - Ajout d'authentification pour les tests qui en nécessitent
  - Utilisation de noms d'utilisateurs uniques pour éviter les conflits
  - Gestion des erreurs avec `pytest.skip()` pour les tests problématiques

### Amélioration des scripts de test
- **Refactoring de `run_tests.py`**:
  - Utilisation de logging standard au lieu de loguru
  - Gestion propre des handlers de log
  - Fermeture correcte des ressources
  - Meilleur support des options en ligne de commande
- **Mise à jour de `run_tests.bat`**:
  - Support UTF-8 avec `chcp 65001`
  - Meilleure gestion des options
  - Formatage cohérent des messages
  - Documentation des options disponibles

### Résultats de test actuels
- **58 tests passent avec succès**
- **1 test est ignoré** pour une raison valide:
  - Test nécessitant une base de données PostgreSQL (sur environnement SQLite)
- **0 échecs** (tous les problèmes ont été résolus)
- **Couverture de code de 64%**

### Documentation mise à jour
- **README.md**: Mise à jour avec les nouvelles fonctionnalités
- **TABLE_DES_MATIERES.md**: Ajout des références aux suppressions en cascade
- **tests/README.md**: Documentation des tests de suppression en cascade
- **tests/TEST_PLAN.md**: Plan de test mis à jour avec les nouvelles fonctionnalités
- **docs/CASCADE_DELETION.md**: Documentation détaillée du système de suppression en cascade
- **docs/API_REFERENCE.md**: Documentation des endpoints de suppression

### Tâches à venir
- Amélioration de la couverture de test des services métier
- Complétion des tests manquants pour la génération d'exercices
- Résolution des avertissements mineurs
- Déploiement des nouvelles fonctionnalités en production

## Remarques spéciales pour le développement

- Les tests de suppression en cascade sont essentiels avant toute modification des modèles
- L'architecture dual-backend (FastAPI/Starlette) nécessite des tests spécifiques pour chaque implémentation
- La migration vers PostgreSQL nécessite attention aux différences de types entre SQLite
- Les changements UI doivent respecter le thème Star Wars établi
- La compatibilité Python 3.13 est une priorité pour la maintenabilité future
- Les migrations Alembic doivent être vérifiées manuellement avant application pour préserver les tables héritées

### Système de journalisation et débogage

Le projet utilise un système de journalisation centralisé qui est essentiel au développement et à la maintenance :

- **Importance pour le débogage** : Le système de logs permet d'identifier rapidement l'origine des problèmes en production et développement
- **Structure standardisée** : Tous les logs suivent le même format permettant une analyse cohérente
- **Isolation par niveau** : La séparation des logs par niveaux (debug.log, error.log, etc.) facilite l'analyse ciblée
- **Rotation des fichiers** : Les fichiers logs sont automatiquement divisés et compressés pour éviter de saturer le disque
- **Conservation limitée** : Les anciens logs sont automatiquement supprimés après 30-60 jours selon leur importance
- **Test du système** : Le script `test_logging.py` permet de vérifier le bon fonctionnement du système de logs

#### Bonnes pratiques pour la journalisation

1. **Utiliser la fonction centralisée** : Toujours importer via `from app.core.logging_config import get_logger`
2. **Nommer correctement le logger** : Utiliser `logger = get_logger(__name__)` pour identifier la source
3. **Choisir le bon niveau** : 
   - DEBUG pour information détaillée utile en développement
   - INFO pour confirmer le déroulement normal
   - WARNING pour les situations anormales mais non critiques
   - ERROR pour les problèmes empêchant une fonctionnalité
   - CRITICAL pour les problèmes bloquants
4. **Enrichir avec le contexte** : Utiliser `logger.bind(user_id=123).info("Action")` pour ajouter des métadonnées
5. **Capturer les exceptions** : Utiliser `logger.exception()` dans les blocs `except` pour enregistrer la stack trace

### Système de migrations Alembic

L'implémentation d'Alembic permet une gestion professionnelle de l'évolution du schéma de base de données tout en préservant les tables héritées:

1. **Protection des tables héritées**: Configuration spéciale dans `env.py` pour éviter la suppression des tables existantes
2. **Structure en deux phases**: Une migration initiale documentant l'état existant et une baseline servant de point de départ
3. **Scripts utilitaires**:
   - `init_alembic.py` pour initialiser la table alembic_version
   - `generate_migration.py` pour créer des migrations sécurisées
   - `alembic_demo.py` pour démontrer le processus complet
4. **Documentation complète**: Guide détaillé dans `docs/ALEMBIC.md`
5. **Vérification automatique des migrations**: Détection des opérations potentiellement dangereuses

#### Bonnes pratiques pour les migrations

1. **Toujours vérifier les migrations générées** avant application
2. **Faire des sauvegardes** avant d'appliquer des migrations importantes
3. **Tester dans un environnement de développement** avant la production
4. **Utiliser les scripts dédiés** plutôt que les commandes Alembic directes
5. **Documenter les changements** dans le CHANGELOG

Cette architecture est conçue pour être extensible, maintenable et évolutive, permettant l'ajout futur de nouvelles fonctionnalités comme l'authenticité, la personnalisation avancée et la gamification.

## 💾 Système d'archivage (Les Archives du Temple Jedi)

### Principes fondamentaux
- Les exercices ne sont JAMAIS supprimés physiquement
- Utilisation du champ `is_archived` pour marquer les exercices archivés
- Conservation de toutes les données associées (tentatives, statistiques, historique)
- Interface dédiée "Les Archives du Temple Jedi"

### Rôles et permissions
- Gardiens du Temple : Peuvent archiver des exercices
- Archivistes : Peuvent archiver et restaurer des exercices
- Logs détaillés de toutes les opérations d'archivage

### Implémentation technique
```python
# Exemple d'archivage dans ExerciseService
@staticmethod
def archive_exercise(db: Session, exercise_id: int) -> bool:
    exercise = ExerciseService.get_exercise(db, exercise_id)
    if not exercise:
        logger.error(f"Exercice avec ID {exercise_id} non trouvé pour archivage")
        return False
    
    exercise.is_archived = True
    exercise.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True
```

### Interface utilisateur
- Section spéciale "Les Archives du Temple Jedi"
- Filtres pour afficher/masquer les exercices archivés
- Boutons d'archivage et de restauration
- Messages de confirmation thématiques

## 🧪 Tests et validation

### Structure des tests
```
tests/
├── unit/                 # Tests unitaires
│   ├── test_models.py
│   └── test_services.py
├── api/                  # Tests API
│   ├── test_endpoints.py
│   └── test_archive.py
├── integration/          # Tests d'intégration
│   └── test_cascade.py
└── functional/          # Tests fonctionnels
    └── test_ui.py
```

### Tests d'archivage
- Vérification de la conservation des données
- Tests des permissions des rôles
- Validation de l'interface utilisateur
- Tests de restauration des archives

## 📊 Statistiques et progression

### Niveaux de difficulté
- **Initié**: Nombres 1-10
- **Padawan**: Nombres 10-50
- **Chevalier**: Nombres 50-100
- **Maître**: Nombres 100-500

### Types d'exercices
- Addition
- Soustraction
- Multiplication
- Division
- Mixte (combinaison)

### Suivi de progression
- Taux de réussite par type
- Séries (streaks) et records
- Recommandations personnalisées
- Rapports détaillés

## 🛠️ Outils et commandes

### CLI (mathakine_cli.py)
```bash
# Démarrage du serveur
python mathakine_cli.py run

# Tests
python mathakine_cli.py test --all
python mathakine_cli.py test --unit
python mathakine_cli.py test --api

# Base de données
python mathakine_cli.py init
python mathakine_cli.py migrate
```

### Scripts utilitaires
- check_project.py : Vérification de la santé du projet
- toggle_database.py : Basculement SQLite/PostgreSQL
- generate_context.py : Génération du contexte

## 📝 Documentation

### Structure
```
docs/
├── Core/                # Documentation principale
│   ├── PROJECT_STATUS.md
│   └── IMPLEMENTATION_PLAN.md
├── Tech/               # Documentation technique
│   ├── API_REFERENCE.md
│   └── DATABASE_GUIDE.md
└── ARCHIVE/           # Documentation archivée
```

### Points clés
- Documentation exhaustive dans docs/
- Guide de démarrage rapide (QUICKSTART.md)
- Documentation API avec Swagger/OpenAPI
- Guides techniques détaillés

## ⚠️ Points d'attention

### Sécurité
- Protection contre la suppression physique
- Journalisation des opérations sensibles
- Gestion stricte des rôles et permissions
- Validation des données avec Pydantic

### Performance
- Cache pour les données fréquentes
- Optimisation des requêtes SQL
- Lazy loading des composants UI
- Compression des assets

### Maintenance
- Tests automatisés complets
- Documentation à jour
- Logs détaillés
- Sauvegardes régulières

## 🎯 Prochaines étapes

### Court terme (Juillet 2025)
1. Finalisation interface holographique
2. Complétion système de rôles
3. Optimisation performances
4. Documentation des nouveautés

### Moyen terme (Août-Sept 2025)
1. Défis logiques complets
2. Système adaptatif
3. Support multilingue
4. Migration microservices

### Long terme (Q4 2025)
1. IA avancée
2. Réalité augmentée
3. Mode multijoueur
4. Extension mobile

## 📈 État actuel
- 58 tests réussis
- 1 test ignoré (PostgreSQL spécifique)
- 0 échecs
- Couverture code: 64%
- Temps d'exécution moyen: ~25 secondes