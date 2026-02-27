# 📕 Gestion projet Mathakine

> Index maître — Audits, recommandations, rapports situationnels  
> **Dernière mise à jour :** 28/02/2026

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

### Audits avec recommandations partielles

| Document | Date | Sujet | État |
|----------|------|-------|------|
| [AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md](./AUDIT_TECHNIQUE_BACKEND_ALPHA2_2026-02-27.md) | 27/02/2026 | ⭐ **Audit Backend Alpha 2** — modularité, config, reprod., observabilité. Plan d'action 5 étapes. | Actif |
| [CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md](./CHALLENGE_AUDIT_TECHNIQUE_BACKEND_2026-02-28.md) | 28/02/2026 | **Challenge factuel** — vérification de l'audit 27/02 vs code réel. Tous les points confirmés. | Référence |
| [PRIORISATION_AUDIT_BACKEND_ALPHA2_2026-02-28.md](./PRIORISATION_AUDIT_BACKEND_ALPHA2_2026-02-28.md) | 28/02/2026 | **Priorisation** — risque × facilité × gain. P1 implémenté (erreurs unifiées, SQL badge → service, requirements). | Référence |
| [AUDIT_DASHBOARD_2026-02.md](./AUDIT_DASHBOARD_2026-02.md) | Fév. 2026 | Dashboard — imports, i18n, handleRefresh | Recos partielles |
| [AUDIT_SENTRY_2026-02.md](./AUDIT_SENTRY_2026-02.md) | Fév. 2026 | Configuration Sentry, monitoring | Référence config |
| [ANALYSE_DUPLICATION_DRY_2026-02.md](./ANALYSE_DUPLICATION_DRY_2026-02.md) | Fév. 2026 | DRY, duplication code | ~90 % traité (db_session, parse_json_body, safe_parse_json) — vérité terrain 25/02 |

### Vulnérabilités (CVE)

→ [SECURITY_AUDIT_REPORT.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/SECURITY_AUDIT_REPORT.md) — archivé (12/02/2026)

### À faire

| Document | Sujet |
|----------|-------|
| [ENDPOINTS_NON_INTEGRES.md](./ENDPOINTS_NON_INTEGRES.md) | Endpoints API — section Admin intégrée (16/02) |
| [PLACEHOLDERS_ET_TODO.md](./PLACEHOLDERS_ET_TODO.md) | Placeholders restants (4 supprimés 22/02) — maintenance_mode, delete_user, etc. |

### Historique (archivé, consultable)

→ Tous les documents archivés : [AUDITS_IMPLEMENTES](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/INDEX.md) | [RAPPORTS_TEMPORAIRES](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/INDEX.md)

Exemples : Backend Alpha 2, Dette qualité frontend, Qualité code, Refacto handlers, Migration Alembic, BILAN_COMPLET, PHASES…

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
