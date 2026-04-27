# Design — Rationalisation du contexte mémoire IA

**Date :** 2026-04-26
**Scope :** Consolider la mémoire de travail .md utilisée par Codex, Claude Code CLI + superpowers, et Octopus en un contrat clair de 3 niveaux, avec un point d'entrée unifié pour toute nouvelle session.
**Contrainte :** Solo founder, zéro changement de code applicatif, zéro migration DB, préserver l'historique git (archiver, ne pas supprimer).

---

## Contexte

Mathakine a 29 commits non-poussés sur `master` (état `3.6.0-beta.4`). L'historique récent mêle code (test/fix/feat), specs superpowers (`docs/superpowers/specs/`), plans superpowers (`docs/superpowers/plans/`), et notes de pilotage Claude (`.claude/`).

L'utilisation parallèle de **trois outils IA** (Codex, Claude Code CLI + superpowers, Octopus) a produit des fichiers de mémoire de travail dans plusieurs zones, sans contrat explicite sur :

- où est l'**état courant** (chantier actif, version, dernier commit significatif),
- quels fichiers une nouvelle session doit lire en priorité,
- quand un fichier de mémoire devient stale et doit être archivé.

Conséquence observée : `.claude/session-plan.md` mentionne `v3.6.0-beta.2` alors que `CLAUDE.md` est aligné sur `3.6.0-beta.4`. C'est le seul fichier `.claude/` tracké git, donc cette stale-ness est partagée.

**Ce qui n'est PAS dans le scope :**

- Refonte de la doc projet (`docs/03-PROJECT/`, 232 fichiers) — sujet séparé.
- Modification du code applicatif.
- Suppression de fichiers (on archive).
- Changement de provider IA, de modèle ou de policy.
- Changement de workflow superpowers (brainstorming → writing-plans → executing-plans reste tel quel).

---

## Audit — état des lieux

### Inventaire mémoire IA active

| Fichier | Lignes | Tracké git | Outil | État |
|---|---|---|---|---|
| `CLAUDE.md` | 120 | oui | Claude Code (canonique projet) | À jour |
| `.claude/session-plan.md` | 214 | **oui** (exception .gitignore) | Claude (note pilotage) | **STALE** — version `beta-2` |
| `.claude/session-intent.md` | 40 | non | Claude (intent contract) | Stale — checklist beta-2 |
| `.claude/audit-runtime-findings.md` | 55 | non | Octopus security-auditor | Audit fermé (cosmétiques traités) |
| `.claude/audit-security-findings.md` | 105 | non | Octopus security-auditor | Audit fermé (B1-B3 corrigés en `83e7763`) |
| `.claude/session-plan-leaderboard-f42-archive.md` | 682 | non | Claude/Octopus (archive 2026-03) | Archive non-déplacée |
| `.claude/claude-octopus.local.md` | 3 | non | Octopus config | Quasi-vide (`knowledge_mode: false`) |
| `docs/superpowers/specs/2026-04-25-beta-stabilisation-design.md` | ~123 | oui | superpowers brainstorming | À jour, commit `9fa9315` |
| `docs/superpowers/specs/2026-04-25-phase3-tests-design.md` | ~219 | oui | superpowers brainstorming | À jour, commit `6282668` (corrigé `5940a8a`) |
| `docs/superpowers/plans/2026-04-25-beta-stabilisation.md` | ~? | oui | superpowers writing-plans | À jour, commit `d818115` |
| `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` | 214 | oui | superpowers writing-plans | À jour, commit `171531b` |
| `docs/superpowers/plans/2026-04-25-phase3-tests.md` | ~? | oui | superpowers writing-plans | À jour, commit `0f95417` |
| `.cursor/plans/b1_transactions_backend_4b238fed.plan.md` | ? | oui | Cursor agent (legacy) | À évaluer |

### Configuration `.gitignore` (lignes 153-155)

```
.claude/*
!.claude/session-plan.md
.claude-octopus/
```

→ Conséquence : seul `session-plan.md` est partagé via git. Les audits, l'intent, l'archive leaderboard, la config octopus sont **strictement locaux à un poste**. Une autre machine ou un fork ne les voit jamais.

### Volume

