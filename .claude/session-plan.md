# Plan F42-Completion - Refonte difficulte globale Mathakine

**Date initiale :** 2026-03-26
**Derniere mise a jour :** 2026-03-27 (apres debat + audit terrain)
**Source :** audit code consolide + debat 4 agents + revue croisee
**Execution :** Cursor Composer
**Validation :** `/octo:review` apres chaque lot

---

## 1. Etat Reel (verite terrain 2026-03-27)

| Couche | Etat initial | Etat reel apres lots |
|--------|-------------|----------------------|
| BDD / persistance | OK | **DONE** — `users.age_group`, `difficulty_tier` sur exercises + logic_challenges |
| Recommandation | OK | **DONE** — filtre tier +-1 exercices, score-penalty defis (design choice documente) |
| Types frontend API | OK | **DONE** — `difficulty_tier` type Exercise + Challenge |
| Generation exercices (local) | PARTIEL | **DONE** — `build_exercise_generation_profile()` + `SpatialNarratives` + `pedagogical_band_override` |
| Generation exercices (OpenAI) | PARTIEL | **DONE** — `calibration_desc` injecte dans system prompt |
| Adaptive second axe exercices | PARTIEL | **DONE** — `AdaptiveGenerationContext`, `resolve_adaptive_context()`, separation age / bande |
| Fallback band cold-start | ANALYSE | **REVERT (2026-03-27)** — fallback reste "learning" (decision produit requise — voir F42-P2) |
| Generation defis / contexte user | PARTIEL | **DONE** — `challenge_generation_context.py` lit `users.age_group` via `build_recommendation_user_context()` |
| SSE defis difficulty_tier (chemin normal) | MANQUANT | **DONE** — `_persist_challenge_sync()` retourne `difficulty_tier` depuis DB |
| SSE defis difficulty_tier (chemin erreur) | MANQUANT | **DONE (2026-03-27)** — `normalize_generated_challenge()` accepte + retourne `difficulty_tier` (fix P1b) |
| Evaluation / progression (bridge) | NON | **DONE** — `mastery_tier_bridge.py` : `mastery_to_tier()`, `enrich_diagnostic_scores_f42()`, `canonical_age_group_with_fallback()` |
| Admin list exercices + defis | NON | **DONE** — `admin_content_service.py` expose `difficulty_tier` + `difficulty_rating` |
| Schema GenerateExerciseResult | INCOMPLET | **DONE** — `difficulty_tier: Optional[int]` + `model_config extra="allow"` |
| Destarwarisation exercices backend | PARTIEL | **DONE** — `SpatialNarratives`, tags IA neutralises, narratifs spatiaux |
| Destarwarisation schemas (docstrings) | NON | **TODO (C1B)** — 4 docstrings residuelles dans exercise.py + logic_challenge.py |
| Destarwarisation i18n (exercise copy) | NON | **TODO (C1B)** |
| Gamification cleanup labels publics | NON | **TODO (C3B)** |
| Extension ladder 5 -> 8 buckets | NON | **TODO (C3C)** |
| Cleanup final Star Wars visible | NON | **TODO (C4)** |

---

## 2. Regles non negociables

1. **Lire avant d'ecrire** - auditer les fichiers reels avant toute modification.
2. **Un lot = un commit.**
3. **Diff strictement borne** - aucun changement hors scope.
4. **RGPD mineurs (critique)** : les libelles de rang du classement public doivent rester bases sur la **progression** (`XP/points`), jamais sur `age_group`.
5. **`preferred_difficulty`** : ne pas supprimer brutalement. Introduire un helper de normalisation (`canonical_age_group(user)`) puis deprecier progressivement.
6. **`DifficultyLevels`** (`INITIE/PADAWAN/...`) : ne pas renommer tant que la boucle evaluation/progression n'est pas stabilisee.
7. **Champ technique legacy** : `jedi_rank` peut rester un identifiant technique temporaire si les labels publics sont neutralises cote affichage.

---

## 3. Sequencage reel

```text
[DONE] F42-C1A  : Generation exercices (local + OpenAI + diagnostic feeder)
[DONE] F42-C2   : Evaluation / progression (bridge mastery -> tier)
[DONE] F42-C3A  : Defis personnalises par contexte utilisateur
[DONE] F42-ADMIN-CHECK : Controle end-to-end admin
[DONE] F42-P1   : Fix P1b uniquement (difficulty_tier dans chemins erreur SSE challenge)
TODO   F42-C1B  : Destarwarisation UI/i18n exercices hors gamification publique
TODO   F42-P2   : Corrections dette technique (cache mastery + safeguard bridge)
TODO   F42-C3B  : Gamification/theme cleanup + surfaces stales + alias enums
TODO   F42-C3C  : Extension ladder publique 5 -> 8 buckets (backend + UI + i18n)
TODO   F42-C4   : Cleanup final des traces Star Wars encore visibles
```

---

## 4. Lots restants

---

### Lot F42-C1B — Destarwarisation UI/i18n exercices

