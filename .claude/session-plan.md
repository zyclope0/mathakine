# Plan de session — Mathakine

## Fermeture du sidecar FFI-L19\* (validate-token / rate-limit / proxy trust)

| Lot          | Statut | Résumé                                                                                                                      |
| ------------ | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| **FFI-L19A** | Fermé  | Bucket backend dédié `validate-token` (90/min/IP) ; login/forgot-password stricts (5/min).                                  |
| **FFI-L19B** | Fermé  | Next server : `validateTokenRuntime.ts` — coalescence + micro-cache succès 2,5 s.                                           |
| **FFI-L19C** | Fermé  | Politique IP explicite : `RATE_LIMIT_TRUST_X_FORWARDED_FOR` + `_get_client_ip` documenté (voir rapport §17, `README_TECH`). |

**La séquence FFI-L19\* est terminée.** Ne pas rouvrir ce fil sans nouveau constat produit ou ticket dédié.

### Hors scope documenté (non traité en L19C)

- Headers CDN type `CF-Connecting-IP` sans setting et preuve infra dédiés.
- Liste `TRUSTED_PROXY_IPS` / CIDR pour n’utiliser XFF que si le hop TCP est un proxy connu.
- Re-key rate-limit par utilisateur (backlog produit distinct).

---

## Recentrage actif : roadmap frontend principale

Après clôture FFI-L19\*, la **priorité d’exécution** revient à la feuille de route **frontend** (standardisation, industrialisation UI, dette UX technique), notamment :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md` et trackers projet associés
- audits de contexte : `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`, `AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` (lecture / priorisation, pas de nouvelle digression backend rate-limit)

Les changements backend hors périmètre roadmap frontend doivent rester **petits, nommés et reviewables** (pas de mélange avec une « suite » FFI-L19 ad hoc).

### Hiérarchie de vérité documentaire

1. `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` pour la priorité produit active
2. `D:\Mathakine\.claude\session-plan.md` pour l’ordre d’exécution courant
3. `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` pour la dette et les patterns frontend encore utiles
4. `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme photographie historique, non comme backlog actif

### État réel frontend après FFI-L18B

- la séquence de standardisation structurelle `FFI-L1` à `FFI-L18B` est considérée **fermée**
- les garde-fous d’architecture restent la protection active contre la rechute en monolithes
- il n’existe plus de dense exception ouverte dans `ALLOWED_DENSE_EXCEPTIONS`
- la suite frontend ne relève plus d’un gros chantier de découpage générique, mais d’un **durcissement ciblé** :
  - vues encore denses hors exception formelle (`BadgeCard`, `BadgesProgressTabsSection`, `SettingsSecuritySection`)
  - homogénéisation design-system/premium encore partielle
  - QA visuelle et a11y humaine sur les surfaces partagées

### Audit frontend d’industrialisation — 2026-04-08

Constat de pilotage :

- la modularité globale du frontend est maintenant **bonne mais non terminale** ; score de maturité retenu : **7.5/10**
- les lots `FFI-L11` à `FFI-L18B` ont bien fermé les mega-pages et hotspots explicitement ciblés
- les risques restants se concentrent dans quelques noyaux transverses :
  - ~~`app/dashboard/page.tsx`~~ (FFI-L20A)
  - ~~`components/exercises/ExerciseSolver.tsx`~~ (FFI-L20B : façade + controller)
  - ~~`hooks/useAuth.ts`~~ (FFI-L20C : facade + lib/auth seams)
  - ~~`components/providers/Providers.tsx`~~ (FFI-L20C : composition + sous-blocs sync)
  - domaine badges (`BadgeCard`, `BadgeGrid`, `BadgesProgressTabsSection`)

Prochaines itérations architecturales recommandées :

1. ~~`FFI-L20A`~~ — dashboard : **fermé**
2. ~~`FFI-L20B`~~ — solver exercices : **fermé**
3. ~~`FFI-L20C`~~ — noyau auth/provider : **fermé** (`lib/auth/types`, `authLoginFlow`, `postLoginRedirect` ; `ThemeBootstrap` / `AccessibilityDomSync` / `AccessibilityHotkeys`)

### Avancement FFI-L20 — 2026-04-08

| Lot          | Statut     | Résumé                                                                                                                                                                                                                                                                                                       |
| ------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **FFI-L20A** | Fermé      | `app/dashboard/page.tsx` est ramené à une coque ~`174` LOC ; runtime déplacé dans `hooks/useDashboardPageController.ts` (~`137` LOC) ; tabs sorties vers `components/dashboard/Dashboard*Section.tsx` et `DashboardTabsNav.tsx` ; tests page + hook ; surface désormais gardée dans `frontendGuardrails.ts`. |
| **FFI-L20B** | Fermé      | `ExerciseSolver.tsx` façade ~`366` LOC ; runtime dans `hooks/useExerciseSolverController.ts` ; helpers purs `lib/exercises/exerciseSolverFlow.ts` ; tests unitaires solver + hook + flow ; surface protégée dans `frontendGuardrails.ts`.                                                                 |
| **FFI-L20C** | Fermé      | `useAuth` allégé (~`204` LOC) + contrats `lib/auth/types.ts`, helpers `authLoginFlow.ts`, override `postLoginRedirect.ts` ; `Providers` composition (~`41` LOC) + `ThemeBootstrap` / `AccessibilityDomSync` / `AccessibilityHotkeys` ; tests useAuth + Providers + authLoginFlow ; guardrails mis à jour. |