`.claude/` total : 9.8 MB (la grosse partie est probablement le cache claude-mem en JSON/JSONL, pas les .md).

### Tensions identifiées

#### T1 — Trou de routing inter-outils

Aucun fichier n'établit "voici où on en est aujourd'hui, voici le chantier actif, voici les specs en cours d'exécution". `CLAUDE.md` est canonique projet (stack, architecture, version), pas un état d'avancement opérationnel. `.claude/session-plan.md` était censé jouer ce rôle mais est stale.

Codex (qui suit la convention `AGENTS.md`) et Octopus (qui lit `claude-octopus.local.md`) n'ont aucune entrée projet-niveau. Ils repartent de `CLAUDE.md` et n'apprennent rien de l'état du moment.

#### T2 — Audits-sources qui survivent à leur exécution

Les `.claude/audit-*-findings.md` ont été produits le 2026-04-25 par Octopus security-auditor. Ils ont alimenté `docs/superpowers/specs/2026-04-25-beta-stabilisation-design.md` Section 1, puis le plan `2026-04-25-cosmetic-findings.md`. Tous les bloquants B1-B3 sont corrigés (commit `83e7763`), les cosmétiques actionnables Run-C1 + Sec-C2 + Sec-C3 sont traités (commits `ec87c35` + `48fb8bf` + `15ed459`).

Aujourd'hui ces fichiers d'audit ne sont plus des sources actives — ils sont des inputs historiques d'un cycle terminé. Ils ne sont pas faux, ils sont périmés en tant que TODO list.

#### T3 — Stale-ness partagée via git

`.claude/session-plan.md` est trackée. Tant qu'elle parle de `beta-2`, chaque clone, chaque CI, chaque agent voit cette information périmée. La règle `!.claude/session-plan.md` dans `.gitignore` a été pensée pour partager du contexte — elle se retourne quand le contexte n'est pas tenu à jour.

#### T4 — Archive non isolée

`.claude/session-plan-leaderboard-f42-archive.md` (682 lignes) est explicitement marquée archive dans son nom, mais reste à la racine de `.claude/`. Toute recherche `grep` ou semantic search dans `.claude/` retombe dessus. Symptôme du fait qu'il n'y a pas de `.claude/archive/`.

#### T5 — Niveaux de mémoire non contractualisés

Trois niveaux existent de fait :

| Niveau | Lieu | Cycle de vie | Visibilité |
|---|---|---|---|
| Canonique projet | `CLAUDE.md`, `docs/03-PROJECT/` | Long terme, modifié sur changement architecture | Tous |
| Working-memory commitée | `docs/superpowers/specs/` + `plans/` | Cycle Define → Develop → Deliver d'un chantier | Tous (git) |
| Working-memory locale | `.claude/`, `.cursor/plans/` | Session ou semaine | Auteur uniquement (sauf exceptions) |

Aucun fichier ne nomme ces niveaux ni ne dit qui appartient à quoi. Conséquence : un finding peut atterrir au mauvais niveau (ex. `audit-*` aurait pu vivre dans `docs/superpowers/audits/` pour être partagé).

---

## Approche retenue — B : `AGENTS.md` unifié + cleanup contractualisé

### Vue d'ensemble

1. Créer un `AGENTS.md` à la racine = **point d'entrée unifié** pour toute session IA (Codex le lit par convention, Claude Code peut être instruit via `CLAUDE.md`, Octopus via une note de routing).
2. Tenir `AGENTS.md` court et opérationnel : version courante, chantier actif, pointeurs vers specs/plans en cours, rappel du contrat de mémoire 3-niveaux.
3. Rafraîchir `CLAUDE.md` pour ajouter une section "Tools onboarding" qui pointe vers `AGENTS.md` et explique la séparation canonique / committed-working / local-ephemeral.
4. Archiver le stale dans `.claude/archive/` (déplacement, pas suppression).
5. Mettre `.claude/session-plan.md` au présent (`beta-4` + Phase 3 livrée + chantier actif courant).
6. Évaluer `.cursor/plans/b1_transactions_backend_4b238fed.plan.md` : à archiver dans `.cursor/plans/archive/` ou à supprimer du tracking si jamais utilisé.
7. Documenter le cycle de vie dans `AGENTS.md` (quand archiver, où archiver, comment renommer).

