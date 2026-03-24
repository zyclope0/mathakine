# Code Review -- Mathakine -- 2026-03-22
> ⚠️ OBSOLETE comme source de verite runtime - snapshot historique de revue conserve pour trace.
> La reference actuelle pour la gouvernance IA runtime et l'observabilite est [../00-REFERENCE/AI_MODEL_GOVERNANCE.md](../00-REFERENCE/AI_MODEL_GOVERNANCE.md).

## Corrections post-review appliquees (24/03/2026)

- Le finding `P1-3` ("pas de done event dans le flux SSE exercices IA") est ferme : `generate_exercise_stream` emet maintenant `done` sur les fins controlees.
- Le pattern `getBackendUrl()` a ete mutualise dans `frontend/lib/api/backendUrl.ts` pour les 4 routes proxy Next.js, avec garde production explicite.
- La revue ciblee `react-hooks/exhaustive-deps` est terminee sur le perimetre traite : `LocaleInitializer` et `CategoryAccuracyChart` corriges, autres disables laisses avec justification.

**Auteur** : Revue automatisee (Claude Opus 4.6)
**Perimetre** : 89 fichiers modifies + ~50 fichiers non-trackes (working tree vs HEAD)
**Lignes changees** : +2433 / -1985

---

## Executive Summary

**Score global : 78/100**

Le working tree represente une iteration majeure couvrant : (1) un systeme de gamification persistant avec ledger de points, (2) une refonte de la politique IA exercices/defis avec allowlist et model families, (3) un contrat IA9 pour les modalites de reponse (response_mode), (4) la migration SSE GET vers POST avec body JSON, (5) une validation metier post-generation pour les exercices IA, et (6) de nombreuses corrections et standardisations.

L'architecture est globalement solide et bien structuree. Le code denote une maturite croissante avec une separation nette des responsabilites, des policies explicites, et une couverture de validation en profondeur. Plusieurs points meritent attention avant fusion en production.

**Findings critiques** : 2
**Findings majeurs** : 8
**Findings mineurs** : 12
**Suggestions** : 9

---

## Scores par domaine

| Domaine | Score /20 | Statut |
|---------|-----------|--------|
| Correctness (logique, regressions) | 15/20 | Bon |
| Security (OWASP, auth, data) | 16/20 | Bon |
| Architecture & Best Practices | 17/20 | Tres bon |
| TDD & Qualite des tests | 13/20 | Passable |
| Performance | 17/20 | Tres bon |

---

## Findings Critiques (P0)

### P0-1. Token tracker en memoire -- perte de donnees de cout en production

**Fichier** : `app/utils/token_tracker.py` (lignes 15-258)

Le `TokenTracker` est une classe singleton en memoire (`defaultdict(list)`) qui accumule chaque appel IA dans `_usage_history` et `_daily_totals`. En production multi-worker (Gunicorn, Render), chaque worker a son propre espace memoire : les couts sont fragmentes et perdus au redemarrage.

De plus, `_usage_history` ne comporte aucun mecanisme d'eviction. Chaque generation IA ajoute un enregistrement, ce qui provoque une croissance illimitee de la memoire :

```python
self._usage_history[challenge_type].append(usage_record)  # ligne 134 -- jamais truncate
```

**Impact** : Fuite memoire progressive en production. Perte de la visibilite des couts IA (potentiellement des centaines de dollars par mois non trackes).

**Suggestion** :
- Court terme : ajouter un plafond (ring buffer ou eviction >48h) dans `_usage_history`.
- Moyen terme : persister en base (table `ai_cost_events`) ou dans Redis, exploitable par le monitoring ops.

---

### P0-2. Concurrence gamification sans verrouillage -- race condition sur total_points

**Fichier** : `app/services/gamification/gamification_service.py` (lignes 86-99)

Le commentaire ligne 86 indique explicitement :

```python
# Pas de with_for_update ici : SQLite (tests) ne le supporte pas ; charge faible sur ce flux.
user = db.query(User).filter(User.id == user_id).one_or_none()
```

Le pattern est : lire `total_points`, calculer `+ delta`, ecrire la nouvelle valeur. Deux requetes concurrentes (badge + daily challenge sur le meme user) peuvent lire le meme `total_points`, et la seconde ecrasera le resultat de la premiere (lost update).

**Impact** : Perte de points de gamification en conditions concurrentes. Pour une plateforme EdTech ciblant des enfants, les points "perdus" peuvent etre frustrants et miner la confiance dans le systeme.

