# Guide de maintenance du projet Mathakine

Ce document explique comment maintenir efficacement le code base de Mathakine, incluant le nettoyage de fichiers obsolètes, les mises à jour de dépendances, et les bonnes pratiques de maintenance.

## Détection et nettoyage des fichiers obsolètes

Le projet inclut un script spécialisé pour identifier les fichiers qui ne sont probablement plus utilisés avec un niveau de confiance élevé (99%).

### Fonctionnement de la détection

Le script `scripts/detect_obsolete_files.py` utilise plusieurs techniques pour identifier les fichiers obsolètes :

1. **Analyse des importations Python** : Détecte les fichiers Python qui ne sont jamais importés
2. **Recherche de références** : Vérifie si un fichier est référencé n'importe où dans le code
3. **Modèles de nommage** : Identifie les fichiers avec préfixes/suffixes typiques de fichiers obsolètes (_old, .bak, etc.)
4. **Analyse temporelle** : Compare les dates de modification avec l'activité globale du projet
5. **Heuristiques avancées** : Vérifie l'existence de versions "propres" de fichiers avec suffixes d'obsolescence

### Utilisation du script

#### 1. Détection simple

Pour simplement lister les fichiers potentiellement obsolètes :

```bash
python -m scripts.detect_obsolete_files
```

#### 2. Mode détaillé

Pour obtenir des informations sur les raisons pour lesquelles un fichier est considéré comme obsolète :

```bash
python -m scripts.detect_obsolete_files --verbose
```

#### 3. Déplacement au lieu de suppression

Pour déplacer les fichiers obsolètes vers un répertoire d'archives (recommandé avant suppression) :

```bash
python -m scripts.detect_obsolete_files --move-to archives/obsolete
```

#### 4. Suppression automatique

Pour supprimer directement les fichiers avec un niveau de confiance très élevé (>95%) :

```bash
python -m scripts.detect_obsolete_files --delete
```

**ATTENTION** : Cette opération est irréversible. Utilisez d'abord l'option `--move-to` pour vérifier.

#### 5. Ajustement du seuil de confiance

Pour ajuster le niveau minimum de confiance (par défaut 85%) :

```bash
python -m scripts.detect_obsolete_files --confidence 90
```

#### 6. Génération d'un rapport détaillé

Pour générer un rapport détaillé au format JSON avec des informations complètes sur chaque fichier détecté :

```bash
python -m scripts.detect_obsolete_files --report rapport_obsolescence.json
```

Ce rapport inclut :
- Des statistiques globales sur les fichiers analysés
- La date de l'analyse
- Des informations détaillées sur chaque fichier potentiellement obsolète
- Des indications sur l'historique Git des fichiers (si disponible)
- Les raisons précises pour lesquelles chaque fichier est considéré comme obsolète

Le rapport peut être utilisé pour :
- Archiver l'historique des nettoyages
- Analyser les tendances d'accumulation de fichiers obsolètes
- Partager les résultats avec l'équipe de développement
- Automatiser des actions basées sur les résultats (via des scripts personnalisés)

### Processus recommandé pour le nettoyage

1. Exécutez d'abord le script en mode verbose pour comprendre quels fichiers sont détectés et pourquoi
2. Déplacez ensuite les fichiers vers un répertoire d'archives temporaire
3. Vérifiez que l'application fonctionne toujours correctement
4. Une fois que vous êtes sûr que les fichiers ne sont pas nécessaires, vous pouvez les supprimer définitivement

```bash
# Étape 1 : Analyser
python -m scripts.detect_obsolete_files --verbose

# Étape 2 : Déplacer
python -m scripts.detect_obsolete_files --move-to archives/temp_obsolete

# Étape 3 : Tester l'application pour vérifier qu'elle fonctionne

# Étape 4 : Supprimer définitivement
rm -rf archives/temp_obsolete
```

## Autres tâches de maintenance

### Mise à jour des dépendances

Pour mettre à jour toutes les dépendances à leurs dernières versions compatibles :

```bash
pip install -U -r requirements.txt
```

Pour vérifier les dépendances obsolètes :

```bash
pip list --outdated
```

### Nettoyage des fichiers de cache

```bash
# Nettoyer les fichiers de cache Python
find . -name __pycache__ -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Nettoyer les fichiers de cache pytest
rm -rf .pytest_cache
```

### Optimisation de la base de données

Pour optimiser la base de données SQLite :

```bash
python scripts/optimize_db.py
```

### Vérification de cohérence

Pour vérifier la cohérence globale du projet :

```bash
python tests/run_all_checks.py
```

## Bonnes pratiques

1. **Toujours faire des sauvegardes** avant d'effectuer des opérations de nettoyage majeures
2. **Exécuter la suite de tests complète** après toute opération de maintenance
3. **Documenter les changements** effectués pendant la maintenance
4. **Utiliser Git** pour suivre les modifications et pouvoir revenir en arrière si nécessaire

## Récapitulatif des commandes principales

| Tâche | Commande |
|------|----------|
| Détecter fichiers obsolètes | `python -m scripts.detect_obsolete_files --verbose` |
| Déplacer fichiers obsolètes | `python -m scripts.detect_obsolete_files --move-to archives/obsolete` |
| Supprimer fichiers obsolètes | `python -m scripts.detect_obsolete_files --delete` |
| Mettre à jour dépendances | `pip install -U -r requirements.txt` |
| Exécuter tous les tests | `python -m tests.run_tests` |
| Vérifier style de code | `python -m scripts.check_pydantic_validators` |

## Fréquence recommandée

- **Détection de fichiers obsolètes** : Après chaque itération majeure du projet
- **Mise à jour des dépendances** : Tous les 2-3 mois ou avant une nouvelle fonctionnalité importante
- **Nettoyage complet** : Tous les 6 mois ou avant une mise en production majeure 