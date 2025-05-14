# Guide de démarrage rapide pour Mathakine

Ce guide vous aidera à mettre en place rapidement l'environnement de développement pour Mathakine et à exécuter l'application.

## Prérequis

- Python 3.11, 3.12 ou 3.13 (recommandé)
- Pip (gestionnaire de paquets Python)
- Environnement de développement (IDE) comme VS Code ou PyCharm
- Git pour le versionnement du code

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/votre-organisation/mathakine.git
   cd mathakine
   ```

2. **Configurer l'environnement avec le CLI**

   Mathakine est désormais équipé d'un outil en ligne de commande puissant qui simplifie la configuration. Utilisez la commande suivante :

   ```bash
   python mathakine_cli.py setup --full
   ```

   Cette commande va :
   - Créer un environnement virtuel Python
   - Installer toutes les dépendances
   - Initialiser la base de données avec des données de test
   - Configurer l'environnement de développement

   > **Remarque** : Sur Windows, vous pouvez également utiliser les scripts batch ou PowerShell inclus.

3. **Vérifier l'installation**

   Assurez-vous que tout fonctionne correctement en exécutant :

   ```bash
   python mathakine_cli.py validate --level simple
   ```

## Démarrage de l'application

L'application peut être facilement démarrée avec le CLI :

```bash
python mathakine_cli.py run --debug --reload
```

Options disponibles :
- `--debug` : Active le mode de débogage
- `--reload` : Active le rechargement à chaud (idéal pour le développement)
- `--port PORT` : Spécifie le port (défaut : 8081)
- `--host HOST` : Spécifie l'hôte (défaut : 127.0.0.1)

L'application sera accessible à l'adresse : http://127.0.0.1:8081

La documentation API est disponible à : http://127.0.0.1:8081/docs

## Structure du projet

```
mathakine-backend/
├── app/                     # Code principal de l'application
│   ├── api/                 # API REST (nouveaux endpoints séparés)
│   ├── core/                # Configuration et utilitaires
│   ├── db/                  # Accès à la base de données
│   ├── models/              # Modèles de données
│   ├── schemas/             # Schémas Pydantic
│   └── services/            # Services métier
├── mathakine_cli.py         # Nouvel outil CLI
└── ...
```

## Commandes CLI utiles

Le nouveau CLI `mathakine_cli.py` offre plusieurs commandes utiles :

```bash
# Initialiser ou réinitialiser la base de données
python mathakine_cli.py init --force

# Exécuter les tests
python mathakine_cli.py test --type unit
python mathakine_cli.py test --type api
python mathakine_cli.py test --coverage

# Ouvrir un shell Python interactif avec le contexte de l'application
python mathakine_cli.py shell

# Valider l'application
python mathakine_cli.py validate --level compatibility
```

## Base de données

Par défaut, l'application utilise SQLite. L'accès à la base de données a été modernisé et est maintenant compatible avec SQLAlchemy 2.0.

Vous pouvez facilement explorer les données via le shell interactif :

```bash
python mathakine_cli.py shell
```

Exemple d'utilisation dans le shell :
```python
# Lister tous les utilisateurs
users = session.query(User).all()

# Trouver un exercice par ID
exercise = session.query(Exercise).filter_by(id=1).first()

# Obtenir les tentatives d'un utilisateur
attempts = session.query(Attempt).filter_by(user_id=1).all()
```

## Développement

### API REST

L'API a été réorganisée avec une structure plus claire. Les nouveaux endpoints sont organisés par domaine fonctionnel. Pour ajouter un nouvel endpoint :

1. Créez ou modifiez un fichier dans `app/api/endpoints/`
2. Définissez vos routes avec FastAPI
3. Ajoutez le routeur dans `app/api/api.py`

### Modèles et schémas

Les modèles SQLAlchemy se trouvent dans `app/models/` et les schémas Pydantic dans `app/schemas/`. Assurez-vous que les deux restent synchronisés lors de vos modifications.

## Compatibilité Python 3.13

Mathakine est désormais compatible avec Python 3.13. Pour plus de détails, consultez [COMPATIBILITY.md](COMPATIBILITY.md).

## Documentation complète

Pour une documentation plus détaillée, consultez :
- [README.md](../../README.md) - Présentation générale du projet
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Architecture technique détaillée
- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - État du projet et roadmap
- [COMPATIBILITY.md](COMPATIBILITY.md) - Guide de compatibilité Python 3.13

## Besoin d'aide ?

Si vous rencontrez des problèmes ou avez des questions :
1. Consultez la section FAQ dans la documentation
2. Utilisez la commande `python mathakine_cli.py validate` pour diagnostiquer les problèmes
3. Créez une issue sur le dépôt Git du projet 