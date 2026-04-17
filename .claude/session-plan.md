# Session Plan - Beta Fermee Mathakine

**Cree :** 2026-04-16  
**Mis a jour :** 2026-04-17  
**Intent Contract :** `.claude/session-intent.md`  
**Version cible :** `v3.6.0-beta.2`

---

## Ou on en est

Le scope beta est maintenant largement en place :

- feedback-debug complet, de la collecte frontend jusqu'au triage admin
- securite/auth durcies pour un premier cercle de testeurs reels
- documentation beta in-app + guide adulte en place
- version visible alignee sur `3.6.0-beta.2`

En pratique, le produit est **proche d'une beta fermee publiable**, mais il reste encore un petit bloc "release readiness" a fermer avant de dire "beta du site prete".

---

## Ce qui est termine

### PHASE 1 - DEFINE (terminee)

| Tache | Statut |
|-------|--------|
| D1 - Audit payload feedback | DONE |
| D2 - Audit affichage admin feedback | DONE |
| D3 - Emplacements feedback discret | DONE |
| D4 - Point architecture OAuth Google | POST-BETA |
| D5 - Inventaire OWASP quick-pass | DONE |

---

### PHASE 2 - DEVELOP

#### Chantier A - Feedback / triage admin (termine)

| Tache | Statut | Commits de reference |
|-------|--------|----------------------|
| A1 - Backend feedback context + migration | DONE | `bd130e3`, `9892fe9`, `af93508`, `daa6fb5` |
| A2 - `FeedbackFab` envoie le contexte frontend | DONE | `bdba53c` |
| A3 - Vue admin enrichie + detail + statut + suppression | DONE | `132368f`, `c27580c`, `a586f4c`, `bc475a4`, `8a4428d`, `a7ea81f` |
| A4 - Triggers feedback discrets (header + fin exercice + fin defi) | DONE | `ae08c8f`, `4281115` |

**Resultat obtenu :**
- feedback capture `user_role`, `active_theme`, `ni_state`, `component_id`
- admin voit le contexte, ouvre le detail, change le statut et supprime si necessaire
- feedback declenchable depuis le FAB global + les points d'entree contextuels

#### Chantier B - Securite / auth (quasi boucle pour la beta)

| Tache | Statut | Commits de reference |
|-------|--------|----------------------|
| B1 - Dependabot #41 / DOMPurify | DONE | `ebfa039` |
| B2 - OWASP quick-pass beta (headers, rate-limit feedback, privacy) | DONE | `4c822fe`, `ef1ea49`, `68c052e` |
| B3 - Evaluation OAuth Google | POST-BETA | - |

**Resultat obtenu :**
- hardening minimum beta present
- feedback rate-limite
- privacy / RGPD mieux cadre
- OAuth Google explicitement sorti du scope beta

#### Chantier C - Documentation beta (termine pour la beta)

| Tache | Statut | Commits de reference |
|-------|--------|----------------------|
| C1 - Micro-guidage contextuel (`DocTip`) | DONE | `4cf56c5` |
| C2 - Doc utilisateur in-app orientee beta (`/docs`) | DONE | `1b13242`, `e9a10b1`, `a45c8d0` |
| C3 - `docs/BETA_GUIDE.md` + convergence parent/enseignant | DONE | `4cf56c5`, `1b13242`, `e9a10b1` |

**Note importante :**
- le besoin "page help contextuelle" a ete absorbe proprement par une page `/docs` refondue, plus utile qu'une nouvelle route `/help`
- le dashboard expose maintenant une entree discrete vers la doc beta

---

## Ce qui manque encore pour dire "beta du site prete"

### PHASE 3 - DELIVER (reste a fermer)

