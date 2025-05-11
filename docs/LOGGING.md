# Système de Journalisation Centralisée

Ce document explique le système de journalisation centralisé mis en place dans le projet Mathakine.

## Objectifs

1. **Centralisation** : Tous les logs sont stockés dans un emplacement unique (`/logs`)
2. **Structuration** : Logs séparés par niveau et fonctionnalité
3. **Rotation** : Gestion automatique de la taille et de l'historique des logs
4. **Configurable** : Adaptation facile via les variables d'environnement
5. **Cohérent** : Même format et comportement dans tout le projet

## Architecture

Le système de journalisation utilise [loguru](https://github.com/Delgan/loguru), une bibliothèque Python simple et puissante.

### Structure des dossiers

```
logs/
├── all.log                 # Tous les logs (tous niveaux)
├── debug.log               # Logs de niveau DEBUG
├── info.log                # Logs de niveau INFO
├── warning.log             # Logs de niveau WARNING
├── error.log               # Logs de niveau ERROR
├── critical.log            # Logs de niveau CRITICAL
├── uncaught_exceptions.log # Exceptions non gérées
└── migration/              # Logs migrés des anciennes versions
    └── ...
```

### Configuration

La configuration de la journalisation est centralisée dans le module `app/core/logging_config.py`. Ce module :

1. Configure loguru pour écrire dans différents fichiers
2. Définit le format des messages de log
3. Configure la rotation et compression des fichiers
4. Gère la capture des exceptions non gérées

## Utilisation

### IMPORTANT: Ne jamais importer loguru directement dans les modules de l'application

L'ancien système utilisait des importations directes :
```python
# ❌ NE PLUS UTILISER cette approche
from loguru import logger
logger.info("Message")
```

Utilisez toujours le système centralisé :
```python
# ✅ UTILISER cette approche
from app.core.logging_config import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

### Dans le code Python

Pour utiliser le système de logs dans un module, importez la fonction `get_logger` :

```python
from app.core.logging_config import get_logger

# Obtenir un logger nommé
logger = get_logger(__name__)

# Utiliser le logger
logger.debug("Message de débogage")
logger.info("Information importante")
logger.warning("Attention !")
logger.error("Une erreur est survenue")
logger.critical("Erreur critique !")

# Avec contexte structuré
logger.bind(user_id=123).info("Action utilisateur")
```

### Niveaux de logs

- **DEBUG** : Informations détaillées, utiles pour le diagnostic
- **INFO** : Confirmation du bon déroulement des opérations
- **WARNING** : Indication d'un problème potentiel
- **ERROR** : Une erreur qui a empêché une fonction de s'exécuter correctement
- **CRITICAL** : Une erreur grave qui peut causer l'arrêt du programme

### Configuration par variables d'environnement

Les niveaux de logs et leur destination peuvent être configurés via les variables d'environnement :

- `LOG_LEVEL` : Niveau de log minimum ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
- `LOGS_DIR` : Dossier de destination des logs (par défaut: "logs")

## Migration des logs

Lors de la mise en place de ce système, des scripts sont disponibles pour migrer les anciens fichiers logs vers la nouvelle structure :

```bash
# Migration des logs existants
python -m scripts.migrate_logs

# Nettoyage des anciens fichiers logs (après vérification)
python -m scripts.cleanup_logs
```

Le script `migrate_logs.py` :
1. Recherche tous les fichiers .log dans le projet
2. Les copie dans le dossier logs/ avec un préfixe indiquant leur emplacement d'origine
3. Maintient les logs originaux en place jusqu'à ce qu'ils soient nettoyés manuellement

Le script `cleanup_logs.py` :
1. Trouve tous les fichiers .log hors du dossier logs/
2. Propose à l'utilisateur de les supprimer ou de les conserver
3. Crée une sauvegarde avant la suppression (optionnel)

## Bonnes pratiques

1. **Nommage** : Utilisez toujours `get_logger(__name__)` pour que les logs indiquent clairement leur source
2. **Contexte** : Ajoutez des informations contextuelles avec `logger.bind()`
3. **Niveau** : Choisissez le bon niveau de log selon l'importance du message
4. **Messages** : Soyez concis mais informatif, incluez les données pertinentes
5. **Exceptions** : Utilisez `logger.exception()` dans les blocs `except` pour inclure la trace complète

## Comment migrer un module vers le nouveau système

Pour mettre à jour un module existant utilisant l'ancien système de logs :

1. Remplacez `from loguru import logger` par `from app.core.logging_config import get_logger`
2. Ajoutez `logger = get_logger(__name__)` immédiatement après
3. Vérifiez que tous les appels au logger fonctionnent avec la nouvelle configuration

Exemple:

```python
# Ancien code
from loguru import logger
logger.info("Message")

# Nouveau code
from app.core.logging_config import get_logger
logger = get_logger(__name__)
logger.info("Message")
```

## Rotation et maintenance

Les fichiers logs sont automatiquement :
- Divisés lorsqu'ils atteignent 10-20 Mo
- Compressés avec zip
- Conservés pendant 30-60 jours selon leur importance

Aucune maintenance manuelle n'est nécessaire pour la gestion des logs.

## Déboggage avancé

Pour les cas difficiles à diagnostiquer, vous pouvez augmenter temporairement le niveau de détail :

```python
# Temporairement augmenter le niveau de détail pour un module
logger.bind(name="mon_module").debug("Message très détaillé").opt(depth=1).exception()
```

## Surveillance en temps réel

Pour surveiller les logs en temps réel, utilisez :

```bash
# Afficher tous les logs en temps réel
tail -f logs/all.log

# Afficher uniquement les erreurs en temps réel
tail -f logs/error.log
```

## Intégration avec d'autres systèmes

Le système a été conçu pour être facilement intégrable avec des outils comme ELK Stack (Elasticsearch, Logstash, Kibana) ou autres services de monitoring. Une configuration supplémentaire peut être ajoutée dans `app/core/logging_config.py` pour supporter ces intégrations. 