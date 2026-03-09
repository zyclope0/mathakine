# Backlog & Priorisation des Features â€” Mathakine

> **Document vivant** â€” DerniÃ¨re MAJ : 09/03/2026 (F32 durci, F07/F33/F35 alignÃ©s, backlog QCM F05-B2 ajoutÃ©, artefact refresh auth F36 formalisÃ©)  
> **RÃ´le** : Source de vÃ©ritÃ© unique pour toutes les features Ã  implÃ©menter.  
> **Cible** : Enfants 5-20 ans + Parents. Contexte : plateforme EdTech maths adaptative.

---

## Table des matiÃ¨res

1. [MÃ©thodologie de priorisation](#1-mÃ©thodologie-de-priorisation)
2. [Matrice synthÃ¨se â€” Toutes les features](#2-matrice-synthÃ¨se)
3. [P0 â€” Impact fort, fondements pÃ©dagogiques solides](#3-p0)
4. [P1 â€” Haute prioritÃ©](#4-p1) *(dont F30, F31, F32 â€” nouvelles)*
5. [P2 â€” PrioritÃ© moyenne](#5-p2)
6. [P3 â€” Investissement long terme](#6-p3)
7. [P4 â€” Backlog distant](#7-p4)
8. [Features implÃ©mentÃ©es (historique)](#8-features-implÃ©mentÃ©es)
9. [RÃ©fÃ©rences scientifiques](#9-rÃ©fÃ©rences-scientifiques)

---

## 1. MÃ©thodologie de priorisation

### 1.1 Axes d'Ã©valuation (1â€“5)

| Axe | Description | 1 | 5 |
|-----|-------------|---|---|
| **D** â€” DifficultÃ© | Effort d'implÃ©mentation estimÃ© | Â½ jour | 2+ semaines |
| **G** â€” Gain utilisateur | Impact direct sur l'engagement et la satisfaction | NÃ©gligeable | Transformateur |
| **E** â€” EdTech | Valeur pÃ©dagogique scientifiquement documentÃ©e (voir Â§1.2) | CosmÃ©tique | Effet fort > 0.6d |
| **R** â€” Risque | Risque technique ou de rÃ©gression | Aucun | Critique |
| **B** â€” Business | RÃ©tention / acquisition / diffÃ©renciation marchÃ© | Nul | DÃ©cisif |

### 1.2 Ã‰chelle EdTech â€” Base scientifique

L'axe EdTech est **le seul Ã  Ãªtre Ã©valuÃ© Ã  partir de donnÃ©es factuelles**, pas d'intuitions produit.

| Score | Signification | CritÃ¨re |
|-------|--------------|---------|
| **5** | Preuve trÃ¨s forte | MÃ©ta-analyse, effet mesurÃ© d â‰¥ 0.6 (Cohen), rÃ©pliquÃ© dans plusieurs populations |
| **4** | Preuve forte | Effet mesurÃ© d = 0.4â€“0.6, ou consensus dans la littÃ©rature EdTech peer-reviewed |
| **3** | Preuve modÃ©rÃ©e | BÃ©nÃ©fice documentÃ© mais conditionnel, population spÃ©cifique ou effet indirect |
| **2** | Preuve faible | Engagement documentÃ©, mais impact sur l'apprentissage mixte ou non mesurÃ© |
| **1** | Pas de preuve | Principalement cosmÃ©tique, spÃ©culatif ou motivation extrinsÃ¨que non corroborÃ©e |

**RÃ©fÃ©rences de base utilisÃ©es pour le scoring** :
- Hattie (2009) â€” *Visible Learning* : mÃ©ta-analyse de 800+ mÃ©ta-analyses (>50 000 Ã©tudes)
- Cepeda et al. (2006) â€” Pratique distribuÃ©e et espacÃ©e â€” *Psychological Bulletin*
- Hattie & Timperley (2007) â€” Pouvoir du feedback â€” *Review of Educational Research*
- VanLehn (2011) â€” Tuteurs IA vs tuteurs humains â€” *Educational Psychologist*
- Bjork (1994) â€” Desirable difficulties in learning
- Sweller (1988) â€” ThÃ©orie de la charge cognitive â€” *Cognitive Science*
- Deci & Ryan (2000) â€” ThÃ©orie de l'autodÃ©termination (SDT)
- Mayer (2001) â€” Multimedia learning theory
- Kivetz et al. (2006) â€” Goal-gradient hypothesis â€” *Journal of Marketing Research*

> **Convention** : `[PROPOSITION]` = feature suggÃ©rÃ©e par l'IA, non issue des docs existants. Ã€ valider produit avant implÃ©mentation.

### 1.3 Formule de score composite

```
Score = (G Ã— 1.5) + (E Ã— 2) + B âˆ’ (D Ã— 0.8) âˆ’ (R Ã— 0.7)
```

Un score Ã©levÃ© indique une feature Ã  haute valeur et faible coÃ»t/risque. Le score **ne remplace pas** le jugement â€” il oriente la discussion.

---

## 2. Matrice synthÃ¨se

*Toutes les features en backlog. LÃ©gende : D=DifficultÃ©, G=Gain, E=EdTech, R=Risque, B=Business.*

| # | Feature | D | G | E | R | B | Score | PrioritÃ© |
|---|---------|---|---|---|---|---|-------|----------|
| F01 | Rendu Markdown/KaTeX explications âœ… | 2 | 4 | 5 | 1 | 3 | **16.8** | P0 |
| F02 | DÃ©fis quotidiens (dÃ©fi du jour) âœ… | 3 | 5 | 4 | 2 | 5 | **16.9** | P0 |
| F03 | Test de diagnostic initial âœ… | 3 | 4 | 5 | 2 | 4 | **16.0** | P0 |
| F04 | RÃ©visions espacÃ©es (SM-2) | 4 | 4 | 5 | 2 | 4 | **14.8** | P0 |
| F30 | [PROP] Effet ProtÃ©gÃ© (corriger erreur IA) | 4 | 4 | 5 | 2 | 4 | **15.4** | P1 |
| F31 | [PROP] Exemples rÃ©solus progressifs (Fading) | 3 | 4 | 5 | 2 | 3 | **15.2** | P1 |
| F32 | [PROP] Mode Pratique EntrelacÃ©e (Interleaving) âœ… | 2 | 3 | 5 | 2 | 3 | **14.5** | P1 |
| F05 | Adaptation dynamique de difficultÃ© âœ… | 4 | 4 | 5 | 3 | 4 | **13.9** | P1 |
| F06 | Conditions d'obtention badges visibles | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F07 | Courbe d'Ã©volution temporelle âœ… | 3 | 4 | 3 | 2 | 3 | **11.2** | P1 |
| F08 | Objectifs personnalisÃ©s | 3 | 3 | 3 | 1 | 3 | **11.1** | P1 |
| F09 | Dashboard parent | 4 | 4 | 3 | 2 | 5 | **11.4** | P1 |
| F10 | [PROP] Mode focus / session ciblÃ©e | 2 | 4 | 3 | 1 | 3 | **13.5** | P1 |
| F11 | [PROP] Partage progression â†’ parents (lien) | 2 | 3 | 3 | 1 | 4 | **12.5** | P1 |
| F12 | Radar chart par discipline | 2 | 3 | 3 | 1 | 2 | **10.9** | P1 |
| F13 | DÃ©blocage automatique badges temps rÃ©el | 2 | 3 | 3 | 1 | 3 | **11.5** | P1 |
| F33 | Feedback Growth Mindset (copywriting) âœ… | 1 | 3 | 3 | 1 | 2 | **11.4** | P1 |
| F14 | Monitoring IA â€” persistance DB | 2 | 2 | 1 | 1 | 3 | **6.9** | P2 |
| F15 | PrÃ©fÃ©rence page d'accueil (connexion) | 1 | 2 | 1 | 1 | 1 | **5.7** | P2 |
| F16 | Heatmap d'activitÃ© | 3 | 3 | 2 | 1 | 3 | **9.1** | P2 |
| F17 | CÃ©lÃ©brations visuelles amÃ©liorÃ©es | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F18 | Ligues hebdomadaires (upgrade leaderboard) | 4 | 4 | 1 | 2 | 4 | **8.9** | P2 |
| F19 | Notifications push + email | 4 | 3 | 2 | 2 | 4 | **8.1** | P2 |
| F20 | Normalisation niveaux de difficultÃ© | 4 | 3 | 2 | 3 | 3 | **6.9** | P2 |
| F21 | Badges secrets | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F22 | Suppression utilisateur admin (RGPD) | 2 | 1 | 1 | 2 | 3 | **4.7** | P2 |
| F35 | [TECH] Redaction secrets dans logs DB (URL SQLAlchemy) âœ… | 1 | 2 | 1 | 1 | 4 | **7.5** | P2 |
| F36 | [UX][TECH] Flash auth au refresh | 2 | 2 | 1 | 1 | 3 | **7.2** | P2 |
| F23 | [PROP] Exercices adaptatifs SR+IA | 4 | 5 | 5 | 3 | 5 | **17.1** | P2* |
| F24 | Tuteur IA contextuel | 5 | 5 | 5 | 3 | 5 | **16.1** | P3 |
| F25 | Mode classe / enseignant | 5 | 4 | 4 | 3 | 5 | **14.9** | P3 |
| F26 | Filtres et tri badges | 2 | 2 | 1 | 1 | 2 | **6.4** | P3 |
| F27 | Optimisation re-renders exercices/dÃ©fis | 3 | 2 | 1 | 2 | 2 | **4.8** | P3 |
| F28 | Mode aventure / histoire narrative | 5 | 5 | 3 | 3 | 5 | **13.1** | P4 |
| F29 | Personnalisation avatar / profil | 3 | 3 | 1 | 1 | 2 | **7.1** | P4 |
| F34 | Module Sciences â€” CuriositÃ©s (Vrai/Faux, format court) | 3 | 4 | 2 | 2 | 4 | **10.4** | P4 |

> *F23 a un score Ã©levÃ© mais dÃ©pend de F04 (rÃ©visions espacÃ©es) â€” dÃ©bloquÃ© aprÃ¨s F04.*

---

## 3. P0 â€” Impact fort, fondements pÃ©dagogiques solides {#3-p0}

Ces quatre features combinent un score composite Ã©levÃ© ET un bÃ©nÃ©fice pÃ©dagogique scientifiquement robuste. Elles constituent le cÅ“ur de la valeur Ã©ducative de Mathakine.

---

### F01 â€” Rendu Markdown/KaTeX dans les explications

**Source** : [ROADMAP Â§4.7](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.8 | D=2, G=4, E=5, R=1, B=3

**ProblÃ¨me** : Les explications post-rÃ©ponse (exercices et dÃ©fis) sont du texte brut. Les formules mathÃ©matiques (`aÂ³+bÂ³`) et les Ã©tapes structurÃ©es sont illisibles.

**Valeur pÃ©dagogique (E=5)** :
- Mayer (2001) â€” *Multimedia Learning* : la segmentation et la mise en forme du texte rÃ©duit la charge cognitive extrinsÃ¨que et amÃ©liore la comprÃ©hension (effet mesurÃ©).
- Sweller (1988) â€” Cognitive Load Theory : l'organisation visuelle de l'information rÃ©duit la charge cognitive irrÃ©levante.
- La lisibilitÃ© de l'explication est un vecteur direct du transfert d'apprentissage.

**Ce qu'il faut faire** :
- IntÃ©grer `react-markdown` + `remark-math` + `rehype-katex` (ou `react-katex`) dans `ExerciseSolver` et `ChallengeSolver`
- Appliquer le rendu dans le bloc "Explication" de la rÃ©ponse
- Style CSS pour les formules math (KaTeX CSS)
- Optionnel : accordÃ©on "voir plus" si explication > 300 mots

**Effort estimÃ©** : 1-2 jours

**Statut** : âœ… ImplÃ©mentÃ© â€” composant `frontend/components/ui/MathText.tsx` (react-markdown + remark-math + rehype-katex), intÃ©grÃ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver` et `DiagnosticSolver`

---

### F02 â€” DÃ©fis quotidiens (dÃ©fi du jour) âœ…

**Source** : [ROADMAP Â§3.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.9 | D=3, G=5, E=4, R=2, B=5

**Statut** : âœ… ImplÃ©mentÃ© (Mars 2026)

**Valeur pÃ©dagogique (E=4)** :
- Cepeda et al. (2006) â€” La pratique distribuÃ©e (daily sessions) produit une meilleure rÃ©tention que la pratique massÃ©e, indÃ©pendamment du temps total (d = 0.46-0.71).
- Deci & Ryan (2000) â€” SDT : les dÃ©fis quotidiens optionnels, adaptÃ©s au niveau, soutiennent le besoin de compÃ©tence sans pression externe (contrairement aux streaks punitifs).

**Conception implÃ©mentÃ©e** : 3 dÃ©fis par jour (volume_exercises, specific_type, logic_challenge), bonus XP, expiration minuit, pas de punition si manquÃ©.

**RÃ©fÃ©rence technique complÃ¨te** : [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---


### F03 â€” Test de diagnostic initial

**Source** : [ROADMAP Â§3.5](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.0 | D=3, G=4, E=5, R=2, B=4

**ProblÃ¨me** : L'onboarding collecte les prÃ©fÃ©rences (classe, Ã¢ge, rythme) mais pas le niveau rÃ©el. Les premiÃ¨res recommandations peuvent Ãªtre inadaptÃ©es, dÃ©gradant le moment critique des 5 premiÃ¨res minutes.

**Valeur pÃ©dagogique (E=5)** :
- Hattie (2009) â€” *Formative assessment* : d = 0.90 (un des effets les plus Ã©levÃ©s en Ã©ducation). Identifier le niveau rÃ©el avant l'enseignement est la condition prÃ©alable Ã  toute personnalisation efficace.
- Sweller (1988) â€” L'alignement entre difficultÃ© et compÃ©tence prÃ©vient la surcharge cognitive (exercices trop faciles = ennui, trop difficiles = anxiÃ©tÃ©).
- *Assessment for learning* (Black & Wiliam, 1998) : le diagnostic prÃ©alable est la fondation de l'apprentissage adaptatif.

**Algorithme adaptatif (Item Response Theory simplifiÃ©)** :
```
1. Commencer au niveau mÃ©dian
2. Correct â†’ question plus difficile (niveau +1)
3. Incorrect â†’ question plus facile (niveau -1)
4. ArrÃªt : 2 erreurs consÃ©cutives au mÃªme niveau â†’ niveau Ã©tabli
5. DurÃ©e max : 10 questions, ~5 minutes
```

**Output** :
- `initial_level` par type d'exercice (addition, soustraction, multiplication, division, logique)
- StockÃ© dans `diagnostic_results` (table dÃ©diÃ©e, scores JSONB par type)
- Alimente immÃ©diatement les recommandations

**Effort estimÃ©** : 3-5 jours

**Statut** : âœ… ImplÃ©mentÃ© le 04/03/2026

**RÃ©fÃ©rence technique complÃ¨te** : [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)

**Ce qui est branchÃ©** :
- Table `diagnostic_results` (migration `20260304_diagnostic`)
- Service IRT (`app/services/diagnostic_service.py`) : algo adaptatif, 10 questions, 4 types
- Endpoints `/api/diagnostic/status|start|question|answer|complete`
- Page `/diagnostic` (accessible depuis onboarding et Settings)
- Section "Ã‰valuation de niveau" dans Settings (affiche date + niveaux par type)
- Recommandations : `RecommendationService` lit le diagnostic via `get_latest_score()` et affine la difficultÃ© mÃ©diane

**Ce qui reste Ã  cÃ¢bler (backlog F03-suite)** :

| Lacune | Impact | PrioritÃ© | Statut |
|--------|--------|----------|--------|
| `/api/exercises/generate` ignore le niveau diagnostic | Un utilisateur scorant InitiÃ© reÃ§oit des exercices selon `age_group`, pas son niveau rÃ©el | Moyen | âœ… RÃ©solu 06/03/2026 â€” `adaptive_difficulty_service` cÃ¢blÃ© en Ã©tape 1 de la cascade |
| `preferred_difficulty` stocke des age_group (`"adulte"`) mais le service attendait des DifficultyLevels | Zyclope (adulte) tombait en fallback PADAWAN malgrÃ© son profil | Moyen | âœ… RÃ©solu 06/03/2026 â€” `_PREF_DIFFICULTY_TO_ORDINAL` Ã©largi aux deux formes |
| Mode de rÃ©ponse QCM/saisie libre calculÃ© sur la difficultÃ© de l'exercice, pas le niveau rÃ©el utilisateur | Un utilisateur INITIE pouvait se voir forcer la saisie libre si l'exercice Ã©tait GRAND_MAITRE | Moyen | âœ… RÃ©solu 06/03/2026 â€” Frontend lit les scores IRT via `useIrtScores()`, dÃ©cide par type |
| Types non couverts IRT (MIXTE, FRACTIONS) sans proxy de niveau | Pas d'adaptation pour ces types | Moyen | âœ… RÃ©solu 06/03/2026 â€” Proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division) |
| Dashboard (`/`) ne lit pas `has_completed` | Pas de message de confirmation "ton niveau a Ã©tÃ© Ã©tabli" | Faible | â³ Backlog |
| GÃ©nÃ©ration IA (`/api/ai/generate`) ignore le diagnostic | MÃªme problÃ¨me que le gÃ©nÃ©rateur interne | Moyen | â³ Backlog |

---

### F04 â€” RÃ©visions espacÃ©es (algorithme SM-2)

**Source** : [ROADMAP Â§3.3](ROADMAP_FONCTIONNALITES.md)  
**Score** : 14.8 | D=4, G=4, E=5, R=2, B=4

**Valeur pÃ©dagogique (E=5) â€” La preuve la plus robuste en Ã©ducation** :
- Ebbinghaus (1885, rÃ©pliquÃ© 100+ fois) â€” Courbe de l'oubli : sans rÃ©vision, 70% d'une connaissance est oubliÃ©e en 24h, 90% en une semaine.
- Cepeda et al. (2006) â€” *Psychological Bulletin* : mÃ©ta-analyse de 317 Ã©tudes. La pratique espacÃ©e amÃ©liore la rÃ©tention de 200%+ sur le long terme vs pratique massÃ©e.
- Kornell & Bjork (2008) â€” Spacing + interleaving : effet particuliÃ¨rement fort en mathÃ©matiques (g = 0.43).
- *L'algorithme SM-2 (Wozniak, 1987) est le fondement de SuperMemo, Anki et DuoLingo.*

**Algorithme SM-2 adaptÃ©** :
```
Intervalles de rÃ©vision :
- 1Ã¨re rÃ©vision : J+1
- 2Ã¨me rÃ©vision : J+3
- 3Ã¨me rÃ©vision : J+7
- Suivantes : intervalle Ã— ease_factor

Ajustement ease_factor (EF, init 2.5) :
- RÃ©ponse correcte rapide (qualitÃ© 4-5) : EF + 0.1
- RÃ©ponse correcte lente (qualitÃ© 3) : EF inchangÃ©
- RÃ©ponse incorrecte (qualitÃ© 0-2) : EF âˆ’ 0.2, retour J+1
```

**ModÃ¨le de donnÃ©es** :
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

**IntÃ©gration** : AprÃ¨s chaque tentative d'exercice, mise Ã  jour de l'item SR. Widget "RÃ©visions du jour" sur le dashboard.

**Effort estimÃ©** : 1-2 semaines (migration + service + UI)

**RÃ©fÃ©rence technique (spec)** : [F04_REVISIONS_ESPACEES.md](F04_REVISIONS_ESPACEES.md)

---

## 4. P1 â€” Haute prioritÃ© {#4-p1}

---

### F05 â€” Adaptation dynamique de difficultÃ© âœ…

**Source** : [WORKFLOW_EDUCATION Â§2.2](WORKFLOW_EDUCATION_REFACTORING.md)  
**Score** : 13.9 | D=4, G=4, E=5, R=3, B=4

**Valeur pÃ©dagogique (E=5)** :
- Vygotsky (1978) â€” Zone proximale de dÃ©veloppement : l'apprentissage optimal se situe juste au-delÃ  de la compÃ©tence actuelle. Trop facile â†’ ennui. Trop difficile â†’ anxiÃ©tÃ©.
- Bjork (1994) â€” *Desirable difficulties* : un niveau de dÃ©fi optimal crÃ©e une rÃ©sistance productive (retrieval effort) qui renforce la mÃ©morisation Ã  long terme.
- Csikszentmihalyi (1990) â€” Ã‰tat de *flow* : atteint quand difficultÃ© â‰ˆ compÃ©tence.

**ImplÃ©mentation (v3.0.0-alpha.3+, MAJ 06/03/2026)** :
- `app/services/adaptive_difficulty_service.py` â€” rÃ©solution par cascade (IRT > progression > profil > fallback), proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division)
- `server/handlers/exercise_handlers.py` â€” branchement adaptatif (`?adaptive=true` par dÃ©faut, dÃ©sactivable par `?adaptive=false` ou `age_group` explicite)
- `app/utils/exercise_generator_helpers.py` ? distracteurs QCM calibr?s par niveau (INITIE: erreurs ?1 + inversion, PADAWAN: retenue ?10, CHEVALIER/MAITRE/GRAND_MAITRE: magnitude % ; `server/exercise_generator_helpers.py` reste un re-export de compatibilite)
- **Mode QCM vs saisie libre** : dÃ©cidÃ© cÃ´tÃ© frontend par `useIrtScores().resolveIsOpenAnswer(exercise_type)` â€” saisie libre uniquement si niveau IRT = GRAND_MAITRE pour ce type. Le backend gÃ©nÃ¨re toujours les `choices`.

**RÃ©fÃ©rence technique complÃ¨te** : [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md)

**Seuils adaptation temps rÃ©el** : `completion_rate > 85% ET streak >= 3` â†’ boost (+1 niveau) ; `completion_rate < 50% ET streak = 0` â†’ descente (-1 niveau).

**Hors scope F05-suite (backlog)** :
- `/api/ai/generate` â€” mÃªme adaptation pour la gÃ©nÃ©ration IA (SSE, complexitÃ© sÃ©parÃ©e)
- Dashboard widget 'ton niveau s'est ajustÃ©' â€” âœ… ImplÃ©mentÃ© 06/03/2026 (`LevelEstablishedWidget` dans l'onglet Vue d'ensemble)
- Seuils boost/descente configurables via admin
- **[F05-B1] Saisie libre dÃ©clenchÃ©e par taux de rÃ©ussite rÃ©el, pas uniquement par niveau IRT** : plutÃ´t que le seuil fixe GRAND_MAITRE, dÃ©clencher la saisie libre quand `completion_rate >= 90 % sur les 5 derniÃ¨res tentatives` pour un type donnÃ© â€” indÃ©pendamment du niveau IRT. Fondement : Roediger & Karpicke (2006) Testing Effect + VanLehn (2011) mÃ©ta-analyse tutoring adaptatif. Ã‰viter d'encoder des erreurs en forÃ§ant le recall avant que la rÃ©cupÃ©ration soit automatique.
- **[F05-B2] Distracteurs QCM plus discriminants, moins dÃ©ductibles** : amÃ©liorer la gÃ©nÃ©ration des `choices` pour Ã©viter les bonnes rÃ©ponses visibles par simple Ã©limination. Cible : 3 distracteurs plausibles, de mÃªme ordre de grandeur, mÃªme format et mÃªme unitÃ© que la bonne rÃ©ponse, issus d'erreurs typiques rÃ©elles (retenue, inversion, confusion opÃ©ratoire, off-by-one, confusion quotient/reste) plutÃ´t que de valeurs trop Ã©loignÃ©es ou structurellement diffÃ©rentes. Ajouter si possible une instrumentation du taux de sÃ©lection des distracteurs pour identifier ceux qui ne trompent jamais. Effort estimÃ© : 1-2 jours. PrioritÃ© produit : moyenne-haute, car impact direct sur la valeur pÃ©dagogique perÃ§ue des exercices.

**DÃ©pendance** : Profite du diagnostic initial (F03) et prÃ©pare les rÃ©visions espacÃ©es (F04).


---

### F06 â€” Conditions d'obtention badges visibles

**Source** : [BADGES_AMELIORATIONS Â§4.2](BADGES_AMELIORATIONS.md)  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Valeur pÃ©dagogique (E=3)** :
- Kivetz et al. (2006) â€” *Goal-gradient effect* : la motivation augmente Ã  mesure que l'objectif est visible et proche. Effet mesurÃ© +40-60% d'engagement.
- Zimmerman (2002) â€” Transparence des critÃ¨res amÃ©liore la rÃ©gulation autonome de l'apprentissage (self-regulation).

**Ce qu'il faut faire** : Afficher les critÃ¨res (`criteria_description`) sur les badges verrouillÃ©s dans `BadgeCard.tsx`. DÃ©jÃ  partiellement prÃ©parÃ© dans le backend (`PLAN_REFONTE_BADGES` archivÃ©).

**Effort estimÃ©** : Â½-1 jour

---

### F07 â€” Courbe d'Ã©volution temporelle

**Source** : [ANALYTICS_PROGRESSION Â§1.1](ANALYTICS_PROGRESSION.md)  
**Score** : 11.2 | D=3, G=4, E=3, R=2, B=3

**Statut** : âœ… ImplÃ©mentÃ© le 07/03/2026

**Valeur pÃ©dagogique (E=3)** :
- Zimmerman & Schunk (2001) â€” *Self-monitoring* : voir sa progression concrÃ¨te dans le temps active la mÃ©tacognition et renforce la motivation intrinsÃ¨que.
- Hattie (2009) â€” *Self-reported grades / metacognitive monitoring* : d = 1.33 (attention : effet de la conscience de sa propre progression, pas du graphique lui-mÃªme).

**Endpoint implÃ©mentÃ©** : `GET /api/users/me/progress/timeline?period=7d|30d`  
**DonnÃ©es sources** : `Attempt.created_at`, `Attempt.is_correct`, `Attempt.time_spent`  

**Ce qui a Ã©tÃ© fait** :
- Service dâ€™agrÃ©gation dÃ©diÃ© : `app/services/progress_timeline_service.py` (jours continus, rÃ©sumÃ© global, `by_type`)
- Handler + route : `server/handlers/user_handlers.py`, `server/routes/users.py`
- Hook + widget frontend : `frontend/hooks/useProgressTimeline.ts`, `frontend/components/dashboard/ProgressTimelineWidget.tsx`
- IntÃ©gration dashboard : onglet Progression (`frontend/app/dashboard/page.tsx`)
- Tests : `tests/unit/test_progress_timeline_service.py`, `tests/api/test_progress_endpoints.py`, `frontend/__tests__/unit/hooks/useProgressTimeline.test.tsx`
- RÃ©fÃ©rence dâ€™implÃ©mentation : [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md)

**Effort estimÃ©** : 3-5 jours

---

### F08 â€” Objectifs personnalisÃ©s

**Source** : [ROADMAP Â§4.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.1 | D=3, G=3, E=3, R=1, B=3

**Valeur pÃ©dagogique (E=3)** :
- Deci & Ryan (2000) â€” SDT : les objectifs auto-dÃ©terminÃ©s (choisis par l'utilisateur, pas imposÃ©s) renforcent la motivation intrinsÃ¨que et le besoin d'autonomie.
- Locke & Latham (1990) â€” *Goal-setting theory* : des objectifs spÃ©cifiques et mesurables amÃ©liorent la performance. Effet plus fort quand l'objectif est choisi par l'individu.

**Types** : Quotidien (ex: 5 exercices/jour), hebdomadaire, de maÃ®trise (ex: "atteindre 80% en division").

**Effort estimÃ©** : 3-5 jours

---

### F09 â€” Dashboard parent

**Source** : [ROADMAP Â§3.1](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.4 | D=4, G=4, E=3, R=2, B=5

**Valeur pÃ©dagogique (E=3)** :
- Hattie (2009) â€” *Parental involvement* : d = 0.49. L'implication parentale dans le suivi scolaire a un effet positif mesurable sur les rÃ©sultats.
- Bryk & Schneider (2002) â€” La confiance famille-institution est un prÃ©dicteur de l'engagement Ã  long terme.

**Architecture minimale (MVP)** :
```
Table: parent_child_links (parent_user_id, child_user_id, created_at, permissions JSON)
Route: /parent/dashboard â†’ vue enfants
Route: /parent/child/[id] â†’ progression dÃ©taillÃ©e
```

**Effort estimÃ©** : 1-2 semaines

---

### F10 â€” [PROPOSITION] Mode focus / session ciblÃ©e

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Concept** : Permettre de lancer une session ciblÃ©e en 2 clics : "5 multiplications niveau PADAWAN". L'utilisateur choisit type + difficultÃ© + nombre, et est guidÃ© directement dans une suite d'exercices sans navigation.

**Valeur pÃ©dagogique (E=3)** :
- Bjork (1994) â€” *Desirable difficulties* : l'interleaving (mÃ©lange de types) est bÃ©nÃ©fique, mais la pratique ciblÃ©e sur un type spÃ©cifique est nÃ©cessaire pour la construction de compÃ©tences (blocked practice pour la phase d'acquisition).
- Deci & Ryan â€” Le choix du type de pratique renforce l'autonomie (SDT).

**Effort estimÃ©** : 1-2 jours (frontend principalement â€” filtres dÃ©jÃ  disponibles en backend)

---

### F11 â€” [PROPOSITION] Partage de progression vers les parents (lien simple)

**Source** : Proposition IA â€” alternative lÃ©gÃ¨re au Dashboard Parent complet (F09)  
**Score** : 12.5 | D=2, G=3, E=3, R=1, B=4

**Concept** : GÃ©nÃ©rer un lien de partage de progression (lecture seule, sans compte requis) permettant au parent de voir les stats de l'enfant sans crÃ©er un espace parent dÃ©diÃ©. Quick win avant l'implÃ©mentation complÃ¨te de F09.

**Valeur pÃ©dagogique (E=3)** : MÃªme base que F09 (engagement parental), avec une friction d'adoption beaucoup plus faible.

**Effort estimÃ©** : 1-2 jours

---

### F12 â€” Radar chart par discipline

**Source** : [ANALYTICS_PROGRESSION Â§1.3](ANALYTICS_PROGRESSION.md)  
**Score** : 10.9 | D=2, G=3, E=3, R=1, B=2

**Valeur pÃ©dagogique (E=3)** : Auto-Ã©valuation et mÃ©tacognition. DonnÃ©es dÃ©jÃ  disponibles dans `/api/exercises/stats` (`by_discipline`). ImplÃ©mentation rapide avec Recharts `RadarChart`.

**Effort estimÃ©** : Â½-1 jour

---

### F13 â€” DÃ©blocage automatique badges (temps rÃ©el)

**Source** : [BADGES_AMELIORATIONS Â§4.4](BADGES_AMELIORATIONS.md)  
**Score** : 11.5 | D=2, G=3, E=3, R=1, B=3

**Valeur pÃ©dagogique (E=3)** :
- Kulik & Kulik (1988) â€” Feedback immÃ©diat amÃ©liore l'apprentissage. S'applique aux rÃ©compenses : un badge dÃ©bloquÃ© 2 jours aprÃ¨s l'effort perd son effet de renforcement.

**Ce qu'il faut faire** : Appeler `check_and_award_badges` aprÃ¨s chaque tentative (dÃ©jÃ  fait pour les dÃ©fis â€” Ã©tendre aux exercices) et afficher un toast avec l'animation de badge.

**Effort estimÃ©** : Â½-1 jour

---

---

### F30 â€” [PROPOSITION] L'Effet ProtÃ©gÃ© ("Corrige l'erreur de l'IA")

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 15.4 | D=4, G=4, E=5, R=2, B=4

> *Score initial proposÃ© : 16.2 (D=3). DifficultÃ© rÃ©visÃ©e Ã  D=4 : gÃ©nÃ©ration IA d'erreurs intentionnelles + composant UI "correction de copie" + vÃ©rification de la justification = pÃ©rimÃ¨tre backend + frontend non nÃ©gligeable.*

**ProblÃ¨me** : RÃ©soudre un problÃ¨me mathÃ©matique est un apprentissage actif classique. Mais le niveau ultime de maÃ®trise s'atteint lorsqu'on doit enseigner Ã  quelqu'un d'autre â€” ou corriger ses erreurs.

**Valeur pÃ©dagogique (E=5)** :
- Chase et al. (2009) â€” *The ProtÃ©gÃ© Effect* : Les Ã©tudiants font plus d'efforts et apprennent plus profondÃ©ment quand ils doivent enseigner Ã  un agent virtuel (effet mesurÃ© trÃ¨s fort).
- Hattie (2009) â€” *Peer Tutoring* : d = 0.55. L'Ã©valuation des erreurs des autres active une mÃ©tacognition supÃ©rieure Ã  la simple rÃ©solution.
- La dÃ©tection d'une erreur de logique (et non de calcul) est un exercice de comprÃ©hension conceptuelle profonde, non mÃ©morisable par substitution de pattern.

**Ce qu'il faut faire** : CrÃ©er un type de dÃ©fi inversÃ©. L'IA prÃ©sente un problÃ¨me et une rÃ©solution Ã©tape par Ã©tape contenant **une seule erreur de logique intentionnelle**. L'Ã©lÃ¨ve doit agir comme le professeur : identifier Ã  quelle Ã©tape l'IA s'est trompÃ©e et expliquer pourquoi.

**Architecture cible** :
- Nouveau `challenge_type` : `error_correction`
- Champ backend : `steps: [{content, is_error: bool, error_explanation}]`
- UI : composant "Correction de copie" â€” affichage des Ã©tapes numÃ©rotÃ©es, sÃ©lection de l'Ã©tape erronÃ©e, champ justification
- Validation : l'Ã©lÃ¨ve doit identifier la bonne Ã©tape ET soumettre une explication (mÃªme courte)

**Effort estimÃ©** : 3-5 jours (nouveau type de dÃ©fi + composant UI + prompt IA pour gÃ©nÃ©ration d'erreurs intentionnelles)  
**PrioritÃ©** : P1 â€” score fort, diffÃ©renciateur pÃ©dagogique unique sur le marchÃ©

---

### F31 â€” [PROPOSITION] Exemples rÃ©solus progressifs (Fading Effect)

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 15.2 | D=3, G=4, E=5, R=2, B=3

**ProblÃ¨me** : Face Ã  un concept totalement nouveau, faire faire des exercices et sanctionner l'erreur (mÃªme avec correction ensuite) gÃ©nÃ¨re de l'anxiÃ©tÃ© et une surcharge cognitive pour les novices.

**Valeur pÃ©dagogique (E=5)** :
- Sweller & Cooper (1985) â€” *Worked Example Effect* : Ã‰tudier des problÃ¨mes dÃ©jÃ  rÃ©solus est **plus efficace pour les novices** que de rÃ©soudre des problÃ¨mes (d = 0.57). RÃ©pliquÃ© extensivement.
- Renkl (1997) â€” *Fading steps* : La transition optimale de novice Ã  expert se fait en retirant progressivement les Ã©tapes guidÃ©es â€” l'autonomie croÃ®t naturellement.
- ComplÃ©mentaire avec F05 (adaptation difficultÃ©) : le fading s'active automatiquement quand l'algorithme dÃ©tecte un concept nouveau (0 tentatives sur ce type).

**Ce qu'il faut faire** : IntÃ©grer une mÃ©canique de "Fading" dans l'onboarding d'un nouveau concept (dÃ©clenchÃ©e quand l'utilisateur rencontre un sous-type d'exercice pour la premiÃ¨re fois) :

| Exercice | Mode | Description |
|----------|------|-------------|
| 1 | **Fully worked** | EntiÃ¨rement rÃ©solu par l'IA, l'Ã©lÃ¨ve lit et clique "J'ai compris" |
| 2 | **Last step missing** | RÃ©solu, mais la derniÃ¨re Ã©tape est Ã  complÃ©ter |
| 3 | **Half faded** | Seule la premiÃ¨re Ã©tape est donnÃ©e, l'Ã©lÃ¨ve finit |
| 4 | **Autonome** | L'Ã©lÃ¨ve fait tout â€” rÃ©gime normal |

**Contrainte de conception** : Ne pas pÃ©naliser l'exercice "fully worked" (pas de score de rÃ©ussite/Ã©chec) â€” c'est un mode observation, pas Ã©valuation.

**Effort estimÃ©** : 3-5 jours (dÃ©clinaison du moteur d'exercices + dÃ©tection "premiÃ¨re fois sur ce sous-type")  
**PrioritÃ©** : P1 â€” particuliÃ¨rement critique pour la rÃ©tention des utilisateurs en onboarding

---

### F32 â€” [PROPOSITION] Mode "Pratique EntrelacÃ©e" (Interleaving) âœ…

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 14.5 | D=2, G=3, E=5, R=2, B=3

**Statut** : âœ… ImplÃ©mentÃ© le 07/03/2026

> *Score initial proposÃ© : 15.2 (R=1). Risque rÃ©visÃ© Ã  R=2 : le mÃ©lange de types d'exercices interagit avec F05 (adaptation dynamique par type) â€” il faut s'assurer que les niveaux par type sont suffisamment calibrÃ©s avant activation.*

**ProblÃ¨me** : Les Ã©lÃ¨ves ont tendance Ã  enchaÃ®ner un seul type d'exercice (ex : 10 additions d'affilÃ©e â€” *Blocked Practice*). Le cerveau se met en pilote automatique et n'apprend pas Ã  **choisir la bonne stratÃ©gie**, compÃ©tence clÃ© en Ã©valuation.

**Valeur pÃ©dagogique (E=5)** :
- Rohrer & Taylor (2007) â€” *Interleaved Practice* : MÃ©langer les types de problÃ¨mes force le cerveau Ã  identifier la stratÃ©gie avant de l'appliquer. **RÃ©tention Ã  long terme amÃ©liorÃ©e de +43%** par rapport Ã  la pratique bloquÃ©e.
- Kornell & Bjork (2008) â€” Effet particuliÃ¨rement fort en mathÃ©matiques : spacing + interleaving combinÃ©s produisent les meilleures performances (g = 0.43).
- **Attention** : L'interleaving est contre-intuitif â€” les Ã©lÃ¨ves ont l'impression d'apprendre moins bien pendant la session (mais retiennent mieux). Ã€ accompagner d'une explication pÃ©dagogique dans l'UI.

**Ce qui a Ã©tÃ© fait** :
- Endpoint dÃ©diÃ© : `GET /api/exercises/interleaved-plan?length=10` (`server/handlers/exercise_handlers.py`, `server/routes/exercises.py`)
- Service d'agrÃ©gation : `app/services/interleaved_practice_service.py` (fenÃªtre 7 jours, Ã©ligibilitÃ© `>=2 tentatives` et `>=60%`, plan round-robin sans doublons consÃ©cutifs)
- Gestion mÃ©tier explicite : `InterleavedNotEnoughVariety` -> `409` avec code `not_enough_variety`
- Quick Action dashboard : 3e CTA dans `QuickStartActions` + instrumentation analytics `quick_start_click` type `interleaved`
- EntrÃ©e session : page `frontend/app/exercises/interleaved/page.tsx` (plan, fallback 409, gÃ©nÃ©ration 1er exercice, redirection)
- Progression session : `ExerciseSolver` en mode `session=interleaved` (progression, bouton "Exercice suivant", Ã©cran de fin)
- i18n FR/EN : clÃ©s `dashboard.quickStart.interleaved*` et `exercises.solver.session*`
- Correctif critique F05/F32 : `POST /api/exercises/generate` passe en `@optional_auth`, ce qui active correctement la rÃ©solution adaptative `age_group` quand `adaptive=true`

**Durcissements post-implÃ©mentation (08/03/2026)** :
- analytics EdTech `interleaved` ramenÃ©es Ã  une sÃ©mantique session : `first_attempt` n'est Ã©mis qu'une seule fois au premier exercice soumis, avec persistance `sessionStorage`
- flux de session durci : `POST /api/exercises/generate` ne renvoie plus de `200` sans `id` quand `save=true` ; en cas d'Ã©chec, le frontend affiche un toast et conserve l'Ã©tat de session
- dette DRY rÃ©duite : la rÃ©solution adaptive `age_group` est factorisÃ©e dans `_resolve_adaptive_age_group_if_needed()` pour Ã©viter la divergence entre `generate_exercise` et `generate_exercise_api`
- quality gate restaurÃ© : `black app/ server/ tests/ --check` repasse au vert ; nettoyage UTF-8 de `tests/unit/test_adaptive_difficulty_service.py` et hygiÃ¨ne repo (`frontend/junit.xml`, `.gitignore`, import inutilisÃ©)

**Tests** :
- `tests/unit/test_interleaved_practice_service.py`
- `tests/api/test_exercise_endpoints.py` (auth, `409 not_enough_variety`, succÃ¨s `200`, non-rÃ©gression `adaptive=true` sans `age_group` explicite)

**Effort rÃ©alisÃ©** : ~1-2 jours  
**DÃ©pendance** : F05 exploitÃ© (difficultÃ© adaptative conservÃ©e)  
**PrioritÃ©** : P1 â€” quick win fort, effort modÃ©rÃ©, impact pÃ©dagogique Ã©levÃ©

---

### F33 â€” Feedback "Growth Mindset" âœ…

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 11.4 | D=1, G=3, E=3, R=1, B=2

> *Score initial proposÃ© : 13.0 (E=4). EdTech rÃ©visÃ© Ã  E=3 : les Ã©tudes Dweck sont robustes mais les interventions de Growth Mindset par texte seul ont des effets faibles sans accompagnement long terme. Yeager et al. (2019) mesure des effets sur populations dÃ©favorisÃ©es spÃ©cifiques â€” le transfert Ã  une plateforme gÃ©nÃ©raliste est conditionnel.*

**Statut** : âœ… ImplÃ©mentÃ© le 07/03/2026

**ProblÃ¨me** : Un message "Faux" ou un feedback nÃ©gatif brutal lors d'un Ã©chec peut renforcer un *Fixed Mindset* ("Je suis nul en maths"). Ce biais est particuliÃ¨rement fort chez les enfants 8-14 ans.

**Valeur pÃ©dagogique (E=3)** :
- Dweck (2006) â€” *Mindset Theory* : Valoriser l'effort et la stratÃ©gie plutÃ´t que l'intelligence innÃ©e ou le rÃ©sultat brut amÃ©liore la rÃ©silience face Ã  l'Ã©chec.
- Yeager et al. (2019) : Une simple intervention Growth Mindset a des effets mesurables sur les rÃ©sultats en maths chez les Ã©lÃ¨ves dÃ©favorisÃ©s.
- **Nuance** : L'effet est conditionnel et nÃ©cessite de la cohÃ©rence dans tout le parcours utilisateur â€” un seul message ne suffit pas.

**Ce qui a Ã©tÃ© fait** (modifications de texte + micro-UI) :

| Avant | AprÃ¨s |
|-------|-------|
| "Mauvaise rÃ©ponse" | "Pas encore ! La prochaine sera la bonne." |
| "Incorrect" | "Ton cerveau est en train d'apprendre !" |
| Score affichÃ© seulement | Valoriser aussi le **temps passÃ©** sur un dÃ©fi difficile |
| â€” | Tooltips de chargement : *"Savais-tu que ton cerveau crÃ©e de nouvelles connexions exactement au moment oÃ¹ tu fais une erreur ?"* |

**Contrainte** : CohÃ©rence avec les textes de feedback existants dans `fr.json` / `en.json`. Ne pas sur-positiver au point de perdre la valeur informative du feedback (Hattie & Timperley, 2007 â€” le feedback doit rester prÃ©cis).

**ImplÃ©mentation** :
- Messages FR/EN alignÃ©s Growth Mindset (`frontend/messages/fr.json`, `frontend/messages/en.json`)
- Feedback d'Ã©chec harmonisÃ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver`
- Bloc partagÃ© factorisÃ© : `frontend/components/ui/GrowthMindsetHint.tsx` (industrialisation, no-DRY)

**Effort rÃ©alisÃ©** : ~Â½ jour  
**PrioritÃ©** : P1 â€” quick win absolu, risque technique faible, impact psychologique documentÃ©

---

## 5. P2 â€” PrioritÃ© moyenne {#5-p2}

| Feature | Note |
|---------|------|
| **F14 â€” Monitoring IA persistance DB** | Voir [ROADMAP Â§4.6](ROADMAP_FONCTIONNALITES.md). Table `AiTokenUsage` + `AiGenerationMetric`. Pattern : `edtech_events`. ~1 jour. |
| **F15 â€” PrÃ©fÃ©rence page d'accueil** | Champ `login_redirect_preference` sur `User`. Option dans ParamÃ¨tres. ~Â½ jour. |
| **F16 â€” Heatmap d'activitÃ©** | Calendrier GitHub-style sur Dashboard/Profil. `react-calendar-heatmap`. Endpoint : `GET /api/users/me/activity/heatmap`. |
| **F17 â€” CÃ©lÃ©brations visuelles amÃ©liorÃ©es** | Confettis au dÃ©blocage badge, modal avec partage. DÃ©sactivable (accessibilitÃ©). |
| **F18 â€” Ligues hebdomadaires** | Upgrade du leaderboard : groupes de 30, promotion/relÃ©gation, reset chaque lundi. Voir [ROADMAP Â§3.4](ROADMAP_FONCTIONNALITES.md). Score EdTech=1 : engagement, pas d'apprentissage direct. |
| **F19 â€” Notifications push + email** | Rappel inactivitÃ©, streak en danger, badge proche. Voir [ROADMAP Â§4.1](ROADMAP_FONCTIONNALITES.md). Infrastructure Ã  dÃ©finir (service push web + SMTP). |
| **F20 â€” Normalisation niveaux de difficultÃ©** | Remplacer nomenclature Star Wars par libellÃ©s universels. Voir [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md). Migration enum risquÃ©e â€” Ã  planifier soigneusement. |
| **F21 â€” Badges secrets** | Badges cachÃ©s dÃ©bloquÃ©s pour comportements inattendus (ex: "Noctambule" aprÃ¨s minuit). Variable reward (Skinner) â€” engagement Ã©levÃ©. |
| **F22 â€” Suppression utilisateur admin (RGPD)** | `DELETE /api/admin/users/{id}` avec soft delete. Voir PLACEHOLDERS_ET_TODO. Compliance obligatoire avant scale. |
| **F35 â€” [TECH] Redaction secrets logs DB âœ…** | ImplÃ©mentÃ© le 07/03/2026. `app/db/base.py` loggue dÃ©sormais une URL redigÃ©e via `redact_database_url_for_log()` (credentials et query params masquÃ©s). Couvert par `tests/unit/test_db_log_redaction.py` (7 tests). |
| **F36 â€” [UX][TECH] Flash auth au refresh** | Artefact visuel observÃ© aprÃ¨s refresh: pendant ~0.5s, le frontend semble repasser par un Ã©tat "non connectÃ©" avant rehydratation correcte de la session. Backend session validÃ©: login OK, session conservÃ©e aprÃ¨s refresh et aprÃ¨s idle prolongÃ©. Cible: supprimer le flash sans changer la chaÃ®ne de session/cookies. Piste probable: bootstrap auth frontend (`ProtectedRoute`, `current-user`, `validate-token`, `sync-cookie`). Ouvrir un lot dÃ©diÃ© seulement si le symptÃ´me devient gÃªnant ou s'accompagne d'une redirection parasite/perte de session. |
| **F23 â€” [PROP] Exercices adaptatifs SR+IA** | GÃ©nÃ©rer des exercices IA ciblÃ©s sur les concepts Ã  rÃ©viser selon la courbe SR (F04). Score composite trÃ¨s Ã©levÃ© (17.1) mais **dÃ©pend de F04**. DÃ©bloquÃ© aprÃ¨s F04. |

---

## 6. P3 â€” Investissement long terme {#6-p3}

### F24 â€” Tuteur IA contextuel

**Score** : 16.1 | D=5, G=5, E=5, R=3, B=5

**Valeur pÃ©dagogique (E=5) â€” parmi les plus fortes en EdTech** :
- VanLehn (2011) â€” *Educational Psychologist* : Les systÃ¨mes de tutoriels intelligents (ITS) atteignent d = 0.55â€“0.66 par rapport aux classes classiques. Seul le tutorat humain individuel fait mieux (d â‰ˆ 2.0).
- *Scaffolding* cognitif (Wood et al., 1976) : l'aide contextuelle qui s'adapte aux erreurs est plus efficace que les explications gÃ©nÃ©riques.
- RÃ¨gle critique : **ne pas donner la rÃ©ponse directement** â€” guider par questions socratiques.

**DiffÃ©rence vs chatbot actuel** : Le chatbot actuel est gÃ©nÃ©rique. Un tuteur IA contextuel connaÃ®t l'exercice en cours, le niveau de l'utilisateur et l'historique d'erreurs sur ce type de problÃ¨me.

**Effort estimÃ©** : 2-4 semaines (intÃ©gration LLM contextuel + design pÃ©dagogique)

---

### F25 â€” Mode classe / enseignant

**Score** : 14.9 | D=5, G=4, E=4, R=3, B=5

**Valeur pÃ©dagogique (E=4)** : L'enseignant mÃ©diateur amplifie les effets de la plateforme (Hattie, d = 0.45 pour *teacher-student relationships*). L'assignation ciblÃ©e d'exercices + les rapports par classe sont des outils pÃ©dagogiques Ã  fort impact.

**Architecture requise** : Table `classes`, `class_memberships`, `assignments`, routes `/teacher/`. IntÃ©gration d'export CSV (dÃ©jÃ  partiellement disponible).

**Effort estimÃ©** : 3-6 semaines

---

### F26 â€” Filtres et tri badges

AmÃ©lioration ergonomique de la page `/badges`. Par statut, catÃ©gorie, difficultÃ©. ~1 jour. DÃ©prioritisÃ© car la page badges est dÃ©jÃ  bien structurÃ©e (onglets En cours / Ã€ dÃ©bloquer).

---

### F27 â€” Optimisation re-renders exercices/dÃ©fis

Flash visible avant stabilisation des pages. Pistes : `placeholderData` TanStack Query, `useMemo` sur les params de query. ~3-5 jours (profiling + corrections).

---

## 7. P4 â€” Backlog distant {#7-p4}

### F28 â€” Mode aventure / histoire narrative

**Score** : 13.1 | D=5, G=5, E=3, R=3, B=5

**Valeur pÃ©dagogique (E=3)** :
- Situated learning (Lave & Wenger, 1991) : les maths contextualisÃ©es dans une narration rÃ©elle amÃ©liorent le transfert des connaissances.
- Mais : l'effet de la gamification narrative sur les rÃ©sultats acadÃ©miques est modÃ©rÃ© et conditionnel (Mayer, 2019 â€” *Computer games don't improve learning*).

**Concept** : Progression narrative oÃ¹ les maths servent l'histoire ("Le vaisseau a besoin de 150 unitÃ©s de carburant, tu as 3 rÃ©servoirs de 45 chacun..."). RÃ©compenses dÃ©bloquant la suite.

**Effort estimÃ©** : 4-8 semaines (design narratif + nouveau type de contenu)

---

### F29 â€” Personnalisation avatar / profil

**Score** : 7.1 | D=3, G=3, E=1, R=1, B=2

Avatars, titres, cadres de profil dÃ©bloquables avec les points. Donne de la valeur aux points gagnÃ©s. Score EdTech=1 : pas de bÃ©nÃ©fice pÃ©dagogique documentÃ©.

---

### F34 â€” Module Sciences â€” CuriositÃ©s scientifiques (Labo des Sciences)

**Score** : 10.4 | D=3, G=4, E=2, R=2, B=4

**Philosophie** :
1. **ZÃ©ro punition** : Si l'Ã©lÃ¨ve clique sur "Faux" (alors que c'est Vrai), pas de croix rouge agressive. IcÃ´ne ampoule bleue douce + texte Â« Et non, c'est pourtant vrai ! Â». Objectif : apprendre un fait amusant, pas Ã©valuer.
2. **Explication gratifiante** : L'explication apparaÃ®t dans un encart en dessous, sans quitter la page (pas de pop-up ou changement d'Ã©cran brutal).
3. **Format rapide** : Format "TikTok/Shorts" appliquÃ© Ã  l'Ã©ducation. L'Ã©lÃ¨ve enchaÃ®ne ~10 anecdotes scientifiques en 3 minutes, gagne de l'XP sans impression de "travailler".

**Contenu** :
- Affirmation scientifique (ex. Â« Le Soleil pourrait contenir environ un million de Terres Â»)
- Boutons Vrai / Faux
- RÃ©ponse correcte : icÃ´ne check verte, Â« Exactement ! +X XP Â»
- RÃ©ponse incorrecte : icÃ´ne ampoule bleue, Â« Et non, c'est pourtant vrai ! Â» (ou Â« Et oui, c'est bien faux ! Â» selon le cas)
- Encart explicatif avec fait dÃ©taillÃ© + bouton Â« Fait suivant Â»

**Technique** :
- Nouveau type de contenu (table `science_facts` ou extension `challenges` avec `challenge_type=science`)
- CatÃ©gories : Astronomie, Biologie, Physique, Chimie, etc.
- Badge catÃ©gorie, compteur sÃ©rie, XP par fait
- Design : glassmorphism, thÃ¨me sombre cohÃ©rent Mathakine

**Prototype** : [F34_SCIENCES_PROTOTYPE.html](F34_SCIENCES_PROTOTYPE.html) â€” HTML statique (Tailwind, Font Awesome, JS vanilla). Ã€ intÃ©grer en Next.js + API.

**Effort estimÃ©** : 1â€“2 semaines (modÃ¨le + API + page `/sciences` + intÃ©gration design system)

---

## 8. Features implÃ©mentÃ©es (historique) {#8-features-implÃ©mentÃ©es}

| Feature | Date | RÃ©fÃ©rence |
|---------|------|-----------|
| F01 â€” Rendu Markdown/KaTeX dans les explications | 2026 | Composant `MathText.tsx` â€” intÃ©grÃ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver` |
| F03 â€” Test de diagnostic initial (IRT adaptatif) | 04/03/2026 | [ROADMAP_FONCTIONNALITES Â§F03](ROADMAP_FONCTIONNALITES.md) |
| F35 â€” Redaction secrets logs DB (sÃ©curitÃ©) | 07/03/2026 | [IMPLEMENTATION_F35_REDACTION_LOGS_DB](../03-PROJECT/IMPLEMENTATION_F35_REDACTION_LOGS_DB.md) |
| F32 â€” Session entrelacÃ©e (interleaving) | 07-08/03/2026 | [IMPLEMENTATION_F32_SESSION_ENTRELACEE](../03-PROJECT/IMPLEMENTATION_F32_SESSION_ENTRELACEE.md) |
| F33 â€” Feedback Growth Mindset (copywriting + micro-UI) | 07/03/2026 | [ROADMAP_FONCTIONNALITES Â§F33](ROADMAP_FONCTIONNALITES.md) |
| F07 â€” Courbe d'Ã©volution temporelle (7j/30j) | 07/03/2026 | [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md) |
| Espace admin complet (rÃ´le archiviste) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Auth complet (inscription, email, login, reset) | Jan-FÃ©v 2026 | [AUTH_FLOW](AUTH_FLOW.md) |
| Sessions actives + rÃ©vocation | 16/02/2026 | SITUATION_FEATURES (archivÃ©) |
| Leaderboard (top 50, filtre Ã¢ge) | 15/02/2026 | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) |
| Badges â€” refonte UX (onglets, cartes compactes) | 17/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges â€” barres de progression (goal-gradient) | 16/02/2026 | [BADGES_AMELIORATIONS](BADGES_AMELIORATIONS.md) |
| Badges â€” B4 reformulation (17 badges) | 17/02/2026 | ArchivÃ© : AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES |
| Badges â€” moteur gÃ©nÃ©rique Lot C (dÃ©fis, mixte) | 17/02/2026 | ArchivÃ© : AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES |
| Quick Win #1 â€” First Exercise < 90s | FÃ©v 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Quick Win #2 â€” Onboarding pÃ©dagogique | FÃ©v 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Calibration Ã  l'inscription (classe, Ã¢ge, objectif) | FÃ©v 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Parcours guidÃ© (QuickStartActions dashboard) | FÃ©v 2026 | [WORKFLOW_EDUCATION](WORKFLOW_EDUCATION_REFACTORING.md) |
| Recommandations personnalisÃ©es (marquer fait) | 16/02/2026 | SITUATION_FEATURES (archivÃ©) |
| Ordre alÃ©atoire + masquer rÃ©ussis | 19/02/2026 | SITUATION_FEATURES (archivÃ©) |
| Analytics EdTech (CTR Quick Start, 1er attempt) | 25/02/2026 | [EDTECH_ANALYTICS](EDTECH_ANALYTICS.md) |
| Monitoring IA (in-memory) | 22/02/2026 | [ROADMAP Â§4.6](ROADMAP_FONCTIONNALITES.md) |
| Mode maintenance + inscriptions (admin config) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](ADMIN_ESPACE_PROPOSITION.md) |
| Streak (basique) | FÃ©v 2026 | IntÃ©grÃ© dans stats utilisateur |
| 7 thÃ¨mes visuels | FÃ©v 2026 | [THEMES](THEMES.md) |
| PWA (mode hors-ligne partiel) | FÃ©v 2026 | â€” |
| Internationalisation FR/EN | Jan 2026 | [I18N](I18N.md) |
| AccessibilitÃ© (5 modes WCAG AAA) | FÃ©v-Mars 2026 | [ACCESSIBILITY](../04-FRONTEND/ACCESSIBILITY.md) |

---

## 9. RÃ©fÃ©rences scientifiques {#9-rÃ©fÃ©rences-scientifiques}

| # | RÃ©fÃ©rence | Pertinence |
|---|-----------|------------|
| 1 | Hattie, J. (2009). *Visible Learning*. Routledge. | MÃ©ta-analyse de rÃ©fÃ©rence â€” effets sur l'apprentissage |
| 2 | Cepeda, N.J. et al. (2006). Distributed practice in verbal recall tasks. *Psychological Bulletin*, 132(3). | Fondement rÃ©visions espacÃ©es (F04) |
| 3 | Hattie, J. & Timperley, H. (2007). The power of feedback. *Review of Educational Research*, 77(1). | Fondement feedback enrichi (F01) |
| 4 | VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. *Educational Psychologist*, 46(4). | Fondement tuteur IA (F24) |
| 5 | Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*, 12(2). | Fondement charge cognitive, mise en forme (F01, F03) |
| 6 | Vygotsky, L.S. (1978). *Mind in Society*. Harvard University Press. | Fondement ZPD, adaptation difficultÃ© (F05) |
| 7 | Bjork, R.A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), *Metacognition*. | Fondement desirable difficulties, mode focus (F05, F10) |
| 8 | Mayer, R.E. (2001). *Multimedia Learning*. Cambridge University Press. | Fondement rendu Markdown/KaTeX (F01) |
| 9 | Deci, E.L. & Ryan, R.M. (2000). The 'what' and 'why' of goal pursuits. *Psychological Inquiry*, 11(4). | Fondement SDT, dÃ©fis optionnels (F02, F08) |
| 10 | Kivetz, R. et al. (2006). The goal-gradient hypothesis resurrected. *Journal of Marketing Research*, 43(1). | Fondement conditions badges visibles (F06) |
| 11 | Black, P. & Wiliam, D. (1998). Assessment and classroom learning. *Assessment in Education*, 5(1). | Fondement diagnostic initial (F03) |
| 12 | Locke, E.A. & Latham, G.P. (1990). *A Theory of Goal Setting and Task Performance*. Prentice Hall. | Fondement objectifs personnalisÃ©s (F08) |
| 13 | Lave, J. & Wenger, E. (1991). *Situated Learning*. Cambridge University Press. | Fondement mode aventure (F28) |
| 14 | Zimmerman, B.J. (2002). Becoming a self-regulated learner. *Theory into Practice*, 41(2). | Fondement mÃ©tacognition, graphiques progression (F07, F12) |
| 15 | Kornell, N. & Bjork, R.A. (2008). Learning concepts and categories. *Psychological Science*, 19(6). | Fondement rÃ©visions espacÃ©es + interleaving (F04, F32) |
| 16 | Chase, C. et al. (2009). Teachable agents and the protÃ©gÃ© effect. *Journal of Science Education and Technology*, 18(4). | Fondement Effet ProtÃ©gÃ© (F30) |
| 17 | Rohrer, D. & Taylor, K. (2007). The shuffling of mathematics problems improves learning. *Instructional Science*, 35(6). | Fondement Pratique EntrelacÃ©e (F32) |
| 18 | Sweller, J. & Cooper, G.A. (1985). The use of worked examples as a substitute for problem solving. *Cognition and Instruction*, 2(1). | Fondement Fading Effect, exemples rÃ©solus (F31) |
| 19 | Renkl, A. (1997). Learning from worked-out examples. *American Educational Research Journal*, 34(3). | Fondement fading progressif (F31) |
| 20 | Dweck, C.S. (2006). *Mindset: The New Psychology of Success*. Random House. | Fondement Growth Mindset, feedback d'erreur (F33) |
| 21 | Yeager, D.S. et al. (2019). A national experiment reveals where a growth mindset improves achievement. *Nature*, 573. | Fondement Growth Mindset appliquÃ© aux maths (F33) |

---

## Documents liÃ©s

| Sujet | Document |
|-------|----------|
| SpÃ©cifications graphiques analytics | [ANALYTICS_PROGRESSION.md](ANALYTICS_PROGRESSION.md) |
| Fondements psychologiques badges | [BADGES_AMELIORATIONS.md](BADGES_AMELIORATIONS.md) |
| Workflow utilisateur complet | [WORKFLOW_EDUCATION_REFACTORING.md](WORKFLOW_EDUCATION_REFACTORING.md) |
| Normalisation difficultÃ© | [NIVEAUX_DIFFICULTE_NORMALISATION.md](NIVEAUX_DIFFICULTE_NORMALISATION.md) |
| Auth flow | [AUTH_FLOW.md](AUTH_FLOW.md) |
| Admin (pÃ©rimÃ¨tre, sÃ©curitÃ©) | [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md), [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) |
| Analytics EdTech (implÃ©mentÃ©) | [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md) |
| Endpoints API | [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) |
| ThÃ¨mes visuels | [THEMES.md](THEMES.md) |
| Internationalisation | [I18N.md](I18N.md) |
| Badges implÃ©mentÃ©s (archive) | [AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md) |