### Pourquoi B et pas A (cleanup seul)

A résout le bruit immédiat mais pas le trou de routing (T1) ni le problème de niveau non contractualisé (T5). Dans 1 mois, le même problème revient.

### Pourquoi B et pas C (refonte)

C migre les audits dans `docs/superpowers/audits/`, génère un `STATUS.md` auto, indexe tout. Effort > bénéfice pour solo founder, et superpowers ne fournit pas de skill `audits/` aujourd'hui — créer la convention nécessiterait de la maintenir.

---

## Spécification détaillée

### Section 1 — `AGENTS.md` racine

Fichier de **80-120 lignes maximum**. Tenu à jour par l'humain à chaque clôture de chantier, pas par l'IA en cours de session.

#### Sections obligatoires

```markdown
# AGENTS.md — Mathakine

## État courant
- Version : 3.6.0-beta.4
- Branche : master
- Dernière phase livrée : Phase 3 tests (3A golden, 3B renderer, 3D solveur perf)
- Chantier actif : <à remplir, ex. "aucun, prêt pour next">
- Dernier audit clos : 2026-04-25 (sécurité B1-B3 + runtime cosmétiques)

## Documents canoniques (lire en premier)
- `CLAUDE.md` — stack, architecture, conventions
- `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_SOLIDIFICATION_2026-04-22.md` — backlog défis IA
- `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` — roadmap produit

## Specs/plans en cours d'exécution
<liste vide ou pointeurs vers docs/superpowers/specs|plans/YYYY-MM-DD-*.md>

## Specs/plans clos non archivés
<même chose, marqués DONE>

## Contrat mémoire IA (3 niveaux)
1. Canonique projet : CLAUDE.md, docs/03-PROJECT/. Long terme.
2. Working-memory commitée : docs/superpowers/specs/ + plans/. Un chantier = un cycle.
3. Working-memory locale : .claude/, .cursor/plans/. Session ou semaine. Non poussée sauf .claude/session-plan.md.

## Règles d'archive
- Audit clos → déplacer dans .claude/archive/audits/
- Plan exécuté et mergé → laisser dans docs/superpowers/plans/ avec ligne "Status: DONE" en tête
- Session-plan obsolète → renommer en .claude/archive/session-plan-<topic>-<date>.md
- Ne jamais supprimer, toujours déplacer

## Onboarding par outil
- Codex : lit AGENTS.md + CLAUDE.md
- Claude Code CLI : lit CLAUDE.md (qui pointe vers AGENTS.md)
- Octopus : lit AGENTS.md, claude-octopus.local.md pour la config locale
- Cursor (cet IDE) : lit AGENTS.md, CLAUDE.md, .cursor/rules/*.mdc
```

#### Critères de qualité