**Suggestion** :
- Utiliser `with_for_update()` en production PostgreSQL et maintenir le test SQLite via un feature flag ou un helper conditionnel :
```python
q = db.query(User).filter(User.id == user_id)
if not settings.TESTING:
    q = q.with_for_update()
user = q.one_or_none()
```
- Alternative : requete atomique `UPDATE users SET total_points = total_points + :delta WHERE id = :id RETURNING total_points`.

---

## Findings Majeurs (P1)

### P1-1. Erreur API OpenAI exposee dans le message SSE

**Fichier** : `app/services/challenges/challenge_ai_service.py` (lignes 314-318)

```python
yield sse_error_message(
    f"Erreur lors de la generation apres plusieurs tentatives: {str(api_error)}"
)
```

Le `str(api_error)` d'une `APIError` ou `RateLimitError` peut contenir des details techniques internes (URLs, headers, clefs partielles). Ce message est transmis tel quel au frontend via SSE et affiche a l'utilisateur.

**Impact** : Information disclosure (OWASP A01) -- un attaquant pourrait extraire des informations sur l'infrastructure backend ou la configuration OpenAI.

**Suggestion** : Utiliser `get_safe_error_message(api_error)` (deja present dans `error_handler.py`) ou un message generique constant.

---

### P1-2. Rate limit desactive systematiquement en tests

**Fichier** : `app/utils/rate_limit.py` (lignes 69-71, 79, 99)

```python
if os.getenv("TESTING", "false").lower() == "true":
    return True
```

