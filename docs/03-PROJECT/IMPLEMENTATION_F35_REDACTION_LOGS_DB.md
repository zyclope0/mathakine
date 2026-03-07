# Implementation F35 - Redaction secrets logs DB

## Statut

- Statut : Implemente le 07/03/2026
- Portee : redaction URL DB au log de demarrage + tests unitaires de non-regression

## Objectif

Corriger un risque de securite dans `app/db/base.py` :

- aujourd'hui le demarrage loggue `settings.SQLALCHEMY_DATABASE_URL` en clair
- cette URL peut contenir `user`, `password`, host interne, port et query params
- ce comportement n'est pas acceptable en production ni en CI

Reference produit/securite :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` -> F35
- `docs/03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md`

## Probleme actuel

Code actuel :

```py
logger.info(f"Initialisation de la base de donnees: {settings.SQLALCHEMY_DATABASE_URL}")
```

Risque :

- exposition de credentials dans logs applicatifs
- fuite potentielle dans CI/CD, Sentry breadcrumbs, journaux Docker ou PaaS
- non alignement avec la politique interne de redaction

## Strategie retenue

Faire un correctif minimal, robuste et testable :

1. Extraire une fonction pure de redaction de l'URL DB.
2. Logger une version sure de l'URL.
3. Ne pas modifier la creation du moteur SQLAlchemy.
4. Ajouter un test unitaire sur la fonction de redaction.

## Scope in

- `app/db/base.py`
- eventuellement une petite fonction helper locale dans ce fichier
- un test unitaire dedie

## Scope out

- aucune modification du `create_engine(...)`
- aucun changement de `settings.SQLALCHEMY_DATABASE_URL`
- aucune refonte globale du systeme de logs
- aucune modification des autres logs applicatifs dans ce lot

## Exigences techniques

### Fonction de redaction

Ajouter une fonction testable, par exemple :

```py
def redact_database_url_for_log(raw_url: str) -> str:
    ...
```

Contraintes :

- ne jamais retourner le mot de passe
- ne jamais retourner le username complet s'il est present
- ne pas logger les query params
- si le parsing echoue, retourner une valeur sure du type `[redacted-db-url]`

### Format de log recommande

Format prefere :

```text
postgresql://<redacted>@db-host:5432/mathakine
```

Acceptable aussi :

```text
dialect=postgresql host=db-host port=5432 db=mathakine
```

Le point important est :

- pas de password
- pas de query string
- pas de secret partiel ambigu

### Robustesse

La fonction doit couvrir au minimum :

- URL PostgreSQL complete avec user/password
- URL sans password
- URL SQLite
- URL invalide ou vide

## Fichiers cibles probables

- `app/db/base.py`
- `tests/unit/test_db_log_redaction.py`

## Criteres d'acceptation

1. Le log de demarrage DB ne contient plus jamais l'URL complete.
2. Un mot de passe de type `:secret@` n'apparait plus dans les logs.
3. Les query params de connexion n'apparaissent plus.
4. Le moteur SQLAlchemy continue de demarrer sans regression.
5. La fonction de redaction est couverte par un test unitaire.

## Tests obligatoires

### Python

- test unitaire de la fonction de redaction
- verification qu'une URL avec password est correctement masque
- verification qu'une URL invalide retourne un fallback sur

### Non regression

- le module `app/db/base.py` reste importable
- pas de changement de comportement sur la creation `engine`

## Commandes de validation avant commit

Depuis la racine du repo :

```bash
pytest tests/unit/test_db_log_redaction.py
black app/ server/ tests/ --check
```

Si le projet utilise aussi ces controles localement, les executer si disponibles :

```bash
npx tsc --noEmit --project frontend/tsconfig.json
```

## Contraintes pour Cursor

- faire un commit separe pour F35
- ne pas melanger F35 avec une feature produit
- ne pas toucher a d'autres fichiers de logs hors scope
- ne pas introduire de dependance externe pour parser une URL

## Definition of done

F35 est termine si :

- la redaction est en place
- le test unitaire passe
- `black --check` passe
- le diff est petit, cible, lisible
