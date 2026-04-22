# ADR-004 : Architecture de la politique modèles IA — dualité exercices / défis

**Date :** 2026-03-27
**Statut :** Accepté (dette technique documentée)

---

## Contexte

Mathakine utilise OpenAI pour deux flux de génération distincts : les exercices (flux SSE `exercise_ai_service`) et les défis logiques (flux SSE `challenge_ai_service`). Ces deux flux ont des exigences différentes en termes de modèle, de reasoning effort et de fallback.

Deux modules de politique coexistent dans la base de code :

**Module A — `app/core/ai_config.py`**
- Classe `AIConfig` : contient `REASONING_EFFORT_MAP`, `VERBOSITY_MAP`, `TEMPERATURE_MAP` par type de défi.
- Contient `ADVANCED_MODEL` et `BASIC_MODEL` comme constantes de référence historiques.
- Expose `get_openai_params(challenge_type, model_id)` : construit les paramètres d'appel OpenAI selon la famille du modèle.
- Rôle : configuration des paramètres d'appel (effort, verbosité, température).

**Module B — `app/core/ai_generation_policy.py`** (exercices)
- Source de vérité pour la résolution du modèle exercices.
- Hiérarchie : `OPENAI_MODEL_EXERCISES_OVERRIDE` > `OPENAI_MODEL_EXERCISES` (legacy) > `DEFAULT_EXERCISES_AI_MODEL` (`o4-mini`).
- Expose `EXERCISES_AI_ALLOWED_MODEL_IDS` : allowlist explicite des identifiants OpenAI autorisés.
- Délégation documentée dans `app/core/app_model_policy` (index multi-workloads).

**Module C — `app/services/challenges/challenge_ai_model_policy.py`** (défis)
- Source de vérité pour la résolution du modèle défis.
- Hiérarchie : `OPENAI_MODEL_CHALLENGES_OVERRIDE` > `OPENAI_MODEL_REASONING` (legacy) > `CHALLENGE_MODEL_BY_TYPE` > `DEFAULT_CHALLENGES_AI_MODEL` (`o4-mini`).
- Réutilise `EXERCISES_AI_ALLOWED_MODEL_IDS` et `normalize_exercise_ai_model_id` depuis le module B.
- Gère en plus le fallback stream vide (`resolve_challenge_ai_fallback_model` → `gpt-4o-mini`).

Cette organisation résulte d'une croissance organique : le module A a été introduit pour les défis, puis le module B a été créé pour les exercices lors de la refonte de la politique IA. Le module C a ensuite été extrait du module A pour isoler la résolution modèle des paramètres d'appel.

Le module A (`ai_config.py`) conserve des constantes `ADVANCED_MODEL` / `BASIC_MODEL` qui ne sont plus utilisées par le flux défis (remplacées par le module C), mais qui subsistent comme référence historique documentée dans les commentaires du module.

---

## Décision

La dualité des trois modules est maintenue dans sa forme actuelle. La consolidation en un seul module est reportée.

Règles d'interprétation :

| Question | Module authorité |
|---|---|
| Quel modèle pour un exercice ? | `app/core/ai_generation_policy.py` |
| Quel modèle pour un défi ? | `app/services/challenges/challenge_ai_model_policy.py` |
| Quels paramètres d'appel OpenAI (effort, verbosité, température) ? | `app/core/ai_config.AIConfig.get_openai_params()` |
| Quels identifiants sont autorisés ? | `EXERCISES_AI_ALLOWED_MODEL_IDS` (partagé B+C) |

Toute modification des modèles par défaut doit être faite dans le module authorité correspondant. Les constantes `ADVANCED_MODEL` / `BASIC_MODEL` dans `ai_config.py` ne doivent pas être utilisées dans de nouveaux flux.

---

## Conséquences

### Positives

- Séparation claire des responsabilités : résolution modèle vs paramètres d'appel.
- Allowlist partagée `EXERCISES_AI_ALLOWED_MODEL_IDS` entre exercices et défis : un seul point de mise à jour lors de l'ajout d'un nouveau modèle OpenAI.
- Compatibilité ascendante : les variables d'environnement legacy (`OPENAI_MODEL_REASONING`, `OPENAI_MODEL_EXERCISES`) continuent de fonctionner sans changement de déploiement.

### Négatives / Risques

- Trois points d'entrée distincts pour la politique modèle : risque de mise à jour incomplète si un nouveau modèle est ajouté sans mettre à jour les trois modules.
- Les constantes `ADVANCED_MODEL` / `BASIC_MODEL` dans `ai_config.py` sont des leurres pour tout lecteur qui ne connaît pas leur statut de deprecated : risque de réutilisation par erreur dans un nouveau flux.
- Absence d'un index unique (`app_model_policy`) effectivement utilisé à l'exécution (il sert de documentation, pas de point d'appel).

### Chemin de consolidation (futur)

Si un troisième flux IA est introduit (ex. assistant pédagogique dédié, génération d'hints), la politique devra être consolidée en un module unique avec une interface de résolution générique. Ce travail est hors scope tant que seuls deux flux coexistent.

### Décisions liées

- `app/core/ai_generation_policy.py` : source de vérité exercices.
- `app/services/challenges/challenge_ai_model_policy.py` : source de vérité défis.
- `app/core/ai_config.AIConfig.get_openai_params()` : paramètres d'appel (effort, verbosité, température).
- `docs/00-REFERENCE/AI_MODEL_GOVERNANCE.md` : gouvernance runtime des modèles (index opérationnel).
