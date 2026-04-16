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

### PHASE 1 — DEFINE (15%) : Inventaire et architecture

**Objectif :** Cadrer chaque chantier avant de toucher le code.

| Tâche | Outil suggéré |
|-------|--------------|
| D1 — Auditer le payload feedback actuel (quels champs manquent) | Claude Code / Grep |
| D2 — Auditer l'affichage admin feedback (champs manquants côté UI) | Claude Code / Read |
| D3 — Lister les emplacements clés pour le bouton feedback discret | Claude Code / Explore |
| D4 — Point d'architecture OAuth Google (Starlette + JWT + next-auth ?) | Claude Code + Codex |
| D5 — Inventaire OWASP : headers, cookies, rate-limit, CSRF | `/octo:security` quick-pass |

**Livrable :** Fiche de chantier par item (scope + approach + risk).

---

### PHASE 2 — DEVELOP (55%) : Trois chantiers en parallèle

#### Chantier A — Feedback-Debug (priorité 1)

**A1 — Enrichissement payload backend**
- Ajouter au modèle `Feedback` : `user_role`, `active_theme`, `ni_state`, `page_path`, `component_id`
- Migration Alembic
- Route POST `/api/feedback` : lire ces champs du body

**A2 — Enrichissement payload frontend**
- `FeedbackFab.tsx` : collecter role (store auth), theme (localeStore / themeStore), ni_state, pathname + composant déclarant
- Pattern recommandé : prop `feedbackContext` sur le composant hôte, injectée dans le body POST

**A3 — Vue admin complète**
- `app/admin/feedback/page.tsx` (ou équivalent) : afficher les nouveaux champs
- Colonnes : rôle, thème, NI, page, composant, message, date

**A4 — Repositionnement bouton**
- Composant `FeedbackTrigger` discret (icône mini, sans FAB) à placer sur :
  - Header global (desktop uniquement)
  - Fin d'exercice (après validation)
  - Fin de défi
  - Page dashboard
- FAB existant conservé en bas-droite sur les pages sans trigger discret

#### Chantier B — Sécurité / Auth

**B1 — Dependabot #41**
- Identifier le package vulnérable : `gh api repos/zyclope0/mathakine/dependabot/alerts/41`
- Appliquer la mise à jour, vérifier CI

**B2 — OWASP quick-pass**
- Headers : `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` dans proxy.ts (CSP déjà fait)
- Cookies : vérifier `SameSite=Strict` sur les cookies auth
- Rate-limiting : vérifier que les endpoints sensibles (/login, /register, /api/feedback) ont leur bucket

**B3 — Évaluation OAuth Google**
- Livrable : doc `docs/02-FEATURES/OAUTH_GOOGLE_ARCHITECTURE.md`
- Contenu : option A (next-auth + backend token exchange) vs option B (backend-only Google OAuth), complexité, risques, effort
- Décision : P0 beta / post-beta P1

#### Chantier C — Documentation utilisateur

**C1 — Onboarding in-app**
- Tooltip/guide first-use sur dashboard (enfant) et tableau de bord parent
- Peut être une séquence de 3 tooltips côté frontend, aucun backend requis

**C2 — Page d'aide contextuelle**
- `/help` ou section FAQ accessible depuis le menu
- Contenu minimal : "Comment ça marche", "Mes points", "Les défis", "Contacter le support"

**C3 — README utilisateur beta**
- `docs/BETA_GUIDE.md` : instructions pour invités, comment signaler un bug (bouton feedback), périmètre beta

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
