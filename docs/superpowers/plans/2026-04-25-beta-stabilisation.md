# Beta Stabilisation v3.6.0 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Solidifier la beta v3.6.0 sans feature nouvelle — audit sécurité, audit runtime, fermer Phase 2A métriques, aligner les docs.

**Architecture:** Approche séquentielle : audits d'abord (findings inconnus, pas de code pré-écrit), puis métriques (code concret ancré sur le code réel lu), puis docs. Zéro migration DB, zéro refonte.

**Tech Stack:** Python 3.12 / Starlette / SQLAlchemy, Next.js 16 / TypeScript, pytest, `/octo:security`, `/octo:review`

---

## Fichiers modifiés ou créés

| Fichier | Action | Responsabilité |
|---------|--------|---------------|
| `app/utils/generation_metrics.py` | Modifier | Percentiles, chess counters, fallback stats, repair_success_rate |
| `app/services/challenges/challenge_ai_service.py` | Modifier | `record_chess_repair` calls, `fallback_trigger_reason` dans record, `generation_confidence` log |
| `tests/unit/test_generation_metrics.py` | Modifier | Tests des nouveaux champs (TDD) |
| `README_TECH.md` | Modifier | Version 3.6.0-beta.4, état ACTIF-03/04 |
| `CLAUDE.md` | Modifier | Version 3.6.0-beta.4 |
| `C:\Users\yanni\.claude\projects\D--Mathakine\memory\project_mathakine_context.md` | Modifier | Snapshot beta.4 |

---

## NOTE SCOPE AUDITS (Tasks 1–4)

Les Tasks 1–4 sont des audits dont les findings sont inconnus à l'avance. Le code des corrections ne peut pas être pré-écrit — il dépend de ce que les outils remontent. Les tâches décrivent le processus exact et les critères de triage. Toutes les corrections bloquantes doivent être commitées avant de passer à la Task 5.

**Critères findings bloquants (à corriger maintenant) :**
- Fuite de données utilisateur (PII en clair dans logs ou réponses HTTP)
- Auth bypass ou token exploitable
- Crash worker possible (exception non catchée, deadspin, timeout absent)
- Défi `rejected` envoyé silencieusement au frontend
- État partagé supposé entre workers Gunicorn (circuit breaker, métriques)

**Critères findings cosmétiques (à logger en roadmap, pas corriger maintenant) :**
- Amélioration de lisibilité, nommage, commentaires
- Optimisations de performance non critiques
- Refactoring hors scope

---

## Task 1 — Audit sécurité

**Files:**
- Read: `server/middleware.py`, `server/auth.py`, `app/core/security.py`
- Read: `app/services/auth/auth_service.py`
- Read: `app/services/challenges/challenge_ai_service.py` (section SSE/stream)

- [ ] **Step 1: Lancer l'audit sécurité**

```
/octo:security
```

Cibles à spécifier dans le prompt octo:security :
```
Audit sécurité ciblé sur :
- server/middleware.py (headers sécurité, HSTS, X-XSS, Permissions-Policy)
- server/auth.py (JWT, cookies SameSite/Secure)
- app/core/security.py (get_cookie_config, _is_production)
- app/services/auth/auth_service.py (PII logs, HMAC alias, recover_refresh_token)
- app/services/challenges/challenge_ai_service.py (SSE rejected path, circuit breaker HALF_OPEN)

Chercher spécifiquement :
1. Headers HSTS/Secure activés hors _is_production() ?
2. username/email en clair dans un log path non couvert par les alias HMAC ?
3. Un défi rejected peut-il partir au frontend avec des données partielles ?
4. Le circuit breaker HALF_OPEN suppose-t-il un état partagé entre workers ?
5. Rate limiting absent ou mal configuré si REDIS_URL manquant en prod ?
```

- [ ] **Step 2: Trier les findings**

Créer un fichier temporaire `.claude/audit-security-findings.md` avec deux sections :
```
## Bloquants
- [finding]: [fichier:ligne] [description]

## Cosmétiques (roadmap)
- [finding]: [description]
```

