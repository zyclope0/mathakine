# ADR-003 : Modèle de concurrence gamification — SELECT FOR UPDATE conditionnel

**Date :** 2026-03-27
**Statut :** Accepté

---

## Contexte

Le service de gamification (`app/services/gamification/gamification_service.py`) attribue des points, met à jour le niveau et distribue des badges à chaque événement de complétion (exercice, défi, défi quotidien).

En production, le backend Mathakine s'exécute sous Gunicorn avec plusieurs workers (processus OS distincts). Chaque worker opère sur la même base PostgreSQL. Deux workers peuvent recevoir simultanément des requêtes de complétion pour le même utilisateur (ex. : double-clic client, retry réseau, complétion parallèle exercice + défi quotidien).

Sans verrou de ligne, la séquence suivante crée une race condition :

```
Worker A : SELECT user WHERE id=42 → total_points=100
Worker B : SELECT user WHERE id=42 → total_points=100
Worker A : UPDATE user SET total_points=110
Worker B : UPDATE user SET total_points=110  ← écrase la mise à jour de A
```

Résultat : un seul incrément effectif pour deux complétions, perte silencieuse de points.

Ce problème a été identifié lors de l'audit technique (2026-03-22, score P0) et résolu dans le même cycle de maintenance.

SQLite (utilisé dans les tests CI) ne supporte pas `SELECT FOR UPDATE` et lève une exception si ce mécanisme est appliqué sans discrimination.

---

## Décision

La requête de lecture de l'utilisateur dans `apply_points()` utilise `query.with_for_update()` conditionnellement au dialecte SQL actif :

```python
bind = db.get_bind()
is_postgres = bind.dialect.name == "postgresql"
query = db.query(User).filter(User.id == user_id)
if is_postgres:
    query = query.with_for_update()
user = query.one_or_none()
```

Ce pattern garantit :
1. Verrou exclusif de ligne sur PostgreSQL en production (sérialisation des mises à jour concurrentes).
2. Compatibilité totale avec SQLite en CI (branche `if is_postgres` non activée).

La condition est vérifiée à chaque appel, sans mise en cache de l'état du dialecte, pour éviter tout faux positif en cas de reconnexion ou de changement de contexte.

---

## Conséquences

### Positives

- Élimination de la race condition d'attribution de points entre workers Gunicorn.
- Aucun overhead en CI (SQLite) : les tests ne portent pas `FOR UPDATE`.
- Compatibilité future : si un autre dialecte SQL est introduit (ex. MySQL), la condition `dialect.name == "postgresql"` l'exclut par défaut (fail-safe).

### Négatives / Risques

- `with_for_update()` crée un verrou exclusif pendant la transaction : toute autre écriture concurrente sur la même ligne est bloquée jusqu'au `COMMIT`. Ce délai est négligeable pour des opérations courtes mais devient un goulot si la transaction `apply_points` inclut des opérations longues (appels réseau, etc.). Règle d'implémentation : maintenir `apply_points` strictement synchrone et sans I/O externe.
- La condition `bind.dialect.name == "postgresql"` est évaluée à chaque appel. Si le contexte DB est exceptionnel (pool exhausted, connection drop), `get_bind()` peut lever. Ce chemin n'est pas isolé dans un try/except dédié — pris en charge par le gestionnaire d'erreurs global.
- Pas de test de régression de concurrence (les tests CI ne testent pas la parallélisation multi-worker). Le comportement correct repose sur l'inspection du code et sur la sémantique garantie par PostgreSQL.

### Décisions liées

- `app/services/gamification/gamification_service.py:93–99` : implémentation de référence.
- Ledger `point_events` (`migrations/versions/20260321_add_point_events_ledger.py`) : journal immuable des attributions ; complément indépendant du verrou ligne.
