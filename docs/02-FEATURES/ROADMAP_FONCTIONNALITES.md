# Backlog & Priorisation des Features â€” Mathakine

> **Document vivant** - Derniere MAJ : 29/03/2026 (F42 clos, A44 clos, F43 migrations additives livrees, F04 exercice livre jusqu'a P5)  
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
8. [Features implementees (historique)](#8-features-implementees)
9. [RÃ©fÃ©rences scientifiques](#9-rÃ©fÃ©rences-scientifiques)

---

## 1. MÃ©thodologie de priorisation

### 1.1 Axes d'Ã©valuation (1â€“5)

| Axe | Description | 1 | 5 |
|-----|-------------|---|---|
| **D** â€” DifficultÃ© | Effort d'implÃ©mentation estimÃ© | Â½ jour | 2+ semaines |
| **G** â€” Gain utilisateur | Impact direct sur l'engagement et la satisfaction | NÃ©gligeable | Transformateur |
| **E** â€” EdTech | Valeur pÃ©dagogique scientifiquement documentÃ©e (voir Ã‚Â§1.2) | CosmÃ©tique | Effet fort > 0.6d |
| **R** â€” Risque | Risque technique ou de rÃ©gression | Aucun | Critique |
| **B** â€” Business | RÃ©tention / acquisition / diffÃ©renciation marchÃ© | Nul | DÃ©cisif |

### 1.2 Ã‰chelle EdTech â€” Base scientifique

L'axe EdTech est **le seul Ã  Ãªtre Ã©valuÃ© Ã  partir de donnÃ©es factuelles**, pas d'intuitions produit.

| Score | Signification | CritÃ¨re |
|-------|--------------|---------|
| **5** | Preuve trÃ¨s forte | MÃ©ta-analyse, effet mesurÃ© d Ã¢â€°Â¥ 0.6 (Cohen), rÃ©pliquÃ© dans plusieurs populations |
| **4** | Preuve forte | Effet mesurÃ© d = 0.4â€“0.6, ou consensus dans la littÃ©rature EdTech peer-reviewed |
| **3** | Preuve modÃ©rÃ©e | BÃ©nÃ©fice documentÃ© mais conditionnel, population spÃ©cifique ou effet indirect |
| **2** | Preuve faible | Engagement documentÃ©, mais impact sur l'apprentissage mixte ou non mesurÃ© |
| **1** | Pas de preuve | Principalement cosmÃ©tique, spÃ©culatif ou motivation extrinsÃ¨que non corroborÃ©e |

**RÃ©fÃ©rences de base utilisÃ©es pour le scoring** :
- Hattie (2009) â€” *Visible Learning* : mÃ©ta-analyse de 800+ mÃ©ta-analyses (>50 000 Ã©tudes)
- Cepeda et al. (2006) â€” Pratique distribuÃ©e et espacÃ©e â€” *Psychological Bulletin*
- Hattie & Timperley (2007) - Pouvoir du feedback - *Review of Educational Research*
- VanLehn (2011) â€” Tuteurs IA vs tuteurs humains â€” *Educational Psychologist*
- Bjork (1994) â€” Desirable difficulties in learning
- Sweller (1988) - Theorie de la charge cognitive - *Cognitive Science*
- Deci & Ryan (2000) â€” ThÃ©orie de l'autodÃ©termination (SDT)
- Mayer (2001) - Multimedia learning theory
- Kivetz et al. (2006) â€” Goal-gradient hypothesis â€” *Journal of Marketing Research*

> **Convention** : `[PROPOSITION]` = feature suggÃ©rÃ©e par l'IA, non issue des docs existants. Ã€ valider produit avant implÃ©mentation.

### 1.3 Formule de score composite

```
Score = (G Ãƒâ€” 1.5) + (E Ãƒâ€” 2) + B Ã¢Ë†â€™ (D Ãƒâ€” 0.8) Ã¢Ë†â€™ (R Ãƒâ€” 0.7)
```

Un score Ã©levÃ© indique une feature Ã  haute valeur et faible coÃ»t/risque. Le score **ne remplace pas** le jugement â€” il oriente la discussion.

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
| F04 | Revisions espacees (SM-2) | [PARTIAL] exercice livre end-to-end ; defis + F23 restent hors scope | 4 | 4 | 5 | 2 | 4 | **14.8** | P0 |
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
| F20 | Normalisation niveaux de difficulte | [PARTIAL] produit visible neutralise, legacy technique conserve | 4 | 3 | 2 | 3 | 3 | **6.9** | P2 |
| F21 | Badges secrets | [BACKLOG] | 2 | 3 | 2 | 1 | 2 | **9.0** | P2 |
| F22 | Suppression utilisateur admin (RGPD) | [DONE] | 2 | 1 | 1 | 2 | 3 | **4.7** | P2 |
| F35 | [TECH] Redaction secrets dans logs DB (URL SQLAlchemy) | [DONE] | 1 | 2 | 1 | 1 | 4 | **7.5** | P2 |
| F36 | [UX][TECH] Flash auth au refresh | [BACKLOG] | 2 | 2 | 1 | 1 | 3 | **7.2** | P2 |
| F37 | [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard | [BACKLOG] actif | 3 | 3 | 4 | 2 | 3 | **11.7** | P2 |
| F38 | [UX][Gamification] Progression compte coherente & historique des gains | [PARTIAL] runtime recale ; lecture produit du ledger encore manquante | 3 | 4 | 2 | 2 | 4 | **10.2** | P1 |
| F23 | [PROP] Exercices adaptatifs SR+IA | [BACKLOG] | 4 | 5 | 5 | 3 | 5 | **17.1** | P2* |
| F24 | Tuteur IA contextuel | [BACKLOG] | 5 | 5 | 5 | 3 | 5 | **16.1** | P3 |
| F25 | Mode classe / enseignant | [BACKLOG] | 5 | 4 | 4 | 3 | 5 | **14.9** | P3 |
| F26 | Filtres et tri badges | [DONE] | 2 | 2 | 1 | 1 | 2 | **6.4** | P3 |
| F27 | Optimisation re-renders exercices/defis | [BACKLOG] | 3 | 2 | 1 | 2 | 2 | **4.8** | P3 |
| F28 | Mode aventure / histoire narrative | [BACKLOG] | 5 | 5 | 3 | 3 | 5 | **13.1** | P4 |
| F29 | Personnalisation avatar / profil | [BACKLOG] | 3 | 3 | 1 | 1 | 2 | **7.1** | P4 |
| F34 | Module Sciences - Curiosites (Vrai/Faux, format court) | [BACKLOG] prototype seulement | 3 | 4 | 2 | 2 | 4 | **10.4** | P4 |
| F39 | [LEGAL] Refonte rangs & suppression IP Star Wars | [PARTIAL] visible neutralise ; `progression_rank` + `thematic_title` livres ; aliases legacy encore servis | 4 | 3 | 1 | 3 | 5 | **6.2** | P1* |
| F40 | Leaderboard â€” position de l'utilisateur hors top 50 | [DONE] | 2 | 4 | 2 | 1 | 3 | **10.7** | P2 |
| F41 | Leaderboard â€” filtre temporel (semaine / mois / tout) | [DONE] | 3 | 4 | 1 | 2 | 3 | **7.2** | P2 |
| F42 | Architecture difficultÃ© â€” sÃ©paration Ã¢ge et niveau sur 2 axes | [DONE] runtime F42 et boundaries alignes, legacy garde en compatibilite | 4 | 3 | 3 | 3 | 4 | **9.2** | P2 |

> *F23 a un score eleve mais depend de F04 (revisions espacees) - debloque apres F04.*
> *F39 : le visible produit est maintenant neutralise. Les migrations additives `progression_rank` et `thematic_title` sont livrees ; les aliases legacy restent intentionnellement servis pendant la transition.*

### 2.1 Vue d'avancement - visible, sans effacer le travail livre

**[DONE] Implemente dans le code**
- F01, F02, F03, F05, F06, F07, F12, F13, F22, F26, F32, F33, F35, F40, F41, F42

**[PARTIAL] Fondations deja posees**
- F04 : exercice scope livre (`P1`..`P5`) avec write path SM-2, resume dashboard, endpoint `reviews/next` et session `spaced-review` ; defis + F23 restent hors scope
- F14 : monitoring IA runtime + admin read-only + runs harness persistes, mais pas encore de persistance DB complete des metriques runtime
- F20 : normalisation visible de la difficulte livree, mais legacy backend/DB volontairement conserve
- F38 : moteur gamification persistant + ledger `point_events` + calcul niveau/XP/rang recales, mais pas encore d'historique utilisateur dedie ni de lecture produit complete du ledger
- F39 : rangs publics et surfaces visibles neutralises ; migrations additives `progression_rank` et `thematic_title` livrees ; aliases legacy encore servis

**[BACKLOG] Encore a livrer**
- le reste de la matrice, avec priorite conservee

### 2.2 Priorite operationnelle reelle (post-F04-P5)

Les scores `D/G/E/R/B` restent la base de reference. En revanche, l'ordre d'execution reel doit tenir compte :
- de l'etat deja livre dans le code
- des dependances entre features
- des dettes contractuelles visibles restantes
- du ratio valeur / risque a court terme

Ordre recommande maintenant :

1. **F38** - historique des gains et lecture produit coherente du ledger compte
2. **F37** - coherence dashboard / temporalite / charge cognitive
3. **F14** - persistance DB complete des metriques runtime IA
4. **F36** - suppression du flash auth au refresh
5. **F09** - dashboard parent
6. **F08** - objectifs personnalises
7. **F10** - mode focus / session ciblee
8. **F23** - exercices adaptatifs SR+IA, maintenant debloques par F04
9. **F30** - effet protege
10. **F31** - exemples resolus progressifs
11. **F11** - partage progression vers parents
12. **F16 / F17 / F18 / F19 / F21** - confort, engagement et croissance
13. **F24 / F25 / F27** - chantiers plus lourds ou structurels
14. **F28 / F29 / F34** - backlog lointain / produit

Lecture simple :
- **P0 operationnel** : F38, F37, F14
- **P1 operationnel** : F36, F09, F08, F10, F23
- **P2 operationnel** : F30, F31, F11, F16, F17, F18, F19, F21
- **P3 operationnel** : F24, F25, F27
- **P4 operationnel** : F28, F29, F34

---

## 3. P0 â€” Impact fort, fondements pÃ©dagogiques solides {#3-p0}

Ces quatre features combinent un score composite Ã©levÃ© ET un bÃ©nÃ©fice pÃ©dagogique scientifiquement robuste. Elles constituent le cÅ“ur de la valeur Ã©ducative de Mathakine.

---

### F01 â€” Rendu Markdown/KaTeX dans les explications

**Source** : [ROADMAP Ã‚Â§4.7](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.8 | D=2, G=4, E=5, R=1, B=3

**ProblÃ¨me** : Les explications post-rÃ©ponse (exercices et dÃ©fis) sont du texte brut. Les formules mathÃ©matiques (`aÂ³+bÂ³`) et les Ã©tapes structurÃ©es sont illisibles.

**Valeur pÃ©dagogique (E=5)** :
- Mayer (2001) - *Multimedia Learning* : la segmentation et la mise en forme du texte reduisent la charge cognitive extrinseque et ameliorent la comprehension (effet mesure).
- Sweller (1988) - Cognitive Load Theory : l'organisation visuelle de l'information reduit la charge cognitive irrelevante.
- La lisibilitÃ© de l'explication est un vecteur direct du transfert d'apprentissage.

**Ce qu'il faut faire** :
- IntÃ©grer `react-markdown` + `remark-math` + `rehype-katex` (ou `react-katex`) dans `ExerciseSolver` et `ChallengeSolver`
- Appliquer le rendu dans le bloc "Explication" de la rÃ©ponse
- Style CSS pour les formules math (KaTeX CSS)
- Optionnel : accordÃ©on "voir plus" si explication > 300 mots

**Effort estimÃ©** : 1-2 jours

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© â€” composant `frontend/components/ui/MathText.tsx` (react-markdown + remark-math + rehype-katex), intÃ©grÃ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver` et `DiagnosticSolver`

---

### F02 â€” DÃ©fis quotidiens (dÃ©fi du jour) Ã¢Å“â€¦

**Source** : [ROADMAP Ã‚Â§3.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.9 | D=3, G=5, E=4, R=2, B=5

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© (Mars 2026)

**Valeur pÃ©dagogique (E=4)** :
- Cepeda et al. (2006) â€” La pratique distribuÃ©e (daily sessions) produit une meilleure rÃ©tention que la pratique massÃ©e, indÃ©pendamment du temps total (d = 0.46-0.71).
- Deci & Ryan (2000) â€” SDT : les dÃ©fis quotidiens optionnels, adaptÃ©s au niveau, soutiennent le besoin de compÃ©tence sans pression externe (contrairement aux streaks punitifs).

**Conception implÃ©mentÃ©e** : 3 dÃ©fis par jour (volume_exercises, specific_type, logic_challenge), bonus XP, expiration minuit, pas de punition si manquÃ©.

**RÃ©fÃ©rence technique complÃ¨te** : [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---


### F03 â€” Test de diagnostic initial

**Source** : [ROADMAP Ã‚Â§3.5](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.0 | D=3, G=4, E=5, R=2, B=4

**ProblÃ¨me** : L'onboarding collecte les prÃ©fÃ©rences (classe, Ã¢ge, rythme) mais pas le niveau rÃ©el. Les premiÃ¨res recommandations peuvent Ãªtre inadaptÃ©es, dÃ©gradant le moment critique des 5 premiÃ¨res minutes.

**Valeur pÃ©dagogique (E=5)** :
- Hattie (2009) â€” *Formative assessment* : d = 0.90 (un des effets les plus Ã©levÃ©s en Ã©ducation). Identifier le niveau rÃ©el avant l'enseignement est la condition prÃ©alable Ã  toute personnalisation efficace.
- Sweller (1988) - L'alignement entre difficulte et competence previent la surcharge cognitive (exercices trop faciles = ennui, trop difficiles = anxiete).
- *Assessment for learning* (Black & Wiliam, 1998) : le diagnostic prÃ©alable est la fondation de l'apprentissage adaptatif.

**Algorithme adaptatif (Item Response Theory simplifiÃ©)** :
```
1. Commencer au niveau mÃ©dian
2. Correct Ã¢â€ â€™ question plus difficile (niveau +1)
3. Incorrect Ã¢â€ â€™ question plus facile (niveau -1)
4. ArrÃªt : 2 erreurs consÃ©cutives au mÃªme niveau Ã¢â€ â€™ niveau Ã©tabli
5. DurÃ©e max : 10 questions, ~5 minutes
```

**Output** :
- `initial_level` par type d'exercice (addition, soustraction, multiplication, division, logique)
- StockÃ© dans `diagnostic_results` (table dÃ©diÃ©e, scores JSONB par type)
- Alimente immÃ©diatement les recommandations

**Effort estimÃ©** : 3-5 jours

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© le 04/03/2026

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
| `/api/exercises/generate` ignore le niveau diagnostic | Un utilisateur scorant InitiÃ© reÃ§oit des exercices selon `age_group`, pas son niveau rÃ©el | Moyen | Ã¢Å“â€¦ RÃ©solu 06/03/2026 â€” `adaptive_difficulty_service` cÃ¢blÃ© en Ã©tape 1 de la cascade |
| `preferred_difficulty` stocke des age_group (`"adulte"`) mais le service attendait des DifficultyLevels | Zyclope (adulte) tombait en fallback PADAWAN malgrÃ© son profil | Moyen | Ã¢Å“â€¦ RÃ©solu 06/03/2026 â€” `_PREF_DIFFICULTY_TO_ORDINAL` Ã©largi aux deux formes |
| Mode de rÃ©ponse QCM/saisie libre calculÃ© sur la difficultÃ© de l'exercice, pas le niveau rÃ©el utilisateur | Un utilisateur INITIE pouvait se voir forcer la saisie libre si l'exercice Ã©tait GRAND_MAITRE | Moyen | Ã¢Å“â€¦ RÃ©solu 06/03/2026 â€” Frontend lit les scores IRT via `useIrtScores()`, dÃ©cide par type |
| Types non couverts IRT (MIXTE, FRACTIONS) sans proxy de niveau | Pas d'adaptation pour ces types | Moyen | Ã¢Å“â€¦ RÃ©solu 06/03/2026 â€” Proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division) |
| Dashboard (`/`) ne lit pas `has_completed` | Pas de message de confirmation "ton niveau a Ã©tÃ© Ã©tabli" | Faible | Ã¢ÂÂ³ Backlog |
| GÃ©nÃ©ration IA (`/api/ai/generate`) ignore le diagnostic | MÃªme problÃ¨me que le gÃ©nÃ©rateur interne | Moyen | Ã¢ÂÂ³ Backlog |

---

### F04 â€” RÃ©visions espacÃ©es (algorithme SM-2)

**Source** : [ROADMAP Ã‚Â§3.3](ROADMAP_FONCTIONNALITES.md)  
**Score** : 14.8 | D=4, G=4, E=5, R=2, B=4

**Statut actuel** : [PARTIAL] exercice livre end-to-end (`F04-P1`..`F04-P5`) ; restent hors scope de ce train :
- integration defis
- compteur `X revisions restantes`
- distinction analytics plus fine pour `spaced-review`
- couplage futur F23 (`SR + IA`)

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
- Suivantes : intervalle Ãƒâ€” ease_factor

Ajustement ease_factor (EF, init 2.5) :
- RÃ©ponse correcte rapide (qualitÃ© 4-5) : EF + 0.1
- RÃ©ponse correcte lente (qualitÃ© 3) : EF inchangÃ©
- RÃ©ponse incorrecte (qualitÃ© 0-2) : EF Ã¢Ë†â€™ 0.2, retour J+1
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

### F05 â€” Adaptation dynamique de difficultÃ© Ã¢Å“â€¦

**Source** : [WORKFLOW_EDUCATION Ã‚Â§2.2](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)  
**Score** : 13.9 | D=4, G=4, E=5, R=3, B=4

**Valeur pÃ©dagogique (E=5)** :
- Vygotsky (1978) - Zone proximale de developpement : l'apprentissage optimal se situe juste au-dela de la competence actuelle. Trop facile -> ennui. Trop difficile -> anxiete.
- Bjork (1994) â€” *Desirable difficulties* : un niveau de dÃ©fi optimal crÃ©e une rÃ©sistance productive (retrieval effort) qui renforce la mÃ©morisation Ã  long terme.
- Csikszentmihalyi (1990) - Etat de *flow* : atteint quand difficulte ~ competence.

**ImplÃ©mentation (v3.0.0-alpha.3+, MAJ 06/03/2026)** :
- `app/services/adaptive_difficulty_service.py` â€” rÃ©solution par cascade (IRT > progression > profil > fallback), proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division)
- `server/handlers/exercise_handlers.py` â€” branchement adaptatif (`?adaptive=true` par dÃ©faut, dÃ©sactivable par `?adaptive=false` ou `age_group` explicite)
- `app/utils/exercise_generator_helpers.py` -> distracteurs QCM calibres par niveau (INITIE: erreurs +/-1 + inversion, PADAWAN: retenue +/-10, CHEVALIER/MAITRE/GRAND_MAITRE: magnitude en %, `server/exercise_generator_helpers.py` restant un re-export de compatibilite)
- **Mode QCM vs saisie libre** : dÃ©cidÃ© cÃ´tÃ© frontend par `useIrtScores().resolveIsOpenAnswer(exercise_type)` â€” saisie libre uniquement si niveau IRT = GRAND_MAITRE pour ce type. Le backend gÃ©nÃ¨re toujours les `choices`.

**RÃ©fÃ©rence technique complÃ¨te** : [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md)

**Seuils adaptation temps reel** : `completion_rate > 85% ET streak >= 3` -> boost (+1 niveau) ; `completion_rate < 50% ET streak = 0` -> descente (-1 niveau).

**Hors scope F05-suite (backlog)** :
- `/api/ai/generate` â€” mÃªme adaptation pour la gÃ©nÃ©ration IA (SSE, complexitÃ© sÃ©parÃ©e)
- Dashboard widget 'ton niveau s'est ajuste' - [DONE] Implemente le 06/03/2026 (`LevelEstablishedWidget` dans l'onglet Vue d'ensemble)
- Seuils boost/descente configurables via admin
- **[F05-B1] Saisie libre dÃ©clenchÃ©e par taux de rÃ©ussite rÃ©el, pas uniquement par niveau IRT** : plutÃ´t que le seuil fixe GRAND_MAITRE, dÃ©clencher la saisie libre quand `completion_rate >= 90 % sur les 5 derniÃ¨res tentatives` pour un type donnÃ© â€” indÃ©pendamment du niveau IRT. Fondement : Roediger & Karpicke (2006) Testing Effect + VanLehn (2011) mÃ©ta-analyse tutoring adaptatif. Ã‰viter d'encoder des erreurs en forÃ§ant le recall avant que la rÃ©cupÃ©ration soit automatique.
- **[F05-B2] Distracteurs QCM plus discriminants, moins dÃ©ductibles** : amÃ©liorer la gÃ©nÃ©ration des `choices` pour Ã©viter les bonnes rÃ©ponses visibles par simple Ã©limination. Cible : 3 distracteurs plausibles, de mÃªme ordre de grandeur, mÃªme format et mÃªme unitÃ© que la bonne rÃ©ponse, issus d'erreurs typiques rÃ©elles (retenue, inversion, confusion opÃ©ratoire, off-by-one, confusion quotient/reste) plutÃ´t que de valeurs trop Ã©loignÃ©es ou structurellement diffÃ©rentes. Ajouter si possible une instrumentation du taux de sÃ©lection des distracteurs pour identifier ceux qui ne trompent jamais. Effort estimÃ© : 1-2 jours. PrioritÃ© produit : moyenne-haute, car impact direct sur la valeur pÃ©dagogique perÃ§ue des exercices.

**DÃ©pendance** : Profite du diagnostic initial (F03) et prÃ©pare les rÃ©visions espacÃ©es (F04).


---

### F06 - Conditions d'obtention badges visibles

**Source** : [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) - section 4.2  
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

### F07 â€” Courbe d'Ã©volution temporelle

**Source** : [ANALYTICS_PROGRESSION Ã‚Â§1.1](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ANALYTICS_PROGRESSION.md)  
**Score** : 11.2 | D=3, G=4, E=3, R=2, B=3

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© le 07/03/2026

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

**Source** : [ROADMAP Ã‚Â§4.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.1 | D=3, G=3, E=3, R=1, B=3

**Valeur pÃ©dagogique (E=3)** :
- Deci & Ryan (2000) â€” SDT : les objectifs auto-dÃ©terminÃ©s (choisis par l'utilisateur, pas imposÃ©s) renforcent la motivation intrinsÃ¨que et le besoin d'autonomie.
- Locke & Latham (1990) â€” *Goal-setting theory* : des objectifs spÃ©cifiques et mesurables amÃ©liorent la performance. Effet plus fort quand l'objectif est choisi par l'individu.

**Types** : Quotidien (ex: 5 exercices/jour), hebdomadaire, de maÃ®trise (ex: "atteindre 80% en division").

**Effort estimÃ©** : 3-5 jours

---

### F09 â€” Dashboard parent

**Source** : [ROADMAP Ã‚Â§3.1](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.4 | D=4, G=4, E=3, R=2, B=5

**Valeur pÃ©dagogique (E=3)** :
- Hattie (2009) â€” *Parental involvement* : d = 0.49. L'implication parentale dans le suivi scolaire a un effet positif mesurable sur les rÃ©sultats.
- Bryk & Schneider (2002) â€” La confiance famille-institution est un prÃ©dicteur de l'engagement Ã  long terme.

**Architecture minimale (MVP)** :
```
Table: parent_child_links (parent_user_id, child_user_id, created_at, permissions JSON)
Route: /parent/dashboard Ã¢â€ â€™ vue enfants
Route: /parent/child/[id] Ã¢â€ â€™ progression dÃ©taillÃ©e
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

### F12 - Radar chart par discipline

**Source** : [ANALYTICS_PROGRESSION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ANALYTICS_PROGRESSION.md) - section 1.3  
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

**Source** : [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) - section 4.4  
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

### F32 â€” [PROPOSITION] Mode "Pratique EntrelacÃ©e" (Interleaving) Ã¢Å“â€¦

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 14.5 | D=2, G=3, E=5, R=2, B=3

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© le 07/03/2026

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

### F33 â€” Feedback "Growth Mindset" Ã¢Å“â€¦

**Source** : Proposition IA â€” non issue des docs existants  
**Score** : 11.4 | D=1, G=3, E=3, R=1, B=2

> *Score initial proposÃ© : 13.0 (E=4). EdTech rÃ©visÃ© Ã  E=3 : les Ã©tudes Dweck sont robustes mais les interventions de Growth Mindset par texte seul ont des effets faibles sans accompagnement long terme. Yeager et al. (2019) mesure des effets sur populations dÃ©favorisÃ©es spÃ©cifiques â€” le transfert Ã  une plateforme gÃ©nÃ©raliste est conditionnel.*

**Statut** : Ã¢Å“â€¦ ImplÃ©mentÃ© le 07/03/2026

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
| **F14 - Monitoring IA persistance DB** | [PARTIAL] Le runtime monitoring et l'admin read-only existent deja (`token_tracker`, `generation_metrics`, `/admin/ai-monitoring`) ainsi que la persistance DB des runs harness. Le backlog restant porte sur une persistance DB complete des metriques runtime live, aujourd'hui surtout en memoire process. |
| **F15 â€” PrÃ©fÃ©rence page d'accueil** | Champ `login_redirect_preference` sur `User`. Option dans ParamÃ¨tres. ~Â½ jour. |
| **F16 â€” Heatmap d'activitÃ©** | Calendrier GitHub-style sur Dashboard/Profil. `react-calendar-heatmap`. Endpoint : `GET /api/users/me/activity/heatmap`. |
| **F17 â€” CÃ©lÃ©brations visuelles amÃ©liorÃ©es** | Confettis au dÃ©blocage badge, modal avec partage. DÃ©sactivable (accessibilitÃ©). |
| **F18 - Ligues hebdomadaires** | Le leaderboard existe deja (top 50, filtres, surfaces de lecture), mais pas encore les ligues / saisons hebdomadaires. Le backlog porte sur les groupes, promotions/relegations et resets periodiques. Score EdTech=1 : engagement, pas d'apprentissage direct. |
| **F19 â€” Notifications push + email** | Rappel inactivitÃ©, streak en danger, badge proche. Voir [ROADMAP Ã‚Â§4.1](ROADMAP_FONCTIONNALITES.md). Infrastructure Ã  dÃ©finir (service push web + SMTP). |
| **F20 â€” Normalisation niveaux de difficultÃ©** | Remplacer nomenclature Star Wars par libellÃ©s universels. Voir [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md) et le manifeste technique associÃ©. Migration enum risquÃ©e â€” Ã  planifier soigneusement. |
| **F21 â€” Badges secrets** | Badges cachÃ©s dÃ©bloquÃ©s pour comportements inattendus (ex: "Noctambule" aprÃ¨s minuit). Variable reward (Skinner) â€” engagement Ã©levÃ©. |
| **F22 - Suppression utilisateur admin (RGPD)** | [DONE] `DELETE /api/admin/users/{id}` existe deja cote admin. Le code supprime physiquement l'utilisateur avec cascade (pas un simple soft delete) et bloque l'auto-suppression admin. |
| **F35 â€” [TECH] Redaction secrets logs DB Ã¢Å“â€¦** | ImplÃ©mentÃ© le 07/03/2026. `app/db/base.py` loggue dÃ©sormais une URL redigÃ©e via `redact_database_url_for_log()` (credentials et query params masquÃ©s). Couvert par `tests/unit/test_db_log_redaction.py` (7 tests). |
| **F36 â€” [UX][TECH] Flash auth au refresh** | Artefact visuel observÃ© aprÃ¨s refresh: pendant ~0.5s, le frontend semble repasser par un Ã©tat "non connectÃ©" avant rehydratation correcte de la session. Backend session validÃ©: login OK, session conservÃ©e aprÃ¨s refresh et aprÃ¨s idle prolongÃ©. Cible: supprimer le flash sans changer la chaÃ®ne de session/cookies. Piste probable: bootstrap auth frontend (`ProtectedRoute`, `current-user`, `validate-token`, `sync-cookie`). Ouvrir un lot dÃ©diÃ© seulement si le symptÃ´me devient gÃªnant ou s'accompagne d'une redirection parasite/perte de session. |
| **F37 - [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard** | Clarifier la portee des filtres temporels dans le dashboard. Conclusion de l'analyse UX : un controle = un perimetre visible. Les widgets temporels doivent avoir un selecteur local ou une periode partagee explicite ; les widgets cumules doivent afficher un badge de portee (`Cumule`, `Tous les temps`) plutot qu'un faux selecteur. Les vues journalieres redondantes dans `Progression` doivent etre rationalisees au profit d'un widget complementaire (ex : regularite de pratique). Si l'on veut une coherence temporelle complete de l'onglet `Progression`, ouvrir ensuite un lot dedie data/hooks/backend pour exposer une periode explicite sur les widgets aujourd'hui cumules. |
| **F38 - [UX][Gamification] Progression compte coherente & historique des gains** | [PARTIAL] Le moteur persistant, le ledger `point_events`, le calcul niveau/XP/rang et plusieurs surfaces de lecture existent deja. Le backlog F38 porte maintenant sur la surface produit coherente : historique des gains, lecture par source et presentation compte explicite. |
| **F23 â€” [PROP] Exercices adaptatifs SR+IA** | GÃ©nÃ©rer des exercices IA ciblÃ©s sur les concepts Ã  rÃ©viser selon la courbe SR (F04). Score composite trÃ¨s Ã©levÃ© (17.1) mais **dÃ©pend de F04**. DÃ©bloquÃ© aprÃ¨s F04. |

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

### F39 - [LEGAL] Refonte rangs et suppression IP Star Wars

**Score** : 6.2 | D=4, G=3, E=1, R=3, B=5

**Statut** : [PARTIAL] Le visible produit est neutralise. `F43-A3` est livre ; la dette restante est surtout contractuelle et technique.

**Probleme reel restant** :
- les labels visibles ne fuitent plus l'univers Star Wars dans les surfaces produit principales
- mais certains noms de champs contractuels restent legacy (`jedi_rank`, `star_wars_title`)
- ces reliquats sont encore visibles pour les integrateurs, Swagger et certains consumers techniques
- les enums/valeurs legacy (`PADAWAN`, `CHEVALIER`, `MAITRE`, etc.) existent encore dans le backend et la persistance

**Decision architecture / produit** :
- **ne pas** lancer un renommage global du legacy
- **ne pas** casser les payloads existants brutalement
- traiter les reliquats visibles par **migration additive**

**Strategie retenue (safe)** :
1. **Phase additive**
   - ajouter une cle neutre a cote de la cle legacy
   - documenter la cle legacy comme `deprecated`
2. **Phase de bascule**
   - frontend, docs et consumers internes lisent uniquement la nouvelle cle
   - la cle legacy reste servie pour compatibilite
3. **Phase de retrait**
   - suppression de la cle legacy seulement apres verification qu'aucun client n'en depend encore

**Lots recommandes dans la roadmap** :
- ~~**F43-A3** - migration contractuelle additive `jedi_rank` -> `progression_rank`~~ **FAIT** (2026-03-28) : cle `progression_rank` ajoutee cote API publique + consumers frontend prioritaires ; `jedi_rank` conserve (alias).
- ~~**F43-A4** - migration contractuelle additive `star_wars_title` -> `thematic_title`~~ **FAIT** (2026-03-28) : cle `thematic_title` sur payloads badges publics + `new_badges` (tentatives) ; `star_wars_title` conserve (alias, meme valeur). (**priorite immediate**)

**Ce que ces lots doivent faire** :
- ajouter les nouvelles cles sans casser le JSON existant
- marquer les anciennes comme legacy/deprecated dans les schemas et la doc API
- basculer les consumers internes du repo sur les nouvelles cles
- garder une fenetre de compatibilite explicite

**Ce que ces lots ne doivent pas faire** :
- renommer les colonnes DB en urgence
- renommer les enums persistants sans migration dediee
- ouvrir un refactor transversal "tout legacy" dans le meme lot

**Dette acceptable a laisser pour plus tard** :
- noms d'enum techniques (`PADAWAN`, `CHEVALIER`, `MAITRE`)
- fonctions/helpers internes type `jedi_rank_for_level()`
- couches de compatibilite backend/DB qui ne fuient plus cote produit

**Relation avec F20 et F42** :
- **F20** a neutralise le visible pedagogique, mais conserve volontairement du legacy backend/DB
- **F42** a etabli le modele canonique runtime pour la difficulte
- **F39** prolonge ce nettoyage sur les contrats visibles, de facon progressive et sure

**Critere de cloture F39** :
- plus de wording sous licence dans les surfaces visibles
- plus de reliquat legacy impose aux nouveaux consumers de l'API
- les anciennes cles contractuelles sont soit retirees apres compat, soit explicitement isolees comme dette technique assume

---
## 6. P3 â€” Investissement long terme {#6-p3}

### F24 â€” Tuteur IA contextuel

**Score** : 16.1 | D=5, G=5, E=5, R=3, B=5

**Valeur pÃ©dagogique (E=5) â€” parmi les plus fortes en EdTech** :
- VanLehn (2011) â€” *Educational Psychologist* : Les systÃ¨mes de tutoriels intelligents (ITS) atteignent d = 0.55â€“0.66 par rapport aux classes classiques. Seul le tutorat humain individuel fait mieux (d Ã¢â€°Ë† 2.0).
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

**Prototype** : [../assets/prototypes/F34_SCIENCES_PROTOTYPE.html](../assets/prototypes/F34_SCIENCES_PROTOTYPE.html) â€” HTML statique (Tailwind, Font Awesome, JS vanilla). Ã€ intÃ©grer en Next.js + API.

**Effort estimÃ©** : 1â€“2 semaines (modÃ¨le + API + page `/sciences` + intÃ©gration design system)

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
| Espace admin complet (role archiviste) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md) |
| Auth complet (inscription, email, login, reset) | Jan-Fev 2026 | [AUTH_FLOW](AUTH_FLOW.md) |
| Sessions actives + revocation | 16/02/2026 | SITUATION_FEATURES (archive) |
| Leaderboard (top 50, enrichissement avatar / sÃ©rie / badges) | 25/03/2026 | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) |
| Badges - refonte UX (onglets, cartes compactes) | 17/02/2026 | [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) |
| Badges - barres de progression (goal-gradient) | 16/02/2026 | [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) |
| Badges - B4 reformulation (17 badges) | 17/02/2026 | Archive : AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES |
| Badges - moteur generique Lot C (defis, mixte) | 17/02/2026 | Archive : AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES |
| Quick Win #1 - First Exercise < 90s | Fev 2026 | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md) |
| Quick Win #2 - Onboarding pedagogique | Fev 2026 | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md) |
| Calibration a l'inscription (classe, age, objectif) | Fev 2026 | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md) |
| Parcours guide (QuickStartActions dashboard) | Fev 2026 | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md) |
| Recommandations personnalisees (marquer fait) | 16/02/2026, MAJ 24/03/2026 | SITUATION_FEATURES (archive) + dashboard `Recommendations.tsx` borne maintenant l'affichage initial a 6 cartes avec toggle local |
| Ordre aleatoire + masquer reussis | 19/02/2026 | SITUATION_FEATURES (archive) |
| Analytics EdTech (CTR Quick Start, 1er attempt) | 25/02/2026 | [EDTECH_ANALYTICS](EDTECH_ANALYTICS.md) |
| Monitoring IA (in-memory) | 22/02/2026 | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section 4.6 |
| Mode maintenance + inscriptions (admin config) | 16/02/2026 | [ADMIN_ESPACE_PROPOSITION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md) |
| Streak (basique) | Fev 2026 | Integre dans stats utilisateur |
| 7 themes visuels | Fev 2026 | [THEMES](THEMES.md) |
| PWA (mode hors-ligne partiel) | Fev 2026 | - |
| Internationalisation FR/EN | Jan 2026 | [I18N](I18N.md) |
| Accessibilite (5 modes WCAG AAA) | Fev-Mars 2026 | [ACCESSIBILITY](../04-FRONTEND/ACCESSIBILITY.md) |

### 8.2 Fondations techniques deja posees mais encore incompletes cote produit

| Feature | Borne de verite | Ce qui existe deja | Ce qui reste a livrer |
|---------|-----------------|--------------------|-----------------------|
| **F40 â€” Leaderboard position utilisateur hors top 50** | PlanifiÃ© 25/03/2026 | Classement top 50 + `is_current_user` flag sur chaque entrÃ©e. | Nouvel endpoint `GET /api/users/me/rank` (COUNT query) + injection rang courant en bas de liste avec sÃ©parateur visuel. Effort S. **Aucun prÃ©requis â€” livrable aprÃ¨s L2 sans F42.** F42 est prÃ©requis de F40-v2 (rang filtrÃ© par groupe d'Ã¢ge) uniquement. |
| **F41 â€” Leaderboard filtre temporel** | LivrÃ© 24/03/2026 (lot L3-B) | `GET /api/users/leaderboard?period=all\|week\|month` + `GET /api/users/me/rank?period=â€¦` ; agrÃ©gation `SUM(points_delta)` sur `point_events` (fenÃªtres glissantes 7j / 30j UTC) ; sÃ©lecteur pÃ©riode sur la page classement. | **DÃ©ploiement produit** : si `point_events` est trÃ¨s peu peuplÃ©, privilÃ©gier le dÃ©faut Â« Tout temps Â» en communication ; surveiller taux de liste vide en Â« 7 jours Â». |
| **F42 â€” Architecture difficultÃ©/Ã¢ge â€” sÃ©paration des deux axes** | [DONE] 27/03/2026 | P1 : `users.age_group`, profil et API. P2 : `difficulty_tier` sur `exercises` et `logic_challenges`, reco exercices tier Â±1 et scoring dÃ©fis par distance de tier. P3 : runtime exercice 4x3, bridges progression/diagnostic, personalization dÃ©fis IA, boundaries admin/API et documentation F42. | Dette assumÃ©e : les champs legacy (`difficulty`, `mastery_level`, `difficulty_rating`) restent comme couches de compatibilitÃ© et de stockage ; pas de migration de suppression ouverte. |
| **Leaderboard â€” filtre par groupe d'Ã¢ge (utilisateur)** | Report 25/03/2026 (lot L1) | Le classement expose `limit` et des champs enrichis ; le paramÃ¨tre `age_group` a Ã©tÃ© **retirÃ©** car il filtrait Ã  tort sur `preferred_difficulty` (difficultÃ© easy/medium/hard â‰  tranche d'Ã¢ge). | DÃ©pend de F42 Phase 1 (colonne `age_group` sur `User`) puis F40. |
| F14 - Monitoring IA persistance DB | Code au 23/03/2026 | monitoring runtime, admin `/admin/ai-monitoring`, token tracker, generation metrics, persistance des runs harness | persistance DB complete des metriques runtime live |
| F38 - Progression gamification compte coherente & historique des gains | Code au 23/03/2026 | `point_events`, `GamificationService.apply_points`, calcul niveau/XP/rang, surfaces `/api/users/me`, `/api/badges/stats`, `/api/badges/user`, `/api/users/leaderboard` | historique utilisateur dedie, agregats par source, UX compte lisible |

### 8.3 Decision d'architecture - Separation des axes difficulte et groupe d'age (F42)

F42 est maintenant livre.

La regle architecture a retenir est simple :

`age_group + pedagogical_band -> difficulty_tier`

### Ce que F42 a ferme

- separation claire entre age pedagogique et niveau de maitrise
- tier F42 `1..12` pour le contenu
- bridges progression/diagnostic -> F42 sans migration de suppression
- generation locale d'exercices pilotee par un vrai contexte adaptatif
- personnalisation des defis IA a partir du contexte utilisateur
- boundaries admin/API alignees sur `difficulty_tier`

### Ce qui reste volontairement legacy

- `difficulty`
- `mastery_level`
- `difficulty_rating`

Ces champs restent legitimes :
- pour le stockage
- pour la compatibilite de contrat
- pour certains chemins historiques

Ils ne sont plus la verite fine unique.

### Regle de lecture pour la suite

- nouvelle logique pedagogique fine -> partir de `age_group`, `pedagogical_band`, `difficulty_tier`
- nouveau wording utilisateur -> ne pas exposer les labels legacy bruts
- nouveau contrat public -> preferer les champs F42 si une finesse pedagogique est requise

### Relation avec les autres features

- F40-v2 (filtre leaderboard par groupe d'age) reste desormais deblocable sans remettre en cause le modele
- F04, F23 et les futurs lots adaptatifs pourront reutiliser le tier F42 plutot que recreer une logique parallele
- une migration plus forte du legacy n'est pas urgente ; elle deviendra utile seulement si le produit veut persister plus largement le canon F42

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

> Note de rationalisation (28/03/2026) : les anciennes notes feature isolÃ©es encore utiles pour le contexte ont Ã©tÃ© dÃ©placÃ©es dans `docs/03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/`. La vÃ©ritÃ© active reste portÃ©e par cette roadmap, les docs runtime actives et le code vivant.

| Sujet | Document |
|-------|----------|
| Carte du dossier features | [README.md](README.md) |
| SpÃ©cifications graphiques analytics | [ANALYTICS_PROGRESSION.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ANALYTICS_PROGRESSION.md) |
| Fondements psychologiques badges | [BADGES_AMELIORATIONS.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) |
| Workflow utilisateur complet | [WORKFLOW_EDUCATION_REFACTORING.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md) |
| Normalisation difficultÃ© | [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md) + [DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md) |
| Auth flow | [AUTH_FLOW.md](AUTH_FLOW.md) |
| Admin (pÃ©rimÃ¨tre, sÃ©curitÃ©) | [ADMIN_ESPACE_PROPOSITION.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md), [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) |
| Analytics EdTech (implÃ©mentÃ©) | [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md) |
| Endpoints API | [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) |
| ThÃ¨mes visuels | [THEMES.md](THEMES.md) |
| Internationalisation | [I18N.md](I18N.md) |
| Badges implÃ©mentÃ©s (archive) | [AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md) |