Utiliser les critères de triage définis en tête de plan.

- [ ] **Step 3: Corriger chaque finding bloquant**

Pour chaque finding bloquant listé : lire le fichier concerné, faire la correction minimale, vérifier que les tests existants passent.

```bash
cd /path/to/project
python -m pytest tests/ -x -q --tb=short 2>&1 | tail -20
```

Expected : aucun test cassé par les corrections.

- [ ] **Step 4: Commit corrections sécurité**

```bash
rtk git add <fichiers modifiés>
rtk git commit -m "fix(security): correct blocking findings from beta security audit"
```

---

## Task 2 — Audit solidité runtime

**Files:**
- Read: `app/services/challenges/challenge_ai_service.py`
- Read: `app/services/challenges/challenge_validator.py`
- Read: `app/services/challenges/challenge_deduction_solver.py`
- Read: `frontend/hooks/useChallengeSolverController.ts`
- Read: `frontend/hooks/useAIChallengeGenerator.ts`
- Read: `frontend/hooks/useSubmitAnswer.ts`

- [ ] **Step 1: Lancer l'audit runtime**

```
/octo:review
```

Cibles à spécifier dans le prompt octo:review :
```
Revue solidité runtime ciblée sur :
- app/services/challenges/challenge_ai_service.py : edge cases SSE (finish_reason=length non détecté, fallback qui échoue aussi, stream coupé sans event done)
- app/services/challenges/challenge_validator.py : règles contradictoires ou faux négatifs sur deduction/chess/probability
- app/services/challenges/challenge_deduction_solver.py : absence de timeout — puzzle pathologique peut-il bloquer le worker ?
- frontend/hooks/useChallengeSolverController.ts + useAIChallengeGenerator.ts + useSubmitAnswer.ts : champs optionnels Python traités comme obligatoires en TypeScript ?
- Gamification : challenge SSE retenté après rejected → double point_events possible ?

Ne pas chercher des améliorations de style. Chercher des chemins qui crashent silencieusement ou corrompent des données.
```

- [ ] **Step 2: Trier les findings**

Ajouter à `.claude/audit-runtime-findings.md` :
```
## Bloquants
- [finding]: [fichier:ligne] [description]

## Cosmétiques (roadmap)
- [finding]: [description]
```

- [ ] **Step 3: Corriger chaque finding bloquant**

Pour chaque finding bloquant : lire, corriger, tester.

```bash
python -m pytest tests/ -x -q --tb=short 2>&1 | tail -20
```

Si le finding concerne un hook TypeScript frontend :
```bash
cd frontend && npx vitest run --reporter=verbose 2>&1 | tail -30
```

Expected : aucun test cassé.

- [ ] **Step 4: Commit corrections runtime**

```bash
rtk git add <fichiers modifiés>
rtk git commit -m "fix(runtime): correct blocking findings from beta runtime audit"
```

---

## Task 3 — Percentiles latence dans GenerationMetrics

**Files:**
- Modify: `app/utils/generation_metrics.py`
- Modify: `tests/unit/test_generation_metrics.py`

Les durées sont déjà stockées dans `_generation_history[key]["duration"]` (en secondes). Il suffit d'ajouter un calcul de percentile sans modifier le stockage.

- [ ] **Step 1: Écrire le test qui échoue**

Ajouter dans `tests/unit/test_generation_metrics.py`, dans la classe `TestGenerationMetricsSummary` :