| Tache | Statut reel | Priorite |
|-------|-------------|----------|
| Smoke test enfant complet (`register -> exercice -> defi -> feedback`) | TODO manuel | Haute |
| Smoke test admin (`login admin -> lecture feedback -> statut -> suppression`) | TODO manuel | Haute |
| Validation CI complete (`tsc`, `prettier`, `vitest`, `pytest`, checks GitHub`) | PARTIEL | Haute |
| Tag Git `v3.6.0-beta.2` | TODO | Haute |
| Preparation/envoi aux 3-5 beta-testeurs | TODO | Moyenne |

### Detail des manques reels

1. **Parcours manuel beta**
- verifier qu'un nouvel utilisateur peut vraiment :
  - creer son compte
  - acceder aux exercices
  - finir un defi
  - envoyer un feedback
- verifier qu'un admin peut :
  - voir ce feedback
  - changer son statut
  - le supprimer

2. **Validation technique complete**
- les checks cibles frontend sont bons
- les checks cibles docs sont bons
- il reste a revalider le bloc backend/global dans un environnement propre, surtout autour de `pytest`

3. **Release operation**
- le changelog beta existe
- la version visible est alignee sur `3.6.0-beta.2`
- **mais le tag Git `v3.6.0-beta.2` n'existe pas encore**

4. **Go-to-beta**
- il faut preparer le micro-cercle de testeurs
- il faut clarifier le message d'invitation et ce qu'on attend d'eux

---

## Ce qui n'est pas bloquant pour la beta

| Sujet | Statut |
|-------|--------|
| OAuth Google | reporte post-beta |
| Dashboard parent/enseignant complet | pas disponible, deja documente comme limite beta |
| Google sign-in | pas bloquant |
| Export PDF de progression | pas bloquant |

---

## Analyse D4 — Social Login (OAuth2/OIDC) [POST-BETA]

**Évaluée le 2026-04-17. Ne pas implémenter avant la beta.**

### Mécanisme

Flux standard OAuth2 + OIDC identique pour tous les fournisseurs :
`clic "Connexion Google" → redirect Google → callback /api/auth/callback/google?code=X → échange code → JWT → même flux qu'un login classique`

### Options évaluées

| Option | Approche | Effort | Compatibilité Mathakine |
|--------|----------|--------|------------------------|
| **A — Auth.js v5 (NextAuth)** | Gestion session côté Next.js | 2-3 j | Couplage non trivial avec JWT Starlette — pont custom nécessaire |
| **B — authlib côté Starlette** | 2 routes backend, JWT inchangé | 1-2 j | Architecture conservée intégralement — **recommandée** |
| **C — Clerk / Auth0 / Supabase Auth** | Service tiers | 3-5 j refacto | Incompatible sans réécriture de la couche auth |

### Recommandation : Option B — authlib + Google uniquement

```python
pip install authlib httpx
# 2 nouvelles routes :
# GET /api/auth/google/authorize
# GET /api/auth/google/callback
# Migration Alembic : colonne google_sub VARCHAR UNIQUE NULLABLE sur users
```

- Conserve JWT HTTP-only, rate-limiting, cookies existants
- Extensible à Apple/Microsoft avec le même pattern

### Fournisseurs à prioriser (post-beta v1)

| Fournisseur | Priorité | Raison |
|-------------|----------|--------|
| **Google** | P1 | Universel familles + enseignants |
| **Apple** | P2 | iOS, bonne image privacy |
| Microsoft | P3 | Enseignants Teams/EDU |
| Facebook | Éviter | Complexité RGPD élevée, audience limitée pour EdTech enfants |

### Contraintes spécifiques Mathakine

- **Mineurs RGPD Art.8** : Google bloque lui-même les <13 ans (Family Link). Consentement parental toujours requis pour 13-15 ans — le vecteur auth ne change pas l'obligation.
- **Fusion compte** : stratégie de merge nécessaire (email = clé de raccordement + confirmation).
- **Migration Alembic** : `google_sub VARCHAR UNIQUE NULLABLE` sur `users`, mot de passe nullable pour comptes social-only.

---

## Verdict actuel

### Beta produit
**Le socle produit beta est pret**

### Beta release
**La release beta n'est pas completement fermee**

Il reste principalement :
- les smoke tests manuels
- une validation complete des checks
- le tag Git beta
- la preparation du premier envoi beta

---

## Prochaines actions recommandees

1. lancer un smoke test enfant complet
2. lancer un smoke test admin complet
3. verifier l'etat reel des checks GitHub / CI
4. creer le tag `v3.6.0-beta.2`
5. preparer le message d'invitation beta et la shortlist testeurs

---

## Checkpoint decision

**Question utile maintenant :**

> Si les smoke tests manuels passent et que la CI est verte, est-ce qu'on tague immediatement `v3.6.0-beta.2` ?

Ma recommandation : **oui**.  
Le scope beta est suffisamment ferme. Le reste est du release management, pas du chantier produit.