Ce pattern est present dans `_check_rate_limit`, `check_ai_generation_rate_limit`, et `check_exercise_ai_generation_rate_limit`. Le probleme n'est pas la desactivation en tests (c'est correct), mais la methode : lire `os.getenv("TESTING")` dans chaque appel au lieu de consulter `settings.TESTING` (deja valide en mode Pydantic). Si le deployement configure `TESTING=true` par erreur (ou via une variable d'environnement residuelle), tout le rate limiting est silencieusement desactive.

**Impact** : Si `TESTING=true` fuite en production (copier-coller .env, variable residuelle CI), aucune protection anti-abus n'est active.

**Suggestion** : Utiliser exclusivement `settings.TESTING` (Pydantic-validated) au lieu de `os.getenv("TESTING")` pour la coherence. Considerer un guard supplementaire : si `_is_production() and settings.TESTING`, lever une exception au demarrage.

---

### P1-3. Pas de "done" event dans le flux SSE exercices IA

**Fichier** : `app/services/exercises/exercise_ai_service.py` (lignes 172-406)

Le generateur `generate_exercise_stream` n'emet jamais d'evenement `{"type": "done"}` en fin de flux. En comparaison, `generate_challenge_stream` (challenge_ai_service.py, ligne 495) emet toujours `data: {"type": "done"}`. Le frontend `consumeSseJsonEvents` repose sur la fermeture du stream, mais un evenement explicite `done` est une bonne pratique pour la robustesse SSE (permet au client de distinguer fin normale vs deconnexion).

**Impact** : Incoherence de contrat entre les deux flux SSE. Un futur refactoring frontend pourrait attendre `done` pour les exercices et ne jamais le recevoir.

**Suggestion** : Ajouter `yield f"data: {json.dumps({'type': 'done'})}\n\n"` en fin de `generate_exercise_stream` (avant le return final).

---

### P1-4. Absence de validation de `user_id` dans le handler de generation exercice

**Fichier** : `server/handlers/exercise_handlers.py` (lignes 342-392)

Le handler `generate_ai_exercise_stream` (appele via le routeur) utilise `require_auth_sse` qui devrait fournir `request.state.user`, mais le code ne verifie pas que `user_id` est non-null avant de le passer au rate limiter et au service de generation. En comparaison, le handler challenge (ligne 157) fait explicitement :

```python
user_id = current_user.get("id")
if not user_id:
    return api_error_response(401, "Utilisateur invalide")
```

**Fichier** : `server/handlers/exercise_handlers.py` (ligne non visible dans l'extrait mais implicite dans le routage POST `/api/exercises/generate-ai-stream`)

**Impact** : Si `current_user.get("id")` retourne `None` (session corrompue), le rate limiter recoit `user_id=None`, et la generation continue sans tracking par utilisateur.

**Suggestion** : Ajouter un guard explicite `if not user_id: return sse_error_response(...)`.

---

### P1-5. `daily_challenge_service` utilise `date.today()` sans timezone

**Fichier** : `app/services/progress/daily_challenge_service.py` (lignes 99, 203, 255)

```python
today = date.today()
```

`date.today()` utilise le fuseau local du serveur. En production sur Render, le fuseau est typiquement UTC, mais ce n'est pas garanti. Un utilisateur en UTC+12 pourrait voir ses defis quotidiens "resettes" au milieu de sa journee.

**Impact** : Incoherence dans le calendrier des defis quotidiens entre serveurs et utilisateurs en fuseaux horaires differents.

**Suggestion** : Utiliser `datetime.now(timezone.utc).date()` partout, et stocker la timezone utilisateur pour un calcul adapte.

---

### P1-6. Duplicate import of `AsyncOpenAI` dans challenge_ai_service

**Fichier** : `app/services/challenges/challenge_ai_service.py` (lignes 11, 234-235)

`AsyncOpenAI` est importe en haut du fichier (ligne 11) ET re-importe dans la methode (ligne 234-235) :

```python
try:
    from openai import AsyncOpenAI
except ImportError:
    yield sse_error_message("Bibliotheque OpenAI non installee")
    return
```

L'import conditionnel est suppose fournir un message d'erreur si openai n'est pas installe, mais si openai manque, l'import de tete (ligne 11) echoue deja au chargement du module, rendant tout le service inaccessible avec une ImportError non-geree a un niveau superieur.

**Impact** : Le try/except inline est du dead code -- il ne sera jamais atteint car le module ne charge pas si openai est absent.

**Suggestion** : Soit deplacer tous les imports openai dans le bloc try (lazy), soit supprimer le try/except inline et laisser l'import de tete.

---

### P1-7. `_persist_challenge_sync` ne propage pas les exceptions metier

**Fichier** : `app/services/challenges/challenge_ai_service.py` (lignes 142-215)

La fonction retourne `None` si la creation echoue (challenge cree mais invalide), et le caller (ligne 483-484) envoie alors le challenge normalise brut au frontend avec `warning: 'Non sauvegarde en base'`. Le frontend affiche ce challenge comme s'il etait valide mais ne le retrouvera pas dans la base.

**Impact** : L'utilisateur voit un challenge genere mais ephemere, sans pouvoir le retrouver ni le resoudre plus tard. UX confuse.

**Suggestion** : Considerer un echec clair plutot qu'un challenge fantome. Si la persistance echoue, emettre une erreur SSE et ne pas exposer le challenge brut.

---

### P1-8. Schemas Pydantic `GenerateChallengeStreamPostBody` et `GenerateExerciseStreamPostBody` sans sanitization du prompt

**Fichiers** :
- `app/schemas/logic_challenge.py` (lignes 301-309)
- `app/schemas/exercise.py` (lignes 277-297)

Les deux schemas acceptent un champ `prompt` avec `max_length=8000`. La longueur est limitee, mais le contenu n'est pas valide au niveau schema. La sanitization est delegee plus tard dans `prepare_stream_context` via `sanitize_user_prompt` / `validate_prompt_safety`, mais si un autre handler utilise ces schemas sans appeler `prepare_stream_context`, le prompt brut est transmis au LLM.

**Impact** : Risque de prompt injection si le pipeline est modifie sans passer par la sanitization.

**Suggestion** : Ajouter un `field_validator` sur `prompt` dans les schemas Pydantic pour effectuer une sanitization basique (strip, rejet de certains patterns) au plus tot.

---

## Findings Mineurs (P2)

### P2-1. Duplicate `colorMap` dans VisualRenderer.tsx

**Fichier** : `frontend/components/challenges/visualizations/VisualRenderer.tsx` (lignes 27-47 et 95-100+)

Le meme mapping couleurs francais/anglais vers CSS est defini deux fois : dans `parseShapeWithColor` et dans `resolveColor`. Toute mise a jour doit etre faite aux deux endroits.

**Suggestion** : Extraire une constante `COLOR_MAP` partagee en haut du fichier.

---

### P2-2. `f-string` avec exception dans les logs (risque PII indirect)

**Fichiers multiples** : `user_service.py`, `challenge_ai_service.py`, etc.

Pattern recurrent :
```python
logger.error(f"Erreur: {some_error}")
```

Certains messages incluent des `username`, `email`, ou le contenu de l'erreur qui peut contenir des donnees utilisateur.

**Suggestion** : Utiliser le format `logger.error("Erreur: %s", some_error)` (lazy evaluation) et verifier que les messages n'exposent pas de PII en production.

---

### P2-3. `cost_per_1k_tokens` defini inline dans chaque appel `track_usage`

**Fichier** : `app/utils/token_tracker.py` (lignes 49-111)

La table de couts est un dictionnaire literal redefini a chaque appel de `track_usage`. Ce n'est pas un bug de logique, mais un probleme de maintenabilite et de micro-performance (creation d'un dict a chaque appel).

**Suggestion** : Deplacer la constante en attribut de classe ou en constante module-level.

---

### P2-4. `list_users` filtre `User.is_active == True` sans index dedie

**Fichier** : `app/services/users/user_service.py` (ligne 111)

```python
query = db.query(User).filter(User.is_active == True)
```

La table `users` a des index sur `username`, `email`, `total_points`, `jedi_rank`, `avatar_url`, mais pas sur `is_active`. Pour une plateforme avec de nombreux utilisateurs, cette requete fait un sequential scan.

**Suggestion** : Ajouter un index partial sur `is_active = true` si la table croit significativement.

---

### P2-5. `exercise_attempt_service.py` importe `BadgeService` deux fois dans le meme flux

**Fichier** : `app/services/exercises/exercise_attempt_service.py` (lignes 121 et 179)

```python
from app.services.badges.badge_service import BadgeService  # ligne 121
# ...
from app.services.badges.badge_service import BadgeService  # ligne 179
```

**Suggestion** : Deplacer l'import en haut du fichier ou le faire une seule fois dans le bloc.

---

### P2-6. FrontiÃ¨re `GET /api/challenges/completed-ids` avec `@optional_auth`

**Fichier** : `server/handlers/challenge_handlers.py` (ligne 225)

Ce handler utilise `@optional_auth` alors que la donnee retournee est specifique a l'utilisateur. Si aucun utilisateur n'est authentifie, il retourne `{"completed_ids": []}`. Ce n'est pas un bug, mais `@require_auth` serait plus explicite -- un utilisateur non-authentifie recevra toujours une liste vide, donc le resultat est inutile sans auth.

---

### P2-7. `scripts/cleanup_edtech_aberrant_data.py` utilise `text(f"...")` (SQL injection potentielle)

**Fichier** : `scripts/verify_user_deletion.py` (lignes 84-88)

```python
r = conn.execute(text(f"""
    SELECT COUNT(*) FROM {table} t
    WHERE t.{col} IS NOT NULL
    ...
"""))
```

Les variables `table` et `col` proviennent d'une liste hardcodee dans le script, mais le pattern `text(f"...")` est un anti-pattern SQL injection. Si ce script est adapte, un copier-coller introduirait une faille.

**Suggestion** : Ajouter un commentaire `# SAFETY: table/col hardcoded, not user input` ou utiliser des identifiers SQLAlchemy.

---

### P2-8. Pas de timeout sur la requete fallback SSE challenge

**Fichier** : `app/services/challenges/challenge_ai_service.py` (lignes 349-365)

Le client fallback est cree avec `timeout=ai_params.get("timeout", 120)` mais la requete n'est pas en streaming -- c'est un appel `create()` non-streame. Un timeout de 120s pour un appel synchrone est excessif.

**Suggestion** : Reduire le timeout du fallback a 30-45s.

---

### P2-9. `exercise_generator.py` modifie la signature de `_generate_choices` de maniere potentiellement fragile

Le diff montre l'ajout d'un parametre `normalized_age_group` dans la chaine d'appels, passant de positional a keyword pour `derived_difficulty`. Si d'autres call sites existent sans mise a jour, cela provoquera un TypeError a l'execution.

---

### P2-10. Migration `20260321_add_point_events_ledger.py` ne verifie pas les index existants avant creation

**Fichier** : `migrations/versions/20260321_add_point_events_ledger.py` (lignes 48-56)

La table est gardee par un `if "point_events" in inspector.get_table_names(): return`, mais les index ne sont pas gardes individuellement. Si la table existe mais un index manque (migration partielle), la migration sera un no-op.

---

### P2-11. `ssePostStream.ts` ne gere pas le cas ou le buffer final contient un dernier "data:" tronque

**Fichier** : `frontend/lib/utils/ssePostStream.ts` (lignes 36-48)

Apres la boucle, le `buffer` restant (derniere ligne sans `\n`) n'est jamais traite. Si le serveur ferme le stream avec un dernier `data: {...}\n` sans `\n` final, cet evenement est perdu.

**Suggestion** : Apres la boucle while, traiter le buffer restant :
```typescript
if (buffer.trim().startsWith("data: ")) {
  const data = JSON.parse(buffer.trim().slice(6));
  await onEvent(data);
}
```

---

### P2-12. `challenge_api_mapper.py` ajoute une logique de resolution `response_mode` qui duplique la logique de `challenge_contract_policy.py`

Le mapper appelle `compute_response_mode` et `sanitize_choices_for_delivery`, mais le `normalize_generated_challenge` dans `challenge_ai_service.py` appelle aussi `compute_response_mode`. Le `response_mode` est potentiellement calcule deux fois avec des inputs legerement differents (pre-persist vs post-persist).

---

## Suggestions (P3)

### P3-1. Centraliser les constantes de couts OpenAI

La table de couts dans `token_tracker.py` est un endroit fragile. Considerer un fichier `app/core/openai_pricing.py` importe par `token_tracker` et par les dashboards admin futurs.

### P3-2. Ajouter un health check pour la connectivite OpenAI

Aucun endpoint ne verifie que `OPENAI_API_KEY` est valide avant qu'un utilisateur tente une generation. Un check au demarrage (ou lazy au premier appel) avec `client.models.list()` permettrait de fail-fast.

### P3-3. Considerer un schema Pydantic pour `normalize_generated_challenge`

Le retour de `normalize_generated_challenge` est un `Dict[str, Any]`. Un schema Pydantic assurerait que les cles attendues sont toujours presentes et typees.

### P3-4. Utiliser `TypedDict` pour les retours de `_daily_challenge_to_dict`

Le retour est un dict brut. Un `TypedDict` ameliorerait l'autocompletion et la verification statique.

### P3-5. Extraire les messages d'erreur SSE en constantes

Les messages comme `"Bibliotheque OpenAI non installee"` et `"OpenAI API key non configuree"` sont dupliques entre `challenge_ai_service.py` et `exercise_ai_service.py`.

### P3-6. Ajouter un test de regression pour la double-creation de daily challenges

`get_or_create_today` pourrait creer des doublons si deux requetes concurrentes arrivent exactement au moment de la creation. Un `UNIQUE(user_id, date, challenge_type)` en base serait protecteur.

### P3-7. Documenter la matrice `TYPE_CONTRACTS` dans un fichier dedie

La matrice dans `challenge_contract_policy.py` est le coeur du contrat IA9. Une documentation separee (ou un tableau dans le README features) faciliterait la comprehension par les contributeurs frontend.

### P3-8. Standardiser le nommage des cles Redis rate limit

Les cles utilisent `rate_limit:ai_generation:hour:{user_id}` et `rate_limit:exercise_ai_generation:hour:{user_id}`. Definir un schema de nommage dans un fichier dedie (`rate_limit_keys.py`) pour eviter les collisions futures.

### P3-9. Migration vers `stream_options: {include_usage: true}` pour les challenges aussi

Le flux exercices utilise `stream_options: {"include_usage": True}` (ligne 278 de `ai_generation_policy.py`) mais le flux challenges ne le fait pas. L'activation permettrait des tokens reels au lieu d'estimations `len(response) // 4`.

---

## Patterns recurrents

### 1. Maturation de l'architecture par policies explicites (positif)
Les fichiers `ai_generation_policy.py`, `challenge_contract_policy.py`, `challenge_ai_model_policy.py`, `challenge_difficulty_policy.py` montrent une evolution vers des decisions metier isolees dans des modules dediees avec allowlists, matrices de capabilities, et enums typees. C'est une excellente pratique.

### 2. Pattern sync wrapper + `run_db_bound` (positif mais risque)
Le pattern `_persist_X_sync` + `sync_db_session` + `run_db_bound` pour isoler les operations DB synchrones dans un contexte async est bien applique. Risque : multiplication des points d'entree sync sans centralisation.

### 3. Logging avec f-strings au lieu de lazy formatting
Pattern recurrent dans tout le codebase :
```python
logger.error(f"Erreur: {variable}")
```
Preferer `logger.error("Erreur: %s", variable)` pour performance et securite.

### 4. Guard clauses `if "savepoint" in locals()` (fragile)
Le pattern dans `exercise_attempt_service.py` (lignes 109, 155) est fragile :
```python
if "progress_savepoint" in locals() and progress_savepoint.is_active:
    progress_savepoint.rollback()
```
Preferer un context manager ou deplacer la declaration avant le try.

### 5. Separation frontend nette via hooks + lib (positif)
Le refactoring des pages `exercises/page.tsx` et `challenges/page.tsx` avec extraction dans des hooks (`useAIExerciseGenerator`, `usePaginatedContent`, `useCompletedItems`) et des utilitaires (`ssePostStream`, `contentListOrder`) est bien structure.

---

## Points positifs

1. **Allowlist IA stricte** : `EXERCISES_AI_ALLOWED_MODEL_IDS` et `classify_exercise_ai_model_family` empechent tout modele non-autorise d'etre utilise, avec erreur explicite et precoce (avant l'appel OpenAI).