```python
def test_latency_percentiles_in_summary(self):
    metrics = GenerationMetrics()
    # 10 records avec des durées connues pour valider P50/P95
    durations = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    for d in durations:
        metrics.record_generation(
            "deduction",
            success=True,
            validation_passed=True,
            duration_seconds=d,
        )

    summary = metrics.get_summary(days=1)
    assert "latency" in summary
    latency = summary["latency"]
    assert "p50_ms" in latency
    assert "p95_ms" in latency
    # P50 sur 10 valeurs triées : interpolation entre index 4 et 5 (500ms et 600ms)
    assert 540.0 <= latency["p50_ms"] <= 560.0
    # P95 sur 10 valeurs : proche de 950ms
    assert 940.0 <= latency["p95_ms"] <= 960.0

def test_latency_percentiles_empty(self):
    metrics = GenerationMetrics()
    summary = metrics.get_summary(days=1)
    assert summary["latency"] == {"p50_ms": 0.0, "p95_ms": 0.0}
```

- [ ] **Step 2: Vérifier que le test échoue**

```bash
python -m pytest tests/unit/test_generation_metrics.py::TestGenerationMetricsSummary::test_latency_percentiles_in_summary -v 2>&1 | tail -15
```

Expected : `FAILED` — `KeyError: 'latency'`

- [ ] **Step 3: Implémenter `_get_latency_percentiles` et l'exposer dans `get_summary`**

Dans `app/utils/generation_metrics.py`, ajouter la méthode après `get_average_duration` (vers ligne 120) :

```python
def _get_latency_percentiles(
    self, challenge_type: Optional[str] = None, days: int = 1
) -> Dict[str, float]:
    """P50 et P95 de latence en ms sur les générations réussies de la fenêtre."""
    records = self._records_in_window(challenge_type, days, success_only=True)
    durations_ms = sorted(r["duration"] * 1000 for r in records)
    if not durations_ms:
        return {"p50_ms": 0.0, "p95_ms": 0.0}

    def _percentile(data: list, p: float) -> float:
        k = (len(data) - 1) * p / 100
        lo, hi = int(k), min(int(k) + 1, len(data) - 1)
        return data[lo] + (data[hi] - data[lo]) * (k - lo)

    return {
        "p50_ms": round(_percentile(durations_ms, 50), 1),
        "p95_ms": round(_percentile(durations_ms, 95), 1),
    }
```

Dans `get_summary`, ajouter la clé `"latency"` :

```python
def get_summary(self, days: int = 1) -> Dict:
    """Return full runtime summary for admin read-only."""
    return {
        "success_rate": self.get_success_rate(days=days),
        "validation_failure_rate": self.get_validation_failure_rate(days=days),
        "auto_correction_rate": self.get_auto_correction_rate(days=days),
        "average_duration": self.get_average_duration(days=days),
        "latency": self._get_latency_percentiles(days=days),          # NOUVEAU
        "error_code_counts": self._get_error_code_counts(days, challenge_type=None),
        "generation_status_counts": self._get_generation_status_counts(
            days, challenge_type=None
        ),
        "by_type": self._get_summary_by_type(days),
        "by_workload": self._get_summary_by_workload(days),
        "error_types": self._get_error_type_counts(days),
        "retention": runtime_ai_metrics_retention_meta(),
        "metrics_disclaimer_fr": (
            "Métriques runtime opportunistes (mémoire process) : pas d'historique long terme ; "
            "pour comparer des runs figés, utiliser les exécutions harness persistées."
        ),
    }
```

Dans `_get_summary_by_type`, ajouter `latency` par type :

```python
def _get_summary_by_type(self, days: int) -> Dict[str, Dict]:
    summary_by_type = {}
    for metric_key in self._generation_history.keys():
        summary_by_type[metric_key] = {
            "success_rate": self.get_success_rate(metric_key, days),
            "validation_failure_rate": self.get_validation_failure_rate(metric_key, days),
            "auto_correction_rate": self.get_auto_correction_rate(metric_key, days),
            "average_duration": self.get_average_duration(metric_key, days),
            "latency": self._get_latency_percentiles(metric_key, days),    # NOUVEAU
            "total_generations": len(self._records_in_window(metric_key, days)),
            "error_code_counts": self._get_error_code_counts(days, challenge_type=metric_key),
            "generation_status_counts": self._get_generation_status_counts(
                days, challenge_type=metric_key
            ),
        }
    return summary_by_type
```

