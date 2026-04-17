# Session Plan — Beta Fermée Mathakine

**Créé :** 2026-04-16  
**Intent Contract :** `.claude/session-intent.md`  
**Version cible :** v3.6.0-beta.1

---

## Ce que tu auras à la fin

Une version beta fermée stable, sécurisée et instrumentée, prête à accueillir des invités réels :
- Feedback-debug opérationnel avec contexte complet (rôle, thème, NI, emplacement)
- Auth solide et Dependabot #41 résolu
- Documentation utilisateur de base pour enfant + parent/enseignant
- Décision architecturale OAuth Google documentée

---

## Plan d'exécution

### PHASE 1 — DEFINE (15%) : Inventaire et architecture ✅ TERMINÉ

**Objectif :** Cadrer chaque chantier avant de toucher le code.

| Tâche | Statut |
|-------|--------|
| D1 — Auditer le payload feedback actuel | ✅ fait (payload enrichi en A1) |
| D2 — Auditer l'affichage admin feedback | ✅ fait (list_feedback_for_admin étendu) |
| D3 — Lister les emplacements feedback discret | ✅ identifié (A4 à venir) |
| D4 — Point d'architecture OAuth Google | ⏳ reporté post-beta |
| D5 — Inventaire OWASP quick-pass | ✅ fait (M1 M2 M3 M4 L1 L2) |

---

### PHASE 2 — DEVELOP (55%) : Trois chantiers en parallèle

#### Chantier A — Feedback-Debug (priorité 1)

| Tâche | Statut | Commit |
|-------|--------|--------|
| **A1** — Modèle + migration + handler backend | ✅ TERMINÉ | `bd130e3` + `9892fe9` + `af93508` + `daa6fb5` |
| **A2** — Frontend `FeedbackFab.tsx` envoie les 4 champs | ✅ TERMINÉ | `bdba53c` |
| **A3** — Vue admin affiche les nouveaux champs | ✅ TERMINÉ | `132368f` |
| **A4** — Repositionnement bouton (header, fin exercice, fin défi) | ✅ TERMINÉ | `ae08c8f` |

#### Chantier B — Sécurité / Auth ✅ TERMINÉ

| Tâche | Statut | Commit |
|-------|--------|--------|
| **B1** — Dependabot #41 (DOMPurify 3.3.3→3.4.0) | ✅ TERMINÉ | `ebfa039` |
| **B2** — OWASP quick-pass (M1 Permissions-Policy, M2 rate-limit feedback, M3 privacy RGPD) | ✅ TERMINÉ | `4c822fe` `ef1ea49` `68c052e` |
| **B3** — Évaluation OAuth Google | ⏳ reporté post-beta | — |

#### Chantier C — Documentation utilisateur

| Tâche | Statut |
|-------|--------|
| **C1** — Onboarding in-app (tooltips first-use) | ⏳ À FAIRE |
| **C2** — Page `/help` FAQ contextuelle | ⏳ À FAIRE |
| **C3** — `docs/BETA_GUIDE.md` (instructions invités) | ⏳ À FAIRE |

---

### PHASE 3 — DELIVER (30%) : Validation et tag

| Tâche | Critère |
|-------|---------|
| Smoke test beta : parcours enfant complet (register → exercice → défi → feedback) | Aucun crash |
| Smoke test admin : login admin → voir feedbacks avec contexte complet | Données correctes |
| `npx tsc --noEmit` + `prettier --check` + `pytest -q` verts | CI verte |
| Tag `v3.6.0-beta.1` + entry CHANGELOG | Fait |
| Email d'invitation aux 3-5 premiers bêta-testeurs | Liste préparée |

---

## Séquencement recommandé (solo founder)

```
Semaine 1 : Phase 1 (Define) + Chantier B1 (Dependabot #41, quick-win)
Semaine 2 : Chantier A1-A3 (feedback backend + admin)
Semaine 3 : Chantier A4 (repositionnement) + Chantier B2 (OWASP)
Semaine 4 : Chantier B3 (OAuth eval) + Chantier C (doc)
Semaine 5 : Phase 3 (Deliver) + tag beta
```

---

## 🔸 Points de décision (debate checkpoints)

| Moment | Question | Format |
|--------|----------|--------|
| Après D4 | "next-auth vs backend-only pour OAuth Google ?" | `/octo:debate` 1 round |
| Après A2 | "prop feedbackContext vs hook usePageContext ?" | Claude Code analyse |
| Avant tag | "la beta est-elle prête ?" | `/octo:review` working-tree |

---

## Providers disponibles

| Provider | Statut | Rôle |
|----------|--------|------|
| 🔴 Codex CLI | Available ✓ | Architecture OAuth, séquencement chantiers |
| 🟡 Gemini CLI | Available ✓ | Audit sécurité OWASP, edge cases |
| 🟣 Perplexity | Not configured ✗ | CVE lookup |
| 🔵 Claude | Available ✓ | Synthèse, review, documentation |

---

## Pour exécuter ce plan

```bash
# Phase par phase
/octo:security   # Chantier B (OWASP quick-pass)
/octo:develop    # Chantier A (feedback-debug)
/octo:docs       # Chantier C (documentation)
/octo:review     # Phase Deliver (validation finale)

# Ou en lifecycle complet
/octo:embrace "beta fermée Mathakine v3.6.0"
```
