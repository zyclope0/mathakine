# 📕 Gestion projet Mathakine

> Index maître — Audits, recommandations, rapports situationnels  
> **Dernière mise à jour :** 07/03/2026 (F32 + F35 documentés, B1/B2/F2 traités)

---

## 📁 Taxonomie des documents

| Type | Description | Emplacement |
|------|-------------|-------------|
| **Référence** | Document de référence actuel, état des lieux | Racine `03-PROJECT/` |
| **Audit actif** | Audit avec recommandations partielles ou en cours | Racine `03-PROJECT/` |
| **À faire** | Endpoints, placeholders, TODO | Racine `03-PROJECT/` |
| **Audits implémentés** | Toutes les recommandations appliquées | `AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` |
| **Rapports situationnels** | Récaps mission, plans, rapports historiques | `AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` |
| **Historique** | Bilan phases, vérifications anciennes | `RAPPORTS_TEMPORAIRES/` |

---

## 📄 Documents actifs (racine 03-PROJECT)

### Référence

| Document | Date | Rôle |
|----------|------|------|
| **[EVALUATION_PROJET_2026-02-07.md](./EVALUATION_PROJET_2026-02-07.md)** | 07/02/2026 | ⭐ **Document de référence** — Évaluation factuelle qualité (scores, risques, priorités). Remplace BILAN_COMPLET et PLAN_ACTION. |
| **[POINT_SITUATION_2026-02-18.md](./POINT_SITUATION_2026-02-18.md)** | 18/02/2026 | **Point de situation** — Bilan fonctionnalités livrées, priorités P1-P2, références rapides. |
| **[CICD_DEPLOY.md](./CICD_DEPLOY.md)** | Fév. 2026 | **CI/CD opérationnel** — CI automatique, smoke test /health, migrations Alembic, rollback manuel. |
| **[POLITIQUE_REDACTION_LOGS_PII.md](./POLITIQUE_REDACTION_LOGS_PII.md)** | 22/02/2026 | **Politique** — Règles PII et secrets dans les logs. |

### Implémentations backlog (récentes)

| Document | Date | Sujet |
|----------|------|-------|
| **[IMPLEMENTATION_F32_SESSION_ENTRELACEE.md](./IMPLEMENTATION_F32_SESSION_ENTRELACEE.md)** | 07/03/2026 | **F32** — Session entrelacée (plan interleaved, CTA Quick Start, flux session côté frontend) |
| **[IMPLEMENTATION_F35_REDACTION_LOGS_DB.md](./IMPLEMENTATION_F35_REDACTION_LOGS_DB.md)** | 07/03/2026 | **F35** — Redaction des secrets dans les logs DB (`app/db/base.py`, tests unitaires) |

### Guidage implementation (Cursor)

| Document | Date | Sujet |
|----------|------|-------|
| **[GUIDAGE_CURSOR_ALIGNEMENT_POST_IMPL_2026-03-08.md](./GUIDAGE_CURSOR_ALIGNEMENT_POST_IMPL_2026-03-08.md)** | 08/03/2026 | **Guide d'execution** — recommandations post-audit pour analytics interleaved, robustesse session, hygiene quality gates, DRY et standardisation |

### Refactoring (terminé P1–P3 / Ph1–Ph3)