- Aucune information dupliquée avec `CLAUDE.md` autre que la version (qui sert de check de fraîcheur).
- Aucun lien cassé vers un fichier inexistant.
- Liste "specs/plans en cours" rigoureusement à jour (la mettre vide si rien d'actif est mieux que la laisser stale).

### Section 2 — Patch `CLAUDE.md`

Ajouter une nouvelle section juste après "État de santé" (avant les conventions) :

```markdown
## Tools onboarding

Tout agent IA démarrant une session sur ce repo doit lire `AGENTS.md` à la racine en priorité — il contient l'état opérationnel courant (version, chantier actif, specs/plans en cours).

Mémoire IA en 3 niveaux :
- **Canonique** : ce fichier, `docs/03-PROJECT/`. Architecture stable.
- **Working-memory commitée** : `docs/superpowers/specs/`, `docs/superpowers/plans/`. Cycle d'un chantier.
- **Working-memory locale** : `.claude/`, `.cursor/plans/`. Éphémère, non partagée sauf `.claude/session-plan.md`.

Voir `AGENTS.md` pour le contrat complet et les règles d'archive.
```

Ne pas modifier le reste de `CLAUDE.md`.

### Section 3 — Cleanup `.claude/`

#### Création du dossier archive

```
.claude/
  archive/
    audits/          # audits clos
    session-plans/   # session-plans périmés
```

#### Déplacements proposés

| Fichier source | Destination | Raison |
|---|---|---|
| `.claude/audit-runtime-findings.md` | `.claude/archive/audits/2026-04-25-runtime-findings.md` | Audit clos, cosmétiques traités en `48fb8bf`/`ec87c35` |
| `.claude/audit-security-findings.md` | `.claude/archive/audits/2026-04-25-security-findings.md` | Bloquants B1-B3 corrigés en `83e7763` |
| `.claude/session-plan-leaderboard-f42-archive.md` | `.claude/archive/session-plans/2026-03-25-leaderboard-f42.md` | Déjà nommé archive, jamais déplacé |
| `.claude/session-intent.md` | `.claude/archive/session-plans/2026-04-16-beta-fermee-intent.md` | Intent contract beta-2, livré |

Tous ces fichiers sont gitignorés sauf `session-plan.md`. Le déplacement est purement local côté disque, n'apparaît pas dans `git status`.

#### Mise à jour `session-plan.md` (le seul tracké)

Le fichier actuel parle de `beta-2` et de chantiers livrés. Le réécrire pour refléter l'état au 2026-04-26 :

- Version courante : `3.6.0-beta.4`
- Chantiers livrés depuis beta-2 : feedback-debug, sécurité OWASP quick-pass, doc beta in-app, audit sécurité (B1-B3), audit runtime (cosmétiques), Phase 1A/1B observabilité, Phase 2A/2B métriques, Phase 3A/3B/3D tests
- Chantier actif : à définir avec l'humain au moment du commit
- Pointer explicitement vers `AGENTS.md` pour l'état opérationnel

Le fichier doit faire **maximum 100 lignes** (vs. 214 actuellement) et garder le rôle de "note locale founder de pilotage", pas devenir un mini-AGENTS.md bis.

#### Section 3.bis — Patch des références aux audits

Deux plans superpowers commités citent les chemins originaux des audits :

| Fichier | Ligne | Référence actuelle |
|---|---|---|
| `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` | 7 | `voir \`.claude/audit-security-findings.md\` et \`.claude/audit-runtime-findings.md\`` |
| `docs/superpowers/plans/2026-04-25-beta-stabilisation.md` | 76, 137 | `Créer un fichier temporaire \`.claude/audit-security-findings.md\`` (instruction d'origine) |

Décision :

- **`2026-04-25-cosmetic-findings.md`** (citation simple) → patcher les chemins vers `.claude/archive/audits/2026-04-25-{runtime,security}-findings.md`. Cohérence sémantique : le plan reste lisible.
- **`2026-04-25-beta-stabilisation.md`** (instruction historique de création) → ne **pas** modifier. C'est l'instruction d'origine qui a effectivement créé les fichiers à leur emplacement original. Le réécrire serait réécrire l'histoire. Ajouter à la place une note en tête du fichier : `> Note 2026-04-26 : les audits référencés ici ont été archivés vers .claude/archive/audits/. Voir AGENTS.md.`

Cette distinction préserve la fidélité historique des plans tout en restant navigable.

#### Décision sur `claude-octopus.local.md`

Le fichier ne contient que `knowledge_mode: false`. Deux options :

- **a)** Le laisser tel quel — c'est une config minimale Octopus, ne fait pas de mal.
- **b)** L'enrichir avec une note explicite sur l'usage Octopus dans ce repo (providers utilisés, skills couramment activés).

Choix par défaut : **a** (YAGNI). On l'enrichira si Octopus prend plus de place.

### Section 4 — Décision sur `.cursor/plans/`

`.cursor/plans/b1_transactions_backend_4b238fed.plan.md` est un plan généré par Cursor pour un chantier "transactions backend". À évaluer manuellement :

- Si livré → archiver en `.cursor/plans/archive/2026-XX-XX-b1-transactions-backend.md`.
- Si jamais lancé → idem archive avec mention "abandonné".
- Si actif → laisser en place et le référencer depuis `AGENTS.md`.

Cette évaluation est faite à l'exécution, pas dans cette spec.

### Section 5 — Ordre d'exécution