- [ ] **Step 4: Vérifier que les tests passent**

```bash
python -m pytest tests/unit/test_generation_metrics.py -v 2>&1 | tail -20
```

Expected : tous les tests `PASSED`, dont les deux nouveaux.

- [ ] **Step 5: Commit**

```bash
rtk git add app/utils/generation_metrics.py tests/unit/test_generation_metrics.py
rtk git commit -m "feat(metrics): add P50/P95 latency percentiles to GenerationMetrics"
```

---

## Task 4 — Compteurs chess repair dans GenerationMetrics

**Files:**
- Modify: `app/utils/generation_metrics.py`
- Modify: `app/services/challenges/challenge_ai_service.py`
- Modify: `tests/unit/test_generation_metrics.py`

Le chess repair est actuellement tracké via `generation_status=repaired_by_ai` mais sans compteur de tentatives/échecs. La variable `chess_repair` dans `generate_challenge_stream` prend les valeurs `"none"`, `"chess_ai_attempted"`, `"chess_ai_succeeded"`, `"chess_ai_failed"`.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `tests/unit/test_generation_metrics.py` une nouvelle classe :

```python
class TestChessRepairMetrics:
    def test_chess_repair_counters_in_summary(self):
        metrics = GenerationMetrics()
        metrics.record_chess_repair(succeeded=True)
        metrics.record_chess_repair(succeeded=False)
        metrics.record_chess_repair(succeeded=True)

        summary = metrics.get_summary(days=1)
        assert "chess_repair" in summary
        cr = summary["chess_repair"]
        assert cr["chess_repair_attempted"] == 3
        assert cr["chess_repair_succeeded"] == 2
        assert cr["chess_repair_failed"] == 1

    def test_chess_repair_empty(self):
        metrics = GenerationMetrics()
        summary = metrics.get_summary(days=1)
        assert summary["chess_repair"] == {
            "chess_repair_attempted": 0,
            "chess_repair_succeeded": 0,
            "chess_repair_failed": 0,
        }
```

- [ ] **Step 2: Vérifier que les tests échouent**

```bash
python -m pytest tests/unit/test_generation_metrics.py::TestChessRepairMetrics -v 2>&1 | tail -15
```

Expected : `FAILED` — `AttributeError: 'GenerationMetrics' object has no attribute 'record_chess_repair'`

- [ ] **Step 3: Ajouter `record_chess_repair` et `_get_chess_repair_stats` dans `GenerationMetrics`**

Dans `__init__`, ajouter après `self._failure_count` :

```python
self._chess_repair_events: List[Dict] = []  # {timestamp: datetime, succeeded: bool}
```

Ajouter la méthode `record_chess_repair` après `record_generation` :

```python
def record_chess_repair(self, succeeded: bool) -> None:
    """Enregistre une tentative de réparation IA chess (tentative et résultat)."""
    self._chess_repair_events.append(
        {"timestamp": datetime.now(), "succeeded": succeeded}
    )
    # Purge simple : garder seulement les 7 derniers jours
    from app.utils import ai_workload_keys as _wk
    cutoff = datetime.now() - timedelta(days=_wk.RUNTIME_AI_METRICS_RETENTION_DAYS)
    self._chess_repair_events = [
        e for e in self._chess_repair_events if e["timestamp"] > cutoff
    ]
```

Ajouter `_get_chess_repair_stats` après `_get_error_code_counts` :

```python
def _get_chess_repair_stats(self, days: int) -> Dict[str, int]:
    """Compteurs de tentatives/succès/échecs du repair IA chess."""
    cutoff = datetime.now() - timedelta(days=days)
    events = [e for e in self._chess_repair_events if e["timestamp"] > cutoff]
    attempted = len(events)
    succeeded = sum(1 for e in events if e["succeeded"])
    return {
        "chess_repair_attempted": attempted,
        "chess_repair_succeeded": succeeded,
        "chess_repair_failed": attempted - succeeded,
    }
```

Dans `get_summary`, ajouter la clé `"chess_repair"` :

