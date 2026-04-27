# AGENTS.md — Mathakine

> **Point d'entrée unifié pour toute session IA** (Codex, Claude Code CLI + superpowers, Octopus, Cursor).
> Ce fichier reflète l'**état opérationnel courant**. Pour la stack/architecture stable, voir `CLAUDE.md`.

---

## État courant

| Champ | Valeur |
|---|---|
| Version | `3.6.0-beta.4` |
| Branche | `master` |
| Dernière phase livrée | Phase 3 tests défis IA (3A golden, 3B renderer contracts, 3D solveur perf) — commit `3f104b2` |
| Dernier audit clos | 2026-04-25 (sécurité B1-B3 corrigés en `83e7763`, runtime cosmétiques traités en `48fb8bf`/`ec87c35`/`15ed459`) |
| Chantier actif | **aucun** — prêt pour next chantier. Définir l'objectif avant toute édition de code. |
| Commits non poussés | ~29 sur `master` (vérifier avec `git log origin/master..master --oneline`) |

---

## Documents canoniques (lire en premier)

| Document | Rôle |
|---|---|
| `CLAUDE.md` | Stack, architecture, conventions projet (canonique) |
| `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_SOLIDIFICATION_2026-04-22.md` | Backlog défis IA — référence active |
| `docs/02-FEATURES/ROADMAP_FONCTIONNALITES.md` | Backlog produit — source de vérité |
| `README_TECH.md` | Référence technique vivante |
| `CHANGELOG.md` | Source de vérité release/version |

---

## Specs/plans superpowers actifs

| Statut | Spec / Plan |
|---|---|
| DONE (commit `5940a8a`) | `docs/superpowers/specs/2026-04-25-phase3-tests-design.md` + `docs/superpowers/plans/2026-04-25-phase3-tests.md` |
| DONE (commit `442f4f4`) | `docs/superpowers/specs/2026-04-25-beta-stabilisation-design.md` + `docs/superpowers/plans/2026-04-25-beta-stabilisation.md` |
| DONE (commit `48fb8bf`) | `docs/superpowers/plans/2026-04-25-cosmetic-findings.md` |
| ACTIVE | `docs/superpowers/specs/2026-04-26-ai-context-rationalization-design.md` (cette rationalisation mémoire IA) |

Aucun plan d'implémentation associé encore généré pour la spec ACTIVE — si on enchaîne, lancer le skill `writing-plans`.

---

## Plans Cursor

| Statut | Fichier |
|---|---|
| ARCHIVED 2026-04-26 | `.cursor/plans/archive/b1_transactions_backend_4b238fed.plan.md` (in_progress historique, à reprendre via une nouvelle spec si la dette transactionnelle redevient prioritaire) |

---

## Contrat mémoire IA (3 niveaux)

| Niveau | Lieu | Cycle de vie | Visibilité |
|---|---|---|---|
| **Canonique** | `CLAUDE.md`, `docs/03-PROJECT/`, `docs/02-FEATURES/`, `README_TECH.md`, `CHANGELOG.md` | Long terme, mis à jour sur changement architecture/produit | Tous (git) |
| **Working-memory commitée** | `docs/superpowers/specs/`, `docs/superpowers/plans/` | Cycle Define → Develop → Deliver d'un chantier (typiquement 1-3 semaines) | Tous (git) |
| **Working-memory locale** | `.claude/`, `.cursor/plans/` | Session ou semaine | Auteur uniquement (gitignored), sauf `.claude/session-plan.md` qui est tracké comme note de pilotage founder |

Règle d'or : un finding/audit/note de session **ne doit pas** rester dans la working-memory locale après clôture du chantier qui l'a produit. Cf. règles d'archive ci-dessous.

---

## Règles d'archive

| Type | Règle |
|---|---|
| Audit clos | Déplacer vers `.claude/archive/audits/YYYY-MM-DD-<topic>.md` |
| Session-plan obsolète | Déplacer vers `.claude/archive/session-plans/YYYY-MM-DD-<topic>.md` |
| Plan superpowers exécuté | Laisser dans `docs/superpowers/plans/` avec mention "DONE — commit `<hash>`" en tête |
| Plan Cursor abandonné/livré | Déplacer vers `.cursor/plans/archive/<original-filename>` |
| Note locale founder périmée | Renommer/déplacer dans `.claude/archive/session-plans/` |

**Toujours déplacer, jamais supprimer.** L'historique git couvre déjà la traçabilité, mais le déplacement permet aux outils de recherche IA de ne pas retomber sur des findings clos.

---

## Onboarding par outil

| Outil | Lecture obligatoire au démarrage de session |
|---|---|
| **Codex** | `AGENTS.md` (ce fichier) + `CLAUDE.md` |
| **Claude Code CLI** | `CLAUDE.md` (qui pointe vers `AGENTS.md`) |
| **superpowers** (skills brainstorming/writing-plans/executing-plans) | `AGENTS.md` + spec/plan en cours dans `docs/superpowers/` |
| **Octopus** | `AGENTS.md` + `.claude/claude-octopus.local.md` (config locale) |
| **Cursor** (Composer/Agent) | `AGENTS.md` + `CLAUDE.md` + `.cursor/rules/*.mdc` |

**Règle impérative inter-outils** : `git commit` avant de changer d'outil. Un seul outil écrit le code à la fois (héritée de `CLAUDE.md` "Workflow outils IA").

---

## Maintenance de ce fichier

- Tenu à jour par l'humain (solo founder) à chaque clôture de chantier.
- L'IA en cours de session **peut proposer** une mise à jour ; l'humain valide.
- La section "État courant" doit rester courte (≤10 lignes) — c'est un radar, pas un journal.
- Si "Chantier actif" reste vide, c'est volontaire : le prochain chantier doit être défini explicitement (skill `brainstorming` recommandé).

---

## Voir aussi

- Spec de cette rationalisation mémoire IA : `docs/superpowers/specs/2026-04-26-ai-context-rationalization-design.md`
- Workflow outils IA détaillé : `CLAUDE.md` section "Workflow outils IA"
- Conventions de code : `CLAUDE.md` section "Conventions du projet"