1. Créer `AGENTS.md` à la racine avec les sections définies en Section 1.
2. Patcher `CLAUDE.md` (ajout de la section "Tools onboarding" — Section 2).
3. Créer `.claude/archive/audits/` et `.claude/archive/session-plans/`.
4. Déplacer les 4 fichiers identifiés en Section 3 (commande mv locale, pas tracké git).
5. Patcher les références aux audits dans `2026-04-25-cosmetic-findings.md` (Section 3.bis), ajouter la note de tête dans `2026-04-25-beta-stabilisation.md`.
6. Réécrire `.claude/session-plan.md` — fichier tracké, donc apparaît dans `git status`.
7. Évaluer `.cursor/plans/` (Section 4) avec l'humain.
8. Vérifier que `git status` ne montre que les changements attendus :
   - `CLAUDE.md` modifié
   - `AGENTS.md` ajouté
   - `.claude/session-plan.md` modifié
   - `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` modifié (chemins audits)
   - `docs/superpowers/plans/2026-04-25-beta-stabilisation.md` modifié (note de tête)
   - Aucun changement sur `.claude/audit-*`, `.claude/session-intent.md`, `.claude/session-plan-leaderboard-f42-archive.md` (tous gitignorés)

### Section 6 — Validation post-exécution

- `cat AGENTS.md` lisible en moins de 30 secondes par un humain frais.
- Tous les liens `AGENTS.md` → autres fichiers résolvent (pas de 404).
- `.claude/session-plan.md` ne contient plus la chaîne `beta-2`.
- `git diff CLAUDE.md` ne touche que la nouvelle section "Tools onboarding".
- `ls .claude/archive/audits/` et `ls .claude/archive/session-plans/` retournent les 4 fichiers déplacés.

### Section 7 — Hors scope explicite

Pour éviter le scope creep :

- **Pas** de migration des 232 .md de `docs/03-PROJECT/`. Sujet séparé.
- **Pas** de génération automatique de `STATUS.md`. YAGNI solo founder.
- **Pas** de modification de `.gitignore`. Le contrat actuel (`!.claude/session-plan.md`) est conservé.
- **Pas** de nouvelle convention superpowers (`audits/`). Les audits restent dans `.claude/`, archivés après exécution.
- **Pas** de commit fait par l'IA. L'humain valide le diff puis commit.

---

## Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| `AGENTS.md` non maintenu, redevient stale en 2 mois | Élevée | Moyen | Section "État courant" minimale (5 lignes), discipline à chaque clôture de chantier ; rappel dans `CLAUDE.md` |
| Un outil (Codex / Octopus) ne lit pas réellement `AGENTS.md` | Moyenne | Faible | Le pire cas est l'inverse du gain : on revient à l'état avant — pas de régression |
| Déplacement casse une référence dans une spec superpowers existante | **Confirmé** | Moyen | 2 plans référencent `.claude/audit-*-findings.md` : `2026-04-25-cosmetic-findings.md` et `2026-04-25-beta-stabilisation.md`. Voir Section 3.bis pour le patch. |
| Réécriture `session-plan.md` perd du contexte historique utile | Faible | Faible | Le contenu actuel est archivé via git history (commit précédent reste accessible) |

---

## Estimation

- Section 1 (`AGENTS.md`) : 15 min
- Section 2 (patch `CLAUDE.md`) : 5 min
- Section 3 (cleanup `.claude/`) : 10 min (dont réécriture `session-plan.md`)
- Section 4 (`.cursor/plans/`) : 5 min de discussion humain
- Validation Section 6 : 5 min

**Total : 30-45 min**, aucune ligne de code applicatif touchée.

---

## Décisions tranchées (2026-04-26)

1. **Chantier actif `AGENTS.md`** : aucun. Phase 3 (3A/3B/3D) vient de livrer en `3f104b2`. La section indique explicitement "aucun chantier actif, prêt pour next" — toute prochaine session doit définir le chantier avant de toucher du code.
2. **`.cursor/plans/b1_transactions_backend_4b238fed.plan.md`** : archive vers `.cursor/plans/archive/2026-XX-XX-b1-transactions-backend.md` (date à inférer du fichier ou laisser sans date).
3. **`.claude/claude-octopus.local.md`** : laissé tel quel. Pas d'enrichissement.