```python
"chess_repair": self._get_chess_repair_stats(days),   # NOUVEAU
```

- [ ] **Step 4: Instrumenter le chess repair dans `challenge_ai_service.py`**

Dans `challenge_ai_service.py`, repérer le bloc chess repair (autour de la ligne 937 où `chess_repair_succeeded = True` est positionné, et ligne 942 où `chess_repair = "chess_ai_failed"`).

Ajouter l'import de `generation_metrics` si non déjà présent en tête du fichier (déjà importé : `from app.utils.generation_metrics import generation_metrics`).

Dans le bloc chess repair, **après** la résolution `is_valid_after_repair` :

```python
# Ligne ~937 — succès repair :
if is_valid_after_repair:
    logger.info("Réparation IA CHESS réussie")
    challenge_data = repaired_challenge
    auto_corrected = True
    chess_repair_succeeded = True
    validation_passed = True
    chess_repair = "chess_ai_succeeded"
    generation_metrics.record_chess_repair(succeeded=True)   # NOUVEAU
else:
    remaining_errors = repair_errors
    chess_repair = "chess_ai_failed"
    generation_metrics.record_chess_repair(succeeded=False)  # NOUVEAU
```

Également ajouter pour le cas `repair_error is not None` (ligne ~926, `chess_repair = "chess_ai_failed"`):

```python
if repair_error is not None:
    chess_repair = "chess_ai_failed"
    generation_metrics.record_chess_repair(succeeded=False)  # NOUVEAU
```

- [ ] **Step 5: Vérifier que les tests passent**

```bash
python -m pytest tests/unit/test_generation_metrics.py -v 2>&1 | tail -20
```

Expected : tous `PASSED`.

- [ ] **Step 6: Commit**

```bash
rtk git add app/utils/generation_metrics.py app/services/challenges/challenge_ai_service.py tests/unit/test_generation_metrics.py
rtk git commit -m "feat(metrics): add explicit chess repair counters to GenerationMetrics"
```

---

## Task 5 — Fallback cause et repair_success_rate dans GenerationMetrics

**Files:**
- Modify: `app/utils/generation_metrics.py`
- Modify: `app/services/challenges/challenge_ai_service.py`
- Modify: `tests/unit/test_generation_metrics.py`

`fallback_trigger_reason` est actuellement loggué mais jamais passé à `record_generation`. `repair_success_rate` se calcule depuis les `generation_status` déjà stockés.

- [ ] **Step 1: Écrire les tests qui échouent**

Ajouter dans `TestGenerationMetricsSummary` :

```python
def test_fallback_stats_in_summary(self):
    metrics = GenerationMetrics()
    metrics.record_generation(
        "visual",
        success=False,
        validation_passed=False,
        duration_seconds=0.5,
        error_type="fallback_empty_response",
        fallback_trigger_reason="empty_response",
    )
    metrics.record_generation(
        "visual",
        success=False,
        validation_passed=False,
        duration_seconds=0.8,
        error_type="fallback_empty_response",
        fallback_trigger_reason="length_truncation",
    )
    metrics.record_generation(
        "visual",
        success=True,
        validation_passed=True,
        duration_seconds=1.2,
    )

    summary = metrics.get_summary(days=1)
    assert "fallback_stats" in summary
    fs = summary["fallback_stats"]
    assert fs["fallback_count"] == 2
    assert abs(fs["fallback_rate"] - 66.67) < 0.1
    assert fs["fallback_causes"]["empty_response"] == 1
    assert fs["fallback_causes"]["length_truncation"] == 1

def test_repair_success_rate_in_summary(self):
    metrics = GenerationMetrics()
    metrics.record_generation(
        "chess",
        success=True,
        validation_passed=True,
        duration_seconds=1.0,
        generation_status="repaired_by_ai",
    )
    metrics.record_generation(
        "chess",
        success=True,
        validation_passed=True,
        duration_seconds=0.9,
        generation_status="repaired",
    )
    metrics.record_generation(
        "chess",
        success=True,
        validation_passed=True,
        duration_seconds=0.8,
        generation_status="accepted",
    )

    summary = metrics.get_summary(days=1)
    assert "repair_success_rate" in summary
    # repaired_by_ai=1 / (repaired + repaired_by_ai)=2 → 50.0%
    assert summary["repair_success_rate"] == 50.0
```