| Document | Date | Sujet |
|----------|------|-------|
| **[REFACTOR_STATUS_2026-02.md](./REFACTOR_STATUS_2026-02.md)** | 07/03/2026 | **État refactor** — Clean Code P1–P3, Architecture Ph1–Ph3, stabilisation pré-backlog (`F1.1/F1.2` faits, `F1.3/F1.4` restants) |
| **[REFACTOR_DASHBOARD_2026-03.md](./REFACTOR_DASHBOARD_2026-03.md)** | 06/03/2026 | **Dashboard** — Réorganisation onglets (Vue d'ensemble, Progression, Mon Profil) |
| **[PLAN_STABILISATION_PRE_BACKLOG_2026-03-06.md](./PLAN_STABILISATION_PRE_BACKLOG_2026-03-06.md)** | 07/03/2026 | **Plan guidé** — Stabilisation backend/frontend avant backlog, B1/B2/F2 traités, `F1.1/F1.2` faits, `F1.3/F1.4` restants |
| [PLAN_CLEAN_CODE_ET_DTO_2026-02.md](./PLAN_CLEAN_CODE_ET_DTO_2026-02.md) | 28/02/2026 | DTO, exceptions, typage — P4 (admin, OpenAPI) restant ; mypy ✅ fait |
| [PLAN_REFACTO_ARCHITECTURE_2026-02.md](./AUDITS_ET_RAPPORTS_ARCHIVES/PLAN_REFACTO_ARCHITECTURE_2026-02.md) | 28/02/2026 | Routes découpées, handlers, ExerciseStatsService — Ph4 reporté |

### Audits avec recommandations partielles

| Document | Date | Sujet | État |
|----------|------|-------|------|
| **[AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md](./AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md)** | 03/03/2026 | Audit frontend exhaustif (Architecture, DRY, Design System, UX, Visuel, A11Y) — 5 axes + plan 5 phases (Phases 0–4) | ✅ **Terminé** (P3.2 en backlog) |
| **[AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md](./AUDIT_BACKEND_INDUSTRIALISATION_2026-02.md)** | 28/02/2026 | Audit backend (5 piliers) + plan itérations Dev/Test/Prod | It1–4 ✅, It5.2 mypy + types critiques ✅ |
| [AUDIT_DASHBOARD_2026-02.md](./AUDIT_DASHBOARD_2026-02.md) | Fév. 2026 | Dashboard — imports, i18n, handleRefresh | Recos partielles |
| [AUDIT_SENTRY_2026-02.md](./AUDIT_SENTRY_2026-02.md) | Fév. 2026 | Configuration Sentry, monitoring | Référence config |
| [ANALYSE_DUPLICATION_DRY_2026-02.md](./ANALYSE_DUPLICATION_DRY_2026-02.md) | Fév. 2026 | DRY, duplication code | ~90 % traité (db_session, parse_json_body, safe_parse_json, api_error_response, exceptions P3) — vérité terrain 28/02 |
| **[AUDIT_CODE_CLEANUP_2026-03-01.md](./AUDIT_CODE_CLEANUP_2026-03-01.md)** | 01/03/2026 | Bugs, dead code, incohérences (app/, server/, frontend/) | 4 CRITICAL, 15 HIGH, 20 MEDIUM — plan d'action priorisé |

### Vulnérabilités (CVE)

→ [SECURITY_AUDIT_REPORT.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/SECURITY_AUDIT_REPORT.md) — archivé (12/02/2026)

### À faire

| Document | Sujet |
|----------|-------|
| [ENDPOINTS_NON_INTEGRES.md](./ENDPOINTS_NON_INTEGRES.md) | Endpoints API — section Admin intégrée (16/02) |
| [PLACEHOLDERS_ET_TODO.md](./AUDITS_ET_RAPPORTS_ARCHIVES/PLACEHOLDERS_ET_TODO.md) | Placeholders restants (4 routes supprimées 22/02 : start_challenge, get_challenge_progress, get_challenge_rewards, get_user_progress_by_exercise_type) |

### Historique (archivé, consultable)

→ Tous les documents archivés : [AUDITS_IMPLEMENTES](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/INDEX.md) | [RAPPORTS_TEMPORAIRES](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md)

Exemples : **Audit Backend Alpha 2** (clôturé 28/02 — [clôture](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/CLOTURE_AUDIT_BACKEND_ALPHA2_2026-02-22.md)), Dette qualité frontend, Refacto handlers, Migration Alembic, BILAN_COMPLET, PHASES…

---

## 📦 Archives

### Audits implémentés

Toutes les recommandations ont été appliquées.

→ **[AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/INDEX.md)**

### Rapports situationnels

Récaps mission, plans, rapports contextuels (contexte historique).

→ **[AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md#rapports_temporaires)**

---

## 📐 Convention de nommage

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| `AUDIT_` | Audits techniques, sécurité, qualité | `AUDIT_DASHBOARD_2026-02.md` |
| `ANALYSE_` | Analyses (DRY, thèmes UX) | `ANALYSE_DUPLICATION_DRY_2026-02.md` |
| `RAPPORT_` | Rapports situationnels, vérifications | `RAPPORT_VERIFICATION_CHALLENGES.md` |
| `EVALUATION_` | Évaluation globale projet | `EVALUATION_PROJET_2026-02-07.md` |

**Format date :** `YYYY-MM` ou `YYYY-MM-DD` en suffixe.

→ Voir [CONVENTION_DOCUMENTATION.md](../CONVENTION_DOCUMENTATION.md) pour les règles complètes.

**Revue trimestrielle** : l'accumulation de rapports historiques rend la maintenance difficile. Prévoir une revue trimestrielle des docs de référence (README, README_TECH) pour aligner avec le code — voir [CONVENTION_DOCUMENTATION.md](../CONVENTION_DOCUMENTATION.md) §7.

---

## 🔗 Navigation

- [← Index documentation](../INDEX.md)
- [Audits implémentés — détail](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/INDEX.md)
- [Archives — README](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