**Statut :** TODO
**Dependance :** aucune (parallelisable)

#### Perimetre exact

**Docstrings a neutraliser :**

- `app/schemas/exercise.py:135` — `Création d'une Épreuve` -> neutre
- `app/schemas/exercise.py:142` — `Modification d'une Épreuve` -> neutre
- `app/schemas/exercise.py:193` — `Archives des Épreuves` -> neutre
- `app/schemas/logic_challenge.py:434` — champ `star_wars_title: Optional[str] = None` -> dette acceptable, documenter uniquement

**i18n exercices :**
- `frontend/messages/fr.json` : textes lies exercices / aide / onboarding si encore Star Wars
- `frontend/messages/en.json` : idem

**Perimetre interdit :**
- `frontend/lib/constants/leaderboard.ts`
- `frontend/components/dashboard/LevelIndicator.tsx`
- Tout ce qui expose les rangs de progression publics

#### Commit cible
`fix(f42): neutralize exercise schemas docstrings and exercise-facing copy`

---

### Lot F42-P2 — Dette technique post-debat

**Statut :** TODO
**Dependance :** aucune (peut etre parallele)
**Priorite :** moyen terme (avant montee en charge, pas urgent a court terme)

#### Actions

**P2a — Decision produit : fallback band cold-start (DECISION REQUISE avant implementation) :**

Contexte exact (Codex 2026-03-27) :
- Sans signal d'age → fallback GROUP_9_11 + "learning" → tier 5
- Avec age 6-8 connu + sans mastery → 6-8 + "learning" → tier 2
- Ce sont deux cas distincts. "learning" est le fallback valide pour tous les lots F42.