- [ ] **Step 2: Vérifier que les tests échouent**

```bash
python -m pytest tests/unit/test_generation_metrics.py::TestGenerationMetricsSummary::test_fallback_stats_in_summary tests/unit/test_generation_metrics.py::TestGenerationMetricsSummary::test_repair_success_rate_in_summary -v 2>&1 | tail -15
```

Expected : `FAILED`

- [ ] **Step 3: Étendre `record_generation` pour stocker `fallback_trigger_reason`**

Dans `app/utils/generation_metrics.py`, ajouter le paramètre à `record_generation` :

```python
def record_generation(
    self,
    challenge_type: str,
    success: bool,
    validation_passed: bool = True,
    auto_corrected: bool = False,
    duration_seconds: float = 0.0,
    error_type: Optional[str] = None,
    generation_status: Optional[str] = None,
    error_codes: Optional[List[str]] = None,
    fallback_trigger_reason: Optional[str] = None,   # NOUVEAU
) -> None:
```

Dans le corps, ajouter dans le `record` dict (après `"generation_status": generation_status,`) :

```python
if fallback_trigger_reason is not None:
    record["fallback_trigger_reason"] = fallback_trigger_reason
```

- [ ] **Step 4: Ajouter `_get_fallback_stats` et `_get_repair_success_rate`**

Ajouter après `_get_chess_repair_stats` :

```python
def _get_fallback_stats(
    self, days: int, challenge_type: Optional[str] = None
) -> Dict:
    """Taux et causes des déclenchements fallback o-series."""
    records = self._records_in_window(challenge_type, days)
    total = len(records)
    fallback_records = [r for r in records if r.get("fallback_trigger_reason")]
    fallback_count = len(fallback_records)
    causes: Dict[str, int] = {}
    for r in fallback_records:
        cause = r["fallback_trigger_reason"]
        causes[cause] = causes.get(cause, 0) + 1
    return {
        "fallback_rate": round((fallback_count / total * 100), 2) if total else 0.0,
        "fallback_count": fallback_count,
        "fallback_causes": causes,
    }

def _get_repair_success_rate(
    self, days: int, challenge_type: Optional[str] = None
) -> float:
    """% de défis réparés qui ont nécessité le repair IA chess (repaired_by_ai / total repaired)."""
    records = self._records_in_window(challenge_type, days)
    total_repaired = sum(
        1 for r in records
        if r.get("generation_status") in ("repaired", "repaired_by_ai")
    )
    repaired_by_ai = sum(
        1 for r in records if r.get("generation_status") == "repaired_by_ai"
    )
    if total_repaired == 0:
        return 0.0
    return round(repaired_by_ai / total_repaired * 100, 1)
```

- [ ] **Step 5: Exposer dans `get_summary`**

Ajouter dans `get_summary` :

```python
"fallback_stats": self._get_fallback_stats(days),          # NOUVEAU
"repair_success_rate": self._get_repair_success_rate(days), # NOUVEAU
```

- [ ] **Step 6: Passer `fallback_trigger_reason` dans `challenge_ai_service.py`**

Dans `challenge_ai_service.py`, localiser `_record_generation_failure` à la ligne ~772 (chemin fallback vide). Étendre la signature de `_record_generation_failure` pour accepter `fallback_trigger_reason`:

La fonction locale `_record_generation_failure` (définie à la ligne ~458) doit passer le paramètre à `generation_metrics.record_generation`. Ajouter :