2. **Validation metier post-generation** : `exercise_ai_validation.py` refuse de persister un exercice dont la bonne reponse n'est pas dans les choix, ou dont les choix ne sont pas distincts. C'est un garde-fou pedagogique essentiel.

3. **Contrat IA9 response_mode** : la decision QCM/texte libre/interaction est portee par le serveur (`response_mode`) et non inferee cote client, ce qui elimine une classe entiere de bugs frontend.

4. **Production hardening** : validation `SECRET_KEY` obligatoire en production, `REDIS_URL` obligatoire pour le rate limit distribue, `POSTGRES_PASSWORD` non-default en production, `LOG_LEVEL=DEBUG` force a INFO.

5. **Migration defensive** : les migrations Alembic verifient l'existence des tables/index avant creation, supportant les replays idempotents.

6. **Gamification avec ledger** : le modele `PointEvent` cree un audit trail de chaque attribution de points, permettant la verification, le debug et les analytics.

7. **Schemas Pydantic POST pour SSE** : `GenerateChallengeStreamPostBody` et `GenerateExerciseStreamPostBody` avec `extra="forbid"` et `str_strip_whitespace=True` ferment la surface d'attaque des payloads inattendus.

8. **Rate limiting separe exercices/defis** : les quotas horaires et journaliers sont distincts entre les deux flux IA, evitant qu'un utilisateur epuise son quota defis en generant des exercices.

