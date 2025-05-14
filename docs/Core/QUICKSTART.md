# Guide de Démarrage Rapide - Mathakine

## Pour les Développeurs

### Prérequis
- Python 3.9+
- PostgreSQL 13+ ou SQLite
- Git
- Node.js 18+ (pour le frontend)
- Docker (optionnel)

### Installation Rapide

1. **Cloner le projet**
   ```bash
   git clone https://github.com/mathakine/mathakine.git
   cd mathakine
   ```

2. **Configurer l'environnement Python**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # ou
   venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt
   ```

3. **Configurer la base de données**
   ```bash
   # SQLite (développement)
   cp .env.example .env
   # Modifier DB_TYPE=sqlite dans .env
   
   # PostgreSQL (optionnel)
   # Créer une base de données PostgreSQL
   # Modifier les variables DB_* dans .env
   ```

4. **Initialiser la base de données**
   ```bash
   python mathakine_cli.py init
   ```

5. **Lancer les tests**
   ```bash
   python -m tests.run_tests --all
   ```

6. **Démarrer le serveur**
   ```bash
   # Mode développement avec rechargement automatique
   python mathakine_cli.py run --dev
   
   # API uniquement
   python mathakine_cli.py run --api-only
   ```

### Accès aux interfaces

- Interface web : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- Interface admin : http://localhost:8000/admin
  - Login : admin@mathakine.fr
  - Mot de passe : admin123 (à changer)

### Outils de développement

1. **CLI Mathakine**
   ```bash
   # Aide générale
   python mathakine_cli.py --help
   
   # Commandes disponibles
   python mathakine_cli.py run    # Lancer le serveur
   python mathakine_cli.py init   # Initialiser la DB
   python mathakine_cli.py test   # Lancer les tests
   python mathakine_cli.py shell  # Shell Python
   ```

2. **Scripts utilitaires**
   ```bash
   # Vérification du code
   scripts/check_project.py
   
   # Correction du style
   scripts/fix_style.py
   
   # Migration base de données
   scripts/migrate_to_postgres.py
   ```

3. **Docker (optionnel)**
   ```bash
   # Construire l'image
   docker build -t mathakine .
   
   # Lancer le conteneur
   docker run -p 8000:8000 mathakine
   ```

### Structure du projet

```
mathakine/
├── app/              # Application principale
├── docs/            # Documentation
├── tests/           # Tests
├── scripts/         # Scripts utilitaires
└── services/        # Services métier
```

### Workflow de développement

1. Créer une branche pour votre fonctionnalité
2. Développer et tester localement
3. Exécuter les tests et vérifier le style
4. Créer une Pull Request

### Ressources utiles

- [Guide de contribution](CONTRIBUTING.md)
- [Documentation technique](../Tech/)
- [Guide des tests](../Tech/TESTING.md)
- [Architecture](ARCHITECTURE_DIAGRAMS.md)

### Besoin d'aide ?

- Discord : [discord.mathakine.fr](https://discord.mathakine.fr)
- Email : dev@mathakine.fr
- Issues GitHub : [github.com/mathakine/issues](https://github.com/mathakine/issues)

## Fonctionnalités principales

### 1. Exercices mathématiques
- Types : Addition, Soustraction, Multiplication, Division
- Niveaux : Initié, Padawan, Chevalier, Maître
- Génération automatique ou manuelle

### 2. Interface thématique Star Wars
- Design holographique
- Messages personnalisés
- Effets visuels thématiques

### 3. Suivi de progression
- Tableau de bord statistique
- Graphiques de performance
- Système de rangs

## Résolution des problèmes courants

### Base de données
```bash
# Réinitialiser la base de données
python mathakine_cli.py reset-db

# Vérifier les migrations
python scripts/check_migrations.py

# Problèmes courants
- Erreur "Database is locked":
  1. Vérifier qu'aucune autre instance n'est en cours
  2. Supprimer le fichier .db-journal s'il existe
  3. Redémarrer l'application

- Erreur "Alembic revision not found":
  1. Exécuter `alembic current` pour voir la version actuelle
  2. Utiliser `alembic stamp head` pour réinitialiser
  3. Relancer les migrations avec `alembic upgrade head`
```

### Serveur
```bash
# Nettoyer le cache
python mathakine_cli.py clean

# Redémarrer en mode debug
python mathakine_cli.py run --debug --reload

# Problèmes courants
- Erreur "Address already in use":
  1. Vérifier les processus : `netstat -ano | findstr :8000`
  2. Arrêter le processus : `taskkill /PID <pid> /F`

- Erreur "Module not found":
  1. Vérifier l'activation de l'environnement virtuel
  2. Réinstaller les dépendances : `pip install -r requirements.txt`
  3. Vérifier le PYTHONPATH
```

### Tests
```bash
# Vérifier la couverture
python -m tests.run_tests --coverage

# Tests spécifiques avec détails
python -m tests.run_tests --unit -v

# Problèmes courants
- Tests échoués avec SQLite:
  1. Vérifier les permissions du dossier
  2. Supprimer la base de test et relancer
  3. Utiliser `--reuse-db` pour déboguer

- Erreurs d'authentification dans les tests:
  1. Vérifier la présence du fichier .env.test
  2. Réinitialiser la base de test
  3. Vérifier les fixtures d'authentification
```

### Outils de diagnostic

#### 1. Logs système
```bash
# Voir les logs en temps réel
tail -f logs/app.log

# Filtrer les erreurs
grep ERROR logs/app.log

# Logs par composant
tail -f logs/api.log     # Logs API
tail -f logs/web.log     # Logs interface web
tail -f logs/db.log      # Logs base de données
```

#### 2. Débogage
```bash
# Mode debug détaillé
python mathakine_cli.py run --debug --log-level DEBUG

# Shell interactif avec contexte
python mathakine_cli.py shell

# Vérification de la configuration
python mathakine_cli.py validate --verbose
```

#### 3. Performance
```bash
# Profiling de base de données
python scripts/analyze_db_performance.py

# Statistiques serveur
python scripts/server_stats.py

# Analyse des requêtes lentes
python scripts/slow_queries.py
```

## Ressources

### Documentation
- [Guide complet](Core/DEVELOPER_GUIDE.md)
- [Architecture](Core/ARCHITECTURE.md)
- [Guide interface](Core/UI_GUIDE.md)
- [Diagrammes](Core/ARCHITECTURE_DIAGRAMS.md)

### Support
- GitHub Issues pour les bugs
- Discord pour l'aide en direct
- Wiki pour la documentation étendue

---

*Dernière mise à jour : 15 juin 2025* 