```python
def _record_generation_failure(
    *,
    error_type: str,
    validation_ok: bool = False,
    auto_corrected_flag: bool = False,
    generation_status: Optional[ChallengePipelineGenerationStatus] = None,
    error_codes: Optional[list[str]] = None,
    fallback_trigger_reason: Optional[str] = None,   # NOUVEAU
) -> None:
    duration = (datetime.now() - start_time).total_seconds()
    generation_metrics.record_generation(
        challenge_type=challenge_type,
        success=False,
        validation_passed=validation_ok,
        auto_corrected=auto_corrected_flag,
        duration_seconds=duration,
        error_type=error_type,
        generation_status=generation_status,
        error_codes=error_codes,
        fallback_trigger_reason=fallback_trigger_reason,   # NOUVEAU
    )
```

Puis à l'appel ligne ~772 (fallback vide) :

```python
_record_generation_failure(
    error_type="fallback_empty_response",
    fallback_trigger_reason=fallback_trigger_reason,   # NOUVEAU
)
```

Également au succès (ligne ~1020), passer `fallback_trigger_reason` si disponible (variable locale déjà définie) :

```python
generation_metrics.record_generation(
    challenge_type=challenge_type,
    success=True,
    validation_passed=validation_passed,
    auto_corrected=auto_corrected,
    duration_seconds=duration,
    generation_status=pipeline_generation_status,
    fallback_trigger_reason=fallback_trigger_reason if fallback_trigger_reason else None,  # NOUVEAU
)
```

- [ ] **Step 7: Vérifier que tous les tests passent**

```bash
python -m pytest tests/unit/test_generation_metrics.py -v 2>&1 | tail -25
```

Expected : tous `PASSED`.

- [ ] **Step 8: Commit**

```bash
rtk git add app/utils/generation_metrics.py app/services/challenges/challenge_ai_service.py tests/unit/test_generation_metrics.py
rtk git commit -m "feat(metrics): add fallback_stats and repair_success_rate to GenerationMetrics (Phase 2A)"
```

---

## Task 6 — generation_confidence log-only dans challenge_ai_service

**Files:**
- Modify: `app/services/challenges/challenge_ai_service.py`

Le score est calculé à partir de variables locales déjà disponibles au moment du `pipeline_generation_status`. `calibration_meta` est accessible via `challenge_data.get("difficulty_calibration", {})` (à ce stade `challenge_data` = `normalized_challenge` issu de `normalize_generated_challenge`).

Pas de test unitaire isolable ici (calcul purement local, pas de retour de fonction). La vérification se fait par lecture des logs en dev.

- [ ] **Step 1: Ajouter le calcul de `generation_confidence` après `pipeline_generation_status`**

Dans `challenge_ai_service.py`, localiser la ligne ~981 (`pipeline_generation_status = _resolve_challenge_pipeline_generation_status(...)`).

Ajouter immédiatement après ce bloc (avant `if chess_repair_succeeded:`) :

```python
# --- generation_confidence (log-only, beta phase) ---
_calibration = (
    challenge_data.get("difficulty_calibration", {})
    if isinstance(challenge_data, dict)
    else {}
)
_difficulty_clamped = bool(
    _calibration.get("caps_applied") or _calibration.get("floors_applied")
)
_confidence = 1.0
if chess_repair_succeeded:
    _confidence -= 0.3
if auto_corrected and not chess_repair_succeeded:
    _confidence -= 0.1
if _difficulty_clamped:
    _confidence -= 0.2
if validation_passed and not auto_corrected:
    _confidence += 0.1
_confidence = round(max(0.0, min(1.0, _confidence)), 2)
logger.info(
    "Challenge generation_confidence: type={}, status={}, confidence={}, "
    "chess_repair={}, auto_corrected={}, difficulty_clamped={}",
    challenge_type,
    pipeline_generation_status,
    _confidence,
    chess_repair_succeeded,
    auto_corrected,
    _difficulty_clamped,
)
# --- fin generation_confidence ---
```

- [ ] **Step 2: Vérifier que le backend démarre sans erreur**

```bash
python -c "from app.services.challenges.challenge_ai_service import generate_challenge_stream; print('OK')"
```

