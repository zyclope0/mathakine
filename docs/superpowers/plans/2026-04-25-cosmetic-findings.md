# Cosmetic Findings — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corriger les 3 findings cosmétiques actionnables issus des audits sécurité et runtime beta stabilisation.

**Architecture:** 3 tâches indépendantes touchant chacune un fichier différent. Aucune migration DB, aucune feature nouvelle. Les 8 autres findings des audits sont documentés comme "no action needed" (voir `.claude/archive/audits/2026-04-25-security-findings.md` et `.claude/archive/audits/2026-04-25-runtime-findings.md` — déplacés en archive le 2026-04-26, cf. `docs/superpowers/specs/2026-04-26-ai-context-rationalization-design.md`).

**Tech Stack:** Python 3.12 / Starlette, loguru, SSE async generator

---

## Triage des 11 findings cosmétiques

| Finding | Action |
|---------|--------|
| Sec-C1 Circuit breaker per-process | Aucune — documenté et assumé |
| **Sec-C2 Logging `{}` vs `%s` dans auth_service.py** | **Task 2** |
| **Sec-C3 `ENVIRONMENT=production` manquant Render** | **Task 3** |
| Sec-C4 Rate limiting fail-closed | Aucune — comportement correct |
| Sec-C5 SSE rejected propre | Aucune — comportement correct |
| Sec-C6 JWT fenêtre 3600s | Aucune — correct après B2/B3 |
| **Run-C1 Missing `done` sur 13 return paths SSE** | **Task 1** |
| Run-C2 finish_reason=length | Aucune — déjà géré |
| Run-C3 Deduction solver timeout | Aucune — déjà géré |
| Run-C4 Gamification double-count | Aucune — pas de problème |
| Run-C5 Contrats frontend/backend | Aucune — acceptable |

---

## Fichiers modifiés

| Fichier | Action |
|---------|--------|
| `app/services/challenges/challenge_ai_service.py` | Ajouter `done` SSE event sur 13 chemins d'erreur |
| `app/services/auth/auth_service.py` | Harmoniser `{}` → `%s` dans les appels logger (23 occurrences) |
| `README_TECH.md` | Ajouter note déploiement `ENVIRONMENT=production` |

---

## Task 1 — Add `done` SSE event to 13 early return paths

**Files:**
- Modify: `app/services/challenges/challenge_ai_service.py`

**Contexte :** Dans `generate_challenge_stream()`, 13 chemins d'erreur font `return` après un `yield sse_error_message(...)` sans émettre d'event `done`. Côté frontend, `consumeSseJsonEvents` ferme proprement au EOF (pas de blocage), mais `setStreamedText` n'est pas appelé — le message "Génération en cours..." peut rester affiché. Le pattern à appliquer :

```python
# AVANT
yield sse_error_message("...")
return

# APRÈS
yield sse_error_message("...")
yield f"data: {json.dumps({'type': 'done'})}\n\n"
return
```

`json` est déjà importé dans le fichier. Le pattern `done` est identique aux 3 chemins existants (lignes 981, 1093, 1113 du fichier actuel).

**Les 13 occurrences à corriger** (contexte unique pour chaque) :

| # | Contexte avant la correction |
|---|------------------------------|
| 1 | `yield sse_error_message("Bibliothèque OpenAI non installée")` |
| 2 | `yield sse_error_message("OpenAI API key non configurée")` |
| 3 | `yield sse_error_message(OPENAI_CIRCUIT_OPEN_USER_MESSAGE)` |
| 4 | `yield sse_error_message(get_safe_error_message(api_error, default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE))` (multiline) |
| 5 | `yield sse_error_message(get_safe_error_message(unexpected_error, default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE))` (multiline) |
| 6 | `yield sse_error_message(get_safe_error_message(stream_api_error, default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE))` (multiline) |
| 7 | `yield sse_error_message(get_safe_error_message(stream_other, default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE))` (multiline) |
| 8 | `yield sse_error_message(CHALLENGE_AI_GENERIC_ERROR_MESSAGE)` (fallback vide) |
| 9 | `yield sse_error_message(get_safe_error_message(fb_err, default=CHALLENGE_AI_TRANSIENT_ERROR_MESSAGE))` (fallback countable) |
| 10 | `yield sse_error_message(get_safe_error_message(fb_err, default=CHALLENGE_AI_GENERIC_ERROR_MESSAGE))` (fallback non-countable) |
| 11 | `yield sse_error_message("Erreur lors du parsing de la réponse JSON")` |
| 12 | `yield sse_error_message("Les données générées sont incomplètes (titre ou description manquant)")` (multiline) |
| 13 | `yield sse_error_message("Erreur lors de la normalisation des données")` |

Pas de test TDD possible ici (les chemins nécessitent des mocks OpenAI complexes). La vérification se fait par grep.

- [ ] **Step 1 : Lire la fonction `generate_challenge_stream` pour repérer chaque return path**

```bash
grep -n "yield sse_error_message\|yield f\"data.*done\|\breturn\b" app/services/challenges/challenge_ai_service.py
```

Vérifier que les 13 occurrences sans `done` correspondent bien au tableau ci-dessus.

- [ ] **Step 2 : Corriger les 13 occurrences**

Pour chaque occurrence du tableau, ajouter la ligne `yield f"data: {json.dumps({'type': 'done'})}\n\n"` entre le `yield sse_error_message(...)` et le `return`. Respecter l'indentation du bloc (`return` peut être à 8, 12 ou 16 espaces selon le niveau d'imbrication).

Exemple pour l'occurrence #1 (indentation 12 espaces) :
```python
            yield sse_error_message("Bibliothèque OpenAI non installée")
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return
```

