# Plan de session - Mathakine

## Fermeture du sidecar FFI-L19* (validate-token / rate-limit / proxy trust)

| Lot | Statut | Résumé |
| --- | --- | --- |
| **FFI-L19A** | Fermé | Bucket backend dédié `validate-token` (90/min/IP) ; login/forgot-password stricts (5/min). |
| **FFI-L19B** | Fermé | Next server : `validateTokenRuntime.ts` - coalescence + micro-cache succès 2,5 s. |
| **FFI-L19C** | Fermé | Politique IP explicite : `RATE_LIMIT_TRUST_X_FORWARDED_FOR` + `_get_client_ip` documenté (voir rapport §17, `README_TECH`). |

**La séquence FFI-L19* est terminée.** Ne pas rouvrir ce fil sans nouveau constat produit ou ticket dédié.

### Hors scope documenté (non traité en L19C)

- Headers CDN type `CF-Connecting-IP` sans setting et preuve infra dédiés.
- Liste `TRUSTED_PROXY_IPS` / CIDR pour n'utiliser XFF que si le hop TCP est un proxy connu.
- Re-key rate-limit par utilisateur (backlog produit distinct).

---

## Recentrage actif : roadmap frontend principale

Après clôture FFI-L19*, la **priorité d'exécution** revient à la feuille de route **frontend** (standardisation, industrialisation UI, dette UX technique), notamment :

- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md`
- `docs/03-PROJECT/README.md` et trackers projet associés
- audits de contexte : `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md`, `AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` (lecture / priorisation, pas de nouvelle digression backend rate-limit)

Les changements backend hors périmètre roadmap frontend doivent rester **petits, nommés et reviewables**.

### Hiérarchie de vérité documentaire

1. `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` pour la priorité produit active
2. `D:\Mathakine\.claude\session-plan.md` pour l'ordre d'exécution courant
3. `docs/03-PROJECT/AUDIT_FRONTEND_STANDARDISATION_2026-03-29.md` pour la dette et les patterns frontend encore utiles
4. `docs/03-PROJECT/AUDIT_FRONTEND_INDUSTRIALISATION_2026-03.md` comme photographie historique, non comme backlog actif

### État réel frontend après FFI-L18B

- la séquence de standardisation structurelle `FFI-L1` à `FFI-L18B` est considérée **fermée**
- les garde-fous d'architecture restent la protection active contre la rechute en monolithes
- il n'existe plus de dense exception ouverte dans `ALLOWED_DENSE_EXCEPTIONS`
- la suite frontend ne relève plus d'un gros chantier de découpage générique, mais d'un **durcissement ciblé**

### Audit frontend d'industrialisation - 2026-04-08

Constat de pilotage :

- la modularité globale du frontend est maintenant **bonne mais non terminale** ; score de maturité retenu : **7.5/10**
- les lots `FFI-L11` à `FFI-L18B` ont bien fermé les mega-pages et hotspots explicitement ciblés
- les anciens risques structurels les plus lourds ont été fermés par `FFI-L20A` à `FFI-L20H`

### Avancement FFI-L20 - 2026-04-08

| Lot | Statut | Résumé |
| --- | --- | --- |
| **FFI-L20A** | Fermé | `app/dashboard/page.tsx` ramené à une coque ; runtime déplacé dans `hooks/useDashboardPageController.ts` ; tabs sorties vers `components/dashboard/*`. |
| **FFI-L20B** | Fermé | `ExerciseSolver.tsx` façade ; runtime dans `hooks/useExerciseSolverController.ts` ; helpers purs `lib/exercises/exerciseSolverFlow.ts`. |
| **FFI-L20C** | Fermé | `useAuth` allégé ; contrats `lib/auth/types.ts`, helpers `authLoginFlow.ts`, `postLoginRedirect.ts` ; `Providers` segmenté en sous-blocs sync. |
| **FFI-L20D** | Fermé | Contrats badges `lib/badges/types.ts` ; dérivations pures `lib/badges/badgePresentation.ts` ; `BadgeCard` / `BadgeGrid` / `BadgesProgressTabsSection` alignés. |
| **FFI-L20E** | Fermé | `SettingsSecuritySection` allégée ; `SettingsSessionsList` / `SettingsSessionRow` ; helpers purs `lib/settings/settingsSecurity.ts`. |
| **FFI-L20F** | Fermé | `AdminReadHeavyPageShell` + `AdminStatePanel` ; factorisation des états read-heavy sur `admin` / `analytics` / `ai-monitoring`. |
| **FFI-L20G** | Fermé | `app/about/page.tsx` + `app/privacy/page.tsx` en Server Components avec `getTranslations` ; suppression du `use client` inutile. |
| **FFI-L20H** | Fermé | Polish a11y / états : `role="alert"` / `status`, `LoadingState`, `SaveButton`, confidentialité / sessions, `BadgeCard`, toolbar listes. |

---

## Après FFI-L20* : file active frontend / plateforme

La séquence d'industrialisation structurelle **FFI-L20A -> FFI-L20H** est **terminée**.
La suite frontend relève maintenant de lots **ciblés**, petits et reviewables, pilotés par risque/coût/solidité plutôt que par un nouveau chantier générique de découpage.

### Constat terrain synthétique - 2026-04-08

- forces confirmées :
  - TypeScript strict fort (`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`)
  - guardrails d'architecture actifs et testés
  - Sentry production-grade (tunnel, replay masqué, release)
  - accessibilité structurelle renforcée par `FFI-L20H`
- point à nuancer :
  - le constat historique sur les **7 thèmes CSS** n'a pas été revalidé exhaustivement dans cette passe ; rien de contradictoire trouvé, mais ce n'est pas un axe de pilotage prioritaire sans audit dédié
- point explicitement **non corrigé à date** :
  - `frontend/components/providers/Providers.tsx` garde un `QueryClient` **singleton module-scope**
  - preuve : lignes `13-21`
  - ce point n'a **pas** été fermé par `FFI-L20C`

### File active recommandée

#### P1 immédiats

1. **CHAT-AUTH-01** - auth sur `/api/chat` et `/api/chat/stream` (frontend + backend)
   - fermer l'exposition coût OpenAI publique
   - aligner proxy/frontend et whitelist backend
2. **RQ-PROVIDERS-02** - instancier `QueryClient` via `useState`/factory locale dans `Providers.tsx`
   - durcir le cycle de vie React Query sans changement produit
3. **CHAT-I18N-03** - extraire les hardcoded FR restants
   - `app/global-error.tsx`
   - `app/not-found.tsx` (CTA restant)
   - `app/api/chat/route.ts`
   - `app/api/chat/stream/route.ts`
4. **CHAT-LOG-04** - conditionner / supprimer les `console.error` en production dans `app/api/chat/stream/route.ts`

#### P1 qualité

5. **LINT-STRICT-05** - passer progressivement les règles ESLint encore en `warn` vers `error`
   - priorité :
     - `@typescript-eslint/no-explicit-any`
     - `react-hooks/exhaustive-deps`
6. **E2E-CORE-06** - étendre les specs Playwright critiques
   - base actuelle : `2` specs pour `35` pages App Router hors API
   - cibles prioritaires :
     - login/auth
     - dashboard
     - badges
     - settings
     - admin read-heavy
7. **SSE-DRY-07** - factoriser les deux proxies SSE quasi identiques
   - `app/api/exercises/generate-ai-stream/route.ts`
   - `app/api/challenges/generate-ai-stream/route.ts`

#### P2 durcissement

8. **CSP-HARDEN-08** - réduire `unsafe-inline` / `unsafe-eval` dans `frontend/next.config.ts`
9. **OG-META-09** - remplacer l'image Open Graph `512x512` par un vrai format social `1200x630`

### Ordre d'exécution recommandé

1. `CHAT-AUTH-01`
2. `RQ-PROVIDERS-02`
3. `CHAT-I18N-03`
4. `CHAT-LOG-04`
5. `LINT-STRICT-05`
6. `E2E-CORE-06`
7. `SSE-DRY-07`
8. `CSP-HARDEN-08`
9. `OG-META-09`

### Règle de pilotage

- ne **pas** rouvrir une nouvelle série `FFI-L20*`
- traiter la suite comme :
  - correctifs ciblés
  - dette qualitative mesurable
  - lots compacts et reviewables
- tout nouveau lot structurel frontend devra partir d'un **nouveau constat terrain**, pas d'une inertie documentaire