Expected : `OK`

- [ ] **Step 3: Vérifier que les tests backend passent**

```bash
python -m pytest tests/ -x -q --tb=short 2>&1 | tail -20
```

Expected : aucun test cassé.

- [ ] **Step 4: Commit**

```bash
rtk git add app/services/challenges/challenge_ai_service.py
rtk git commit -m "feat(metrics): add generation_confidence log-only score to challenge pipeline (Phase 2B)"
```

---

## Task 7 — Alignement docs/version

**Files:**
- Modify: `README_TECH.md`
- Modify: `CLAUDE.md`
- Modify: `C:\Users\yanni\.claude\projects\D--Mathakine\memory\project_mathakine_context.md`

- [ ] **Step 1: Mettre à jour `README_TECH.md`**

Localiser la ligne `- \`3.6.0-beta.2\`` (première occurrence en tête du fichier) et remplacer par :

```
- `3.6.0-beta.4`
```

Localiser `pyproject.toml now carries the equivalent PEP 440 package metadata version: \`3.6.0b2\`` et remplacer par :

```
pyproject.toml now carries the equivalent PEP 440 package metadata version: `3.6.0b4`
```

Vérifier que nulle part ailleurs `beta.2` ou `beta.3` n'apparaît comme version courante (grep avant commit).

```bash
grep -n "beta\.2\|beta\.3\|3\.6\.0b2\|3\.6\.0b3" README_TECH.md
```

Si des occurrences historiques apparaissent dans des notes de fermeture, les laisser — elles sont contextuelles. Ne corriger que la version courante en tête de fichier.

- [ ] **Step 2: Mettre à jour `CLAUDE.md`**

Localiser `**Version** : \`3.6.0-beta.2\`` dans la table Stack technique et remplacer par :

```
**Version** : `3.6.0-beta.4`
```

Localiser la ligne `- Version` dans la table Stack technique :

```
| Version       | `3.6.0-beta.2`                                                          |
```

Remplacer par :

```
| Version       | `3.6.0-beta.4`                                                          |
```

Localiser dans **Position produit** la ligne `- train visible courant : **\`3.6.0-beta.2\`**` et remplacer par :

```
- train visible courant : **`3.6.0-beta.4`**
```

- [ ] **Step 3: Mettre à jour le fichier mémoire**

Ouvrir `C:\Users\yanni\.claude\projects\D--Mathakine\memory\project_mathakine_context.md`.

Mettre à jour la version et l'état du plan solidification :
- Version : `3.6.0-beta.4`
- Plan solidification défis : Phase 0, 1A, 1B = réalisées ; Phase 2A = fermée (métriques repair, chess, fallback, percentiles) ; Phase 2B = log-only confidence ajouté ; Phase 3, 4, json_schema = non démarré

- [ ] **Step 4: Vérifier la cohérence**

```bash
grep -rn "3\.6\.0-beta\.2\|3\.6\.0-beta\.3" CLAUDE.md README_TECH.md
```

Expected : zéro occurrence en position de version courante (les occurrences dans CHANGELOG ou notes historiques sont acceptables).

- [ ] **Step 5: Commit**

```bash
rtk git add README_TECH.md CLAUDE.md "C:\Users\yanni\.claude\projects\D--Mathakine\memory\project_mathakine_context.md"
rtk git commit -m "docs(version): align README_TECH, CLAUDE.md and memory to 3.6.0-beta.4"
```

---

## Vérification finale

- [ ] `python -m pytest tests/ -q --tb=short 2>&1 | tail -10` — aucune régression backend
- [ ] `cd frontend && npx vitest run 2>&1 | tail -15` — aucune régression frontend
- [ ] `grep "generation_confidence\|chess_repair_attempted\|fallback_rate\|p50_ms" app/utils/generation_metrics.py` — tous présents
- [ ] `grep "3.6.0-beta.4" README_TECH.md CLAUDE.md` — version correcte dans les deux fichiers