9. **Frontend SSE via POST** : migration du GET (prompt dans l'URL) vers POST (body JSON) pour les deux flux IA, eliminant les problemes de longueur URL et l'exposition du prompt dans les logs serveur.

10. **TypedDict pour les retours de services** : `app/core/types.py` definit des types verifiables statiquement pour les retours de dashboard, auth, et pagination.

---

## Plan d'action recommande

### Priorite immediate (avant merge)

| # | Action | Effort | Fichier(s) |
|---|--------|--------|------------|
| 1 | Ajouter eviction ou plafond au TokenTracker (P0-1) | 1h | `app/utils/token_tracker.py` |
| 2 | Ajouter `with_for_update()` conditionnel dans gamification (P0-2) | 1h | `app/services/gamification/gamification_service.py` |
| 3 | Masquer les erreurs API OpenAI dans les messages SSE (P1-1) | 30min | `app/services/challenges/challenge_ai_service.py` |
| 4 | Utiliser `settings.TESTING` au lieu de `os.getenv("TESTING")` (P1-2) | 30min | `app/utils/rate_limit.py` |

### Priorite haute (sprint suivant)

| # | Action | Effort | Fichier(s) |
|---|--------|--------|------------|
| 5 | Ajouter event `done` au flux SSE exercices (P1-3) | 15min | `app/services/exercises/exercise_ai_service.py` |
| 6 | Valider `user_id` non-null dans handler exercice AI (P1-4) | 15min | `server/handlers/exercise_handlers.py` |
| 7 | Utiliser `datetime.now(timezone.utc).date()` dans daily challenges (P1-5) | 30min | `app/services/progress/daily_challenge_service.py` |
| 8 | Cleanup double import AsyncOpenAI (P1-6) | 15min | `app/services/challenges/challenge_ai_service.py` |
| 9 | Traiter le buffer final dans ssePostStream.ts (P2-11) | 15min | `frontend/lib/utils/ssePostStream.ts` |

### Backlog (dette technique)

| # | Action | Effort |
|---|--------|--------|
| 10 | Extraire colorMap en constante partagee (P2-1) | 15min |
| 11 | Centraliser les couts OpenAI (P3-1) | 1h |
| 12 | Ajouter `UNIQUE(user_id, date, challenge_type)` pour daily challenges (P3-6) | 30min |
| 13 | Standardiser nommage cles Redis (P3-8) | 30min |

---

*Revue effectuee le 2026-03-22. Perimetre : 89 fichiers modifies + ~50 nouveaux fichiers dans le working tree.*

