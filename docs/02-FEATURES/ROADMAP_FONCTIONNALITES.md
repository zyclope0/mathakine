# Backlog & Priorisation des Features — Mathakine

> **Document vivant** - Derniere MAJ : 24/03/2026 (statuts realignes sur le code ; les features livrees restent visibles dans la roadmap au lieu de disparaitre)  
> **Rôle** : Source de vérité unique pour toutes les features à implémenter.  
> **Cible** : Enfants 5-20 ans + Parents. Contexte : plateforme EdTech maths adaptative.

---

## Table des matières

1. [Méthodologie de priorisation](#1-méthodologie-de-priorisation)
2. [Matrice synthèse — Toutes les features](#2-matrice-synthèse)
3. [P0 — Impact fort, fondements pédagogiques solides](#3-p0)
4. [P1 — Haute priorité](#4-p1) *(dont F30, F31, F32 — nouvelles)*
5. [P2 — Priorité moyenne](#5-p2)
6. [P3 — Investissement long terme](#6-p3)
7. [P4 — Backlog distant](#7-p4)
8. [Features implementees (historique)](#8-features-implementees)
9. [Références scientifiques](#9-références-scientifiques)

---

## 1. Méthodologie de priorisation

### 1.1 Axes d'évaluation (1–5)

| Axe | Description | 1 | 5 |
|-----|-------------|---|---|
| **D** — Difficulté | Effort d'implémentation estimé | ½ jour | 2+ semaines |
| **G** — Gain utilisateur | Impact direct sur l'engagement et la satisfaction | Négligeable | Transformateur |
| **E** — EdTech | Valeur pédagogique scientifiquement documentée (voir Â§1.2) | Cosmétique | Effet fort > 0.6d |
| **R** — Risque | Risque technique ou de régression | Aucun | Critique |
| **B** — Business | Rétention / acquisition / différenciation marché | Nul | Décisif |

### 1.2 Échelle EdTech — Base scientifique

L'axe EdTech est **le seul à être évalué à partir de données factuelles**, pas d'intuitions produit.

| Score | Signification | Critère |
|-------|--------------|---------|
| **5** | Preuve très forte | Méta-analyse, effet mesuré d â‰¥ 0.6 (Cohen), répliqué dans plusieurs populations |
| **4** | Preuve forte | Effet mesuré d = 0.4–0.6, ou consensus dans la littérature EdTech peer-reviewed |
| **3** | Preuve modérée | Bénéfice documenté mais conditionnel, population spécifique ou effet indirect |
| **2** | Preuve faible | Engagement documenté, mais impact sur l'apprentissage mixte ou non mesuré |
| **1** | Pas de preuve | Principalement cosmétique, spéculatif ou motivation extrinsèque non corroborée |

**Références de base utilisées pour le scoring** :
- Hattie (2009) — *Visible Learning* : méta-analyse de 800+ méta-analyses (>50 000 études)
- Cepeda et al. (2006) — Pratique distribuée et espacée — *Psychological Bulletin*
- Hattie & Timperley (2007) - Pouvoir du feedback - *Review of Educational Research*
- VanLehn (2011) — Tuteurs IA vs tuteurs humains — *Educational Psychologist*
- Bjork (1994) — Desirable difficulties in learning
- Sweller (1988) - Theorie de la charge cognitive - *Cognitive Science*
- Deci & Ryan (2000) — Théorie de l'autodétermination (SDT)
- Mayer (2001) - Multimedia learning theory
- Kivetz et al. (2006) — Goal-gradient hypothesis — *Journal of Marketing Research*

> **Convention** : `[PROPOSITION]` = feature suggérée par l'IA, non issue des docs existants. À valider produit avant implémentation.

### 1.3 Formule de score composite

```
Score = (G Ã— 1.5) + (E Ã— 2) + B âˆ’ (D Ã— 0.8) âˆ’ (R Ã— 0.7)
```

Un score élevé indique une feature à haute valeur et faible coût/risque. Le score **ne remplace pas** le jugement — il oriente la discussion.

### 1.4 Rituel de mise a jour apres chaque lot

Pour eviter qu'une feature livree "disparaisse" de la roadmap ou qu'un backlog stale survive trop longtemps :

1. relire le code reel du lot termine avant de modifier la roadmap
2. mettre a jour la ligne de matrice concernee avec un statut explicite : `[DONE]`, `[PARTIAL]`, `[BACKLOG]`
3. conserver les elements livres dans `2.1 Vue d'avancement` et `8.1 Features livrees et visibles`
4. si seule une fondation technique a ete posee, documenter le point en `8.2` au lieu de survendre la feature produit
5. si un document dedie change de verite (badges, workflow, API, IA, etc.), le mettre a jour dans le meme lot que le code

Ce rituel est obligatoire pour garder une roadmap motivante, lisible et alignee sur la verite terrain.

---

## 2. Matrice synthese

*Vue consolidee du backlog et du deja livre. Legende : D=Difficulte, G=Gain, E=EdTech, R=Risque, B=Business.*

| # | Feature | Statut reel code | D | G | E | R | B | Score | Priorite |
|---|---------|------------------|---|---|---|---|---|-------|----------|
| F01 | Rendu Markdown/KaTeX explications | [DONE] | 2 | 4 | 5 | 1 | 3 | **16.8** | P0 |
| F02 | Defis quotidiens (defi du jour) | [DONE] | 3 | 5 | 4 | 2 | 5 | **16.9** | P0 |
| F03 | Test de diagnostic initial | [DONE] | 3 | 4 | 5 | 2 | 4 | **16.0** | P0 |
| F04 | Revisions espacees (SM-2) | [BACKLOG] | 4 | 4 | 5 | 2 | 4 | **14.8** | P0 |
| F30 | [PROP] Effet Protege (corriger erreur IA) | [BACKLOG] | 4 | 4 | 5 | 2 | 4 | **15.4** | P1 |
| F31 | [PROP] Exemples resolus progressifs (Fading) | [BACKLOG] | 3 | 4 | 5 | 2 | 3 | **15.2** | P1 |
| F32 | [PROP] Mode Pratique Entrelacee (Interleaving) | [DONE] | 2 | 3 | 5 | 2 | 3 | **14.5** | P1 |
| F05 | Adaptation dynamique de difficulte | [DONE] | 4 | 4 | 5 | 3 | 4 | **13.9** | P1 |
| F06 | Conditions d'obtention badges visibles | [DONE] | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F07 | Courbe d'evolution temporelle | [DONE] | 3 | 4 | 3 | 2 | 3 | **11.2** | P1 |
| F08 | Objectifs personnalises | [BACKLOG] | 3 | 3 | 3 | 1 | 3 | **11.1** | P1 |
| F09 | Dashboard parent | [BACKLOG] | 4 | 4 | 3 | 2 | 5 | **11.4** | P1 |
| F10 | [PROP] Mode focus / session ciblee | [BACKLOG] | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F11 | [PROP] Partage progression -> parents (lien) | [BACKLOG] | 2 | 3 | 3 | 1 | 4 | **12.5** | P1 |
| F12 | Radar chart par discipline | [DONE] | 2 | 3 | 3 | 1 | 2 | **10.9** | P1 |
| F13 | Deblocage automatique badges temps reel | [DONE] | 2 | 3 | 3 | 1 | 3 | **11.5** | P1 |
| F33 | Feedback Growth Mindset (copywriting) | [DONE] | 1 | 3 | 3 | 1 | 2 | **11.4** | P1 |
| F14 | Monitoring IA - persistance DB | [PARTIAL] | 2 | 2 | 1 | 1 | 3 | **6.9** | P2 |
| F15 | Preference page d'accueil (connexion) | [BACKLOG] | 1 | 2 | 1 | 1 | 1 | **5.7** | P2 |
| F16 | Heatmap d'activite | [BACKLOG] | 3 | 3 | 2 | 1 | 3 | **9.1** | P2 |
| F17 | Celebrations visuelles ameliorees | [BACKLOG] | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F18 | Ligues hebdomadaires (upgrade leaderboard) | [BACKLOG] (leaderboard deja present) | 4 | 4 | 1 | 2 | 4 | **8.9** | P2 |
| F19 | Notifications push + email | [BACKLOG] | 4 | 3 | 2 | 2 | 4 | **8.1** | P2 |
| F20 | Normalisation niveaux de difficulte | [BACKLOG] | 4 | 3 | 2 | 3 | 3 | **6.9** | P2 |
| F21 | Badges secrets | [BACKLOG] | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F22 | Suppression utilisateur admin (RGPD) | [DONE] | 2 | 1 | 1 | 2 | 3 | **4.7** | P2 |
| F35 | [TECH] Redaction secrets dans logs DB (URL SQLAlchemy) | [DONE] | 1 | 2 | 1 | 1 | 4 | **7.5** | P2 |
| F36 | [UX][TECH] Flash auth au refresh | [BACKLOG] | 2 | 2 | 1 | 1 | 3 | **7.2** | P2 |
| F37 | [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard | [BACKLOG] actif | 3 | 3 | 4 | 2 | 3 | **11.7** | P2 |
| F38 | [UX][Gamification] Progression compte coherente & historique des gains | [PARTIAL] | 3 | 4 | 2 | 2 | 4 | **10.2** | P2 |
| F23 | [PROP] Exercices adaptatifs SR+IA | [BACKLOG] | 4 | 5 | 5 | 3 | 5 | **17.1** | P2* |
| F24 | Tuteur IA contextuel | [BACKLOG] | 5 | 5 | 5 | 3 | 5 | **16.1** | P3 |
| F25 | Mode classe / enseignant | [BACKLOG] | 5 | 4 | 4 | 3 | 5 | **14.9** | P3 |
| F26 | Filtres et tri badges | [DONE] | 2 | 2 | 1 | 1 | 2 | **6.4** | P3 |
| F27 | Optimisation re-renders exercices/defis | [BACKLOG] | 3 | 2 | 1 | 2 | 2 | **4.8** | P3 |
| F28 | Mode aventure / histoire narrative | [BACKLOG] | 5 | 5 | 3 | 3 | 5 | **13.1** | P4 |
| F29 | Personnalisation avatar / profil | [BACKLOG] | 3 | 3 | 1 | 1 | 2 | **7.1** | P4 |
| F34 | Module Sciences - Curiosites (Vrai/Faux, format court) | [BACKLOG] prototype seulement | 3 | 4 | 2 | 2 | 4 | **10.4** | P4 |
| F39 | [LEGAL] Refonte rangs & suppression IP Star Wars | [BACKLOG] critique | 4 | 3 | 1 | 3 | 5 | **6.2** | P2* |
| F40 | Leaderboard — position de l'utilisateur hors top 50 | [BACKLOG] | 2 | 4 | 2 | 1 | 3 | **10.7** | P2 |
| F41 | Leaderboard — filtre temporel (semaine / mois / tout) | [BACKLOG] | 3 | 4 | 1 | 2 | 3 | **7.2** | P2 |
| F42 | Architecture difficulté — séparation âge et niveau sur 2 axes | [BACKLOG] | 4 | 3 | 3 | 3 | 4 | **9.2** | P2 |

> *F23 a un score eleve mais depend de F04 (revisions espacees) - debloque apres F04.*
> *F39 : score composite 6.2 mais risque juridique Disney/Lucasfilm = bloquant avant toute commercialisation a grande echelle. Traiter avant la premiere campagne d'acquisition.*
> *F42 : prérequis architectural pour F40 (filtre âge leaderboard), les recommandations adaptatives et l'équité des comparaisons. Traiter avant toute refonte du système de recommandation.*

### 2.1 Vue d'avancement - visible, sans effacer le travail livre

**[DONE] Implemente dans le code**
- F01, F02, F03, F05, F06, F07, F12, F13, F22, F26, F32, F33, F35

**[PARTIAL] Fondations deja posees**
- F14 : monitoring IA runtime + admin read-only + runs harness persistes, mais pas encore de persistance DB complete des metriques runtime
- F38 : moteur gamification persistant + ledger `point_events` + calcul niveau/XP/rang, mais pas encore d'historique utilisateur dedie ni de lecture produit complete du ledger

**[BACKLOG] Encore a livrer**
- le reste de la matrice, avec priorite conservee

---

## 3. P0 — Impact fort, fondements pédagogiques solides {#3-p0}

Ces quatre features combinent un score composite élevé ET un bénéfice pédagogique scientifiquement robuste. Elles constituent le cœur de la valeur éducative de Mathakine.

---

### F01 — Rendu Markdown/KaTeX dans les explications

**Source** : [ROADMAP Â§4.7](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.8 | D=2, G=4, E=5, R=1, B=3

**Problème** : Les explications post-réponse (exercices et défis) sont du texte brut. Les formules mathématiques (`a³+b³`) et les étapes structurées sont illisibles.

**Valeur pédagogique (E=5)** :
- Mayer (2001) - *Multimedia Learning* : la segmentation et la mise en forme du texte reduisent la charge cognitive extrinseque et ameliorent la comprehension (effet mesure).
- Sweller (1988) - Cognitive Load Theory : l'organisation visuelle de l'information reduit la charge cognitive irrelevante.
- La lisibilité de l'explication est un vecteur direct du transfert d'apprentissage.

**Ce qu'il faut faire** :
- Intégrer `react-markdown` + `remark-math` + `rehype-katex` (ou `react-katex`) dans `ExerciseSolver` et `ChallengeSolver`
- Appliquer le rendu dans le bloc "Explication" de la réponse
- Style CSS pour les formules math (KaTeX CSS)
- Optionnel : accordéon "voir plus" si explication > 300 mots

**Effort estimé** : 1-2 jours

**Statut** : âœ… Implémenté — composant `frontend/components/ui/MathText.tsx` (react-markdown + remark-math + rehype-katex), intégré dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver` et `DiagnosticSolver`

---

### F02 — Défis quotidiens (défi du jour) âœ…

**Source** : [ROADMAP Â§3.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.9 | D=3, G=5, E=4, R=2, B=5

**Statut** : âœ… Implémenté (Mars 2026)

**Valeur pédagogique (E=4)** :
- Cepeda et al. (2006) — La pratique distribuée (daily sessions) produit une meilleure rétention que la pratique massée, indépendamment du temps total (d = 0.46-0.71).
- Deci & Ryan (2000) — SDT : les défis quotidiens optionnels, adaptés au niveau, soutiennent le besoin de compétence sans pression externe (contrairement aux streaks punitifs).

**Conception implémentée** : 3 défis par jour (volume_exercises, specific_type, logic_challenge), bonus XP, expiration minuit, pas de punition si manqué.

**Référence technique complète** : [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---


### F03 — Test de diagnostic initial

**Source** : [ROADMAP Â§3.5](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.0 | D=3, G=4, E=5, R=2, B=4

**Problème** : L'onboarding collecte les préférences (classe, âge, rythme) mais pas le niveau réel. Les premières recommandations peuvent être inadaptées, dégradant le moment critique des 5 premières minutes.

**Valeur pédagogique (E=5)** :
- Hattie (2009) — *Formative assessment* : d = 0.90 (un des effets les plus élevés en éducation). Identifier le niveau réel avant l'enseignement est la condition préalable à toute personnalisation efficace.
- Sweller (1988) - L'alignement entre difficulte et competence previent la surcharge cognitive (exercices trop faciles = ennui, trop difficiles = anxiete).
- *Assessment for learning* (Black & Wiliam, 1998) : le diagnostic préalable est la fondation de l'apprentissage adaptatif.

**Algorithme adaptatif (Item Response Theory simplifié)** :
```
1. Commencer au niveau médian
2. Correct â†’ question plus difficile (niveau +1)
3. Incorrect â†’ question plus facile (niveau -1)
4. Arrêt : 2 erreurs consécutives au même niveau â†’ niveau établi
5. Durée max : 10 questions, ~5 minutes
```

**Output** :
- `initial_level` par type d'exercice (addition, soustraction, multiplication, division, logique)
- Stocké dans `diagnostic_results` (table dédiée, scores JSONB par type)
- Alimente immédiatement les recommandations

**Effort estimé** : 3-5 jours

**Statut** : âœ… Implémenté le 04/03/2026

**Référence technique complète** : [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)

**Ce qui est branché** :
- Table `diagnostic_results` (migration `20260304_diagnostic`)
- Service IRT (`app/services/diagnostic_service.py`) : algo adaptatif, 10 questions, 4 types
- Endpoints `/api/diagnostic/status|start|question|answer|complete`
- Page `/diagnostic` (accessible depuis onboarding et Settings)
- Section "Évaluation de niveau" dans Settings (affiche date + niveaux par type)
- Recommandations : `RecommendationService` lit le diagnostic via `get_latest_score()` et affine la difficulté médiane

**Ce qui reste à câbler (backlog F03-suite)** :

| Lacune | Impact | Priorité | Statut |
|--------|--------|----------|--------|
| `/api/exercises/generate` ignore le niveau diagnostic | Un utilisateur scorant Initié reçoit des exercices selon `age_group`, pas son niveau réel | Moyen | âœ… Résolu 06/03/2026 — `adaptive_difficulty_service` câblé en étape 1 de la cascade |
| `preferred_difficulty` stocke des age_group (`"adulte"`) mais le service attendait des DifficultyLevels | Zyclope (adulte) tombait en fallback PADAWAN malgré son profil | Moyen | âœ… Résolu 06/03/2026 — `_PREF_DIFFICULTY_TO_ORDINAL` élargi aux deux formes |
| Mode de réponse QCM/saisie libre calculé sur la difficulté de l'exercice, pas le niveau réel utilisateur | Un utilisateur INITIE pouvait se voir forcer la saisie libre si l'exercice était GRAND_MAITRE | Moyen | âœ… Résolu 06/03/2026 — Frontend lit les scores IRT via `useIrtScores()`, décide par type |
| Types non couverts IRT (MIXTE, FRACTIONS) sans proxy de niveau | Pas d'adaptation pour ces types | Moyen | âœ… Résolu 06/03/2026 — Proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division) |
| Dashboard (`/`) ne lit pas `has_completed` | Pas de message de confirmation "ton niveau a été établi" | Faible | â³ Backlog |
| Génération IA (`/api/ai/generate`) ignore le diagnostic | Même problème que le générateur interne | Moyen | â³ Backlog |

---

### F04 — Révisions espacées (algorithme SM-2)

**Source** : [ROADMAP Â§3.3](ROADMAP_FONCTIONNALITES.md)  
**Score** : 14.8 | D=4, G=4, E=5, R=2, B=4

**Valeur pédagogique (E=5) — La preuve la plus robuste en éducation** :
- Ebbinghaus (1885, répliqué 100+ fois) — Courbe de l'oubli : sans révision, 70% d'une connaissance est oubliée en 24h, 90% en une semaine.
- Cepeda et al. (2006) — *Psychological Bulletin* : méta-analyse de 317 études. La pratique espacée améliore la rétention de 200%+ sur le long terme vs pratique massée.
- Kornell & Bjork (2008) — Spacing + interleaving : effet particulièrement fort en mathématiques (g = 0.43).
- *L'algorithme SM-2 (Wozniak, 1987) est le fondement de SuperMemo, Anki et DuoLingo.*

**Algorithme SM-2 adapté** :
```
Intervalles de révision :
- 1ère révision : J+1
- 2ème révision : J+3
- 3ème révision : J+7
- Suivantes : intervalle Ã— ease_factor

Ajustement ease_factor (EF, init 2.5) :
- Réponse correcte rapide (qualité 4-5) : EF + 0.1
- Réponse correcte lente (qualité 3) : EF inchangé
- Réponse incorrecte (qualité 0-2) : EF âˆ’ 0.2, retour J+1
```

**Modèle de données** :
```sql
spaced_repetition_items (
  id, user_id, exercise_id,
  ease_factor FLOAT DEFAULT 2.5,
  interval_days INT DEFAULT 1,
  next_review_date DATE,
  repetition_count INT DEFAULT 0,
  last_quality INT -- 0-5
)
```

**Intégration** : Après chaque tentative d'exercice, mise à jour de l'item SR. Widget "Révisions du jour" sur le dashboard.

**Effort estimé** : 1-2 semaines (migration + service + UI)

**Référence technique (spec)** : [F04_REVISIONS_ESPACEES.md](F04_REVISIONS_ESPACEES.md)

---

## 4. P1 — Haute priorité {#4-p1}

---

### F05 — Adaptation dynamique de difficulté âœ…

**Source** : [WORKFLOW_EDUCATION Â§2.2](WORKFLOW_EDUCATION_REFACTORING.md)  
**Score** : 13.9 | D=4, G=4, E=5, R=3, B=4

**Valeur pédagogique (E=5)** :
- Vygotsky (1978) - Zone proximale de developpement : l'apprentissage optimal se situe juste au-dela de la competence actuelle. Trop facile -> ennui. Trop difficile -> anxiete.
- Bjork (1994) — *Desirable difficulties* : un niveau de défi optimal crée une résistance productive (retrieval effort) qui renforce la mémorisation à long terme.
- Csikszentmihalyi (1990) - Etat de *flow* : atteint quand difficulte ~ competence.

**Implémentation (v3.0.0-alpha.3+, MAJ 06/03/2026)** :
- `app/services/adaptive_difficulty_service.py` — résolution par cascade (IRT > progression > profil > fallback), proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division)
- `server/handlers/exercise_handlers.py` — branchement adaptatif (`?adaptive=true` par défaut, désactivable par `?adaptive=false` ou `age_group` explicite)
- `app/utils/exercise_generator_helpers.py` -> distracteurs QCM calibres par niveau (INITIE: erreurs +/-1 + inversion, PADAWAN: retenue +/-10, CHEVALIER/MAITRE/GRAND_MAITRE: magnitude en %, `server/exercise_generator_helpers.py` restant un re-export de compatibilite)
- **Mode QCM vs saisie libre** : décidé côté frontend par `useIrtScores().resolveIsOpenAnswer(exercise_type)` — saisie libre uniquement si niveau IRT = GRAND_MAITRE pour ce type. Le backend génère toujours les `choices`.

**Référence technique complète** : [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md)

**Seuils adaptation temps reel** : `completion_rate > 85% ET streak >= 3` -> boost (+1 niveau) ; `completion_rate < 50% ET streak = 0` -> descente (-1 niveau).

**Hors scope F05-suite (backlog)** :
- `/api/ai/generate` — même adaptation pour la génération IA (SSE, complexité séparée)
- Dashboard widget 'ton niveau s'est ajuste' - [DONE] Implemente le 06/03/2026 (`LevelEstablishedWidget` dans l'onglet Vue d'ensemble)
- Seuils boost/descente configurables via admin
- **[F05-B1] Saisie libre déclenchée par taux de réussite réel, pas uniquement par niveau IRT** : plutôt que le seuil fixe GRAND_MAITRE, déclencher la saisie libre quand `completion_rate >= 90 % sur les 5 dernières tentatives` pour un type donné — indépendamment du niveau IRT. Fondement : Roediger & Karpicke (2006) Testing Effect + VanLehn (2011) méta-analyse tutoring adaptatif. Éviter d'encoder des erreurs en forçant le recall avant que la récupération soit automatique.
- **[F05-B2] Distracteurs QCM plus discriminants, moins déductibles** : améliorer la génération des `choices` pour éviter les bonnes réponses visibles par simple élimination. Cible : 3 distracteurs plausibles, de même ordre de grandeur, même format et même unité que la bonne réponse, issus d'erreurs typiques réelles (retenue, inversion, confusion opératoire, off-by-one, confusion quotient/reste) plutôt que de valeurs trop éloignées ou structurellement différentes. Ajouter si possible une instrumentation du taux de sélection des distracteurs pour identifier ceux qui ne trompent jamais. Effort estimé : 1-2 jours. Priorité produit : moyenne-haute, car impact direct sur la valeur pédagogique perçue des exercices.

**Dépendance** : Profite du diagnostic initial (F03) et prépare les révisions espacées (F04).


---

### F06 - Conditions d'obtention badges visibles

**Source** : [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) - section 4.2  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Statut** : [DONE] present dans le code au 23/03/2026 via `frontend/components/badges/BadgeCard.tsx` (affichage des `criteria_text` + progression sur badges verrouilles)

**Valeur pedagogique (E=3)** :
- Kivetz et al. (2006) - *Goal-gradient effect* : la motivation augmente a mesure que l'objectif est visible et proche. Effet mesure +40-60% d'engagement.
- Zimmerman (2002) - Transparence des criteres ameliore la regulation autonome de l'apprentissage (self-regulation).

**Ce qui est en place** :
- criteres affiches sur les badges verrouilles
- progression visible quand un objectif est quantifiable
- formulation orientee objectif proche (`plusQue`, `tuApproches`) dans l'UI badges

**Ce qui peut encore etre ameliore** :
- enrichir le wording de certains criteres si produit le souhaite
- ajouter plus de tri / filtrage sur la page badges (backlog F26 distinct)

**Effort realise** : present dans le code au 23/03/2026

---

### F07 — Courbe d'évolution temporelle

**Source** : [ANALYTICS_PROGRESSION Â§1.1](ANALYTICS_PROGRESSION.md)  
**Score** : 11.2 | D=3, G=4, E=3, R=2, B=3

**Statut** : âœ… Implémenté le 07/03/2026

**Valeur pédagogique (E=3)** :
- Zimmerman & Schunk (2001) — *Self-monitoring* : voir sa progression concrète dans le temps active la métacognition et renforce la motivation intrinsèque.
- Hattie (2009) — *Self-reported grades / metacognitive monitoring* : d = 1.33 (attention : effet de la conscience de sa propre progression, pas du graphique lui-même).

**Endpoint implémenté** : `GET /api/users/me/progress/timeline?period=7d|30d`  
**Données sources** : `Attempt.created_at`, `Attempt.is_correct`, `Attempt.time_spent`  

**Ce qui a été fait** :
- Service d’agrégation dédié : `app/services/progress_timeline_service.py` (jours continus, résumé global, `by_type`)
- Handler + route : `server/handlers/user_handlers.py`, `server/routes/users.py`
- Hook + widget frontend : `frontend/hooks/useProgressTimeline.ts`, `frontend/components/dashboard/ProgressTimelineWidget.tsx`
- Intégration dashboard : onglet Progression (`frontend/app/dashboard/page.tsx`)
- Tests : `tests/unit/test_progress_timeline_service.py`, `tests/api/test_progress_endpoints.py`, `frontend/__tests__/unit/hooks/useProgressTimeline.test.tsx`
- Référence d’implémentation : [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md)

**Effort estimé** : 3-5 jours

---

### F08 — Objectifs personnalisés

**Source** : [ROADMAP Â§4.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.1 | D=3, G=3, E=3, R=1, B=3

**Valeur pédagogique (E=3)** :
- Deci & Ryan (2000) — SDT : les objectifs auto-déterminés (choisis par l'utilisateur, pas imposés) renforcent la motivation intrinsèque et le besoin d'autonomie.
- Locke & Latham (1990) — *Goal-setting theory* : des objectifs spécifiques et mesurables améliorent la performance. Effet plus fort quand l'objectif est choisi par l'individu.

**Types** : Quotidien (ex: 5 exercices/jour), hebdomadaire, de maîtrise (ex: "atteindre 80% en division").

**Effort estimé** : 3-5 jours

---

### F09 — Dashboard parent

**Source** : [ROADMAP Â§3.1](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.4 | D=4, G=4, E=3, R=2, B=5

**Valeur pédagogique (E=3)** :
- Hattie (2009) — *Parental involvement* : d = 0.49. L'implication parentale dans le suivi scolaire a un effet positif mesurable sur les résultats.
- Bryk & Schneider (2002) — La confiance famille-institution est un prédicteur de l'engagement à long terme.

**Architecture minimale (MVP)** :
```
Table: parent_child_links (parent_user_id, child_user_id, created_at, permissions JSON)
Route: /parent/dashboard â†’ vue enfants
Route: /parent/child/[id] â†’ progression détaillée
```

**Effort estimé** : 1-2 semaines

---

### F10 — [PROPOSITION] Mode focus / session ciblée

**Source** : Proposition IA — non issue des docs existants  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Concept** : Permettre de lancer une session ciblée en 2 clics : "5 multiplications niveau PADAWAN". L'utilisateur choisit type + difficulté + nombre, et est guidé directement dans une suite d'exercices sans navigation.

**Valeur pédagogique (E=3)** :
- Bjork (1994) — *Desirable difficulties* : l'interleaving (mélange de types) est bénéfique, mais la pratique ciblée sur un type spécifique est nécessaire pour la construction de compétences (blocked practice pour la phase d'acquisition).
- Deci & Ryan — Le choix du type de pratique renforce l'autonomie (SDT).

**Effort estimé** : 1-2 jours (frontend principalement — filtres déjà disponibles en backend)

---

### F11 — [PROPOSITION] Partage de progression vers les parents (lien simple)

**Source** : Proposition IA — alternative légère au Dashboard Parent complet (F09)  
**Score** : 12.5 | D=2, G=3, E=3, R=1, B=4

**Concept** : Générer un lien de partage de progression (lecture seule, sans compte requis) permettant au parent de voir les stats de l'enfant sans créer un espace parent dédié. Quick win avant l'implémentation complète de F09.

**Valeur pédagogique (E=3)** : Même base que F09 (engagement parental), avec une friction d'adoption beaucoup plus faible.

**Effort estimé** : 1-2 jours

---

### F12 - Radar chart par discipline

**Source** : [ANALYTICS_PROGRESSION](ANALYTICS_PROGRESSION.md) - section 1.3  
**Score** : 10.9 | D=2, G=3, E=3, R=1, B=2

**Statut** : [DONE] present dans le code au 23/03/2026 via `frontend/components/dashboard/CategoryAccuracyChart.tsx` (`RadarChart` Recharts)

**Valeur pedagogique (E=3)** : Auto-evaluation et metacognition. Donnees deja disponibles dans `/api/exercises/stats` (`by_discipline`).

**Ce qui est en place** :
- visualisation radar par categorie / discipline
- integration dashboard
- lecture de donnees reelles, pas mockees

**Effort realise** : present dans le code au 23/03/2026

---

### F13 - Deblocage automatique badges (temps reel)

**Source** : [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) - section 4.4  
**Score** : 11.5 | D=2, G=3, E=3, R=1, B=3

**Statut** : [DONE] verification et attribution automatiques deja branchees apres tentative cote exercices et defis

**Valeur pedagogique (E=3)** :
- Kulik & Kulik (1988) - Feedback immediat ameliore l'apprentissage. S'applique aux recompenses : un badge debloque 2 jours apres l'effort perd son effet de renforcement.

**Ce qui est en place** :
- verification des badges apres tentatives d'exercices (`app/services/exercises/exercise_attempt_service.py`)
- verification des badges apres tentatives de defis (`app/services/challenges/challenge_attempt_service.py`)
- propagation des gains de points quand un badge attribue une recompense

**Ce qui reste perfectible** :
- enrichir le feedback UI (toast/animation) si produit souhaite une celebration plus visible

**Effort realise** : present dans le code au 23/03/2026

---

---

### F30 — [PROPOSITION] L'Effet Protégé ("Corrige l'erreur de l'IA")

**Source** : Proposition IA — non issue des docs existants  
**Score** : 15.4 | D=4, G=4, E=5, R=2, B=4

> *Score initial proposé : 16.2 (D=3). Difficulté révisée à D=4 : génération IA d'erreurs intentionnelles + composant UI "correction de copie" + vérification de la justification = périmètre backend + frontend non négligeable.*

**Problème** : Résoudre un problème mathématique est un apprentissage actif classique. Mais le niveau ultime de maîtrise s'atteint lorsqu'on doit enseigner à quelqu'un d'autre — ou corriger ses erreurs.

**Valeur pédagogique (E=5)** :
- Chase et al. (2009) — *The Protégé Effect* : Les étudiants font plus d'efforts et apprennent plus profondément quand ils doivent enseigner à un agent virtuel (effet mesuré très fort).
- Hattie (2009) — *Peer Tutoring* : d = 0.55. L'évaluation des erreurs des autres active une métacognition supérieure à la simple résolution.
- La détection d'une erreur de logique (et non de calcul) est un exercice de compréhension conceptuelle profonde, non mémorisable par substitution de pattern.

**Ce qu'il faut faire** : Créer un type de défi inversé. L'IA présente un problème et une résolution étape par étape contenant **une seule erreur de logique intentionnelle**. L'élève doit agir comme le professeur : identifier à quelle étape l'IA s'est trompée et expliquer pourquoi.

**Architecture cible** :
- Nouveau `challenge_type` : `error_correction`
- Champ backend : `steps: [{content, is_error: bool, error_explanation}]`
- UI : composant "Correction de copie" — affichage des étapes numérotées, sélection de l'étape erronée, champ justification
- Validation : l'élève doit identifier la bonne étape ET soumettre une explication (même courte)

**Effort estimé** : 3-5 jours (nouveau type de défi + composant UI + prompt IA pour génération d'erreurs intentionnelles)  
**Priorité** : P1 — score fort, différenciateur pédagogique unique sur le marché

---

### F31 — [PROPOSITION] Exemples résolus progressifs (Fading Effect)

**Source** : Proposition IA — non issue des docs existants  
**Score** : 15.2 | D=3, G=4, E=5, R=2, B=3

**Problème** : Face à un concept totalement nouveau, faire faire des exercices et sanctionner l'erreur (même avec correction ensuite) génère de l'anxiété et une surcharge cognitive pour les novices.

**Valeur pédagogique (E=5)** :
- Sweller & Cooper (1985) — *Worked Example Effect* : Étudier des problèmes déjà résolus est **plus efficace pour les novices** que de résoudre des problèmes (d = 0.57). Répliqué extensivement.
- Renkl (1997) — *Fading steps* : La transition optimale de novice à expert se fait en retirant progressivement les étapes guidées — l'autonomie croît naturellement.
- Complémentaire avec F05 (adaptation difficulté) : le fading s'active automatiquement quand l'algorithme détecte un concept nouveau (0 tentatives sur ce type).

**Ce qu'il faut faire** : Intégrer une mécanique de "Fading" dans l'onboarding d'un nouveau concept (déclenchée quand l'utilisateur rencontre un sous-type d'exercice pour la première fois) :

| Exercice | Mode | Description |
|----------|------|-------------|
| 1 | **Fully worked** | Entièrement résolu par l'IA, l'élève lit et clique "J'ai compris" |
| 2 | **Last step missing** | Résolu, mais la dernière étape est à compléter |
| 3 | **Half faded** | Seule la première étape est donnée, l'élève finit |
| 4 | **Autonome** | L'élève fait tout — régime normal |

**Contrainte de conception** : Ne pas pénaliser l'exercice "fully worked" (pas de score de réussite/échec) — c'est un mode observation, pas évaluation.

**Effort estimé** : 3-5 jours (déclinaison du moteur d'exercices + détection "première fois sur ce sous-type")  
**Priorité** : P1 — particulièrement critique pour la rétention des utilisateurs en onboarding

---

### F32 — [PROPOSITION] Mode "Pratique Entrelacée" (Interleaving) âœ…

**Source** : Proposition IA — non issue des docs existants  
**Score** : 14.5 | D=2, G=3, E=5, R=2, B=3

**Statut** : âœ… Implémenté le 07/03/2026

> *Score initial proposé : 15.2 (R=1). Risque révisé à R=2 : le mélange de types d'exercices interagit avec F05 (adaptation dynamique par type) — il faut s'assurer que les niveaux par type sont suffisamment calibrés avant activation.*

**Problème** : Les élèves ont tendance à enchaîner un seul type d'exercice (ex : 10 additions d'affilée — *Blocked Practice*). Le cerveau se met en pilote automatique et n'apprend pas à **choisir la bonne stratégie**, compétence clé en évaluation.

**Valeur pédagogique (E=5)** :
- Rohrer & Taylor (2007) — *Interleaved Practice* : Mélanger les types de problèmes force le cerveau à identifier la stratégie avant de l'appliquer. **Rétention à long terme améliorée de +43%** par rapport à la pratique bloquée.
- Kornell & Bjork (2008) — Effet particulièrement fort en mathématiques : spacing + interleaving combinés produisent les meilleures performances (g = 0.43).
- **Attention** : L'interleaving est contre-intuitif — les élèves ont l'impression d'apprendre moins bien pendant la session (mais retiennent mieux). À accompagner d'une explication pédagogique dans l'UI.

**Ce qui a été fait** :
- Endpoint dédié : `GET /api/exercises/interleaved-plan?length=10` (`server/handlers/exercise_handlers.py`, `server/routes/exercises.py`)
- Service d'agrégation : `app/services/interleaved_practice_service.py` (fenêtre 7 jours, éligibilité `>=2 tentatives` et `>=60%`, plan round-robin sans doublons consécutifs)
- Gestion métier explicite : `InterleavedNotEnoughVariety` -> `409` avec code `not_enough_variety`
- Quick Action dashboard : 3e CTA dans `QuickStartActions` + instrumentation analytics `quick_start_click` type `interleaved`
- Entrée session : page `frontend/app/exercises/interleaved/page.tsx` (plan, fallback 409, génération 1er exercice, redirection)
- Progression session : `ExerciseSolver` en mode `session=interleaved` (progression, bouton "Exercice suivant", écran de fin)
- i18n FR/EN : clés `dashboard.quickStart.interleaved*` et `exercises.solver.session*`
- Correctif critique F05/F32 : `POST /api/exercises/generate` passe en `@optional_auth`, ce qui active correctement la résolution adaptative `age_group` quand `adaptive=true`

**Durcissements post-implémentation (08/03/2026)** :
- analytics EdTech `interleaved` ramenées à une sémantique session : `first_attempt` n'est émis qu'une seule fois au premier exercice soumis, avec persistance `sessionStorage`
- flux de session durci : `POST /api/exercises/generate` ne renvoie plus de `200` sans `id` quand `save=true` ; en cas d'échec, le frontend affiche un toast et conserve l'état de session
- dette DRY réduite : la résolution adaptive `age_group` est factorisée dans `_resolve_adaptive_age_group_if_needed()` pour éviter la divergence entre `generate_exercise` et `generate_exercise_api`
- quality gate restauré : `black app/ server/ tests/ --check` repasse au vert ; nettoyage UTF-8 de `tests/unit/test_adaptive_difficulty_service.py` et hygiène repo (`frontend/junit.xml`, `.gitignore`, import inutilisé)

**Tests** :
- `tests/unit/test_interleaved_practice_service.py`
- `tests/api/test_exercise_endpoints.py` (auth, `409 not_enough_variety`, succès `200`, non-régression `adaptive=true` sans `age_group` explicite)

**Effort réalisé** : ~1-2 jours  
**Dépendance** : F05 exploité (difficulté adaptative conservée)  
**Priorité** : P1 — quick win fort, effort modéré, impact pédagogique élevé

---

### F33 — Feedback "Growth Mindset" âœ…

**Source** : Proposition IA — non issue des docs existants  
**Score** : 11.4 | D=1, G=3, E=3, R=1, B=2

> *Score initial proposé : 13.0 (E=4). EdTech révisé à E=3 : les études Dweck sont robustes mais les interventions de Growth Mindset par texte seul ont des effets faibles sans accompagnement long terme. Yeager et al. (2019) mesure des effets sur populations défavorisées spécifiques — le transfert à une plateforme généraliste est conditionnel.*

**Statut** : âœ… Implémenté le 07/03/2026

**Problème** : Un message "Faux" ou un feedback négatif brutal lors d'un échec peut renforcer un *Fixed Mindset* ("Je suis nul en maths"). Ce biais est particulièrement fort chez les enfants 8-14 ans.

**Valeur pédagogique (E=3)** :
- Dweck (2006) — *Mindset Theory* : Valoriser l'effort et la stratégie plutôt que l'intelligence innée ou le résultat brut améliore la résilience face à l'échec.
- Yeager et al. (2019) : Une simple intervention Growth Mindset a des effets mesurables sur les résultats en maths chez les élèves défavorisés.
- **Nuance** : L'effet est conditionnel et nécessite de la cohérence dans tout le parcours utilisateur — un seul message ne suffit pas.

**Ce qui a été fait** (modifications de texte + micro-UI) :

| Avant | Après |
|-------|-------|
| "Mauvaise réponse" | "Pas encore ! La prochaine sera la bonne." |
| "Incorrect" | "Ton cerveau est en train d'apprendre !" |
| Score affiché seulement | Valoriser aussi le **temps passé** sur un défi difficile |
| — | Tooltips de chargement : *"Savais-tu que ton cerveau crée de nouvelles connexions exactement au moment où tu fais une erreur ?"* |

**Contrainte** : Cohérence avec les textes de feedback existants dans `fr.json` / `en.json`. Ne pas sur-positiver au point de perdre la valeur informative du feedback (Hattie & Timperley, 2007 — le feedback doit rester précis).

**Implémentation** :
- Messages FR/EN alignés Growth Mindset (`frontend/messages/fr.json`, `frontend/messages/en.json`)
- Feedback d'échec harmonisé dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver`
- Bloc partagé factorisé : `frontend/components/ui/GrowthMindsetHint.tsx` (industrialisation, no-DRY)

**Effort réalisé** : ~½ jour  
**Priorité** : P1 — quick win absolu, risque technique faible, impact psychologique documenté

---

## 5. P2 — Priorité moyenne {#5-p2}

| Feature | Note |
|---------|------|
| **F14 - Monitoring IA persistance DB** | [PARTIAL] Le runtime monitoring et l'admin read-only existent deja (`token_tracker`, `generation_metrics`, `/admin/ai-monitoring`) ainsi que la persistance DB des runs harness. Le backlog restant porte sur une persistance DB complete des metriques runtime live, aujourd'hui surtout en memoire process. |
| **F15 — Préférence page d'accueil** | Champ `login_redirect_preference` sur `User`. Option dans Paramètres. ~½ jour. |
| **F16 — Heatmap d'activité** | Calendrier GitHub-style sur Dashboard/Profil. `react-calendar-heatmap`. Endpoint : `GET /api/users/me/activity/heatmap`. |
| **F17 — Célébrations visuelles améliorées** | Confettis au déblocage badge, modal avec partage. Désactivable (accessibilité). |
| **F18 - Ligues hebdomadaires** | Le leaderboard existe deja (top 50, filtres, surfaces de lecture), mais pas encore les ligues / saisons hebdomadaires. Le backlog porte sur les groupes, promotions/relegations et resets periodiques. Score EdTech=1 : engagement, pas d'apprentissage direct. |
| **F19 — Notifications push + email** | Rappel inactivité, streak en danger, badge proche. Voir [ROADMAP Â§4.1](ROADMAP_FONCTIONNALITES.md). Infrastructure à définir (service push web + SMTP). |
| **F20 — Normalisation niveaux de difficulté** | Remplacer nomenclature Star Wars par libellés universels. Voir [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md). Migration enum risquée — à planifier soigneusement. |
| **F21 — Badges secrets** | Badges cachés débloqués pour comportements inattendus (ex: "Noctambule" après minuit). Variable reward (Skinner) — engagement élevé. |
| **F22 - Suppression utilisateur admin (RGPD)** | [DONE] `DELETE /api/admin/users/{id}` existe deja cote admin. Le code supprime physiquement l'utilisateur avec cascade (pas un simple soft delete) et bloque l'auto-suppression admin. |
| **F35 — [TECH] Redaction secrets logs DB âœ…** | Implémenté le 07/03/2026. `app/db/base.py` loggue désormais une URL redigée via `redact_database_url_for_log()` (credentials et query params masqués). Couvert par `tests/unit/test_db_log_redaction.py` (7 tests). |
| **F36 — [UX][TECH] Flash auth au refresh** | Artefact visuel observé après refresh: pendant ~0.5s, le frontend semble repasser par un état "non connecté" avant rehydratation correcte de la session. Backend session validé: login OK, session conservée après refresh et après idle prolongé. Cible: supprimer le flash sans changer la chaîne de session/cookies. Piste probable: bootstrap auth frontend (`ProtectedRoute`, `current-user`, `validate-token`, `sync-cookie`). Ouvrir un lot dédié seulement si le symptôme devient gênant ou s'accompagne d'une redirection parasite/perte de session. |
| **F37 - [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard** | Clarifier la portee des filtres temporels dans le dashboard. Conclusion de l'analyse UX : un controle = un perimetre visible. Les widgets temporels doivent avoir un selecteur local ou une periode partagee explicite ; les widgets cumules doivent afficher un badge de portee (`Cumule`, `Tous les temps`) plutot qu'un faux selecteur. Les vues journalieres redondantes dans `Progression` doivent etre rationalisees au profit d'un widget complementaire (ex : regularite de pratique). Si l'on veut une coherence temporelle complete de l'onglet `Progression`, ouvrir ensuite un lot dedie data/hooks/backend pour exposer une periode explicite sur les widgets aujourd'hui cumules. |
| **F38 - [UX][Gamification] Progression compte coherente & historique des gains** | [PARTIAL] Le moteur persistant, le ledger `point_events`, le calcul niveau/XP/rang et plusieurs surfaces de lecture existent deja. Le backlog F38 porte maintenant sur la surface produit coherente : historique des gains, lecture par source et presentation compte explicite. |
| **F23 — [PROP] Exercices adaptatifs SR+IA** | Générer des exercices IA ciblés sur les concepts à réviser selon la courbe SR (F04). Score composite très élevé (17.1) mais **dépend de F04**. Débloqué après F04. |

---

### F37 - Coherence progression & selecteurs de temporalite dashboard

**Score** : 11.7 | D=3, G=3, E=4, R=2, B=3

**Probleme** : Le dashboard peut exposer plusieurs controles de periode qui ne pilotent pas le meme perimetre. Sur `Progression`, cela cree une incoherence UX : certains widgets sont temporels, d'autres cumules, et un filtre de header peut laisser croire a tort a une portee globale. Pour un apprenant, cette ambiguite consomme de la charge cognitive inutile.

**Conclusion de l'analyse** :
- **Un controle = un perimetre visible.** Aucun widget ne doit dependre d'une periode choisie ailleurs sans feedback clair.
- **Widgets temporels** : selecteur local ou periode partagee explicite a l'echelle du bloc.
- **Widgets cumules** : pas de faux selecteur ; afficher un badge de portee type `Cumule` / `Tous les temps`.
- **Pas de doublons visuels** : deux widgets journaliers qui repondent presque a la meme question doivent etre fusionnes ou remplaces par un angle pedagogique complementaire (ex : regularite de pratique).

**Valeur pedagogique (E=4)** :
- Sweller (1988) - la reduction de charge cognitive extrinseque ameliore la comprehension et la focalisation sur la tache d'apprentissage.
- Mayer (2001) - la clarte de presentation et la coherence des signaux visuels ameliorent l'assimilation.
- Hattie & Timperley (2007) - un feedback utile doit etre interpretable immediatement ; un filtre ambigu deforme le feedback plutot qu'il ne l'aide.

**Cible backlog** :
1. Rationaliser l'onglet `Progression` pour que chaque widget exprime clairement son scope temporel.
2. Eliminer les dependances invisibles a un filtre de header masque ou partiellement applique.
3. Remplacer les widgets redondants par des widgets complementaires a valeur pedagogique plus forte.
4. Ouvrir ensuite, si necessaire, un lot dedie data/hooks/backend pour rendre `Progression` entierement coherent sur la temporalite (periode explicite sur stats/progress/challenges aujourd'hui cumules).

**Effort estime** : 2-4 jours pour la rationalisation frontend ; lot separe si la coherence complete demande une evolution API/hook.

**Statut** : [BACKLOG] actif - a traiter avant toute refonte visuelle plus large du dashboard.

---

### F38 - Progression gamification compte coherente & historique des gains

**Score** : 10.2 | D=3, G=4, E=2, R=2, B=4

**Statut** : [PARTIAL] Fondations implementees - moteur persistant, ledger `point_events`, calcul niveau/XP/rang et surfaces de lecture compte deja presents ; backlog restant sur l'historique utilisateur et la lecture produit coherente du ledger

**Probleme** : Le moteur de gamification persistant existe desormais (points, niveau, XP dans le palier, rang, ledger des gains), mais il n'est pas encore exploite comme surface produit coherente. Le risque n'est pas technique : c'est de laisser cette fondation invisible, ou pire, de la sur-vendre comme une progression pedagogique alors qu'elle releve de la motivation et du feedback compte.

**Regle produit non negociable** :
- **Gamification compte** : points, niveau, XP palier, rang, historique des gains.
- **Progression pedagogique** : IRT, maitrise par type, performance d'exercice.
- **Interdiction** de fusionner ces deux dimensions dans l'UI ou dans les libelles.

**Conclusion de l'analyse** :
- Le moteur unique `GamificationService.apply_points` + le ledger `point_events` ouvrent enfin une lecture fiable du compte.
- Cette lecture doit rester **sobre, compacte, explicite**, et ne jamais concurrencer l'apprentissage en cours.
- Les gains doivent etre expliques par **source visible** (`badge_awarded`, `daily_challenge_completed`, futures sources), pas par un total opaque.

**Valeur pedagogique / produit (E=2)** :
- Deci & Ryan (2000) : la motivation extrinseque ne doit pas prendre le dessus sur le sentiment de competence. Utilisee avec moderation, une gamification lisible peut soutenir l'engagement sans polluer l'apprentissage.
- Hattie & Timperley (2007) : le feedback utile doit repondre a "ou j'en suis" et "quelle est la prochaine etape". Ici : points restants avant le niveau suivant, dernier gain, progression dans le palier.
- Sweller (1988) : si la gamification devient trop visuelle ou trop bavarde, elle augmente la charge cognitive extrinseque. Les composants doivent rester compacts et secondaires par rapport aux exercices.

**Cibles backlog** :
1. **Widget compte stable** sur dashboard/profil :
   - points totaux
   - XP dans le palier courant
   - points restants avant niveau suivant
   - rang/titre courant
2. **Historique recent des gains** (lecture du ledger) :
   - dernieres attributions de points
   - libelle par source
   - date / delta
3. **Repartition par source** :
   - badges
   - defis quotidiens
   - futures sources
4. **Fondation pour suites produit** :
   - F19 : notifications "il te manque X points pour le niveau suivant"
   - F18 : ligues / saisons si un jour ouvertes
   - F29 : elements profil debloquables lies au compte

**Contraintes UX EdTech** :
- pas de gros panneau gamification qui eclipse la progression pedagogique
- pas d'animations decoratives pendant les phases de reflexion
- feedback visuel lisible et localise
- preferer cartes compactes / historique discret a un "mur" de recompenses
- textes explicites : `progression compte`, pas `niveau de maitrise`

**Architecture cible** :
- backend : endpoint de lecture du ledger et agregats par source, branches sur la source de verite persistante existante
- frontend : composants purs + hook de lecture dedie ; aucune formule de points/niveau cote client
- export : ne montrer que les donnees persistantes du compte si l'information est vraiment utile

**Effort estime** : 2-5 jours pour un premier lot lisible (historique + widget compte), plus si agregats / pagination / filtres par source.

**Statut** : Backlog actif. A traiter apres stabilisation du moteur persistant, sans rouvrir la confusion avec l'IRT ou la maitrise pedagogique.

---
## 6. P3 — Investissement long terme {#6-p3}

### F24 — Tuteur IA contextuel

**Score** : 16.1 | D=5, G=5, E=5, R=3, B=5

**Valeur pédagogique (E=5) — parmi les plus fortes en EdTech** :
- VanLehn (2011) — *Educational Psychologist* : Les systèmes de tutoriels intelligents (ITS) atteignent d = 0.55–0.66 par rapport aux classes classiques. Seul le tutorat humain individuel fait mieux (d â‰ˆ 2.0).
- *Scaffolding* cognitif (Wood et al., 1976) : l'aide contextuelle qui s'adapte aux erreurs est plus efficace que les explications génériques.
- Règle critique : **ne pas donner la réponse directement** — guider par questions socratiques.

**Différence vs chatbot actuel** : Le chatbot actuel est générique. Un tuteur IA contextuel connaît l'exercice en cours, le niveau de l'utilisateur et l'historique d'erreurs sur ce type de problème.

**Effort estimé** : 2-4 semaines (intégration LLM contextuel + design pédagogique)

---

### F25 — Mode classe / enseignant

**Score** : 14.9 | D=5, G=4, E=4, R=3, B=5

**Valeur pédagogique (E=4)** : L'enseignant médiateur amplifie les effets de la plateforme (Hattie, d = 0.45 pour *teacher-student relationships*). L'assignation ciblée d'exercices + les rapports par classe sont des outils pédagogiques à fort impact.

**Architecture requise** : Table `classes`, `class_memberships`, `assignments`, routes `/teacher/`. Intégration d'export CSV (déjà partiellement disponible).

**Effort estimé** : 3-6 semaines

---

### F26 — Filtres et tri badges

**Statut** : [DONE] present dans le code au 23/03/2026

Amelioration ergonomique de la page `/badges`, aujourd'hui reellement en place :
- filtres par statut, categorie et difficulte
- vue "proches" pour les badges presque debloques
- tri par progression, date, points et categorie
- reset des filtres depuis la page

**Verite terrain** :
- `frontend/app/badges/page.tsx`
- `frontend/components/badges/BadgeGrid.tsx`

La feature reste documentee ici pour garder visible le travail deja livre, meme si elle n'est plus un backlog actif.

---

### F27 — Optimisation re-renders exercices/défis

Flash visible avant stabilisation des pages. Pistes : `placeholderData` TanStack Query, `useMemo` sur les params de query. ~3-5 jours (profiling + corrections).

---

## 7. P4 — Backlog distant {#7-p4}

### F28 — Mode aventure / histoire narrative

**Score** : 13.1 | D=5, G=5, E=3, R=3, B=5

**Valeur pédagogique (E=3)** :
- Situated learning (Lave & Wenger, 1991) : les maths contextualisées dans une narration réelle améliorent le transfert des connaissances.
- Mais : l'effet de la gamification narrative sur les résultats académiques est modéré et conditionnel (Mayer, 2019 — *Computer games don't improve learning*).

**Concept** : Progression narrative où les maths servent l'histoire ("Le vaisseau a besoin de 150 unités de carburant, tu as 3 réservoirs de 45 chacun..."). Récompenses débloquant la suite.

**Effort estimé** : 4-8 semaines (design narratif + nouveau type de contenu)

---

### F29 — Personnalisation avatar / profil

**Score** : 7.1 | D=3, G=3, E=1, R=1, B=2

Avatars, titres, cadres de profil débloquables avec les points. Donne de la valeur aux points gagnés. Score EdTech=1 : pas de bénéfice pédagogique documenté.

---

### F34 — Module Sciences — Curiosités scientifiques (Labo des Sciences)

**Score** : 10.4 | D=3, G=4, E=2, R=2, B=4

**Philosophie** :
1. **Zéro punition** : Si l'élève clique sur "Faux" (alors que c'est Vrai), pas de croix rouge agressive. Icône ampoule bleue douce + texte « Et non, c'est pourtant vrai ! ». Objectif : apprendre un fait amusant, pas évaluer.
2. **Explication gratifiante** : L'explication apparaît dans un encart en dessous, sans quitter la page (pas de pop-up ou changement d'écran brutal).
3. **Format rapide** : Format "TikTok/Shorts" appliqué à l'éducation. L'élève enchaîne ~10 anecdotes scientifiques en 3 minutes, gagne de l'XP sans impression de "travailler".

**Contenu** :
- Affirmation scientifique (ex. « Le Soleil pourrait contenir environ un million de Terres »)
- Boutons Vrai / Faux
- Réponse correcte : icône check verte, « Exactement ! +X XP »
- Réponse incorrecte : icône ampoule bleue, « Et non, c'est pourtant vrai ! » (ou « Et oui, c'est bien faux ! » selon le cas)
- Encart explicatif avec fait détaillé + bouton « Fait suivant »

**Technique** :
- Nouveau type de contenu (table `science_facts` ou extension `challenges` avec `challenge_type=science`)
- Catégories : Astronomie, Biologie, Physique, Chimie, etc.
- Badge catégorie, compteur série, XP par fait
- Design : glassmorphism, thème sombre cohérent Mathakine

**Prototype** : [../assets/prototypes/F34_SCIENCES_PROTOTYPE.html](../assets/prototypes/F34_SCIENCES_PROTOTYPE.html) — HTML statique (Tailwind, Font Awesome, JS vanilla). À intégrer en Next.js + API.

**Effort estimé** : 1–2 semaines (modèle + API + page `/sciences` + intégration design system)

---

## 8. Features implementees (historique) {#8-features-implementees}

### 8.1 Features livrees et visibles

| Feature | Date / borne de verite | Reference |
|---------|------------------------|-----------|
| F01 - Rendu Markdown/KaTeX dans les explications | Present dans le code au 23/03/2026 | Composant `MathText.tsx` - integre dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver` |
| F02 - Defis quotidiens (daily challenges) | 03/2026 | [F02_DEFIS_QUOTIDIENS](F02_DEFIS_QUOTIDIENS.md) |
| F03 - Test de diagnostic initial (IRT adaptatif) | 04/03/2026 | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section F03 |
| F05 - Adaptation dynamique de difficulte | 06/03/2026 | [F05_ADAPTATION_DYNAMIQUE](F05_ADAPTATION_DYNAMIQUE.md) |
| F06 - Conditions d'obtention badges visibles | Present dans le code au 23/03/2026 | `frontend/components/badges/BadgeCard.tsx` |
| F07 - Courbe d'evolution temporelle (7j/30j) | 07/03/2026 | [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md) |
| F12 - Radar chart par discipline | Present dans le code au 23/03/2026 | `frontend/components/dashboard/CategoryAccuracyChart.tsx` |
| F13 - Deblocage automatique badges temps reel | Present dans le code au 23/03/2026 | `exercise_attempt_service.py`, `challenge_attempt_service.py` |
| F22 - Suppression utilisateur admin (RGPD) | Present dans le code au 23/03/2026 | `DELETE /api/admin/users/{id}` + suppression physique avec cascade |
| F26 - Filtres et tri badges | Present dans le code au 23/03/2026 | `frontend/app/badges/page.tsx` + `frontend/components/badges/BadgeGrid.tsx` |
| F32 - Session entrelacee (interleaving) | 07-08/03/2026 | [IMPLEMENTATION_F32_SESSION_ENTRELACEE](../03-PROJECT/IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) |
| F33 - Feedback Growth Mindset (copywriting + micro-UI) | 07/03/2026 | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section F33 |
| F35 - Redaction secrets logs DB (securite) | 07/03/2026 | [IMPLEMENTATION_F35_REDACTION_LOGS_DB](../03-PROJECT/IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) |
| Espace admin complet (role archiviste) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Auth complet (inscription, email, login, reset) | Jan-Fev 2026 | [AUTH_FLOW](AUTH_FLOW.md) |
| Sessions actives + revocation | 16/02/2026 | SITUATION_FEATURES (archive) |
| Leaderboard (top 50, enrichissement avatar / série / badges) | 25/03/2026 | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) |
| Badges - refonte UX (onglets, cartes compactes) | 17/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges - barres de progression (goal-gradient) | 16/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges - B4 reformulation (17 badges) | 17/02/2026 | Archive : AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES |
| Badges - moteur generique Lot C (defis, mixte) | 17/02/2026 | Archive : AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES |
| Quick Win #1 - First Exercise < 90s | Fev 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Quick Win #2 - Onboarding pedagogique | Fev 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Calibration a l'inscription (classe, age, objectif) | Fev 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Parcours guide (QuickStartActions dashboard) | Fev 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Recommandations personnalisees (marquer fait) | 16/02/2026, MAJ 24/03/2026 | SITUATION_FEATURES (archive) + dashboard `Recommendations.tsx` borne maintenant l'affichage initial a 6 cartes avec toggle local |
| Ordre aleatoire + masquer reussis | 19/02/2026 | SITUATION_FEATURES (archive) |
| Analytics EdTech (CTR Quick Start, 1er attempt) | 25/02/2026 | [EDTECH_ANALYTICS](EDTECH_ANALYTICS.md) |
| Monitoring IA (in-memory) | 22/02/2026 | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section 4.6 |
| Mode maintenance + inscriptions (admin config) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Streak (basique) | Fev 2026 | Integre dans stats utilisateur |
| 7 themes visuels | Fev 2026 | [THEMES](THEMES.md) |
| PWA (mode hors-ligne partiel) | Fev 2026 | - |
| Internationalisation FR/EN | Jan 2026 | [I18N](I18N.md) |
| Accessibilite (5 modes WCAG AAA) | Fev-Mars 2026 | [ACCESSIBILITY](../04-FRONTEND/ACCESSIBILITY.md) |

### 8.2 Fondations techniques deja posees mais encore incompletes cote produit

| Feature | Borne de verite | Ce qui existe deja | Ce qui reste a livrer |
|---------|-----------------|--------------------|-----------------------|
| **F40 — Leaderboard position utilisateur hors top 50** | Planifié 25/03/2026 | Classement top 50 + `is_current_user` flag sur chaque entrée. | Nouvel endpoint `GET /api/users/me/rank` (COUNT query) + injection rang courant en bas de liste avec séparateur visuel. Effort S. **Aucun prérequis — livrable après L2 sans F42.** F42 est prérequis de F40-v2 (rang filtré par groupe d'âge) uniquement. |
| **F41 — Leaderboard filtre temporel** | Planifié 25/03/2026 | Table `point_events` opérationnelle + index `ix_point_events_user_created (user_id, created_at)` déjà en place (migration 20260321). `apply_points` déjà branché sur exercices standard (`exercise_attempt_service.py` l.127). | Query agrégée sur `point_events` par fenêtre (`period=week\|month\|all`) + sélecteur frontend. Effort M. **Pas de blocage technique.** Condition de déploiement : vérifier volume `point_events` en prod avant activation (classement vide = mauvaise UX). |
| **F42 — Architecture difficulté/âge — séparation des deux axes** | Planifié 25/03/2026 (voir section 8.3 ci-dessous) | `preferred_difficulty` sur `User` ; `age_group` sur `Exercise` et `LogicChallenge`. | Phase 1 : colonne `age_group` sur `User` + backfill conditionnel batché (voir §8.3). Phase 2 : `difficulty_tier` 1-12 + double-lecture dans recommandations. Libellés pédagogiques réservés au dashboard parent (RGPD mineurs). |
| **Leaderboard — filtre par groupe d'âge (utilisateur)** | Report 25/03/2026 (lot L1) | Le classement expose `limit` et des champs enrichis ; le paramètre `age_group` a été **retiré** car il filtrait à tort sur `preferred_difficulty` (difficulté easy/medium/hard ≠ tranche d'âge). | Dépend de F42 Phase 1 (colonne `age_group` sur `User`) puis F40. |
| F14 - Monitoring IA persistance DB | Code au 23/03/2026 | monitoring runtime, admin `/admin/ai-monitoring`, token tracker, generation metrics, persistance des runs harness | persistance DB complete des metriques runtime live |
| F38 - Progression gamification compte coherente & historique des gains | Code au 23/03/2026 | `point_events`, `GamificationService.apply_points`, calcul niveau/XP/rang, surfaces `/api/users/me`, `/api/badges/stats`, `/api/badges/user`, `/api/users/leaderboard` | historique utilisateur dedie, agregats par source, UX compte lisible |

### 8.3 Décision d'architecture — Séparation des axes difficulté et groupe d'âge (F42)

**Origine** : découverte lors du lot Leaderboard L1 (25/03/2026). Le filtre `age_group`
du classement filtrait sur `User.preferred_difficulty` — deux concepts distincts traités
comme un seul, provoquant des résultats incohérents.

#### Problème actuel

Le profil utilisateur possède :
- `grade_level : Integer` — niveau scolaire (ex : CM1 = 4)
- `preferred_difficulty : String` — préférence de difficulté (`easy` / `medium` / `hard`)

Le contenu (exercices, défis) possède :
- `age_group : String` — tranche d'âge cible (`6-8` / `9-11` / `12-14` / `15+`)
- `difficulty : String` — dérivé de `age_group` par correspondance implicite

Ces deux axes sont **orthogonaux** : un exercice difficile pour 6-8 ans reste probablement
plus simple qu'un exercice facile pour 12-14 ans. Les mélanger biaise les recommandations,
fausse les comparaisons de classement et rend les progrès peu lisibles.

#### Matrice cible

```
                  | Découverte | Apprentissage | Consolidation
------------------|------------|---------------|---------------
Explorateurs 6-8  |     1      |       2       |       3
Navigateurs 9-11  |     4      |       5       |       6
Pilotes 12-14     |     7      |       8       |       9
Commandants 15+   |    10      |      11       |      12
```

Les libellés de groupe (`Explorateurs`, `Navigateurs`, `Pilotes`, `Commandants`) sont des
repères de communication — neutres, évolutifs, sans référence à une franchise particulière.
Les libellés de difficulté (`Découverte`, `Apprentissage`, `Consolidation`) remplacent
`easy/medium/hard` dans les surfaces utilisateur sans casser les valeurs DB existantes.

#### Plan de migration (deux phases indépendantes)

> **Note séquençage (débat 25/03/2026)** : F42 Phase 1 n'est PAS un prérequis de F40 (rang global).
> F42 Phase 1 est prérequis de F40-v2 (rang filtré par groupe d'âge). F40 livrable avant F42.

**Phase 1 — Colonne `age_group` sur `User`** (effort S)

```sql
ALTER TABLE users ADD COLUMN age_group VARCHAR(10);
-- Backfill conditionnel (batché par tranches de 500 pour éviter lock en prod multi-worker) :
UPDATE users SET age_group = CASE
  WHEN grade_system = 'suisse' THEN NULL   -- numérotation différente, traitement manuel
  WHEN grade_level BETWEEN 1 AND 3 THEN '6-8'
  WHEN grade_level BETWEEN 4 AND 6 THEN '9-11'
  WHEN grade_level BETWEEN 7 AND 9 THEN '12-14'
  WHEN grade_level >= 10 THEN '15+'        -- pas de borne haute
  ELSE NULL
END WHERE age_group IS NULL;
-- NULL → NULL acceptable ; à compléter via formulaire de profil
```

Audit obligatoire lors de Phase 1 : schémas Pydantic `UserResponse`/`UserPublic`
→ ajouter `age_group: Optional[str]` pour éviter validation error si `extra="forbid"`.

Débloque : filtre classement par groupe (F40-v2), recommandations précises, comparaisons équitables.

**Phase 2 — Champ `difficulty_tier` sur le contenu** (effort M, dépend de Phase 1)

```python
# Sur Exercise et LogicChallenge
difficulty_tier = Column(Integer)  # 1 à 12 (voir matrice ci-dessus)
# Calculé et stocké à la création/mise à jour :
# tier = (age_group_index * 3) + difficulty_index
```

Pattern double-lecture **imposé** dans `build_recommendation_user_context` lors de Phase 2 :
```python
# Zéro régression pour les utilisateurs avec age_group = NULL
age_group = user.age_group or _grade_to_age_group(user.grade_level)
```

Débloque : algorithmes de progression lisibles, adaptation fine du tuteur IA (F24),
révisions espacées calibrées (F04).

#### Libellés — périmètre d'exposition

Les libellés pédagogiques (Explorateurs 6-8, Navigateurs 9-11, Pilotes 12-14, Étoiles 15+)
**révèlent indirectement l'âge de l'enfant**. Sur une plateforme B2C mineurs :

- ✅ **Dashboard parent/enseignant** (couche payante) — contexte sécurisé, approprié
- ❌ **Classement public** — exposition de l'âge à d'autres joueurs, non conforme RGPD mineurs

Dans le classement public : conserver uniquement les rangs de progression (F39 à traiter).
"Commandants" écarté (connotation militaire) → remplacé par "Étoiles" pour 15+.

#### Ce qui ne change pas

- Les valeurs DB `age_group` sur le contenu (`"6-8"`, `"9-11"`, …) — inchangées
- Les valeurs DB `preferred_difficulty` sur `User` (`"easy"`, `"medium"`, `"hard"`) — conservées
- Le contrat API existant — backward-compatible (ajout de champs, pas de suppression)

---

## 9. Références scientifiques {#9-références-scientifiques}

| # | Référence | Pertinence |
|---|-----------|------------|
| 1 | Hattie, J. (2009). *Visible Learning*. Routledge. | Méta-analyse de référence — effets sur l'apprentissage |
| 2 | Cepeda, N.J. et al. (2006). Distributed practice in verbal recall tasks. *Psychological Bulletin*, 132(3). | Fondement révisions espacées (F04) |
| 3 | Hattie, J. & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1). | Fondement feedback enrichi (F01) |
| 4 | VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4). | Fondement tuteur IA (F24) |
| 5 | Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12(2). | Fondement charge cognitive, mise en forme (F01, F03) |
| 6 | Vygotsky, L.S. (1978). *Mind in Society*. Harvard University Press. | Fondement ZPD, adaptation difficulté (F05) |
| 7 | Bjork, R.A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), *Metacognition*. | Fondement desirable difficulties, mode focus (F05, F10) |
| 8 | Mayer, R.E. (2001). *Multimedia Learning*. Cambridge University Press. | Fondement rendu Markdown/KaTeX (F01) |
| 9 | Deci, E.L. & Ryan, R.M. (2000). The 'what' and 'why' of goal pursuits. *Psychological Inquiry*, 11(4). | Fondement SDT, défis optionnels (F02, F08) |
| 10 | Kivetz, R. et al. (2006). The goal-gradient hypothesis resurrected. *Journal of Marketing Research*, 43(1). | Fondement conditions badges visibles (F06) |
| 11 | Black, P. & Wiliam, D. (1998). Assessment and classroom learning. *Assessment in Education*, 5(1). | Fondement diagnostic initial (F03) |
| 12 | Locke, E.A. & Latham, G.P. (1990). *A Theory of Goal Setting and Task Performance*. Prentice Hall. | Fondement objectifs personnalisés (F08) |
| 13 | Lave, J. & Wenger, E. (1991). *Situated Learning*. Cambridge University Press. | Fondement mode aventure (F28) |
| 14 | Zimmerman, B.J. (2002). Becoming a self-regulated learner. *Theory into Practice*, 41(2). | Fondement métacognition, graphiques progression (F07, F12) |
| 15 | Kornell, N. & Bjork, R.A. (2008). Learning concepts and categories. *Psychological Science*, 19(6). | Fondement révisions espacées + interleaving (F04, F32) |
| 16 | Chase, C. et al. (2009). Teachable agents and the protégé effect. *Journal of Science Education and Technology*, 18(4). | Fondement Effet Protégé (F30) |
| 17 | Rohrer, D. & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*, 35(6). | Fondement Pratique Entrelacée (F32) |
| 18 | Sweller, J. & Cooper, G.A. (1985). The use of worked examples as a substitute for problem solving. *Cognition and Instruction*, 2(1). | Fondement Fading Effect, exemples résolus (F31) |
| 19 | Renkl, A. (1997). Learning from worked-out examples. *American Educational Research Journal*, 34(3). | Fondement fading progressif (F31) |
| 20 | Dweck, C.S. (2006). *Mindset: The New Psychology of Success*. Random House. | Fondement Growth Mindset, feedback d'erreur (F33) |
| 21 | Yeager, D.S. et al. (2019). A national experiment reveals where a growth mindset improves achievement. *Nature*, 573. | Fondement Growth Mindset appliqué aux maths (F33) |

---

## Documents liés

| Sujet | Document |
|-------|----------|
| Carte du dossier features | [README.md](README.md) |
| Spécifications graphiques analytics | [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md) |
| Fondements psychologiques badges | [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md) |
| Workflow utilisateur complet | [WORKFLOW_EDUCATION_REFACTORING.md](WORKFLOW_EDUCATION_REFACTORING.md) |
| Normalisation difficulté | [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md) |
| Auth flow | [AUTH_FLOW.md](AUTH_FLOW.md) |
| Admin (périmètre, sécurité) | [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md), [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) |
| Analytics EdTech (implémenté) | [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md) |
| Endpoints API | [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) |
| Thèmes visuels | [THEMES.md](THEMES.md) |
| Internationalisation | [I18N.md](I18N.md) |
| Badges implémentés (archive) | [AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md) |