Trois options produit a choisir explicitement :
- Option A : conserver `"learning"` (neutre, compatible, statu quo)
- Option B : `"discovery"` pour TOUS les cas sans mastery (plus conservateur, impact global)
- Option C : `"discovery"` seulement quand `mastery_source == "fallback"` ET age_group == GROUP_9_11 (fallback d'age aussi)

Fichier : `app/services/exercises/adaptive_difficulty_service.py` ligne ~643

**P2b — Cache in-process mastery (effort faible, ROI elevé) :**
- Ajouter un cache applicatif TTL 5min sur `resolve_adaptive_context()` (keyed sur `user_id + exercise_type`)
- Implémentation : dict in-process avec timestamp, pas Redis
- Fichier : `app/services/exercises/adaptive_difficulty_service.py`

**P2c — Safeguard bridge (effort minimal) :**
- Ajouter un assert/clamp + log d'alerte sur la valeur de sortie de `mastery_to_tier()`
- Fichier : `app/core/mastery_tier_bridge.py`
- Objectif : detecter dégradation silencieuse si valeur hors 1-12

**P2d — Instrumenter taux de réussite par tier :**
- Mesurer le taux de réussite par `difficulty_tier` en production
- Objectif : valider empiriquement que les 12 tiers produisent des taux dans la fenetre 60-80%

#### Commit cible
`fix(f42): cold-start fallback decision + mastery cache + bridge safeguard`

---

### Lot F42-C3B — Gamification/theme cleanup + surfaces stales

**Statut :** TODO
**Dependance :** C1B confirme (labels exercices neutres avant nettoyage gamification)

#### Objectif
- Neutraliser les labels publics encore Jedi quand c'est un choix produit valide
- Nettoyer les surfaces/documentations stales
- Finaliser les alias/renommages de constantes seulement si C2 et C3A sont stabilises (ils le sont)

#### Fichiers typiques
- `app/services/gamification/compute.py`
- `app/services/gamification/level_titles.py`
- `frontend/lib/constants/leaderboard.ts`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`
- `app/models/exercise.py`
- `app/core/constants.py`

#### Regle RGPD / produit
- Le classement public reste base sur la progression.
- Si les labels deviennent spatiaux, ils doivent rester des **labels de progression**, pas des labels correles a l'age.
- Les labels age type `Explorateurs / Navigateurs / Pilotes / Etoiles` sont reserves aux surfaces parent/enseignant si le produit le valide plus tard.

#### Note sur les enums
Le renommage ou l'alias fort de `DifficultyLevels` est **optionnel** dans ce lot.
Si le cout de compatibilite est trop eleve, le laisser en dette explicite est acceptable.

#### Commit cible
`fix(f42): finish theme cleanup and stale surface alignment`

---

### Lot F42-C3C — Extension ladder publique 5 -> 8 buckets

**Statut :** TODO
**Dependance :** C3B (neutraliser labels avant etendre la ladder)

**Note terrain :** Le backend a DEJA 8 buckets (`cadet`, `scout`, `explorer`, `navigator`, `cartographer`, `commander`, `stellar_archivist`, `cosmic_legend`). Verifier si le frontend et l'i18n sont alignes avant de coder quoi que ce soit.

#### Fichiers typiques
- `app/services/gamification/compute.py` — 8 buckets deja presents, verifier seuils
- `app/services/gamification/level_titles.py`
- `app/services/gamification/gamification_service.py`
- `frontend/lib/constants/leaderboard.ts`
- `frontend/lib/gamification/progressionRankLabel.ts`
- `frontend/app/leaderboard/page.tsx`
- `frontend/components/dashboard/LeaderboardWidget.tsx`
- `frontend/app/badges/page.tsx`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`

#### Regle produit
- Les buckets restent des **rangs de progression** derives des points / niveaux compte.
- Ils ne doivent jamais etre interpretes comme une difficulte pedagogique.

#### Commit cible
`feat(f42): align frontend rank ladder to 8 canonical buckets`

---

### Lot F42-C4 — Cleanup final des traces Star Wars encore visibles

**Statut :** TODO
**Dependance :** C3B confirme (progression publique stabilisee)

#### Priorites
1. emails transactionnels et verification
2. persona / prompts du chat
3. surfaces admin visibles encore libellees Star Wars
4. reliquats frontend visibles hors gamification deja nettoyee
5. constantes/messages branchees qui restent affichees a l'utilisateur

#### Fichiers typiques
- `app/utils/email_templates.py`
- `app/services/communication/chat_service.py`
- `frontend/components/admin/BadgeCreateModal.tsx`
- `frontend/components/admin/BadgeEditModal.tsx`
- `frontend/app/admin/users/page.tsx`
- `frontend/components/dashboard/Recommendations.tsx`
- `app/core/messages.py` seulement pour les chaines encore reellement branchees

#### Regle de tri
- **Prioritaire** : tout texte visible (UI, emails, chat, tooltips, labels, placeholders)
- **Secondaire** : commentaires, tests, fixtures
- **Dette acceptable** : noms techniques internes (`jedi_rank`, enums legacy, variables/fonctions) tant qu'ils ne fuient pas visiblement

#### Commit cible
`fix(f42): remove remaining visible starwars references`

---

## 5. Dette technique assumee (hors perimetre)

| Item | Raison du report |
|------|-----------------|
| `star_wars_title: Optional[str]` dans `ChallengeBadgeEarned` | Champ nullable, migration optionnelle, documenter uniquement |
| Cache mastery (P2a) | Pas urgent < quelques centaines users simultanes |
| Migration DB `difficulty_tier` sur tentatives/progress | Seulement apres validation couche service |
| Filtre dur reco defis (vs score penalty) | Design choice documente — asymetrie intentionnelle |
| Dashboard parent/enseignant labels age dedies | Produit payant, lot separe |
| Filtre leaderboard par groupe d'age (`F40-v2`) | Depend clarification produit post-C3B |
| Renommage physique champs API legacy (`jedi_rank`, etc.) | Migration de contrat dediee |
| Extension matrice F42 (5eme groupe age, 4eme bande) | Pas avant besoin utilisateur reel valide |

---

## 6. Points de vigilance post-debat

### Risques identifies par le debat 4 agents (2026-03-27)

| Risque | Priorite | Action |
|--------|----------|--------|
| Fallback band "learning" -> nouvel user recoit tier 5 | **CORRIGE** P1a | discovery par defaut |
| difficulty_tier absent chemins erreur SSE challenge | **CORRIGE** P1b | normalize_generated_challenge() |
| Cache mastery absent | P2 | lot F42-P2, avant montee en charge |
| Safeguard bridge silencieux | P2 | lot F42-P2 |
| Seuils bandes pédagogiques non valides empiriquement | Moyen terme | instrumenter taux reussite / tier |
| Double query Progress chemin IRT | Acceptable | faible risque multi-worker, surveiller |

### Validite pedagogique

Le debat scientifique (reference Hattie, Vygotsky, Sweller, Deci & Ryan, Siegler) confirme :
- La matrice 4x3 est **approximative mais viable** — plausible, pas prouve theoriquement
- Les seuils mastery -> bande sont des **stipulations pragmatiques**, pas des calibrations empiriques
- L'age comme premier axe **contredit** la variabilite intra-age (Siegler 1996) mais reste acceptable pour un MVP
- **Action cle** : instrumenter les taux de reussite par tier en production pour validation empirique

---

## 7. Gate standard

### Backend
```powershell
D:\Mathakine\.venv\Scripts\python.exe -m pytest tests\ -q --tb=short --maxfail=20 --no-cov --ignore=tests\api\test_admin_auth_stability.py
D:\Mathakine\.venv\Scripts\python.exe -m black <fichiers touches> --check
D:\Mathakine\.venv\Scripts\python.exe -m isort <fichiers touches> --check-only
D:\Mathakine\.venv\Scripts\python.exe -m flake8 --select=E9,F63,F7,F82 <fichiers touches>
```

### Frontend
```powershell
cd D:\Mathakine\frontend && npm run lint
cd D:\Mathakine\frontend && npx tsc --noEmit
cd D:\Mathakine\frontend && npx prettier --check <fichiers touches>
```
