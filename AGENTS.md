# AGENTS.md — Mathakine

> **Point d'entrée unifié pour toute session IA** (Codex, Claude Code CLI + superpowers, Octopus, Cursor).
> Ce fichier reflète l'**état opérationnel courant**. Pour la stack/architecture stable, voir `CLAUDE.md`.

---

## État courant

| Champ | Valeur |
|---|---|
| Version | `3.6.0-beta.5` |
| Branche | `master` |
| Dernière phase livrée | `3.6.0-beta.5` - stabilisation défis IA + Phase 3 tests (3A golden, 3B renderer contracts, 3D solveur perf) + VarietySeed (lot Qualité, commits 74ffb14→33bb325) + docs release - commit `da794f4` |
| Dernier audit clos | 2026-04-28 (audit documentaire complet — alignement docs racine sur ground-truth v3.6.0-beta.5) |
| Chantier actif | **Plan qualité génération défis IA (2026-04-28)** — `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_QUALITY_LLM_BEST_PRACTICES_2026-04-28.md` — audit 10 défis a révélé 3 défis cassés (gen 3 visual auto-contradictoire, gen 4 puzzle insoluble, gen 10 chess invalide). Plan priorité GÉNÉRATION > DÉTECTION : Structured Outputs strict, Responses API, python-chess validator, Self-Consistency 2-sampling. Sprint 1 en attente de démarrage. |
| Commits non poussés | 0 attendu après publication `3.6.0-beta.5` (vérifier avec `git log origin/master..master --oneline`) |

---

## Documents canoniques (lire en premier)

| Document | Rôle |
|---|---|
| `CLAUDE.md` | Stack, architecture, conventions projet (canonique) |
| `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_SOLIDIFICATION_2026-04-22.md` | Backlog défis IA Phase 1-3 (clos avec `3.6.0-beta.5`) |
| `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_QUALITY_LLM_BEST_PRACTICES_2026-04-28.md` | **Plan actif** — qualité génération + best practices LLM o-series + non-régression Sentry 115344051 |
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
| DONE (commit `da794f4`) | `docs/superpowers/specs/2026-04-26-ai-context-rationalization-design.md` (rationalisation mémoire IA — intégré dans le cycle 3.6.0-beta.5) |
| DONE (2026-04-28) | `docs/superpowers/specs/2026-04-28-doc-audit-design.md` + `docs/superpowers/plans/2026-04-28-doc-audit.md` (audit documentaire complet v3.6.0-beta.5 — ~60 fichiers alignés sur ground-truth) |
| ACTIVE | `docs/03-PROJECT/PLAN_CHALLENGE_GENERATION_QUALITY_LLM_BEST_PRACTICES_2026-04-28.md` (plan qualité génération défis IA — Sprint 1 en attente de démarrage) |

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

- Audit documentaire courant : `docs/superpowers/specs/2026-04-28-ground-truth-snapshot.md`
- Workflow outils IA détaillé : `CLAUDE.md` section "Workflow outils IA"
- Conventions de code : `CLAUDE.md` section "Conventions du projet"
