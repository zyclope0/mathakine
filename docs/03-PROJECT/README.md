# 📕 Gestion projet Mathakine

> Index maître — Audits, recommandations, rapports situationnels  
> **Dernière mise à jour :** 16/02/2026

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
| **[DEPLOIEMENT_2026-02-06.md](./DEPLOIEMENT_2026-02-06.md)** | 06/02/2026 | Guide déploiement Render, variables d'environnement |

### Audits avec recommandations partielles

| Document | Date | Sujet | État |
|----------|------|-------|------|
| [AUDIT_DASHBOARD_2026-02.md](./AUDIT_DASHBOARD_2026-02.md) | Fév. 2026 | Dashboard — imports, i18n, handleRefresh | Recos partielles |
| [AUDIT_SENTRY_2026-02.md](./AUDIT_SENTRY_2026-02.md) | Fév. 2026 | Configuration Sentry, monitoring | Référence config |
| [AUDIT_SECURITE_APPLICATIVE_2026-02.md](./AUDIT_SECURITE_APPLICATIVE_2026-02.md) | Fév. 2026 | OWASP Top 10, sécurité applicative | ✅ Post-corrections |
| [ANALYSE_DUPLICATION_DRY_2026-02.md](./ANALYSE_DUPLICATION_DRY_2026-02.md) | Fév. 2026 | DRY, duplication code | ~70–80 % traité |

### Vulnérabilités (CVE / npm / pip)

| Document | Emplacement | Sujet |
|----------|-------------|-------|
| [SECURITY_AUDIT_REPORT.md](../SECURITY_AUDIT_REPORT.md) | `docs/` racine | CVE Next.js, requests, Jinja2, npm audit — statut des vulnérabilités |

### À faire

| Document | Sujet |
|----------|-------|
| [ENDPOINTS_NON_INTEGRES.md](./ENDPOINTS_NON_INTEGRES.md) | Endpoints API — section Admin intégrée (16/02) |
| [PLACEHOLDERS_ET_TODO.md](./PLACEHOLDERS_ET_TODO.md) | Placeholders restants (badges progress, recommandations complete, etc.) |

### Historique (archivé, consultable)

| Document | Rôle |
|----------|------|
| [BILAN_COMPLET.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/BILAN_COMPLET.md) | Phases 1–6 (nov. 2025) — remplacé par EVALUATION_PROJET |
| [RAPPORT_VERIFICATION_CHALLENGES.md](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/RAPPORT_VERIFICATION_CHALLENGES.md) | Vérification défis 29/11/2025 |
| [PHASES/](./AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/PHASES/) | Documentation phases historiques (RECAP, PHASE6) |

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

---

## 🔗 Navigation

- [← Index documentation](../INDEX.md)
- [Audits implémentés — détail](./AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/INDEX.md)
- [Archives — README](./AUDITS_ET_RAPPORTS_ARCHIVES/README.md)
