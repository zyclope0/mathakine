# Guide de Compatibilité - Mathakine

Ce document détaille les problèmes de compatibilité connus et leurs solutions pour le projet Mathakine.

## Compatibilité Python

### Python 3.13+

Python 3.13 a introduit des changements qui peuvent affecter la compatibilité avec certaines bibliothèques utilisées dans Mathakine.

| Composant | Problème | Solution |
|-----------|----------|----------|
| SQLAlchemy < 2.0.27 | Incompatible avec Python 3.13 | Mettre à jour vers SQLAlchemy 2.0.27+ |
| Pydantic < 2.0 | `BaseSettings` déplacé | Utiliser `pydantic-settings` |
| FastAPI < 0.100.0 | Problèmes divers | Mettre à jour vers FastAPI 0.100.0+ |

### Solution Recommandée

```bash
# Installation des versions compatibles
pip install sqlalchemy>=2.0.27 fastapi>=0.100.0 pydantic>=2.0.0 pydantic-settings
```

### Modifications de Code Nécessaires

1. **Pour Pydantic 2.0+**

Remplacer:
```python
from pydantic import BaseSettings
```

Par:
```python
from pydantic_settings import BaseSettings
```

2. **Pour Pydantic 2.0+ (validateurs)**

Remplacer:
```python
from pydantic import validator
```

Par:
```python
from pydantic import field_validator
```

3. **Pour SQLAlchemy 2.0+**

Remplacer:
```python
from sqlalchemy.ext.declarative import declarative_base
```

Par:
```python
from sqlalchemy.orm import declarative_base
```

4. **Pour FastAPI (gestion du cycle de vie)**

Remplacer:
```python
@app.on_event("startup")
async def startup_event():
    # ...

@app.on_event("shutdown")
async def shutdown_event():
    # ...
```

Par:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # ...
    
    yield
    
    # Shutdown
    # ...

app = FastAPI(lifespan=lifespan)
```

## Compatibilité des Frameworks

### SQLAlchemy

| Version | Compatibilité | Remarques |
|---------|---------------|-----------|
| < 2.0.0 | ❌ Python 3.13 | Utiliser <3.13 ou mettre à jour |
| 2.0.0 - 2.0.26 | ❌ Python 3.13 | Mettre à jour vers 2.0.27+ |
| 2.0.27+ | ✅ Python 3.13 | Compatible |

### Pydantic

| Version | Compatibilité | Remarques |
|---------|---------------|-----------|
| < 2.0.0 | ⚠️ Python 3.13 | Utiliser pydantic-settings |
| 2.0.0+ | ✅ Python 3.13 | Compatible avec modifications |

### FastAPI

| Version | Compatibilité | Remarques |
|---------|---------------|-----------|
| < 0.95.0 | ❌ Python 3.13 | Utiliser <3.13 ou mettre à jour |
| 0.95.0 - 0.99.0 | ⚠️ Python 3.13 | Compatible avec avertissements |
| 0.100.0+ | ✅ Python 3.13 | Compatible |

## Vérification de Compatibilité

Pour vérifier automatiquement la compatibilité de votre environnement:

```bash
python tests/compatibility_check.py
```

## Rapport de Compatibilité Complet

Pour un rapport détaillé incluant la compatibilité:

```bash
python tests/generate_report.py --include-compatibility
```

## Environnement Virtuel Recommandé

Pour une compatibilité maximale, nous recommandons la configuration suivante:

```bash
python -m venv venv-mathakine
source venv-mathakine/bin/activate  # Sous Linux/Mac
# ou
venv-mathakine\Scripts\activate  # Sous Windows

pip install -r requirements.txt
```

## Résolution des Problèmes Courants

| Erreur | Cause Probable | Solution |
|--------|----------------|----------|
| `ImportError: cannot import name 'declarative_base'` | SQLAlchemy ancien avec Python 3.13 | Mettre à jour SQLAlchemy |
| `ImportError: cannot import name 'BaseSettings'` | Pydantic 2.0+ sans pydantic-settings | Installer pydantic-settings |
| `TypeError: FastAPI() got an unexpected keyword argument 'lifespan'` | FastAPI trop ancien | Mettre à jour FastAPI |

## Compatibilité Future

L'équipe de développement maintient ce document à jour avec chaque nouvelle version de Python ou des dépendances majeures. Consultez ce document régulièrement pour vous assurer de la compatibilité de votre environnement.

# Compatibilité Python 3.13 et Pydantic v2

Ce document détaille les mesures prises pour assurer la compatibilité du projet Mathakine avec Python 3.13 et Pydantic v2.

## Python 3.13

### Changements importants dans Python 3.13

Python 3.13 a introduit plusieurs changements qui ont nécessité des adaptations dans notre code :

1. **Nouvelle syntaxe asyncio** : Utilisation des contextes asynchrones modernes
2. **Changements d'API dans les bibliothèques standard** : Notamment dans les modules `asyncio`, `typing` et `pathlib`
3. **Améliorations de performance** : Optimisations pour tirer parti des améliorations de performance

### Adaptations réalisées

1. **Mise à jour des dépendances** :
   - SQLAlchemy 2.0+
   - FastAPI 0.100+
   - Pydantic 2.0+
   - pytest 7.0+

2. **Modifications de code** :
   - Remplacement des décorateurs `@asynccontextmanager` par les gestionnaires `lifespan` de FastAPI
   - Mise à jour des annotations de type
   - Conversion des f-strings imbriqués vers une syntaxe compatible

## Pydantic v2

### Changements majeurs dans Pydantic v2

1. **Nouvelle API pour la définition des modèles**
2. **Performance améliorée** 
3. **Validation plus stricte**
4. **Meilleur support pour les types génériques**

### Adaptations réalisées

1. **Mise à jour des modèles** :
   - Utilisation de `Field` au lieu de `field`
   - Adaptation des validateurs avec la nouvelle syntaxe
   - Utilisation de `model_config` au lieu de `Config`

2. **Configuration** :
   - Migration de `BaseSettings` vers `pydantic-settings`
   - Utilisation de `model_json_schema` au lieu de `schema`

3. **Tests** :
   - Mise à jour des fonctions de test pour tenir compte de la validation plus stricte

## SQLAlchemy 2.0

1. **Utilisation de la nouvelle API** :
   - Migration vers la syntaxe 2.0 recommandée
   - Mise à jour des requêtes pour utiliser `select()` au lieu de `.query()`

2. **Gestion des sessions** :
   - Utilisation de l'approche moderne de contexte pour les sessions

## Rapports de compatibilité

### Tests automatisés

Tous les tests automatisés ont été mis à jour pour fonctionner avec Python 3.13 et les nouvelles versions des bibliothèques. Nous avons également ajouté des tests spécifiques pour vérifier la compatibilité.

### CI/CD

Le pipeline CI/CD a été configuré pour tester automatiquement la compatibilité avec Python 3.13 pour chaque commit.

---

*Dernière mise à jour: 20/04/2025* 