Exemple pour l'occurrence #8 (indentation 20 espaces — dans un `else` d'un `if has_fallback_body`) :
```python
                    yield sse_error_message(CHALLENGE_AI_GENERIC_ERROR_MESSAGE)
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return
```

- [ ] **Step 3 : Vérifier par grep qu'il ne reste aucun `return` sans `done` dans la fonction**

```bash
grep -n "yield sse_error_message\|yield f\"data.*done\|\breturn\b" app/services/challenges/challenge_ai_service.py
```

Vérifier visuellement que chaque `return` précédé d'un `sse_error_message` a maintenant un `done` entre les deux.

- [ ] **Step 4 : Vérifier que le module importe sans erreur**

```bash
python -c "from app.services.challenges.challenge_ai_service import generate_challenge_stream; print('OK')"
```

Expected : `OK`

- [ ] **Step 5 : Commit**

```bash
git add app/services/challenges/challenge_ai_service.py
git commit -m "fix(sse): add done event to all early error return paths in generate_challenge_stream"
```

---

## Task 2 — Harmoniser format logging dans auth_service.py

**Files:**
- Modify: `app/services/auth/auth_service.py`

**Contexte :** `auth_service.py` utilise le format loguru `{}` (ex: `"user_alias={}"`) au lieu de la convention projet `%s` (CLAUDE.md : `logger.error("msg %s", var)`). Les deux fonctionnent avec loguru, mais la convention `%s` est celle du reste du codebase. Il y a 23 occurrences de `{}` dans des chaînes de log. Cette tâche les remplace toutes par `%s`.

**Règle simple :** dans une string argument d'un logger call, remplacer chaque `{}` par `%s`. Le nombre d'arguments passés après la string ne change pas (loguru accepte les deux styles avec la même syntaxe d'appel).

- [ ] **Step 1 : Confirmer les 23 occurrences**

```bash
grep -n '{}' app/services/auth/auth_service.py
```

Expected : 23 lignes. Toutes sont des chaînes de format dans des appels `logger.*()`.

- [ ] **Step 2 : Remplacer toutes les occurrences**

Utiliser l'outil Edit avec `replace_all: true` sur le pattern `{}` → `%s` dans le fichier.

**Attention :** certaines strings ont plusieurs `{}` sur la même ligne (ex: `"user_id={} user_alias={}"`) — chaque `{}` devient `%s`, le nombre d'arguments ne change pas.

Résultat attendu — exemples avant/après :

```python
# AVANT
logger.debug(
    "Tentative d'authentification user_alias={}",
    _mask_username_for_logs(username),
)
# APRÈS
logger.debug(
    "Tentative d'authentification user_alias=%s",
    _mask_username_for_logs(username),
)
```

```python
# AVANT
logger.warning(
    "Compte désactivé user_id={} user_alias={}",
    user.id,
    _mask_username_for_logs(username),
)
# APRÈS
logger.warning(
    "Compte désactivé user_id=%s user_alias=%s",
    user.id,
    _mask_username_for_logs(username),
)
```

- [ ] **Step 3 : Vérifier qu'il ne reste aucun `{}` dans les logger calls**

```bash
grep -n '{}' app/services/auth/auth_service.py
```

Expected : 0 ligne.

- [ ] **Step 4 : Vérifier que le module importe sans erreur**

```bash
python -c "from app.services.auth.auth_service import authenticate_user; print('OK')"
```

Expected : `OK`

- [ ] **Step 5 : Commit**

```bash
git add app/services/auth/auth_service.py
git commit -m "style(auth): harmonize loguru format {} to %s in auth_service.py"
```

---

## Task 3 — Documenter ENVIRONMENT=production dans README_TECH.md

**Files:**
- Modify: `README_TECH.md`

**Contexte :** `_is_production()` dans `app/core/security.py` vérifie `NODE_ENV=production` OU `ENVIRONMENT=production` OU `MATH_TRAINER_PROFILE=prod`. Sur Render, si `ENVIRONMENT=production` n'est pas configuré dans les env vars du service, `_is_production()` retourne `False` et les headers HSTS ne sont pas envoyés. Ce n'est pas un bug code, mais une dépendance de déploiement non documentée.

- [ ] **Step 1 : Lire la section Runtime Truth de README_TECH.md**

```bash
grep -n "Render\|prod\|deploy\|ENVIRONMENT\|_is_production" README_TECH.md | head -20
```

- [ ] **Step 2 : Ajouter une note Render dans la section Runtime Truth**

Localiser le bloc Render existant (autour de la ligne qui mentionne `gunicorn enhanced_server:app`) et ajouter après :

```markdown
- **Render env vars requises en prod** : `ENVIRONMENT=production` doit être explicitement positionné dans les variables d'environnement Render pour activer `_is_production()` (headers HSTS, cookies Secure). Sans cette variable, les headers sécurité sont désactivés même en production.
```

- [ ] **Step 3 : Vérifier que la note est bien insérée**

```bash
grep -n "ENVIRONMENT=production" README_TECH.md
```

Expected : au moins 1 ligne.

- [ ] **Step 4 : Commit**

```bash
git add README_TECH.md
git commit -m "docs(deploy): document ENVIRONMENT=production Render requirement for security headers"
```

---

## Vérification finale

- [ ] `grep -c "yield sse_error_message" app/services/challenges/challenge_ai_service.py` — compter les `sse_error_message` sans `done` immédiatement après
- [ ] `grep '{}' app/services/auth/auth_service.py` — 0 résultat
- [ ] `grep "ENVIRONMENT=production" README_TECH.md` — 1 résultat
- [ ] `python -c "from app.services.challenges.challenge_ai_service import generate_challenge_stream; from app.services.auth.auth_service import authenticate_user; print('OK')"` — `OK`
