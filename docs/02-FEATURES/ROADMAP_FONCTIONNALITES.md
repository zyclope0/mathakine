# Backlog & Priorisation des Features — Mathakine

> **Document vivant** — Dernière MAJ : 04/03/2026 (F01 ✅ + F03 ✅ confirmés)  
> **Rôle** : Source de vérité unique pour toutes les features à implémenter.  
> **Cible** : Enfants 5-20 ans + Parents. Contexte : plateforme EdTech maths adaptative.

---

## Table des matières

1. [Méthodologie de priorisation](#1-méthodologie-de-priorisation)
2. [Matrice synthèse — Toutes les features](#2-matrice-synthèse)
3. [P0 — Impact fort, fondements pédagogiques solides](#3-p0)
4. [P1 — Haute priorité](#4-p1) *(dont F30, F31, F32, F33 — nouvelles)*
5. [P2 — Priorité moyenne](#5-p2)
6. [P3 — Investissement long terme](#6-p3)
7. [P4 — Backlog distant](#7-p4)
8. [Features implémentées (historique)](#8-features-implémentées)
9. [Références scientifiques](#9-références-scientifiques)

---

## 1. Méthodologie de priorisation

### 1.1 Axes d'évaluation (1–5)

| Axe | Description | 1 | 5 |
|-----|-------------|---|---|
| **D** — Difficulté | Effort d'implémentation estimé | ½ jour | 2+ semaines |
| **G** — Gain utilisateur | Impact direct sur l'engagement et la satisfaction | Négligeable | Transformateur |
| **E** — EdTech | Valeur pédagogique scientifiquement documentée (voir §1.2) | Cosmétique | Effet fort > 0.6d |
| **R** — Risque | Risque technique ou de régression | Aucun | Critique |
| **B** — Business | Rétention / acquisition / différenciation marché | Nul | Décisif |

### 1.2 Échelle EdTech — Base scientifique

L'axe EdTech est **le seul à être évalué à partir de données factuelles**, pas d'intuitions produit.

| Score | Signification | Critère |
|-------|--------------|---------|
| **5** | Preuve très forte | Méta-analyse, effet mesuré d ≥ 0.6 (Cohen), répliqué dans plusieurs populations |
| **4** | Preuve forte | Effet mesuré d = 0.4–0.6, ou consensus dans la littérature EdTech peer-reviewed |
| **3** | Preuve modérée | Bénéfice documenté mais conditionnel, population spécifique ou effet indirect |
| **2** | Preuve faible | Engagement documenté, mais impact sur l'apprentissage mixte ou non mesuré |
| **1** | Pas de preuve | Principalement cosmétique, spéculatif ou motivation extrinsèque non corroborée |

**Références de base utilisées pour le scoring** :
- Hattie (2009) — *Visible Learning* : méta-analyse de 800+ méta-analyses (>50 000 études)
- Cepeda et al. (2006) — Pratique distribuée et espacée — *Psychological Bulletin*
- Hattie & Timperley (2007) — Pouvoir du feedback — *Review of Educational Research*
- VanLehn (2011) — Tuteurs IA vs tuteurs humains — *Educational Psychologist*
- Bjork (1994) — Desirable difficulties in learning
- Sweller (1988) — Théorie de la charge cognitive — *Cognitive Science*
- Deci & Ryan (2000) — Théorie de l'autodétermination (SDT)
- Mayer (2001) — Multimedia learning theory
- Kivetz et al. (2006) — Goal-gradient hypothesis — *Journal of Marketing Research*

> **Convention** : `[PROPOSITION]` = feature suggérée par l'IA, non issue des docs existants. À valider produit avant implémentation.

### 1.3 Formule de score composite

```
Score = (G × 1.5) + (E × 2) + B − (D × 0.8) − (R × 0.7)
```

Un score élevé indique une feature à haute valeur et faible coût/risque. Le score **ne remplace pas** le jugement — il oriente la discussion.

---

## 2. Matrice synthèse

*Toutes les features en backlog. Légende : D=Difficulté, G=Gain, E=EdTech, R=Risque, B=Business.*

| # | Feature | D | G | E | R | B | Score | Priorité |
|---|---------|---|---|---|---|---|-------|----------|
| F01 | Rendu Markdown/KaTeX explications ✅ | 2 | 4 | 5 | 1 | 3 | **16.8** | P0 |
| F02 | Défis quotidiens (défi du jour) | 3 | 5 | 4 | 2 | 5 | **16.9** | P0 |
| F03 | Test de diagnostic initial ✅ | 3 | 4 | 5 | 2 | 4 | **16.0** | P0 |
| F04 | Révisions espacées (SM-2) | 4 | 4 | 5 | 2 | 4 | **14.8** | P0 |
| F30 | [PROP] Effet Protégé (corriger erreur IA) | 4 | 4 | 5 | 2 | 4 | **15.4** | P1 |
| F31 | [PROP] Exemples résolus progressifs (Fading) | 3 | 4 | 5 | 2 | 3 | **15.2** | P1 |
| F32 | [PROP] Mode Pratique Entrelacée (Interleaving) | 2 | 3 | 5 | 2 | 3 | **14.5** | P1 |
| F05 | Adaptation dynamique de difficulté | 4 | 4 | 5 | 3 | 4 | **13.9** | P1 |
| F06 | Conditions d'obtention badges visibles | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F07 | Courbe d'évolution temporelle | 3 | 4 | 3 | 2 | 3 | **11.2** | P1 |
| F08 | Objectifs personnalisés | 3 | 3 | 3 | 1 | 3 | **11.1** | P1 |
| F09 | Dashboard parent | 4 | 4 | 3 | 2 | 5 | **11.4** | P1 |
| F10 | [PROP] Mode focus / session ciblée | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F11 | [PROP] Partage progression → parents (lien) | 2 | 3 | 3 | 1 | 4 | **12.5** | P1 |
| F12 | Radar chart par discipline | 2 | 3 | 3 | 1 | 2 | **10.9** | P1 |
| F13 | Déblocage automatique badges temps réel | 2 | 3 | 3 | 1 | 3 | **11.5** | P1 |
| F33 | [PROP] Feedback Growth Mindset (copywriting) | 1 | 3 | 3 | 1 | 2 | **11.4** | P1 |
| F14 | Monitoring IA — persistance DB | 2 | 2 | 1 | 1 | 3 | **6.9** | P2 |
| F15 | Préférence page d'accueil (connexion) | 1 | 2 | 1 | 1 | 1 | **5.7** | P2 |
| F16 | Heatmap d'activité | 3 | 3 | 2 | 1 | 3 | **9.1** | P2 |
| F17 | Célébrations visuelles améliorées | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F18 | Ligues hebdomadaires (upgrade leaderboard) | 4 | 4 | 1 | 2 | 4 | **8.9** | P2 |
| F19 | Notifications push + email | 4 | 3 | 2 | 2 | 4 | **8.1** | P2 |
| F20 | Normalisation niveaux de difficulté | 4 | 3 | 2 | 3 | 3 | **6.9** | P2 |
| F21 | Badges secrets | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F22 | Suppression utilisateur admin (RGPD) | 2 | 1 | 1 | 2 | 3 | **4.7** | P2 |
| F23 | [PROP] Exercices adaptatifs SR+IA | 4 | 5 | 5 | 3 | 5 | **17.1** | P2* |
| F24 | Tuteur IA contextuel | 5 | 5 | 5 | 3 | 5 | **16.1** | P3 |
| F25 | Mode classe / enseignant | 5 | 4 | 4 | 3 | 5 | **14.9** | P3 |
| F26 | Filtres et tri badges | 2 | 2 | 1 | 1 | 2 | **6.4** | P3 |
| F27 | Optimisation re-renders exercices/défis | 3 | 2 | 1 | 2 | 2 | **4.8** | P3 |
| F28 | Mode aventure / histoire narrative | 5 | 5 | 3 | 3 | 5 | **13.1** | P4 |
| F29 | Personnalisation avatar / profil | 3 | 3 | 1 | 1 | 2 | **7.1** | P4 |

> *F23 a un score élevé mais dépend de F04 (révisions espacées) — débloqué après F04.*

---

## 3. P0 — Impact fort, fondements pédagogiques solides {#3-p0}

Ces quatre features combinent un score composite élevé ET un bénéfice pédagogique scientifiquement robuste. Elles constituent le cœur de la valeur éducative de Mathakine.

---

### F01 — Rendu Markdown/KaTeX dans les explications

**Source** : [ROADMAP §4.7](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.8 | D=2, G=4, E=5, R=1, B=3

**Problème** : Les explications post-réponse (exercices et défis) sont du texte brut. Les formules mathématiques (`a³+b³`) et les étapes structurées sont illisibles.

**Valeur pédagogique (E=5)** :
- Mayer (2001) — *Multimedia Learning* : la segmentation et la mise en forme du texte réduit la charge cognitive extrinsèque et améliore la compréhension (effet mesuré).
- Sweller (1988) — Cognitive Load Theory : l'organisation visuelle de l'information réduit la charge cognitive irrélevante.
- La lisibilité de l'explication est un vecteur direct du transfert d'apprentissage.

**Ce qu'il faut faire** :
- Intégrer `react-markdown` + `remark-math` + `rehype-katex` (ou `react-katex`) dans `ExerciseSolver` et `ChallengeSolver`
- Appliquer le rendu dans le bloc "Explication" de la réponse
- Style CSS pour les formules math (KaTeX CSS)
- Optionnel : accordéon "voir plus" si explication > 300 mots

**Effort estimé** : 1-2 jours

**Statut** : ✅ Implémenté — composant `frontend/components/ui/MathText.tsx` (react-markdown + remark-math + rehype-katex), intégré dans `ExerciseSolver`, `ChallengeSolver` et `DiagnosticSolver`

---

### F02 — Défis quotidiens (défi du jour)

**Source** : [ROADMAP §3.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.9 | D=3, G=5, E=4, R=2, B=5

**Problème** : Aucun mécanisme de retour quotidien motivé. L'utilisateur n'a pas de raison intrinsèque de revenir chaque jour.

**Valeur pédagogique (E=4)** :
- Cepeda et al. (2006) — La pratique distribuée (daily sessions) produit une meilleure rétention que la pratique massée, indépendamment du temps total (d = 0.46-0.71).
- Deci & Ryan (2000) — SDT : les défis quotidiens optionnels, adaptés au niveau, soutiennent le besoin de compétence sans pression externe (contrairement aux streaks punitifs).
- **Attention** : Un défi quotidien obligatoire ou punitif peut créer du FOMO négatif. La conception doit préserver l'autonomie (pas de punition si manqué).

**Conception recommandée** :

| Élément | Recommandation |
|---------|----------------|
| Nombre | 3 défis par jour (pas plus) |
| Difficulté | Adaptée au profil utilisateur (onboarding + historique) |
| Récompense | Points bonus + progression vers badge |
| Expiration | Fin de journée (minuit), pas de pression multi-jours |
| Comportement si manqué | Aucune perte, aucun streak cassé — simple reset |

**Modèle de données** :
```sql
daily_challenges (
  id, user_id, date DATE, challenge_type,
  target_count INT, completed_count INT,
  status ENUM('pending', 'completed', 'expired'),
  bonus_points INT, created_at, completed_at
)
```

**Effort estimé** : 3-5 jours (backend + frontend)

---

### F03 — Test de diagnostic initial

**Source** : [ROADMAP §3.5](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.0 | D=3, G=4, E=5, R=2, B=4

**Problème** : L'onboarding collecte les préférences (classe, âge, rythme) mais pas le niveau réel. Les premières recommandations peuvent être inadaptées, dégradant le moment critique des 5 premières minutes.

**Valeur pédagogique (E=5)** :
- Hattie (2009) — *Formative assessment* : d = 0.90 (un des effets les plus élevés en éducation). Identifier le niveau réel avant l'enseignement est la condition préalable à toute personnalisation efficace.
- Sweller (1988) — L'alignement entre difficulté et compétence prévient la surcharge cognitive (exercices trop faciles = ennui, trop difficiles = anxiété).
- *Assessment for learning* (Black & Wiliam, 1998) : le diagnostic préalable est la fondation de l'apprentissage adaptatif.

**Algorithme adaptatif (Item Response Theory simplifié)** :
```
1. Commencer au niveau médian
2. Correct → question plus difficile (niveau +1)
3. Incorrect → question plus facile (niveau -1)
4. Arrêt : 2 erreurs consécutives au même niveau → niveau établi
5. Durée max : 10 questions, ~5 minutes
```

**Output** :
- `initial_level` par type d'exercice (addition, soustraction, multiplication, division, logique)
- Stocké dans `diagnostic_results` (table dédiée, scores JSONB par type)
- Alimente immédiatement les recommandations

**Effort estimé** : 3-5 jours

**Statut** : ✅ Implémenté le 04/03/2026

**Ce qui est branché** :
- Table `diagnostic_results` (migration `20260304_diagnostic`)
- Service IRT (`app/services/diagnostic_service.py`) : algo adaptatif, 10 questions, 4 types
- Endpoints `/api/diagnostic/status|start|question|answer|complete`
- Page `/diagnostic` (accessible depuis onboarding et Settings)
- Section "Évaluation de niveau" dans Settings (affiche date + niveaux par type)
- Recommandations : `RecommendationService` lit le diagnostic via `get_latest_score()` et affine la difficulté médiane

**Ce qui reste à câbler (backlog F03-suite)** :

| Lacune | Impact | Priorité |
|--------|--------|----------|
| `/api/exercises/generate` ignore le niveau diagnostic | Un utilisateur scorant Initié reçoit des exercices selon `age_group`, pas son niveau réel | Moyen |
| Dashboard (`/`) ne lit pas `has_completed` | Pas de message de confirmation "ton niveau a été établi" | Faible |
| Génération IA (`/api/ai/generate`) ignore le diagnostic | Même problème que le générateur interne | Moyen |

---

### F04 — Révisions espacées (algorithme SM-2)

**Source** : [ROADMAP §3.3](ROADMAP_FONCTIONNALITES.md)  
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
- Suivantes : intervalle × ease_factor

Ajustement ease_factor (EF, init 2.5) :
- Réponse correcte rapide (qualité 4-5) : EF + 0.1
- Réponse correcte lente (qualité 3) : EF inchangé
- Réponse incorrecte (qualité 0-2) : EF − 0.2, retour J+1
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

---

## 4. P1 — Haute priorité {#4-p1}

---

### F05 — Adaptation dynamique de difficulté

**Source** : [WORKFLOW_EDUCATION §2.2](WORKFLOW_EDUCATION_REFACTORING.md)  
**Score** : 13.9 | D=4, G=4, E=5, R=3, B=4

**Valeur pédagogique (E=5)** :
- Vygotsky (1978) — Zone proximale de développement : l'apprentissage optimal se situe juste au-delà de la compétence actuelle. Trop facile → ennui. Trop difficile → anxiété.
- Bjork (1994) — *Desirable difficulties* : un niveau de défi optimal crée une résistance productive (retrieval effort) qui renforce la mémorisation à long terme.
- Csikszentmihalyi (1990) — État de *flow* : atteint quand difficulté ≈ compétence.

**Implémentation** : Basée sur le taux de réussite glissant (7 derniers jours) par type d'exercice. Seuils : > 85% → augmenter difficulté, < 50% → diminuer.

**Dépendance** : Profite du diagnostic initial (F03) et prépare les révisions espacées (F04).

**Effort estimé** : 1-2 semaines

---

### F06 — Conditions d'obtention badges visibles

**Source** : [BADGES_AMELIORATIONS §4.2](BADGES_AMELIORATIONS.md)  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Valeur pédagogique (E=3)** :
- Kivetz et al. (2006) — *Goal-gradient effect* : la motivation augmente à mesure que l'objectif est visible et proche. Effet mesuré +40-60% d'engagement.
- Zimmerman (2002) — Transparence des critères améliore la régulation autonome de l'apprentissage (self-regulation).

**Ce qu'il faut faire** : Afficher les critères (`criteria_description`) sur les badges verrouillés dans `BadgeCard.tsx`. Déjà partiellement préparé dans le backend (`PLAN_REFONTE_BADGES` archivé).

**Effort estimé** : ½-1 jour

---

### F07 — Courbe d'évolution temporelle

**Source** : [ANALYTICS_PROGRESSION §1.1](ANALYTICS_PROGRESSION.md)  
**Score** : 11.2 | D=3, G=4, E=3, R=2, B=3

**Valeur pédagogique (E=3)** :
- Zimmerman & Schunk (2001) — *Self-monitoring* : voir sa progression concrète dans le temps active la métacognition et renforce la motivation intrinsèque.
- Hattie (2009) — *Self-reported grades / metacognitive monitoring* : d = 1.33 (attention : effet de la conscience de sa propre progression, pas du graphique lui-même).

**Endpoint à créer** : `GET /api/users/me/progress/timeline?period=week|month`  
**Données sources** : `Attempt.created_at` + `Attempt.is_correct`

**Effort estimé** : 3-5 jours

---

### F08 — Objectifs personnalisés

**Source** : [ROADMAP §4.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.1 | D=3, G=3, E=3, R=1, B=3

**Valeur pédagogique (E=3)** :
- Deci & Ryan (2000) — SDT : les objectifs auto-déterminés (choisis par l'utilisateur, pas imposés) renforcent la motivation intrinsèque et le besoin d'autonomie.
- Locke & Latham (1990) — *Goal-setting theory* : des objectifs spécifiques et mesurables améliorent la performance. Effet plus fort quand l'objectif est choisi par l'individu.

**Types** : Quotidien (ex: 5 exercices/jour), hebdomadaire, de maîtrise (ex: "atteindre 80% en division").

**Effort estimé** : 3-5 jours

---

### F09 — Dashboard parent

**Source** : [ROADMAP §3.1](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.4 | D=4, G=4, E=3, R=2, B=5

**Valeur pédagogique (E=3)** :
- Hattie (2009) — *Parental involvement* : d = 0.49. L'implication parentale dans le suivi scolaire a un effet positif mesurable sur les résultats.
- Bryk & Schneider (2002) — La confiance famille-institution est un prédicteur de l'engagement à long terme.

**Architecture minimale (MVP)** :
```
Table: parent_child_links (parent_user_id, child_user_id, created_at, permissions JSON)
Route: /parent/dashboard → vue enfants
Route: /parent/child/[id] → progression détaillée
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

### F12 — Radar chart par discipline

**Source** : [ANALYTICS_PROGRESSION §1.3](ANALYTICS_PROGRESSION.md)  
**Score** : 10.9 | D=2, G=3, E=3, R=1, B=2

**Valeur pédagogique (E=3)** : Auto-évaluation et métacognition. Données déjà disponibles dans `/api/exercises/stats` (`by_discipline`). Implémentation rapide avec Recharts `RadarChart`.

**Effort estimé** : ½-1 jour

---

### F13 — Déblocage automatique badges (temps réel)

**Source** : [BADGES_AMELIORATIONS §4.4](BADGES_AMELIORATIONS.md)  
**Score** : 11.5 | D=2, G=3, E=3, R=1, B=3

**Valeur pédagogique (E=3)** :
- Kulik & Kulik (1988) — Feedback immédiat améliore l'apprentissage. S'applique aux récompenses : un badge débloqué 2 jours après l'effort perd son effet de renforcement.

**Ce qu'il faut faire** : Appeler `check_and_award_badges` après chaque tentative (déjà fait pour les défis — étendre aux exercices) et afficher un toast avec l'animation de badge.

**Effort estimé** : ½-1 jour

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

### F32 — [PROPOSITION] Mode "Pratique Entrelacée" (Interleaving)

**Source** : Proposition IA — non issue des docs existants  
**Score** : 14.5 | D=2, G=3, E=5, R=2, B=3

> *Score initial proposé : 15.2 (R=1). Risque révisé à R=2 : le mélange de types d'exercices interagit avec F05 (adaptation dynamique par type) — il faut s'assurer que les niveaux par type sont suffisamment calibrés avant activation.*

**Problème** : Les élèves ont tendance à enchaîner un seul type d'exercice (ex : 10 additions d'affilée — *Blocked Practice*). Le cerveau se met en pilote automatique et n'apprend pas à **choisir la bonne stratégie**, compétence clé en évaluation.

**Valeur pédagogique (E=5)** :
- Rohrer & Taylor (2007) — *Interleaved Practice* : Mélanger les types de problèmes force le cerveau à identifier la stratégie avant de l'appliquer. **Rétention à long terme améliorée de +43%** par rapport à la pratique bloquée.
- Kornell & Bjork (2008) — Effet particulièrement fort en mathématiques : spacing + interleaving combinés produisent les meilleures performances (g = 0.43).
- **Attention** : L'interleaving est contre-intuitif — les élèves ont l'impression d'apprendre moins bien pendant la session (mais retiennent mieux). À accompagner d'une explication pédagogique dans l'UI.

**Ce qu'il faut faire** : Ajouter une Quick Action sur le Dashboard : **"Session Entrelacée (10 min)"**. Le backend sélectionne délibérément des exercices de catégories différentes et de niveaux validés (≥ 60% de réussite sur les 7 derniers jours), forçant le *context switching* cérébral.

**Paramètres de sélection** :
- 3-4 types différents dans une session de 10 exercices
- Seulement les types où l'utilisateur a un historique (pas d'interleaving sur concepts non vus)
- Tooltip dans l'UI : *"Ton cerveau travaille plus fort — c'est normal ! C'est exactement ce qui aide à mémoriser."*

**Effort estimé** : 1-2 jours (endpoint backend avec logique de sélection + bouton frontend)  
**Dépendance faible** : Fonctionne mieux après F05 (niveaux calibrés), mais utilisable dès maintenant sur les niveaux par défaut  
**Priorité** : P1 — quick win fort, effort minimal, impact pédagogique maximal

---

### F33 — [PROPOSITION] Feedback "Growth Mindset"

**Source** : Proposition IA — non issue des docs existants  
**Score** : 11.4 | D=1, G=3, E=3, R=1, B=2

> *Score initial proposé : 13.0 (E=4). EdTech révisé à E=3 : les études Dweck sont robustes mais les interventions de Growth Mindset par texte seul ont des effets faibles sans accompagnement long terme. Yeager et al. (2019) mesure des effets sur populations défavorisées spécifiques — le transfert à une plateforme généraliste est conditionnel.*

**Problème** : Un message "Faux" ou un feedback négatif brutal lors d'un échec peut renforcer un *Fixed Mindset* ("Je suis nul en maths"). Ce biais est particulièrement fort chez les enfants 8-14 ans.

**Valeur pédagogique (E=3)** :
- Dweck (2006) — *Mindset Theory* : Valoriser l'effort et la stratégie plutôt que l'intelligence innée ou le résultat brut améliore la résilience face à l'échec.
- Yeager et al. (2019) : Une simple intervention Growth Mindset a des effets mesurables sur les résultats en maths chez les élèves défavorisés.
- **Nuance** : L'effet est conditionnel et nécessite de la cohérence dans tout le parcours utilisateur — un seul message ne suffit pas.

**Ce qu'il faut faire** (modifications de texte + micro-UI) :

| Avant | Après |
|-------|-------|
| "Mauvaise réponse" | "Pas encore ! La prochaine sera la bonne." |
| "Incorrect" | "Ton cerveau est en train d'apprendre !" |
| Score affiché seulement | Valoriser aussi le **temps passé** sur un défi difficile |
| — | Tooltips de chargement : *"Savais-tu que ton cerveau crée de nouvelles connexions exactement au moment où tu fais une erreur ?"* |

**Contrainte** : Cohérence avec les textes de feedback existants dans `fr.json` / `en.json`. Ne pas sur-positiver au point de perdre la valeur informative du feedback (Hattie & Timperley, 2007 — le feedback doit rester précis).

**Effort estimé** : ½ jour (modifications de texte dans les fichiers i18n + micro-ajustements UI)  
**Priorité** : P1 — quick win absolu, aucun risque technique, impact psychologique documenté

---

## 5. P2 — Priorité moyenne {#5-p2}

| Feature | Note |
|---------|------|
| **F14 — Monitoring IA persistance DB** | Voir [ROADMAP §4.6](ROADMAP_FONCTIONNALITES.md). Table `AiTokenUsage` + `AiGenerationMetric`. Pattern : `edtech_events`. ~1 jour. |
| **F15 — Préférence page d'accueil** | Champ `login_redirect_preference` sur `User`. Option dans Paramètres. ~½ jour. |
| **F16 — Heatmap d'activité** | Calendrier GitHub-style sur Dashboard/Profil. `react-calendar-heatmap`. Endpoint : `GET /api/users/me/activity/heatmap`. |
| **F17 — Célébrations visuelles améliorées** | Confettis au déblocage badge, modal avec partage. Désactivable (accessibilité). |
| **F18 — Ligues hebdomadaires** | Upgrade du leaderboard : groupes de 30, promotion/relégation, reset chaque lundi. Voir [ROADMAP §3.4](ROADMAP_FONCTIONNALITES.md). Score EdTech=1 : engagement, pas d'apprentissage direct. |
| **F19 — Notifications push + email** | Rappel inactivité, streak en danger, badge proche. Voir [ROADMAP §4.1](ROADMAP_FONCTIONNALITES.md). Infrastructure à définir (service push web + SMTP). |
| **F20 — Normalisation niveaux de difficulté** | Remplacer nomenclature Star Wars par libellés universels. Voir [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md). Migration enum risquée — à planifier soigneusement. |
| **F21 — Badges secrets** | Badges cachés débloqués pour comportements inattendus (ex: "Noctambule" après minuit). Variable reward (Skinner) — engagement élevé. |
| **F22 — Suppression utilisateur admin (RGPD)** | `DELETE /api/admin/users/{id}` avec soft delete. Voir PLACEHOLDERS_ET_TODO. Compliance obligatoire avant scale. |
| **F23 — [PROP] Exercices adaptatifs SR+IA** | Générer des exercices IA ciblés sur les concepts à réviser selon la courbe SR (F04). Score composite très élevé (17.1) mais **dépend de F04**. Débloqué après F04. |

---

## 6. P3 — Investissement long terme {#6-p3}

### F24 — Tuteur IA contextuel

**Score** : 16.1 | D=5, G=5, E=5, R=3, B=5

**Valeur pédagogique (E=5) — parmi les plus fortes en EdTech** :
- VanLehn (2011) — *Educational Psychologist* : Les systèmes de tutoriels intelligents (ITS) atteignent d = 0.55–0.66 par rapport aux classes classiques. Seul le tutorat humain individuel fait mieux (d ≈ 2.0).
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

Amélioration ergonomique de la page `/badges`. Par statut, catégorie, difficulté. ~1 jour. Déprioritisé car la page badges est déjà bien structurée (onglets En cours / À débloquer).

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

## 8. Features implémentées (historique) {#8-features-implémentées}

| Feature | Date | Référence |
|---------|------|-----------|
| F01 — Rendu Markdown/KaTeX dans les explications | 2026 | Composant `MathText.tsx` — intégré dans `ExerciseSolver`, `ChallengeSolver`, `DiagnosticSolver` |
| F03 — Test de diagnostic initial (IRT adaptatif) | 04/03/2026 | [ROADMAP_FONCTIONNALITES §F03](ROADMAP_FONCTIONNALITES.md) |
| Espace admin complet (rôle archiviste) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Auth complet (inscription, email, login, reset) | Jan-Fév 2026 | [AUTH_FLOW](AUTH_FLOW.md) |
| Sessions actives + révocation | 16/02/2026 | SITUATION_FEATURES (archivé) |
| Leaderboard (top 50, filtre âge) | 15/02/2026 | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) |
| Badges — refonte UX (onglets, cartes compactes) | 17/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges — barres de progression (goal-gradient) | 16/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges — B4 reformulation (17 badges) | 17/02/2026 | Archivé : AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES |
| Badges — moteur générique Lot C (défis, mixte) | 17/02/2026 | Archivé : AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES |
| Quick Win #1 — First Exercise < 90s | Fév 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Quick Win #2 — Onboarding pédagogique | Fév 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Calibration à l'inscription (classe, âge, objectif) | Fév 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Parcours guidé (QuickStartActions dashboard) | Fév 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Recommandations personnalisées (marquer fait) | 16/02/2026 | SITUATION_FEATURES (archivé) |
| Ordre aléatoire + masquer réussis | 19/02/2026 | SITUATION_FEATURES (archivé) |
| Analytics EdTech (CTR Quick Start, 1er attempt) | 25/02/2026 | [EDTECH_ANALYTICS](EDTECH_ANALYTICS.md) |
| Monitoring IA (in-memory) | 22/02/2026 | [ROADMAP §4.6](ROADMAP_FONCTIONNALITES.md) |
| Mode maintenance + inscriptions (admin config) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Streak (basique) | Fév 2026 | Intégré dans stats utilisateur |
| 7 thèmes visuels | Fév 2026 | [THEMES](THEMES.md) |
| PWA (mode hors-ligne partiel) | Fév 2026 | — |
| Internationalisation FR/EN | Jan 2026 | [I18N](I18N.md) |
| Accessibilité (5 modes WCAG AAA) | Fév-Mars 2026 | [ACCESSIBILITY](../04-FRONTEND/ACCESSIBILITY.md) |

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
