# Backlog & Priorisation des Features Ã¢â‚¬â€ Mathakine

> **Document vivant** - Derniere MAJ : 06/04/2026 (realignement verite terrain : parent priorise, F15/F36 recales, NI-03 partiel, NI-09 livre ; F42 clos, A44 clos, F43 migrations additives livrees, F04 exercice livre jusqu'a P5, F44 backlog produit defis documente)  
> **RÃƒÂ´le** : Source de vÃƒÂ©ritÃƒÂ© unique pour toutes les features ÃƒÂ  implÃƒÂ©menter.  
> **Cible** : Enfants 5-20 ans + Parents. Contexte : plateforme EdTech maths adaptative.

---

## Table des matiÃƒÂ¨res

1. [MÃƒÂ©thodologie de priorisation](#1-mÃƒÂ©thodologie-de-priorisation)
2. [Matrice synthÃƒÂ¨se Ã¢â‚¬â€ Toutes les features](#2-matrice-synthÃƒÂ¨se)
3. [P0 Ã¢â‚¬â€ Impact fort, fondements pÃƒÂ©dagogiques solides](#3-p0)
4. [P1 Ã¢â‚¬â€ Haute prioritÃƒÂ©](#4-p1) _(dont F30, F31, F32 Ã¢â‚¬â€ nouvelles)_
5. [P2 Ã¢â‚¬â€ PrioritÃƒÂ© moyenne](#5-p2)
6. [P3 Ã¢â‚¬â€ Investissement long terme](#6-p3)
7. [P4 Ã¢â‚¬â€ Backlog distant](#7-p4)
8. [Features implementees (historique)](#8-features-implementees)
9. [RÃƒÂ©fÃƒÂ©rences scientifiques](#9-rÃƒÂ©fÃƒÂ©rences-scientifiques)

---

## Addendum - 2026-04-05

Apres stabilisation du train visible `3.6.0-alpha.1`, le prochain ajout produit
vise a etre le **dashboard parent + gestion des enfants**.

Ce cadrage ne change pas le fait que `parent` n'est **pas encore** implemente.
Il donne simplement la priorite produit suivante a :

- `F09` dashboard parent
- le futur role metier `parent`
- la relation parent-enfant
- la surface `/parent/dashboard`

Spec associee :

- [PARENT_DASHBOARD_AND_CHILD_LINKS.md](PARENT_DASHBOARD_AND_CHILD_LINKS.md)

---

## Addendum - 2026-04-06 — Neuro-inclusion et discipline UX (tickets d'implementation)

**Source de verite detaillee** : [DEBAT_NEURO_INCLUSION_2026-03-30.md](../03-PROJECT/DEBAT_NEURO_INCLUSION_2026-03-30.md)

Ce lot traduit les chantiers A-H du document d'audit en **tickets executables**.
Etat terrain au 06/04/2026 :

- `NI-03` est **entame** cote discovery/lists (`Exercises` + `Challenges` alignes, progressive disclosure et generateur hierarchise), mais le compromis final reste a valider.
- `NI-09` est **livre** (`useCountUp` recale, warnings React critiques nettoyes, lint propre).
- le reste des tickets NI ci-dessous reste **ouvert**.

### Tickets (ordre d'execution recommande)

| ID    | Titre                                               | Sprint | Fichiers / zone principale                                                                                              | Definition of done (resume)                                                                                                                                     |
| ----- | --------------------------------------------------- | -----: | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NI-01 | Onboarding : max 2 decisions avant premiere valeur  |      1 | `frontend/app/onboarding/page.tsx`, `frontend/messages/fr.json`, `frontend/messages/en.json`                            | Parcours redefini ; `learningGoal` et `practiceRhythm` reportes apres premiere pratique ou profil ; progression visible ; message de valeur avant soumission    |
| NI-02 | Primitives tactiles minimum 44x44 sur mobile        |      1 | `frontend/components/ui/button.tsx`, `select.tsx`, `switch.tsx`, toolbars (`AIGeneratorBase`, pages concernees)         | Cibles interactives principales >= 44px en contexte mobile ; pas de regression de layout majeure                                                                |
| NI-03 | Page defis : compromis acces rapide / filtres       |      1 | `frontend/app/challenges/page.tsx`, `ContentListProgressiveFilterToolbar.tsx`, `AIGenerator.tsx`, `AIGeneratorBase.tsx` | Fast path + filtres avances accessibles en **une** ouverture de panneau max ; criteres pragmatiques (actions jusqu'a filtre utile / lancement defi) documentes  |
| NI-04 | Contextes visuels Education / Hybrid / Gamification |      2 | `frontend/app/globals.css`, `frontend/components/shared/ContentCardBase.tsx`, conventions composants                    | Trois contextes nommes et **enforceables** (doc + conventions Tailwind / segregation imports ou variantes) ; pas d'heritage accidentel overdrive sur l'educatif |
| NI-05 | Shared UI : reduire effets demonstratifs fugitifs   |      2 | `globals.css`, `LevelIndicator.tsx`, `StudentChallengesBoard.tsx`, autres cartes partagees                              | Surfaces **Education Core** stables quel que soit le theme ; shell gamification garde l'expressivite assumee                                                    |
| NI-06 | Hardcodes couleur vers tokens semantiques           |      2 | `frontend/components/challenges/ChallengeSolver.tsx`, autres fichiers listes dans l'audit                               | Couleurs prioritaires via tokens ; pas de tons fixes hors systeme sur solveurs / zones critiques                                                                |
| NI-07 | Resilience : global-error et error boundaries       |      3 | `frontend/app/global-error.tsx`, `frontend/app/error.tsx`, boundaries onboarding / challenges / solveurs                | Fallbacks critiques alignes design system ; ton rassurant et actionnable ; pas d'inline style hors systeme sur chemins critiques                                |
| NI-08 | Preuve A11y : tests Axe + garde-fou CI              |      3 | `frontend/__tests__`, config Vitest, workflow CI si applicable                                                          | Au moins **un** test Axe par surface critique (onboarding, espace apprenant, defis, challenge solver) ; regressions majeures visibles avant merge               |
| NI-09 | Dette lint / perf : `useCountUp` et warnings React  |      3 | `frontend/lib/hooks/useCountUp.ts`, fichiers signales par `npm run lint` sur la couche critique                         | Constat aligne sur le lint reel ; plus de warning React **significatif** sur la couche critique ; formatage des fichiers touches propre                         |

**Dependances** : NI-04 fige la nomenclature technique des contextes — NI-05 s'appuie dessus ou progresse en parallele sur des classes deja identifiees. **NI-08 peut demarrer en parallele du Sprint 1** pour limiter les regressions pendant NI-02 / NI-03.

**Positionnement vs matrice F\*** : le lot **complete** la charge cognitive et la coherence UX (proche de **F37**) sans remplacer **F38** (lecture ledger), **F14** ou **F09**. Ordre fondateur suggere pour un solo founder : enchainer **NI-01 → NI-02 → NI-03**, puis trancher entre **F38** et **NI-04** selon la pression immediate (activation utilisateur vs systematicite du design system).

**Critere produit ouvert** : NI-03 reste partiellement subjectif (« compromis juge efficace ») — completer par **metriques** (ex. nombre d'actions jusqu'a un filtre utile) ou un **test utilisateur court** avant de fermer le ticket.

**Statut reel simplifie** :

- `NI-01` `[BACKLOG]`
- `NI-02` `[BACKLOG]`
- `NI-03` `[PARTIAL]`
- `NI-04` `[BACKLOG]`
- `NI-05` `[BACKLOG]`
- `NI-06` `[BACKLOG]`
- `NI-07` `[BACKLOG]`
- `NI-08` `[BACKLOG]`
- `NI-09` `[DONE]`

---

## 1. MÃƒÂ©thodologie de priorisation

### 1.1 Axes d'ÃƒÂ©valuation (1Ã¢â‚¬â€œ5)

| Axe                            | Description                                                              | 1              | 5                 |
| ------------------------------ | ------------------------------------------------------------------------ | -------------- | ----------------- |
| **D** Ã¢â‚¬â€ DifficultÃƒÂ©    | Effort d'implÃƒÂ©mentation estimÃƒÂ©                                     | Ã‚Â½ jour      | 2+ semaines       |
| **G** Ã¢â‚¬â€ Gain utilisateur | Impact direct sur l'engagement et la satisfaction                        | NÃƒÂ©gligeable | Transformateur    |
| **E** Ã¢â‚¬â€ EdTech           | Valeur pÃƒÂ©dagogique scientifiquement documentÃƒÂ©e (voir Ãƒâ€šÃ‚Â§1.2) | CosmÃƒÂ©tique  | Effet fort > 0.6d |
| **R** Ã¢â‚¬â€ Risque           | Risque technique ou de rÃƒÂ©gression                                     | Aucun          | Critique          |
| **B** Ã¢â‚¬â€ Business         | RÃƒÂ©tention / acquisition / diffÃƒÂ©renciation marchÃƒÂ©                | Nul            | DÃƒÂ©cisif        |

### 1.2 Ãƒâ€°chelle EdTech Ã¢â‚¬â€ Base scientifique

L'axe EdTech est **le seul ÃƒÂ  ÃƒÂªtre ÃƒÂ©valuÃƒÂ© ÃƒÂ  partir de donnÃƒÂ©es factuelles**, pas d'intuitions produit.

| Score | Signification        | CritÃƒÂ¨re                                                                                                |
| ----- | -------------------- | --------------------------------------------------------------------------------------------------------- |
| **5** | Preuve trÃƒÂ¨s forte | MÃƒÂ©ta-analyse, effet mesurÃƒÂ© d ÃƒÂ¢Ã¢â‚¬Â°Ã‚Â¥ 0.6 (Cohen), rÃƒÂ©pliquÃƒÂ© dans plusieurs populations |
| **4** | Preuve forte         | Effet mesurÃƒÂ© d = 0.4Ã¢â‚¬â€œ0.6, ou consensus dans la littÃƒÂ©rature EdTech peer-reviewed              |
| **3** | Preuve modÃƒÂ©rÃƒÂ©e | BÃƒÂ©nÃƒÂ©fice documentÃƒÂ© mais conditionnel, population spÃƒÂ©cifique ou effet indirect                 |
| **2** | Preuve faible        | Engagement documentÃƒÂ©, mais impact sur l'apprentissage mixte ou non mesurÃƒÂ©                           |
| **1** | Pas de preuve        | Principalement cosmÃƒÂ©tique, spÃƒÂ©culatif ou motivation extrinsÃƒÂ¨que non corroborÃƒÂ©e                |

**RÃƒÂ©fÃƒÂ©rences de base utilisÃƒÂ©es pour le scoring** :

- Hattie (2009) Ã¢â‚¬â€ _Visible Learning_ : mÃƒÂ©ta-analyse de 800+ mÃƒÂ©ta-analyses (>50 000 ÃƒÂ©tudes)
- Cepeda et al. (2006) Ã¢â‚¬â€ Pratique distribuÃƒÂ©e et espacÃƒÂ©e Ã¢â‚¬â€ _Psychological Bulletin_
- Hattie & Timperley (2007) - Pouvoir du feedback - _Review of Educational Research_
- VanLehn (2011) Ã¢â‚¬â€ Tuteurs IA vs tuteurs humains Ã¢â‚¬â€ _Educational Psychologist_
- Bjork (1994) Ã¢â‚¬â€ Desirable difficulties in learning
- Sweller (1988) - Theorie de la charge cognitive - _Cognitive Science_
- Deci & Ryan (2000) Ã¢â‚¬â€ ThÃƒÂ©orie de l'autodÃƒÂ©termination (SDT)
- Mayer (2001) - Multimedia learning theory
- Kivetz et al. (2006) Ã¢â‚¬â€ Goal-gradient hypothesis Ã¢â‚¬â€ _Journal of Marketing Research_

> **Convention** : `[PROPOSITION]` = feature suggÃƒÂ©rÃƒÂ©e par l'IA, non issue des docs existants. Ãƒâ‚¬ valider produit avant implÃƒÂ©mentation.

### 1.3 Formule de score composite

```
Score = (G ÃƒÆ’Ã¢â‚¬â€ 1.5) + (E ÃƒÆ’Ã¢â‚¬â€ 2) + B ÃƒÂ¢Ã‹â€ Ã¢â‚¬â„¢ (D ÃƒÆ’Ã¢â‚¬â€ 0.8) ÃƒÂ¢Ã‹â€ Ã¢â‚¬â„¢ (R ÃƒÆ’Ã¢â‚¬â€ 0.7)
```

Un score ÃƒÂ©levÃƒÂ© indique une feature ÃƒÂ  haute valeur et faible coÃƒÂ»t/risque. Le score **ne remplace pas** le jugement Ã¢â‚¬â€ il oriente la discussion.

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

_Vue consolidee du backlog et du deja livre. Legende : D=Difficulte, G=Gain, E=EdTech, R=Risque, B=Business._

| #   | Feature                                                                         | Statut reel code                                                                                                             | D   | G   | E   | R   | B   | Score    | Priorite |
| --- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | --- | --- | --- | --- | --- | -------- | -------- |
| F01 | Rendu Markdown/KaTeX explications                                               | [DONE]                                                                                                                       | 2   | 4   | 5   | 1   | 3   | **16.8** | P0       |
| F02 | Defis quotidiens (defi du jour)                                                 | [DONE]                                                                                                                       | 3   | 5   | 4   | 2   | 5   | **16.9** | P0       |
| F03 | Test de diagnostic initial                                                      | [DONE]                                                                                                                       | 3   | 4   | 5   | 2   | 4   | **16.0** | P0       |
| F04 | Revisions espacees (SM-2)                                                       | [PARTIAL] exercice livre end-to-end ; defis + F23 restent hors scope                                                         | 4   | 4   | 5   | 2   | 4   | **14.8** | P0       |
| F30 | [PROP] Effet Protege (corriger erreur IA)                                       | [BACKLOG]                                                                                                                    | 4   | 4   | 5   | 2   | 4   | **15.4** | P1       |
| F31 | [PROP] Exemples resolus progressifs (Fading)                                    | [BACKLOG]                                                                                                                    | 3   | 4   | 5   | 2   | 3   | **15.2** | P1       |
| F32 | [PROP] Mode Pratique Entrelacee (Interleaving)                                  | [DONE]                                                                                                                       | 2   | 3   | 5   | 2   | 3   | **14.5** | P1       |
| F05 | Adaptation dynamique de difficulte                                              | [DONE]                                                                                                                       | 4   | 4   | 5   | 3   | 4   | **13.9** | P1       |
| F06 | Conditions d'obtention badges visibles                                          | [DONE]                                                                                                                       | 2   | 4   | 3   | 1   | 3   | **13.5** | P1       |
| F07 | Courbe d'evolution temporelle                                                   | [DONE]                                                                                                                       | 3   | 4   | 3   | 2   | 3   | **11.2** | P1       |
| F08 | Objectifs personnalises                                                         | [BACKLOG]                                                                                                                    | 3   | 3   | 3   | 1   | 3   | **11.1** | P1       |
| F09 | Dashboard parent                                                                | [BACKLOG]                                                                                                                    | 4   | 4   | 3   | 2   | 5   | **11.4** | P1       |
| F10 | [PROP] Mode focus / session ciblee                                              | [BACKLOG]                                                                                                                    | 2   | 4   | 3   | 1   | 3   | **13.5** | P1       |
| F11 | [PROP] Partage progression -> parents (lien)                                    | [BACKLOG]                                                                                                                    | 2   | 3   | 3   | 1   | 4   | **12.5** | P1       |
| F12 | Radar chart par discipline                                                      | [DONE]                                                                                                                       | 2   | 3   | 3   | 1   | 2   | **10.9** | P1       |
| F13 | Deblocage automatique badges temps reel                                         | [DONE]                                                                                                                       | 2   | 3   | 3   | 1   | 3   | **11.5** | P1       |
| F33 | Feedback Growth Mindset (copywriting)                                           | [DONE]                                                                                                                       | 1   | 3   | 3   | 1   | 2   | **11.4** | P1       |
| F14 | Monitoring IA - persistance DB                                                  | [PARTIAL]                                                                                                                    | 2   | 2   | 1   | 1   | 3   | **6.9**  | P2       |
| F15 | Preference page d'accueil (connexion)                                           | [PARTIAL] route par role livree ; vraie preference utilisateur encore absente                                                | 1   | 2   | 1   | 1   | 1   | **5.7**  | P2       |
| F16 | Heatmap d'activite                                                              | [BACKLOG]                                                                                                                    | 3   | 3   | 2   | 1   | 3   | **9.1**  | P2       |
| F17 | Celebrations visuelles ameliorees                                               | [BACKLOG]                                                                                                                    | 2   | 3   | 2   | 1   | 2   | **9.0**  | P2       |
| F18 | Ligues hebdomadaires (upgrade leaderboard)                                      | [BACKLOG] (leaderboard deja present)                                                                                         | 4   | 4   | 1   | 2   | 4   | **8.9**  | P2       |
| F19 | Notifications push + email                                                      | [BACKLOG]                                                                                                                    | 4   | 3   | 2   | 2   | 4   | **8.1**  | P2       |
| F20 | Normalisation niveaux de difficulte                                             | [PARTIAL] produit visible neutralise, legacy technique conserve                                                              | 4   | 3   | 2   | 3   | 3   | **6.9**  | P2       |
| F21 | Badges secrets                                                                  | [BACKLOG]                                                                                                                    | 2   | 3   | 2   | 1   | 2   | **9.0**  | P2       |
| F22 | Suppression utilisateur admin (RGPD)                                            | [DONE]                                                                                                                       | 2   | 1   | 1   | 2   | 3   | **4.7**  | P2       |
| F35 | [TECH] Redaction secrets dans logs DB (URL SQLAlchemy)                          | [DONE]                                                                                                                       | 1   | 2   | 1   | 1   | 4   | **7.5**  | P2       |
| F36 | [UX][TECH] Flash auth au refresh                                                | [PARTIAL] boundary serveur+client livre sur routes protegees ; artefact global residuel a confirmer                          | 2   | 2   | 1   | 1   | 3   | **7.2**  | P2       |
| F37 | [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard        | [BACKLOG] actif                                                                                                              | 3   | 3   | 4   | 2   | 3   | **11.7** | P2       |
| F38 | [UX][Gamification] Progression compte coherente & historique des gains          | [PARTIAL] runtime recale ; lecture produit du ledger encore manquante                                                        | 3   | 4   | 2   | 2   | 4   | **10.2** | P1       |
| F44 | [UX][Produit] Coherence interaction defis (`challenge_type` vs `response_mode`) | [BACKLOG] decision produit exhaustive requise ; un meme type peut encore rendre QCM, interaction ou texte libre selon policy | 4   | 4   | 4   | 3   | 3   | **11.7** | P1       |
| F23 | [PROP] Exercices adaptatifs SR+IA                                               | [BACKLOG]                                                                                                                    | 4   | 5   | 5   | 3   | 5   | **17.1** | P2\*     |
| F24 | Tuteur IA contextuel                                                            | [BACKLOG]                                                                                                                    | 5   | 5   | 5   | 3   | 5   | **16.1** | P3       |
| F25 | Mode classe / enseignant                                                        | [BACKLOG]                                                                                                                    | 5   | 4   | 4   | 3   | 5   | **14.9** | P3       |
| F26 | Filtres et tri badges                                                           | [DONE]                                                                                                                       | 2   | 2   | 1   | 1   | 2   | **6.4**  | P3       |
| F27 | Optimisation re-renders exercices/defis                                         | [BACKLOG]                                                                                                                    | 3   | 2   | 1   | 2   | 2   | **4.8**  | P3       |
| F28 | Mode aventure / histoire narrative                                              | [BACKLOG]                                                                                                                    | 5   | 5   | 3   | 3   | 5   | **13.1** | P4       |
| F29 | Personnalisation avatar / profil                                                | [BACKLOG]                                                                                                                    | 3   | 3   | 1   | 1   | 2   | **7.1**  | P4       |
| F34 | Module Sciences - Curiosites (Vrai/Faux, format court)                          | [BACKLOG] prototype seulement                                                                                                | 3   | 4   | 2   | 2   | 4   | **10.4** | P4       |
| F39 | [LEGAL] Refonte rangs & suppression IP Star Wars                                | [PARTIAL] visible neutralise ; roles canoniques livres ; aliases legacy rangs/DB encore servis                               | 4   | 3   | 1   | 3   | 5   | **6.2**  | P1\*     |
| F40 | Leaderboard Ã¢â‚¬â€ position de l'utilisateur hors top 50                       | [DONE]                                                                                                                       | 2   | 4   | 2   | 1   | 3   | **10.7** | P2       |
| F41 | Leaderboard Ã¢â‚¬â€ filtre temporel (semaine / mois / tout)                     | [DONE]                                                                                                                       | 3   | 4   | 1   | 2   | 3   | **7.2**  | P2       |
| F42 | Architecture difficultÃƒÂ© Ã¢â‚¬â€ sÃƒÂ©paration ÃƒÂ¢ge et niveau sur 2 axes    | [DONE] runtime F42 et boundaries alignes, legacy garde en compatibilite                                                      | 4   | 3   | 3   | 3   | 4   | **9.2**  | P2       |

> _F23 a un score eleve mais depend de F04 (revisions espacees) - debloque apres F04._
> _F39 : le visible produit est maintenant neutralise. Les migrations additives `progression_rank` et `thematic_title` sont livrees ; les aliases legacy restent intentionnellement servis pendant la transition._

### 2.1 Vue d'avancement - visible, sans effacer le travail livre

**[DONE] Implemente dans le code**

- F01, F02, F03, F05, F06, F07, F12, F13, F22, F26, F32, F33, F35, F40, F41, F42

**[PARTIAL] Fondations deja posees**

- F04 : exercice scope livre (`P1`..`P5`) avec write path SM-2, resume dashboard, endpoint `reviews/next` et session `spaced-review` ; defis + F23 restent hors scope
- F14 : monitoring IA runtime + admin read-only + runs harness persistes, mais pas encore de persistance DB complete des metriques runtime
- F15 : redirection post-login dependante du role livree (`apprenant` -> `/home-learner`, autres -> `/dashboard`) ; pas encore de preference utilisateur persistante
- F20 : normalisation visible de la difficulte livree, mais legacy backend/DB volontairement conserve
- F36 : boundary serveur+client sur `/home-learner`, `/dashboard` et `/admin` livre ; un eventuel flash global hors routes protegees reste une dette de polish
- F38 : moteur gamification persistant + ledger `point_events` + calcul niveau/XP/rang recales, mais pas encore d'historique utilisateur dedie ni de lecture produit complete du ledger
- F39 : rangs publics et surfaces visibles neutralises ; migrations additives `progression_rank` et `thematic_title` livrees ; aliases legacy encore servis
- F44 : la coherence percue des defis reste a decider produit ; aujourd'hui `challenge_type` et `response_mode` sont separes et peuvent produire des interactions differentes pour un meme type visible

**[BACKLOG] Encore a livrer**

- le reste de la matrice, avec priorite conservee

### 2.2 Priorite operationnelle reelle (post-F04-P5)

Les scores `D/G/E/R/B` restent la base de reference. En revanche, l'ordre d'execution reel doit tenir compte :

- de l'etat deja livre dans le code
- des dependances entre features
- des dettes contractuelles visibles restantes
- du ratio valeur / risque a court terme

Ordre recommande maintenant :

1. **F09** - dashboard parent + relation parent-enfant
2. **F38** - historique des gains et lecture produit coherente du ledger compte
3. **F37** - coherence dashboard / temporalite / charge cognitive
4. **F44** - coherence interaction defis (`challenge_type` vs `response_mode`) - cadrage produit exhaustif avant implementation
5. **F14** - persistance DB complete des metriques runtime IA
6. **F08** - objectifs personnalises
7. **F10** - mode focus / session ciblee
8. **F36** - suppression du reliquat de flash auth au refresh, si encore visible hors routes protegees
9. **F23** - exercices adaptatifs SR+IA, maintenant debloques par F04
10. **F30** - effet protege
11. **F31** - exemples resolus progressifs
12. **F11** - partage progression vers parents
13. **F16 / F17 / F18 / F19 / F21** - confort, engagement et croissance
14. **F24 / F25 / F27** - chantiers plus lourds ou structurels
15. **F28 / F29 / F34** - backlog lointain / produit

Lecture simple :

- **P0 operationnel** : F09, F38, F37
- **P1 operationnel** : F44, F14, F08, F10, F36, F23
- **P2 operationnel** : F30, F31, F11, F16, F17, F18, F19, F21
- **P3 operationnel** : F24, F25, F27
- **P4 operationnel** : F28, F29, F34

---

## 3. P0 Ã¢â‚¬â€ Impact fort, fondements pÃƒÂ©dagogiques solides {#3-p0}

Ces quatre features combinent un score composite ÃƒÂ©levÃƒÂ© ET un bÃƒÂ©nÃƒÂ©fice pÃƒÂ©dagogique scientifiquement robuste. Elles constituent le cÃ…â€œur de la valeur ÃƒÂ©ducative de Mathakine.

---

### F01 Ã¢â‚¬â€ Rendu Markdown/KaTeX dans les explications

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§4.7](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.8 | D=2, G=4, E=5, R=1, B=3

**ProblÃƒÂ¨me** : Les explications post-rÃƒÂ©ponse (exercices et dÃƒÂ©fis) sont du texte brut. Les formules mathÃƒÂ©matiques (`aÃ‚Â³+bÃ‚Â³`) et les ÃƒÂ©tapes structurÃƒÂ©es sont illisibles.

**Valeur pÃƒÂ©dagogique (E=5)** :

- Mayer (2001) - _Multimedia Learning_ : la segmentation et la mise en forme du texte reduisent la charge cognitive extrinseque et ameliorent la comprehension (effet mesure).
- Sweller (1988) - Cognitive Load Theory : l'organisation visuelle de l'information reduit la charge cognitive irrelevante.
- La lisibilitÃƒÂ© de l'explication est un vecteur direct du transfert d'apprentissage.

**Ce qu'il faut faire** :

- IntÃƒÂ©grer `react-markdown` + `remark-math` + `rehype-katex` (ou `react-katex`) dans `ExerciseSolver` et `ChallengeSolver`
- Appliquer le rendu dans le bloc "Explication" de la rÃƒÂ©ponse
- Style CSS pour les formules math (KaTeX CSS)
- Optionnel : accordÃƒÂ©on "voir plus" si explication > 300 mots

**Effort estimÃƒÂ©** : 1-2 jours

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© Ã¢â‚¬â€ composant `frontend/components/ui/MathText.tsx` (react-markdown + remark-math + rehype-katex), intÃƒÂ©grÃƒÂ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver` et `DiagnosticSolver`

---

### F02 Ã¢â‚¬â€ DÃƒÂ©fis quotidiens (dÃƒÂ©fi du jour) ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§3.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.9 | D=3, G=5, E=4, R=2, B=5

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© (Mars 2026)

**Valeur pÃƒÂ©dagogique (E=4)** :

- Cepeda et al. (2006) Ã¢â‚¬â€ La pratique distribuÃƒÂ©e (daily sessions) produit une meilleure rÃƒÂ©tention que la pratique massÃƒÂ©e, indÃƒÂ©pendamment du temps total (d = 0.46-0.71).
- Deci & Ryan (2000) Ã¢â‚¬â€ SDT : les dÃƒÂ©fis quotidiens optionnels, adaptÃƒÂ©s au niveau, soutiennent le besoin de compÃƒÂ©tence sans pression externe (contrairement aux streaks punitifs).

**Conception implÃƒÂ©mentÃƒÂ©e** : 3 dÃƒÂ©fis par jour (volume_exercises, specific_type, logic_challenge), bonus XP, expiration minuit, pas de punition si manquÃƒÂ©.

**RÃƒÂ©fÃƒÂ©rence technique complÃƒÂ¨te** : [F02_DEFIS_QUOTIDIENS.md](F02_DEFIS_QUOTIDIENS.md)

---

### F03 Ã¢â‚¬â€ Test de diagnostic initial

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§3.5](ROADMAP_FONCTIONNALITES.md)  
**Score** : 16.0 | D=3, G=4, E=5, R=2, B=4

**ProblÃƒÂ¨me** : L'onboarding collecte les prÃƒÂ©fÃƒÂ©rences (classe, ÃƒÂ¢ge, rythme) mais pas le niveau rÃƒÂ©el. Les premiÃƒÂ¨res recommandations peuvent ÃƒÂªtre inadaptÃƒÂ©es, dÃƒÂ©gradant le moment critique des 5 premiÃƒÂ¨res minutes.

**Valeur pÃƒÂ©dagogique (E=5)** :

- Hattie (2009) Ã¢â‚¬â€ _Formative assessment_ : d = 0.90 (un des effets les plus ÃƒÂ©levÃƒÂ©s en ÃƒÂ©ducation). Identifier le niveau rÃƒÂ©el avant l'enseignement est la condition prÃƒÂ©alable ÃƒÂ  toute personnalisation efficace.
- Sweller (1988) - L'alignement entre difficulte et competence previent la surcharge cognitive (exercices trop faciles = ennui, trop difficiles = anxiete).
- _Assessment for learning_ (Black & Wiliam, 1998) : le diagnostic prÃƒÂ©alable est la fondation de l'apprentissage adaptatif.

**Algorithme adaptatif (Item Response Theory simplifiÃƒÂ©)** :

```
1. Commencer au niveau mÃƒÂ©dian
2. Correct ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ question plus difficile (niveau +1)
3. Incorrect ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ question plus facile (niveau -1)
4. ArrÃƒÂªt : 2 erreurs consÃƒÂ©cutives au mÃƒÂªme niveau ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ niveau ÃƒÂ©tabli
5. DurÃƒÂ©e max : 10 questions, ~5 minutes
```

**Output** :

- `initial_level` par type d'exercice (addition, soustraction, multiplication, division, logique)
- StockÃƒÂ© dans `diagnostic_results` (table dÃƒÂ©diÃƒÂ©e, scores JSONB par type)
- Alimente immÃƒÂ©diatement les recommandations

**Effort estimÃƒÂ©** : 3-5 jours

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© le 04/03/2026

**RÃƒÂ©fÃƒÂ©rence technique complÃƒÂ¨te** : [F03_DIAGNOSTIC_INITIAL.md](F03_DIAGNOSTIC_INITIAL.md)

**Ce qui est branchÃƒÂ©** :

- Table `diagnostic_results` (migration `20260304_diagnostic`)
- Service IRT (`app/services/diagnostic_service.py`) : algo adaptatif, 10 questions, 4 types
- Endpoints `/api/diagnostic/status|start|question|answer|complete`
- Page `/diagnostic` (accessible depuis onboarding et Settings)
- Section "Ãƒâ€°valuation de niveau" dans Settings (affiche date + niveaux par type)
- Recommandations : `RecommendationService` lit le diagnostic via `get_latest_score()` et affine la difficultÃƒÂ© mÃƒÂ©diane

**Ce qui reste ÃƒÂ  cÃƒÂ¢bler (backlog F03-suite)** :

| Lacune                                                                                                               | Impact                                                                                             | PrioritÃƒÂ© | Statut                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------- |
| `/api/exercises/generate` ignore le niveau diagnostic                                                                | Un utilisateur scorant InitiÃƒÂ© reÃƒÂ§oit des exercices selon `age_group`, pas son niveau rÃƒÂ©el | Moyen       | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ RÃƒÂ©solu 06/03/2026 Ã¢â‚¬â€ `adaptive_difficulty_service` cÃƒÂ¢blÃƒÂ© en ÃƒÂ©tape 1 de la cascade |
| `preferred_difficulty` stocke des age_group (`"adulte"`) mais le service attendait des DifficultyLevels              | Zyclope (adulte) tombait en fallback PADAWAN malgrÃƒÂ© son profil                                  | Moyen       | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ RÃƒÂ©solu 06/03/2026 Ã¢â‚¬â€ `_PREF_DIFFICULTY_TO_ORDINAL` ÃƒÂ©largi aux deux formes               |
| Mode de rÃƒÂ©ponse QCM/saisie libre calculÃƒÂ© sur la difficultÃƒÂ© de l'exercice, pas le niveau rÃƒÂ©el utilisateur | Un utilisateur INITIE pouvait se voir forcer la saisie libre si l'exercice ÃƒÂ©tait GRAND_MAITRE   | Moyen       | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ RÃƒÂ©solu 06/03/2026 Ã¢â‚¬â€ Frontend lit les scores IRT via `useIrtScores()`, dÃƒÂ©cide par type  |
| Types non couverts IRT (MIXTE, FRACTIONS) sans proxy de niveau                                                       | Pas d'adaptation pour ces types                                                                    | Moyen       | ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ RÃƒÂ©solu 06/03/2026 Ã¢â‚¬â€ Proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division)         |
| Home apprenant / settings ne valorisent pas encore `has_completed`                                                   | Pas de message de confirmation stable type "ton niveau a ete etabli" sur la surface apprenant      | Faible      | ÃƒÂ¢Ã‚ÂÃ‚Â³ Backlog                                                                                                 |
| GÃƒÂ©nÃƒÂ©ration IA (`/api/ai/generate`) ignore le diagnostic                                                        | MÃƒÂªme problÃƒÂ¨me que le gÃƒÂ©nÃƒÂ©rateur interne                                                | Moyen       | ÃƒÂ¢Ã‚ÂÃ‚Â³ Backlog                                                                                                 |

---

### F04 Ã¢â‚¬â€ RÃƒÂ©visions espacÃƒÂ©es (algorithme SM-2)

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§3.3](ROADMAP_FONCTIONNALITES.md)  
**Score** : 14.8 | D=4, G=4, E=5, R=2, B=4

**Statut actuel** : [PARTIAL] exercice livre end-to-end (`F04-P1`..`F04-P5`) ; restent hors scope de ce train :

- integration defis
- compteur `X revisions restantes`
- distinction analytics plus fine pour `spaced-review`
- couplage futur F23 (`SR + IA`)

**Valeur pÃƒÂ©dagogique (E=5) Ã¢â‚¬â€ La preuve la plus robuste en ÃƒÂ©ducation** :

- Ebbinghaus (1885, rÃƒÂ©pliquÃƒÂ© 100+ fois) Ã¢â‚¬â€ Courbe de l'oubli : sans rÃƒÂ©vision, 70% d'une connaissance est oubliÃƒÂ©e en 24h, 90% en une semaine.
- Cepeda et al. (2006) Ã¢â‚¬â€ _Psychological Bulletin_ : mÃƒÂ©ta-analyse de 317 ÃƒÂ©tudes. La pratique espacÃƒÂ©e amÃƒÂ©liore la rÃƒÂ©tention de 200%+ sur le long terme vs pratique massÃƒÂ©e.
- Kornell & Bjork (2008) Ã¢â‚¬â€ Spacing + interleaving : effet particuliÃƒÂ¨rement fort en mathÃƒÂ©matiques (g = 0.43).
- _L'algorithme SM-2 (Wozniak, 1987) est le fondement de SuperMemo, Anki et DuoLingo._

**Algorithme SM-2 adaptÃƒÂ©** :

```
Intervalles de rÃƒÂ©vision :
- 1ÃƒÂ¨re rÃƒÂ©vision : J+1
- 2ÃƒÂ¨me rÃƒÂ©vision : J+3
- 3ÃƒÂ¨me rÃƒÂ©vision : J+7
- Suivantes : intervalle ÃƒÆ’Ã¢â‚¬â€ ease_factor

Ajustement ease_factor (EF, init 2.5) :
- RÃƒÂ©ponse correcte rapide (qualitÃƒÂ© 4-5) : EF + 0.1
- RÃƒÂ©ponse correcte lente (qualitÃƒÂ© 3) : EF inchangÃƒÂ©
- RÃƒÂ©ponse incorrecte (qualitÃƒÂ© 0-2) : EF ÃƒÂ¢Ã‹â€ Ã¢â‚¬â„¢ 0.2, retour J+1
```

**ModÃƒÂ¨le de donnÃƒÂ©es** :

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

**IntÃƒÂ©gration** : AprÃƒÂ¨s chaque tentative d'exercice, mise ÃƒÂ  jour de l'item SR. Widget "RÃƒÂ©visions du jour" sur le dashboard.

**Effort estimÃƒÂ©** : 1-2 semaines (migration + service + UI)

**RÃƒÂ©fÃƒÂ©rence technique (spec)** : [F04_REVISIONS_ESPACEES.md](F04_REVISIONS_ESPACEES.md)

---

## 4. P1 Ã¢â‚¬â€ Haute prioritÃƒÂ© {#4-p1}

---

### F05 Ã¢â‚¬â€ Adaptation dynamique de difficultÃƒÂ© ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦

**Source** : [WORKFLOW_EDUCATION Ãƒâ€šÃ‚Â§2.2](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)  
**Score** : 13.9 | D=4, G=4, E=5, R=3, B=4

**Valeur pÃƒÂ©dagogique (E=5)** :

- Vygotsky (1978) - Zone proximale de developpement : l'apprentissage optimal se situe juste au-dela de la competence actuelle. Trop facile -> ennui. Trop difficile -> anxiete.
- Bjork (1994) Ã¢â‚¬â€ _Desirable difficulties_ : un niveau de dÃƒÂ©fi optimal crÃƒÂ©e une rÃƒÂ©sistance productive (retrieval effort) qui renforce la mÃƒÂ©morisation ÃƒÂ  long terme.
- Csikszentmihalyi (1990) - Etat de _flow_ : atteint quand difficulte ~ competence.

**ImplÃƒÂ©mentation (v3.0.0-alpha.3+, MAJ 06/03/2026)** :

- `app/services/adaptive_difficulty_service.py` Ã¢â‚¬â€ rÃƒÂ©solution par cascade (IRT > progression > profil > fallback), proxys MIXTE (min des 4 bases) et FRACTIONS (niveau division)
- `server/handlers/exercise_handlers.py` Ã¢â‚¬â€ branchement adaptatif (`?adaptive=true` par dÃƒÂ©faut, dÃƒÂ©sactivable par `?adaptive=false` ou `age_group` explicite)
- `app/utils/exercise_generator_helpers.py` -> distracteurs QCM calibres par niveau (INITIE: erreurs +/-1 + inversion, PADAWAN: retenue +/-10, CHEVALIER/MAITRE/GRAND_MAITRE: magnitude en %, `server/exercise_generator_helpers.py` restant un re-export de compatibilite)
- **Mode QCM vs saisie libre** : dÃƒÂ©cidÃƒÂ© cÃƒÂ´tÃƒÂ© frontend par `useIrtScores().resolveIsOpenAnswer(exercise_type)` Ã¢â‚¬â€ saisie libre uniquement si niveau IRT = GRAND_MAITRE pour ce type. Le backend gÃƒÂ©nÃƒÂ¨re toujours les `choices`.

**RÃƒÂ©fÃƒÂ©rence technique complÃƒÂ¨te** : [F05_ADAPTATION_DYNAMIQUE.md](F05_ADAPTATION_DYNAMIQUE.md)

**Seuils adaptation temps reel** : `completion_rate > 85% ET streak >= 3` -> boost (+1 niveau) ; `completion_rate < 50% ET streak = 0` -> descente (-1 niveau).

**Hors scope F05-suite (backlog)** :

- `/api/ai/generate` Ã¢â‚¬â€ mÃƒÂªme adaptation pour la gÃƒÂ©nÃƒÂ©ration IA (SSE, complexitÃƒÂ© sÃƒÂ©parÃƒÂ©e)
- Dashboard widget 'ton niveau s'est ajuste' - [DONE] Implemente le 06/03/2026 (`LevelEstablishedWidget` dans l'onglet Vue d'ensemble)
- Seuils boost/descente configurables via admin
- **[F05-B1] Saisie libre dÃƒÂ©clenchÃƒÂ©e par taux de rÃƒÂ©ussite rÃƒÂ©el, pas uniquement par niveau IRT** : plutÃƒÂ´t que le seuil fixe GRAND_MAITRE, dÃƒÂ©clencher la saisie libre quand `completion_rate >= 90 % sur les 5 derniÃƒÂ¨res tentatives` pour un type donnÃƒÂ© Ã¢â‚¬â€ indÃƒÂ©pendamment du niveau IRT. Fondement : Roediger & Karpicke (2006) Testing Effect + VanLehn (2011) mÃƒÂ©ta-analyse tutoring adaptatif. Ãƒâ€°viter d'encoder des erreurs en forÃƒÂ§ant le recall avant que la rÃƒÂ©cupÃƒÂ©ration soit automatique.
- **[F05-B2] Distracteurs QCM plus discriminants, moins dÃƒÂ©ductibles** : amÃƒÂ©liorer la gÃƒÂ©nÃƒÂ©ration des `choices` pour ÃƒÂ©viter les bonnes rÃƒÂ©ponses visibles par simple ÃƒÂ©limination. Cible : 3 distracteurs plausibles, de mÃƒÂªme ordre de grandeur, mÃƒÂªme format et mÃƒÂªme unitÃƒÂ© que la bonne rÃƒÂ©ponse, issus d'erreurs typiques rÃƒÂ©elles (retenue, inversion, confusion opÃƒÂ©ratoire, off-by-one, confusion quotient/reste) plutÃƒÂ´t que de valeurs trop ÃƒÂ©loignÃƒÂ©es ou structurellement diffÃƒÂ©rentes. Ajouter si possible une instrumentation du taux de sÃƒÂ©lection des distracteurs pour identifier ceux qui ne trompent jamais. Effort estimÃƒÂ© : 1-2 jours. PrioritÃƒÂ© produit : moyenne-haute, car impact direct sur la valeur pÃƒÂ©dagogique perÃƒÂ§ue des exercices.

**DÃƒÂ©pendance** : Profite du diagnostic initial (F03) et prÃƒÂ©pare les rÃƒÂ©visions espacÃƒÂ©es (F04).

---

### F06 - Conditions d'obtention badges visibles

**Source** : [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md) - section 4.2  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Statut** : [DONE] present dans le code au 23/03/2026 via `frontend/components/badges/BadgeCard.tsx` (affichage des `criteria_text` + progression sur badges verrouilles)

**Valeur pedagogique (E=3)** :

- Kivetz et al. (2006) - _Goal-gradient effect_ : la motivation augmente a mesure que l'objectif est visible et proche. Effet mesure +40-60% d'engagement.
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

### F07 Ã¢â‚¬â€ Courbe d'ÃƒÂ©volution temporelle

**Source** : [ANALYTICS_PROGRESSION Ãƒâ€šÃ‚Â§1.1](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ANALYTICS_PROGRESSION.md)  
**Score** : 11.2 | D=3, G=4, E=3, R=2, B=3

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© le 07/03/2026

**Valeur pÃƒÂ©dagogique (E=3)** :

- Zimmerman & Schunk (2001) Ã¢â‚¬â€ _Self-monitoring_ : voir sa progression concrÃƒÂ¨te dans le temps active la mÃƒÂ©tacognition et renforce la motivation intrinsÃƒÂ¨que.
- Hattie (2009) Ã¢â‚¬â€ _Self-reported grades / metacognitive monitoring_ : d = 1.33 (attention : effet de la conscience de sa propre progression, pas du graphique lui-mÃƒÂªme).

**Endpoint implÃƒÂ©mentÃƒÂ©** : `GET /api/users/me/progress/timeline?period=7d|30d`  
**DonnÃƒÂ©es sources** : `Attempt.created_at`, `Attempt.is_correct`, `Attempt.time_spent`

**Ce qui a ÃƒÂ©tÃƒÂ© fait** :

- Service dÃ¢â‚¬â„¢agrÃƒÂ©gation dÃƒÂ©diÃƒÂ© : `app/services/progress_timeline_service.py` (jours continus, rÃƒÂ©sumÃƒÂ© global, `by_type`)
- Handler + route : `server/handlers/user_handlers.py`, `server/routes/users.py`
- Hook + widget frontend : `frontend/hooks/useProgressTimeline.ts`, `frontend/components/dashboard/ProgressTimelineWidget.tsx`
- IntÃƒÂ©gration dashboard : onglet Progression (`frontend/app/dashboard/page.tsx`)
- Tests : `tests/unit/test_progress_timeline_service.py`, `tests/api/test_progress_endpoints.py`, `frontend/hooks/useProgressTimeline.test.tsx`
- RÃƒÂ©fÃƒÂ©rence dÃ¢â‚¬â„¢implÃƒÂ©mentation : [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md)

**Effort estimÃƒÂ©** : 3-5 jours

---

### F08 Ã¢â‚¬â€ Objectifs personnalisÃƒÂ©s

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§4.2](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.1 | D=3, G=3, E=3, R=1, B=3

**Valeur pÃƒÂ©dagogique (E=3)** :

- Deci & Ryan (2000) Ã¢â‚¬â€ SDT : les objectifs auto-dÃƒÂ©terminÃƒÂ©s (choisis par l'utilisateur, pas imposÃƒÂ©s) renforcent la motivation intrinsÃƒÂ¨que et le besoin d'autonomie.
- Locke & Latham (1990) Ã¢â‚¬â€ _Goal-setting theory_ : des objectifs spÃƒÂ©cifiques et mesurables amÃƒÂ©liorent la performance. Effet plus fort quand l'objectif est choisi par l'individu.

**Types** : Quotidien (ex: 5 exercices/jour), hebdomadaire, de maÃƒÂ®trise (ex: "atteindre 80% en division").

**Effort estimÃƒÂ©** : 3-5 jours

---

### F09 Ã¢â‚¬â€ Dashboard parent

**Source** : [ROADMAP Ãƒâ€šÃ‚Â§3.1](ROADMAP_FONCTIONNALITES.md)  
**Score** : 11.4 | D=4, G=4, E=3, R=2, B=5

**Valeur pÃƒÂ©dagogique (E=3)** :

- Hattie (2009) Ã¢â‚¬â€ _Parental involvement_ : d = 0.49. L'implication parentale dans le suivi scolaire a un effet positif mesurable sur les rÃƒÂ©sultats.
- Bryk & Schneider (2002) Ã¢â‚¬â€ La confiance famille-institution est un prÃƒÂ©dicteur de l'engagement ÃƒÂ  long terme.

**Architecture minimale (MVP)** :

```
Table: parent_child_links (parent_user_id, child_user_id, created_at, permissions JSON)
Route: /parent/dashboard ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ vue enfants
Route: /parent/child/[id] ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ progression dÃƒÂ©taillÃƒÂ©e
```

**Cadrage produit actif** : voir aussi [PARENT_DASHBOARD_AND_CHILD_LINKS.md](PARENT_DASHBOARD_AND_CHILD_LINKS.md) pour le MVP, la relation `parent_child_links` et les surfaces cible.

**Effort estimÃƒÂ©** : 1-2 semaines

---

### F10 Ã¢â‚¬â€ [PROPOSITION] Mode focus / session ciblÃƒÂ©e

**Source** : Proposition IA Ã¢â‚¬â€ non issue des docs existants  
**Score** : 13.5 | D=2, G=4, E=3, R=1, B=3

**Concept** : Permettre de lancer une session ciblee en 2 clics : "5 multiplications niveau adapte". L'utilisateur choisit type + difficulte + nombre, et est guide directement dans une suite d'exercices sans navigation. Le wording visible doit rester neutre et compatible avec F20/F39.

**Valeur pÃƒÂ©dagogique (E=3)** :

- Bjork (1994) Ã¢â‚¬â€ _Desirable difficulties_ : l'interleaving (mÃƒÂ©lange de types) est bÃƒÂ©nÃƒÂ©fique, mais la pratique ciblÃƒÂ©e sur un type spÃƒÂ©cifique est nÃƒÂ©cessaire pour la construction de compÃƒÂ©tences (blocked practice pour la phase d'acquisition).
- Deci & Ryan Ã¢â‚¬â€ Le choix du type de pratique renforce l'autonomie (SDT).

**Effort estimÃƒÂ©** : 1-2 jours (frontend principalement Ã¢â‚¬â€ filtres dÃƒÂ©jÃƒÂ  disponibles en backend)

---

### F11 Ã¢â‚¬â€ [PROPOSITION] Partage de progression vers les parents (lien simple)

**Source** : Proposition IA Ã¢â‚¬â€ alternative lÃƒÂ©gÃƒÂ¨re au Dashboard Parent complet (F09)  
**Score** : 12.5 | D=2, G=3, E=3, R=1, B=4

**Concept** : GÃƒÂ©nÃƒÂ©rer un lien de partage de progression (lecture seule, sans compte requis) permettant au parent de voir les stats de l'enfant sans crÃƒÂ©er un espace parent dÃƒÂ©diÃƒÂ©. Quick win avant l'implÃƒÂ©mentation complÃƒÂ¨te de F09.

**Valeur pÃƒÂ©dagogique (E=3)** : MÃƒÂªme base que F09 (engagement parental), avec une friction d'adoption beaucoup plus faible.

**Effort estimÃƒÂ©** : 1-2 jours

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

### F30 Ã¢â‚¬â€ [PROPOSITION] L'Effet ProtÃƒÂ©gÃƒÂ© ("Corrige l'erreur de l'IA")

**Source** : Proposition IA Ã¢â‚¬â€ non issue des docs existants  
**Score** : 15.4 | D=4, G=4, E=5, R=2, B=4

> _Score initial proposÃƒÂ© : 16.2 (D=3). DifficultÃƒÂ© rÃƒÂ©visÃƒÂ©e ÃƒÂ  D=4 : gÃƒÂ©nÃƒÂ©ration IA d'erreurs intentionnelles + composant UI "correction de copie" + vÃƒÂ©rification de la justification = pÃƒÂ©rimÃƒÂ¨tre backend + frontend non nÃƒÂ©gligeable._

**ProblÃƒÂ¨me** : RÃƒÂ©soudre un problÃƒÂ¨me mathÃƒÂ©matique est un apprentissage actif classique. Mais le niveau ultime de maÃƒÂ®trise s'atteint lorsqu'on doit enseigner ÃƒÂ  quelqu'un d'autre Ã¢â‚¬â€ ou corriger ses erreurs.

**Valeur pÃƒÂ©dagogique (E=5)** :

- Chase et al. (2009) Ã¢â‚¬â€ _The ProtÃƒÂ©gÃƒÂ© Effect_ : Les ÃƒÂ©tudiants font plus d'efforts et apprennent plus profondÃƒÂ©ment quand ils doivent enseigner ÃƒÂ  un agent virtuel (effet mesurÃƒÂ© trÃƒÂ¨s fort).
- Hattie (2009) Ã¢â‚¬â€ _Peer Tutoring_ : d = 0.55. L'ÃƒÂ©valuation des erreurs des autres active une mÃƒÂ©tacognition supÃƒÂ©rieure ÃƒÂ  la simple rÃƒÂ©solution.
- La dÃƒÂ©tection d'une erreur de logique (et non de calcul) est un exercice de comprÃƒÂ©hension conceptuelle profonde, non mÃƒÂ©morisable par substitution de pattern.

**Ce qu'il faut faire** : CrÃƒÂ©er un type de dÃƒÂ©fi inversÃƒÂ©. L'IA prÃƒÂ©sente un problÃƒÂ¨me et une rÃƒÂ©solution ÃƒÂ©tape par ÃƒÂ©tape contenant **une seule erreur de logique intentionnelle**. L'ÃƒÂ©lÃƒÂ¨ve doit agir comme le professeur : identifier ÃƒÂ  quelle ÃƒÂ©tape l'IA s'est trompÃƒÂ©e et expliquer pourquoi.

**Architecture cible** :

- Nouveau `challenge_type` : `error_correction`
- Champ backend : `steps: [{content, is_error: bool, error_explanation}]`
- UI : composant "Correction de copie" Ã¢â‚¬â€ affichage des ÃƒÂ©tapes numÃƒÂ©rotÃƒÂ©es, sÃƒÂ©lection de l'ÃƒÂ©tape erronÃƒÂ©e, champ justification
- Validation : l'ÃƒÂ©lÃƒÂ¨ve doit identifier la bonne ÃƒÂ©tape ET soumettre une explication (mÃƒÂªme courte)

**Effort estimÃƒÂ©** : 3-5 jours (nouveau type de dÃƒÂ©fi + composant UI + prompt IA pour gÃƒÂ©nÃƒÂ©ration d'erreurs intentionnelles)  
**PrioritÃƒÂ©** : P1 Ã¢â‚¬â€ score fort, diffÃƒÂ©renciateur pÃƒÂ©dagogique unique sur le marchÃƒÂ©

---

### F31 Ã¢â‚¬â€ [PROPOSITION] Exemples rÃƒÂ©solus progressifs (Fading Effect)

**Source** : Proposition IA Ã¢â‚¬â€ non issue des docs existants  
**Score** : 15.2 | D=3, G=4, E=5, R=2, B=3

**ProblÃƒÂ¨me** : Face ÃƒÂ  un concept totalement nouveau, faire faire des exercices et sanctionner l'erreur (mÃƒÂªme avec correction ensuite) gÃƒÂ©nÃƒÂ¨re de l'anxiÃƒÂ©tÃƒÂ© et une surcharge cognitive pour les novices.

**Valeur pÃƒÂ©dagogique (E=5)** :

- Sweller & Cooper (1985) Ã¢â‚¬â€ _Worked Example Effect_ : Ãƒâ€°tudier des problÃƒÂ¨mes dÃƒÂ©jÃƒÂ  rÃƒÂ©solus est **plus efficace pour les novices** que de rÃƒÂ©soudre des problÃƒÂ¨mes (d = 0.57). RÃƒÂ©pliquÃƒÂ© extensivement.
- Renkl (1997) Ã¢â‚¬â€ _Fading steps_ : La transition optimale de novice ÃƒÂ  expert se fait en retirant progressivement les ÃƒÂ©tapes guidÃƒÂ©es Ã¢â‚¬â€ l'autonomie croÃƒÂ®t naturellement.
- ComplÃƒÂ©mentaire avec F05 (adaptation difficultÃƒÂ©) : le fading s'active automatiquement quand l'algorithme dÃƒÂ©tecte un concept nouveau (0 tentatives sur ce type).

**Ce qu'il faut faire** : IntÃƒÂ©grer une mÃƒÂ©canique de "Fading" dans l'onboarding d'un nouveau concept (dÃƒÂ©clenchÃƒÂ©e quand l'utilisateur rencontre un sous-type d'exercice pour la premiÃƒÂ¨re fois) :

| Exercice | Mode                  | Description                                                                   |
| -------- | --------------------- | ----------------------------------------------------------------------------- |
| 1        | **Fully worked**      | EntiÃƒÂ¨rement rÃƒÂ©solu par l'IA, l'ÃƒÂ©lÃƒÂ¨ve lit et clique "J'ai compris" |
| 2        | **Last step missing** | RÃƒÂ©solu, mais la derniÃƒÂ¨re ÃƒÂ©tape est ÃƒÂ  complÃƒÂ©ter                 |
| 3        | **Half faded**        | Seule la premiÃƒÂ¨re ÃƒÂ©tape est donnÃƒÂ©e, l'ÃƒÂ©lÃƒÂ¨ve finit              |
| 4        | **Autonome**          | L'ÃƒÂ©lÃƒÂ¨ve fait tout Ã¢â‚¬â€ rÃƒÂ©gime normal                              |

**Contrainte de conception** : Ne pas pÃƒÂ©naliser l'exercice "fully worked" (pas de score de rÃƒÂ©ussite/ÃƒÂ©chec) Ã¢â‚¬â€ c'est un mode observation, pas ÃƒÂ©valuation.

**Effort estimÃƒÂ©** : 3-5 jours (dÃƒÂ©clinaison du moteur d'exercices + dÃƒÂ©tection "premiÃƒÂ¨re fois sur ce sous-type")  
**PrioritÃƒÂ©** : P1 Ã¢â‚¬â€ particuliÃƒÂ¨rement critique pour la rÃƒÂ©tention des utilisateurs en onboarding

---

### F32 Ã¢â‚¬â€ [PROPOSITION] Mode "Pratique EntrelacÃƒÂ©e" (Interleaving) ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦

**Source** : Proposition IA Ã¢â‚¬â€ non issue des docs existants  
**Score** : 14.5 | D=2, G=3, E=5, R=2, B=3

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© le 07/03/2026

> _Score initial proposÃƒÂ© : 15.2 (R=1). Risque rÃƒÂ©visÃƒÂ© ÃƒÂ  R=2 : le mÃƒÂ©lange de types d'exercices interagit avec F05 (adaptation dynamique par type) Ã¢â‚¬â€ il faut s'assurer que les niveaux par type sont suffisamment calibrÃƒÂ©s avant activation._

**ProblÃƒÂ¨me** : Les ÃƒÂ©lÃƒÂ¨ves ont tendance ÃƒÂ  enchaÃƒÂ®ner un seul type d'exercice (ex : 10 additions d'affilÃƒÂ©e Ã¢â‚¬â€ _Blocked Practice_). Le cerveau se met en pilote automatique et n'apprend pas ÃƒÂ  **choisir la bonne stratÃƒÂ©gie**, compÃƒÂ©tence clÃƒÂ© en ÃƒÂ©valuation.

**Valeur pÃƒÂ©dagogique (E=5)** :

- Rohrer & Taylor (2007) Ã¢â‚¬â€ _Interleaved Practice_ : MÃƒÂ©langer les types de problÃƒÂ¨mes force le cerveau ÃƒÂ  identifier la stratÃƒÂ©gie avant de l'appliquer. **RÃƒÂ©tention ÃƒÂ  long terme amÃƒÂ©liorÃƒÂ©e de +43%** par rapport ÃƒÂ  la pratique bloquÃƒÂ©e.
- Kornell & Bjork (2008) Ã¢â‚¬â€ Effet particuliÃƒÂ¨rement fort en mathÃƒÂ©matiques : spacing + interleaving combinÃƒÂ©s produisent les meilleures performances (g = 0.43).
- **Attention** : L'interleaving est contre-intuitif Ã¢â‚¬â€ les ÃƒÂ©lÃƒÂ¨ves ont l'impression d'apprendre moins bien pendant la session (mais retiennent mieux). Ãƒâ‚¬ accompagner d'une explication pÃƒÂ©dagogique dans l'UI.

**Ce qui a ÃƒÂ©tÃƒÂ© fait** :

- Endpoint dÃƒÂ©diÃƒÂ© : `GET /api/exercises/interleaved-plan?length=10` (`server/handlers/exercise_handlers.py`, `server/routes/exercises.py`)
- Service d'agrÃƒÂ©gation : `app/services/interleaved_practice_service.py` (fenÃƒÂªtre 7 jours, ÃƒÂ©ligibilitÃƒÂ© `>=2 tentatives` et `>=60%`, plan round-robin sans doublons consÃƒÂ©cutifs)
- Gestion mÃƒÂ©tier explicite : `InterleavedNotEnoughVariety` -> `409` avec code `not_enough_variety`
- Quick Action dashboard : 3e CTA dans `QuickStartActions` + instrumentation analytics `quick_start_click` type `interleaved`
- EntrÃƒÂ©e session : page `frontend/app/exercises/interleaved/page.tsx` (plan, fallback 409, gÃƒÂ©nÃƒÂ©ration 1er exercice, redirection)
- Progression session : `ExerciseSolver` en mode `session=interleaved` (progression, bouton "Exercice suivant", ÃƒÂ©cran de fin)
- i18n FR/EN : clÃƒÂ©s `dashboard.quickStart.interleaved*` et `exercises.solver.session*`
- Correctif critique F05/F32 : `POST /api/exercises/generate` passe en `@optional_auth`, ce qui active correctement la rÃƒÂ©solution adaptative `age_group` quand `adaptive=true`

**Durcissements post-implÃƒÂ©mentation (08/03/2026)** :

- analytics EdTech `interleaved` ramenÃƒÂ©es ÃƒÂ  une sÃƒÂ©mantique session : `first_attempt` n'est ÃƒÂ©mis qu'une seule fois au premier exercice soumis, avec persistance `sessionStorage`
- flux de session durci : `POST /api/exercises/generate` ne renvoie plus de `200` sans `id` quand `save=true` ; en cas d'ÃƒÂ©chec, le frontend affiche un toast et conserve l'ÃƒÂ©tat de session
- dette DRY rÃƒÂ©duite : la rÃƒÂ©solution adaptive `age_group` est factorisÃƒÂ©e dans `_resolve_adaptive_age_group_if_needed()` pour ÃƒÂ©viter la divergence entre `generate_exercise` et `generate_exercise_api`
- quality gate restaurÃƒÂ© : `black app/ server/ tests/ --check` repasse au vert ; nettoyage UTF-8 de `tests/unit/test_adaptive_difficulty_service.py` et hygiÃƒÂ¨ne repo (`frontend/junit.xml`, `.gitignore`, import inutilisÃƒÂ©)

**Tests** :

- `tests/unit/test_interleaved_practice_service.py`
- `tests/api/test_exercise_endpoints.py` (auth, `409 not_enough_variety`, succÃƒÂ¨s `200`, non-rÃƒÂ©gression `adaptive=true` sans `age_group` explicite)

**Effort rÃƒÂ©alisÃƒÂ©** : ~1-2 jours  
**DÃƒÂ©pendance** : F05 exploitÃƒÂ© (difficultÃƒÂ© adaptative conservÃƒÂ©e)  
**PrioritÃƒÂ©** : P1 Ã¢â‚¬â€ quick win fort, effort modÃƒÂ©rÃƒÂ©, impact pÃƒÂ©dagogique ÃƒÂ©levÃƒÂ©

---

### F33 Ã¢â‚¬â€ Feedback "Growth Mindset" ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦

**Source** : Proposition IA Ã¢â‚¬â€ non issue des docs existants  
**Score** : 11.4 | D=1, G=3, E=3, R=1, B=2

> _Score initial proposÃƒÂ© : 13.0 (E=4). EdTech rÃƒÂ©visÃƒÂ© ÃƒÂ  E=3 : les ÃƒÂ©tudes Dweck sont robustes mais les interventions de Growth Mindset par texte seul ont des effets faibles sans accompagnement long terme. Yeager et al. (2019) mesure des effets sur populations dÃƒÂ©favorisÃƒÂ©es spÃƒÂ©cifiques Ã¢â‚¬â€ le transfert ÃƒÂ  une plateforme gÃƒÂ©nÃƒÂ©raliste est conditionnel._

**Statut** : ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦ ImplÃƒÂ©mentÃƒÂ© le 07/03/2026

**ProblÃƒÂ¨me** : Un message "Faux" ou un feedback nÃƒÂ©gatif brutal lors d'un ÃƒÂ©chec peut renforcer un _Fixed Mindset_ ("Je suis nul en maths"). Ce biais est particuliÃƒÂ¨rement fort chez les enfants 8-14 ans.

**Valeur pÃƒÂ©dagogique (E=3)** :

- Dweck (2006) Ã¢â‚¬â€ _Mindset Theory_ : Valoriser l'effort et la stratÃƒÂ©gie plutÃƒÂ´t que l'intelligence innÃƒÂ©e ou le rÃƒÂ©sultat brut amÃƒÂ©liore la rÃƒÂ©silience face ÃƒÂ  l'ÃƒÂ©chec.
- Yeager et al. (2019) : Une simple intervention Growth Mindset a des effets mesurables sur les rÃƒÂ©sultats en maths chez les ÃƒÂ©lÃƒÂ¨ves dÃƒÂ©favorisÃƒÂ©s.
- **Nuance** : L'effet est conditionnel et nÃƒÂ©cessite de la cohÃƒÂ©rence dans tout le parcours utilisateur Ã¢â‚¬â€ un seul message ne suffit pas.

**Ce qui a ÃƒÂ©tÃƒÂ© fait** (modifications de texte + micro-UI) :

| Avant                      | AprÃƒÂ¨s                                                                                                                               |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| "Mauvaise rÃƒÂ©ponse"      | "Pas encore ! La prochaine sera la bonne."                                                                                             |
| "Incorrect"                | "Ton cerveau est en train d'apprendre !"                                                                                               |
| Score affichÃƒÂ© seulement | Valoriser aussi le **temps passÃƒÂ©** sur un dÃƒÂ©fi difficile                                                                         |
| Ã¢â‚¬â€                    | Tooltips de chargement : _"Savais-tu que ton cerveau crÃƒÂ©e de nouvelles connexions exactement au moment oÃƒÂ¹ tu fais une erreur ?"_ |

**Contrainte** : CohÃƒÂ©rence avec les textes de feedback existants dans `fr.json` / `en.json`. Ne pas sur-positiver au point de perdre la valeur informative du feedback (Hattie & Timperley, 2007 Ã¢â‚¬â€ le feedback doit rester prÃƒÂ©cis).

**ImplÃƒÂ©mentation** :

- Messages FR/EN alignÃƒÂ©s Growth Mindset (`frontend/messages/fr.json`, `frontend/messages/en.json`)
- Feedback d'ÃƒÂ©chec harmonisÃƒÂ© dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver`
- Bloc partagÃƒÂ© factorisÃƒÂ© : `frontend/components/ui/GrowthMindsetHint.tsx` (industrialisation, no-DRY)

**Effort rÃƒÂ©alisÃƒÂ©** : ~Ã‚Â½ jour  
**PrioritÃƒÂ©** : P1 Ã¢â‚¬â€ quick win absolu, risque technique faible, impact psychologique documentÃƒÂ©

---

## 5. P2 Ã¢â‚¬â€ PrioritÃƒÂ© moyenne {#5-p2}

| Feature                                                                            | Note                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **F14 - Monitoring IA persistance DB**                                             | [PARTIAL] Le runtime monitoring et l'admin read-only existent deja (`token_tracker`, `generation_metrics`, `/admin/ai-monitoring`) ainsi que la persistance DB des runs harness. Le backlog restant porte sur une persistance DB complete des metriques runtime live, aujourd'hui surtout en memoire process.                                                                                                                                                                                                                                                                                                                                                                                   |
| **F15 Ã¢â‚¬â€ PrÃƒÂ©fÃƒÂ©rence page d'accueil**                                    | [PARTIAL] Les routes par defaut dependent deja du role (`apprenant` -> `/home-learner`, autres -> `/dashboard`), mais il n'existe pas encore de preference utilisateur explicite type `login_redirect_preference` dans Settings.                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **F16 Ã¢â‚¬â€ Heatmap d'activitÃƒÂ©**                                              | Calendrier GitHub-style sur Dashboard/Profil. `react-calendar-heatmap`. Endpoint : `GET /api/users/me/activity/heatmap`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **F17 Ã¢â‚¬â€ CÃƒÂ©lÃƒÂ©brations visuelles amÃƒÂ©liorÃƒÂ©es**                      | Confettis au dÃƒÂ©blocage badge, modal avec partage. DÃƒÂ©sactivable (accessibilitÃƒÂ©).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **F18 - Ligues hebdomadaires**                                                     | Le leaderboard existe deja (top 50, filtres, surfaces de lecture), mais pas encore les ligues / saisons hebdomadaires. Le backlog porte sur les groupes, promotions/relegations et resets periodiques. Score EdTech=1 : engagement, pas d'apprentissage direct.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **F19 Ã¢â‚¬â€ Notifications push + email**                                         | Rappel inactivitÃƒÂ©, streak en danger, badge proche. Voir [ROADMAP Ãƒâ€šÃ‚Â§4.1](ROADMAP_FONCTIONNALITES.md). Infrastructure ÃƒÂ  dÃƒÂ©finir (service push web + SMTP).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **F20 Ã¢â‚¬â€ Normalisation niveaux de difficultÃƒÂ©**                             | [PARTIAL] Le visible produit est deja neutralise et F42 a separe age/niveau ; la dette restante est surtout legacy backend/DB et migration enum a planifier soigneusement. Voir [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md) et le manifeste technique associÃƒÂ©.                                                                                                                                                                                                                                                                                                                                                                                      |
| **F21 Ã¢â‚¬â€ Badges secrets**                                                     | Badges cachÃƒÂ©s dÃƒÂ©bloquÃƒÂ©s pour comportements inattendus (ex: "Noctambule" aprÃƒÂ¨s minuit). Variable reward (Skinner) Ã¢â‚¬â€ engagement ÃƒÂ©levÃƒÂ©.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **F22 - Suppression utilisateur admin (RGPD)**                                     | [DONE] `DELETE /api/admin/users/{id}` existe deja cote admin. Le code supprime physiquement l'utilisateur avec cascade (pas un simple soft delete) et bloque l'auto-suppression admin.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **F35 Ã¢â‚¬â€ [TECH] Redaction secrets logs DB ÃƒÂ¢Ã…â€œÃ¢â‚¬Â¦**                  | ImplÃƒÂ©mentÃƒÂ© le 07/03/2026. `app/db/base.py` loggue dÃƒÂ©sormais une URL redigÃƒÂ©e via `redact_database_url_for_log()` (credentials et query params masquÃƒÂ©s). Couvert par `tests/unit/test_db_log_redaction.py` (7 tests).                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **F36 Ã¢â‚¬â€ [UX][TECH] Flash auth au refresh**                                   | [PARTIAL] Les routes protegees sensibles passent maintenant par un boundary serveur + client (`proxy.ts` + `ProtectedRoute`) et le logout reset l'etat visuel sans stale header. Le reliquat eventuel concerne surtout le bootstrap auth hors routes protegees et les surfaces publiques. Ne rouvrir un lot dedie que si un vrai flash reste visible ou s'accompagne d'une redirection parasite / perte de session.                                                                                                                                                                                                                                                                             |
| **F37 - [UX][EdTech] Coherence progression & selecteurs de temporalite dashboard** | Clarifier la portee des filtres temporels dans le dashboard. Conclusion de l'analyse UX : un controle = un perimetre visible. Les widgets temporels doivent avoir un selecteur local ou une periode partagee explicite ; les widgets cumules doivent afficher un badge de portee (`Cumule`, `Tous les temps`) plutot qu'un faux selecteur. Les vues journalieres redondantes dans `Progression` doivent etre rationalisees au profit d'un widget complementaire (ex : regularite de pratique). Si l'on veut une coherence temporelle complete de l'onglet `Progression`, ouvrir ensuite un lot dedie data/hooks/backend pour exposer une periode explicite sur les widgets aujourd'hui cumules. |
| **F38 - [UX][Gamification] Progression compte coherente & historique des gains**   | [PARTIAL] Le moteur persistant, le ledger `point_events`, le calcul niveau/XP/rang et plusieurs surfaces de lecture existent deja. Le backlog F38 porte maintenant sur la surface produit coherente : historique des gains, lecture par source et presentation compte explicite.                                                                                                                                                                                                                                                                                                                                                                                                                |
| **F23 Ã¢â‚¬â€ [PROP] Exercices adaptatifs SR+IA**                                  | GÃƒÂ©nÃƒÂ©rer des exercices IA ciblÃƒÂ©s sur les concepts ÃƒÂ  rÃƒÂ©viser selon la courbe SR (F04). Score composite trÃƒÂ¨s ÃƒÂ©levÃƒÂ© (17.1) mais **dÃƒÂ©pend de F04**. DÃƒÂ©bloquÃƒÂ© aprÃƒÂ¨s F04.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

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

### F44 - Coherence interaction defis (`challenge_type` vs `response_mode`)

**Score** : 11.7 | D=4, G=4, E=4, R=3, B=3

**Statut** : [BACKLOG] decision produit exhaustive requise avant implementation

**Probleme** : Aujourd'hui, la verite machine des defis distingue volontairement :

- le **type pedagogique** visible (`challenge_type`)
- la **modalite d'interaction** (`response_mode`)

Cette separation est saine cote architecture, mais elle peut produire une incoherence
percue cote utilisateur final : un meme type visible peut render en **QCM**, en
**interaction visuelle / grille / ordre**, ou en **texte libre** selon :

- la policy backend par type
- la difficulte finale
- la presence de `choices`
- la validite de ces `choices` apres sanitization
- la presence / forme de `visual_data`

**Verite terrain actuelle** :

- la generation IA ne decide pas seule `response_mode`
- le backend normalise d'abord le contenu, puis calcule `response_mode`
- priorite forte au QCM si des `choices` valides survivent a la policy
- sinon fallback vers le mode par defaut du type

**Conséquence UX** :

- coherent pour le code
- **pas totalement coherent pour l'enfant / le parent / l'enseignant**
- un utilisateur peut percevoir deux defis `VISUAL` ou `PUZZLE` comme "de meme type" mais rencontrer des interactions differentes
- cette variabilite consomme de la charge cognitive et brouille l'attente produit

**Decision produit a prendre** :

1. **Quel niveau de stabilite veut-on par type ?**
   - un type visible = une interaction stable
   - ou un type visible = une famille pouvant admettre plusieurs interactions
2. **Quels types peuvent legitiment rester variables ?**
   - ex. `VISUAL`, `PUZZLE`, `SEQUENCE`
3. **Le QCM doit-il garder la priorite ?**
   - pour tous les types `OPTIONAL`
   - seulement pour les types faciles
   - ou etre interdit pour certaines familles afin de preserver une experience plus stable
4. **Comment rendre la variabilite lisible si elle est conservee ?**
   - libelles explicites
   - badge / sous-titre de modalite
   - onboarding / hint adapte au mode

**Travail backlog exhaustif attendu** :

1. **Inventaire produit reel**
   - lister toutes les combinaisons observees `challenge_type x response_mode`
   - separer contenu manuel, legacy, IA
   - distinguer les cas rares des cas frequents
2. **Audit end-user**
   - identifier les combinaisons qui troublent un enfant 8-12 ans
   - identifier les combinaisons acceptables pour parent / enseignant
   - definir les attentes UI par type visible
3. **Matrice cible**
   - fixer, pour chaque type, ce qui est :
     - interdit
     - tolere
     - prefere
     - fallback exceptionnel
4. **Decision sur le QCM**
   - garder / limiter / supprimer la priorite QCM par famille de defis
   - documenter si la difficulte doit encore influencer cette decision
5. **Alignement complet**
   - prompts de generation IA
   - `challenge_contract_policy.py`
   - validateurs / sanitization
   - mapping API detail
   - hints et copy frontend selon le mode
6. **Migration / nettoyage**
   - contenu legacy incoherent
   - challenges persistés avec `generation_parameters.response_mode` obsolete
   - telemetry minimale pour verifier la comprehension / friction

**Regle UX proposee (a challenger, pas encore validee)** :

- **un type visible ne doit pas changer d'interaction sans signal produit explicite**
- si une variabilite est maintenue, elle doit etre **nommee, assumee et compréhensible**
- a defaut, privilegier la stabilite de l'interaction sur la flexibilite machine

**Valeur pedagogique (E=4)** :

- Sweller (1988) - la reduction de charge cognitive extrinseque passe par une interface plus predicible
- Mayer (2001) - la coherence de presentation aide l'utilisateur a former un modele mental stable
- Hattie & Timperley (2007) - un feedback utile doit etre interpretable dans un cadre d'interaction stable

**Effort estime** :

- cadrage produit / audit exhaustif : 1-2 jours
- lot d'implementation ensuite : 3-5 jours minimum selon la matrice retenue

**Positionnement** :

- **ticket produit prioritaire**
- **hors sequence FFI d'industrialisation frontend**
- a traiter comme une decision produit + contrat, pas comme un simple polish de copy ou de rendu

---

### F39 - [LEGAL] Refonte rangs et suppression IP Star Wars

**Score** : 6.2 | D=4, G=3, E=1, R=3, B=5

**Statut** : [PARTIAL] Le visible produit est neutralise. Les roles canoniques sont livres cote code/API/frontend ; la dette restante est surtout contractuelle, legacy et DB.

**Probleme reel restant** :

- les labels visibles ne fuitent plus l'univers Star Wars dans les surfaces produit principales
- les roles utilisateur exposes sont deja canoniques (`apprenant`, `enseignant`, `moderateur`, `admin`) cote code/API/frontend
- certains noms de champs contractuels restent legacy (`jedi_rank`, `star_wars_title`)
- ces reliquats sont encore visibles pour les integrateurs, Swagger et certains consumers techniques
- des valeurs legacy restent en DB / compat interne, mais ne doivent plus redevenir la verite visible

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

- noms d'enum / valeurs DB legacy tant qu'ils restent isoles de la surface visible
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

## 6. P3 Ã¢â‚¬â€ Investissement long terme {#6-p3}

### F24 Ã¢â‚¬â€ Tuteur IA contextuel

**Score** : 16.1 | D=5, G=5, E=5, R=3, B=5

**Valeur pÃƒÂ©dagogique (E=5) Ã¢â‚¬â€ parmi les plus fortes en EdTech** :

- VanLehn (2011) Ã¢â‚¬â€ _Educational Psychologist_ : Les systÃƒÂ¨mes de tutoriels intelligents (ITS) atteignent d = 0.55Ã¢â‚¬â€œ0.66 par rapport aux classes classiques. Seul le tutorat humain individuel fait mieux (d ÃƒÂ¢Ã¢â‚¬Â°Ã‹â€  2.0).
- _Scaffolding_ cognitif (Wood et al., 1976) : l'aide contextuelle qui s'adapte aux erreurs est plus efficace que les explications gÃƒÂ©nÃƒÂ©riques.
- RÃƒÂ¨gle critique : **ne pas donner la rÃƒÂ©ponse directement** Ã¢â‚¬â€ guider par questions socratiques.

**DiffÃƒÂ©rence vs chatbot actuel** : Le chatbot actuel est gÃƒÂ©nÃƒÂ©rique. Un tuteur IA contextuel connaÃƒÂ®t l'exercice en cours, le niveau de l'utilisateur et l'historique d'erreurs sur ce type de problÃƒÂ¨me.

**Effort estimÃƒÂ©** : 2-4 semaines (intÃƒÂ©gration LLM contextuel + design pÃƒÂ©dagogique)

---

### F25 Ã¢â‚¬â€ Mode classe / enseignant

**Score** : 14.9 | D=5, G=4, E=4, R=3, B=5

**Valeur pÃƒÂ©dagogique (E=4)** : L'enseignant mÃƒÂ©diateur amplifie les effets de la plateforme (Hattie, d = 0.45 pour _teacher-student relationships_). L'assignation ciblÃƒÂ©e d'exercices + les rapports par classe sont des outils pÃƒÂ©dagogiques ÃƒÂ  fort impact.

**Architecture requise** : Table `classes`, `class_memberships`, `assignments`, routes `/teacher/`. IntÃƒÂ©gration d'export CSV (dÃƒÂ©jÃƒÂ  partiellement disponible).

**Effort estimÃƒÂ©** : 3-6 semaines

---

### F26 Ã¢â‚¬â€ Filtres et tri badges

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

### F27 Ã¢â‚¬â€ Optimisation re-renders exercices/dÃƒÂ©fis

Flash visible avant stabilisation des pages. Pistes : `placeholderData` TanStack Query, `useMemo` sur les params de query. ~3-5 jours (profiling + corrections).

---

## 7. P4 Ã¢â‚¬â€ Backlog distant {#7-p4}

### B01 - Rate limit validate-token : passer de par-IP a par-token/user_id

**Contexte** : En prod multi-worker Gunicorn (Render), tous les workers sortent avec la meme IP egress Render (74.220.51.250). Le rate limit validate-token keyed par IP agregee le trafic legitime de tous les users, ce qui declenche des 429 sur des sessions normales.

**Cause prouvee** : logs prod 2026-04-05/06 - rafales a quelques ms d'ecart depuis 74.220.51.250 = IP sortante Render (hostname frankfurt-egress.render.com), declenchees au redemarrage de worker ou lors de navigation multi-onglets.

**Solution recommandee** : supprimer le rate limit IP sur validate-token ou le re-keyer par JWT/user_id. validate-token ne presente pas de surface brute-force (le secret JWT ne peut pas etre devine) - le rate limit par IP n'apporte aucune securite reelle ici.

**Effort** : < 1h (1-2 lignes dans app/utils/rate_limit.py)

---

### F28 Ã¢â‚¬â€ Mode aventure / histoire narrative

**Score** : 13.1 | D=5, G=5, E=3, R=3, B=5

**Valeur pÃƒÂ©dagogique (E=3)** :

- Situated learning (Lave & Wenger, 1991) : les maths contextualisÃƒÂ©es dans une narration rÃƒÂ©elle amÃƒÂ©liorent le transfert des connaissances.
- Mais : l'effet de la gamification narrative sur les rÃƒÂ©sultats acadÃƒÂ©miques est modÃƒÂ©rÃƒÂ© et conditionnel (Mayer, 2019 Ã¢â‚¬â€ _Computer games don't improve learning_).

**Concept** : Progression narrative oÃƒÂ¹ les maths servent l'histoire ("Le vaisseau a besoin de 150 unitÃƒÂ©s de carburant, tu as 3 rÃƒÂ©servoirs de 45 chacun..."). RÃƒÂ©compenses dÃƒÂ©bloquant la suite.

**Effort estimÃƒÂ©** : 4-8 semaines (design narratif + nouveau type de contenu)

---

### F29 Ã¢â‚¬â€ Personnalisation avatar / profil

**Score** : 7.1 | D=3, G=3, E=1, R=1, B=2

Avatars, titres, cadres de profil dÃƒÂ©bloquables avec les points. Donne de la valeur aux points gagnÃƒÂ©s. Score EdTech=1 : pas de bÃƒÂ©nÃƒÂ©fice pÃƒÂ©dagogique documentÃƒÂ©.

---

### F34 Ã¢â‚¬â€ Module Sciences Ã¢â‚¬â€ CuriositÃƒÂ©s scientifiques (Labo des Sciences)

**Score** : 10.4 | D=3, G=4, E=2, R=2, B=4

**Philosophie** :

1. **ZÃƒÂ©ro punition** : Si l'ÃƒÂ©lÃƒÂ¨ve clique sur "Faux" (alors que c'est Vrai), pas de croix rouge agressive. IcÃƒÂ´ne ampoule bleue douce + texte Ã‚Â« Et non, c'est pourtant vrai ! Ã‚Â». Objectif : apprendre un fait amusant, pas ÃƒÂ©valuer.
2. **Explication gratifiante** : L'explication apparaÃƒÂ®t dans un encart en dessous, sans quitter la page (pas de pop-up ou changement d'ÃƒÂ©cran brutal).
3. **Format rapide** : Format "TikTok/Shorts" appliquÃƒÂ© ÃƒÂ  l'ÃƒÂ©ducation. L'ÃƒÂ©lÃƒÂ¨ve enchaÃƒÂ®ne ~10 anecdotes scientifiques en 3 minutes, gagne de l'XP sans impression de "travailler".

**Contenu** :

- Affirmation scientifique (ex. Ã‚Â« Le Soleil pourrait contenir environ un million de Terres Ã‚Â»)
- Boutons Vrai / Faux
- RÃƒÂ©ponse correcte : icÃƒÂ´ne check verte, Ã‚Â« Exactement ! +X XP Ã‚Â»
- RÃƒÂ©ponse incorrecte : icÃƒÂ´ne ampoule bleue, Ã‚Â« Et non, c'est pourtant vrai ! Ã‚Â» (ou Ã‚Â« Et oui, c'est bien faux ! Ã‚Â» selon le cas)
- Encart explicatif avec fait dÃƒÂ©taillÃƒÂ© + bouton Ã‚Â« Fait suivant Ã‚Â»

**Technique** :

- Nouveau type de contenu (table `science_facts` ou extension `challenges` avec `challenge_type=science`)
- CatÃƒÂ©gories : Astronomie, Biologie, Physique, Chimie, etc.
- Badge catÃƒÂ©gorie, compteur sÃƒÂ©rie, XP par fait
- Design : glassmorphism, thÃƒÂ¨me sombre cohÃƒÂ©rent Mathakine

**Prototype** : [../assets/prototypes/F34_SCIENCES_PROTOTYPE.html](../assets/prototypes/F34_SCIENCES_PROTOTYPE.html) Ã¢â‚¬â€ HTML statique (Tailwind, Font Awesome, JS vanilla). Ãƒâ‚¬ intÃƒÂ©grer en Next.js + API.

**Effort estimÃƒÂ©** : 1Ã¢â‚¬â€œ2 semaines (modÃƒÂ¨le + API + page `/sciences` + intÃƒÂ©gration design system)

---

## 8. Features implementees (historique) {#8-features-implementees}

### 8.1 Features livrees et visibles

| Feature                                                                      | Date / borne de verite             | Reference                                                                                                                                                                                         |
| ---------------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F01 - Rendu Markdown/KaTeX dans les explications                             | Present dans le code au 23/03/2026 | Composant `MathText.tsx` - integre dans `ExerciseSolver`, `ExerciseModal`, `ChallengeSolver`, `DiagnosticSolver`                                                                                  |
| F02 - Defis quotidiens (daily challenges)                                    | 03/2026                            | [F02_DEFIS_QUOTIDIENS](F02_DEFIS_QUOTIDIENS.md)                                                                                                                                                   |
| F03 - Test de diagnostic initial (IRT adaptatif)                             | 04/03/2026                         | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section F03                                                                                                                               |
| F05 - Adaptation dynamique de difficulte                                     | 06/03/2026                         | [F05_ADAPTATION_DYNAMIQUE](F05_ADAPTATION_DYNAMIQUE.md)                                                                                                                                           |
| F06 - Conditions d'obtention badges visibles                                 | Present dans le code au 23/03/2026 | `frontend/components/badges/BadgeCard.tsx`                                                                                                                                                        |
| F07 - Courbe d'evolution temporelle (7j/30j)                                 | 07/03/2026                         | [IMPLEMENTATION_F07_TIMELINE](../03-PROJECT/IMPLEMENTATION_F07_TIMELINE.md)                                                                                                                       |
| F12 - Radar chart par discipline                                             | Present dans le code au 23/03/2026 | `frontend/components/dashboard/CategoryAccuracyChart.tsx`                                                                                                                                         |
| F13 - Deblocage automatique badges temps reel                                | Present dans le code au 23/03/2026 | `exercise_attempt_service.py`, `challenge_attempt_service.py`                                                                                                                                     |
| F22 - Suppression utilisateur admin (RGPD)                                   | Present dans le code au 23/03/2026 | `DELETE /api/admin/users/{id}` + suppression physique avec cascade                                                                                                                                |
| F26 - Filtres et tri badges                                                  | Present dans le code au 23/03/2026 | `frontend/app/badges/page.tsx` + `frontend/components/badges/BadgeGrid.tsx`                                                                                                                       |
| F32 - Session entrelacee (interleaving)                                      | 07-08/03/2026                      | [IMPLEMENTATION_F32_SESSION_ENTRELACEE](../03-PROJECT/IMPLEMENTATION_F32_SESSION_ENTRELACEE.md)                                                                                                   |
| F33 - Feedback Growth Mindset (copywriting + micro-UI)                       | 07/03/2026                         | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section F33                                                                                                                               |
| F35 - Redaction secrets logs DB (securite)                                   | 07/03/2026                         | [POLITIQUE_REDACTION_LOGS_PII](../03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md) + archive note `../03-PROJECT/archives/IMPLEMENTATION_NOTES_CLOSED_2026-04/IMPLEMENTATION_F35_REDACTION_LOGS_DB.md` |
| Surface apprenant dediee (`/home-learner`) + boundary de roles canonical     | 04-05/04/2026                      | [UX_SURFACES](../04-FRONTEND/UX_SURFACES.md) + [USER_ROLE_NOMENCLATURE](../00-REFERENCE/USER_ROLE_NOMENCLATURE.md)                                                                                |
| Neuro-inclusion solveurs/listes (hint premier contact + filtres progressifs) | 06/04/2026                         | [DEBAT_NEURO_INCLUSION_2026-03-30](../03-PROJECT/DEBAT_NEURO_INCLUSION_2026-03-30.md)                                                                                                             |
| Espace admin complet (role admin canonique, alias DB legacy `archiviste`)    | 16/02/2026                         | [ADMIN_ESPACE_PROPOSITION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md)                                                                                |
| Auth complet (inscription, email, login, reset)                              | Jan-Fev 2026                       | [AUTH_FLOW](AUTH_FLOW.md)                                                                                                                                                                         |
| Sessions actives + revocation                                                | 16/02/2026                         | SITUATION_FEATURES (archive)                                                                                                                                                                      |
| Leaderboard (top 50, rang utilisateur hors top 50, filtre temporel)          | 24-25/03/2026                      | [API_QUICK_REFERENCE](API_QUICK_REFERENCE.md) + lots F40/F41                                                                                                                                      |
| Badges - refonte UX (onglets, cartes compactes)                              | 17/02/2026                         | [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md)                                                                                        |
| Badges - barres de progression (goal-gradient)                               | 16/02/2026                         | [BADGES_AMELIORATIONS](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md)                                                                                        |
| Badges - B4 reformulation (17 badges)                                        | 17/02/2026                         | Archive : AUDITS_IMPLEMENTES/B4_REFORMULATION_BADGES                                                                                                                                              |
| Badges - moteur generique Lot C (defis, mixte)                               | 17/02/2026                         | Archive : AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES                                                                                                                                                  |
| Quick Win #1 - First Exercise < 90s                                          | Fev 2026                           | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)                                                                                |
| Quick Win #2 - Onboarding pedagogique                                        | Fev 2026                           | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)                                                                                |
| Calibration a l'inscription (classe, age, objectif)                          | Fev 2026                           | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)                                                                                |
| Parcours guide (QuickStartActions dashboard)                                 | Fev 2026                           | [WORKFLOW_EDUCATION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)                                                                                |
| Recommandations personnalisees (marquer fait)                                | 16/02/2026, MAJ 24/03/2026         | SITUATION_FEATURES (archive) + dashboard `Recommendations.tsx` borne maintenant l'affichage initial a 6 cartes avec toggle local                                                                  |
| Ordre aleatoire + masquer reussis                                            | 19/02/2026                         | SITUATION_FEATURES (archive)                                                                                                                                                                      |
| Analytics EdTech (CTR Quick Start, 1er attempt)                              | 25/02/2026                         | [EDTECH_ANALYTICS](EDTECH_ANALYTICS.md)                                                                                                                                                           |
| Monitoring IA (in-memory)                                                    | 22/02/2026                         | [ROADMAP_FONCTIONNALITES](ROADMAP_FONCTIONNALITES.md) - section 4.6                                                                                                                               |
| Mode maintenance + inscriptions (admin config)                               | 16/02/2026                         | [ADMIN_ESPACE_PROPOSITION](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md)                                                                                |
| Streak (basique)                                                             | Fev 2026                           | Integre dans stats utilisateur                                                                                                                                                                    |
| 8 themes visuels                                                             | Fev 2026                           | [THEMES](THEMES.md)                                                                                                                                                                               |
| PWA (mode hors-ligne partiel)                                                | Fev 2026                           | -                                                                                                                                                                                                 |
| Internationalisation FR/EN                                                   | Jan 2026                           | [I18N](I18N.md)                                                                                                                                                                                   |
| Accessibilite (5 modes WCAG AAA)                                             | Fev-Mars 2026                      | [ACCESSIBILITY](../04-FRONTEND/ACCESSIBILITY.md)                                                                                                                                                  |

### 8.2 Fondations techniques deja posees mais encore incompletes cote produit

| Feature                                                                               | Borne de verite            | Ce qui existe deja                                                                                                                                                                                                                                                                                          | Ce qui reste a livrer                                                                                                                                                                         |
| ------------------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **F42 Ã¢â‚¬â€ Architecture difficultÃƒÂ©/ÃƒÂ¢ge Ã¢â‚¬â€ sÃƒÂ©paration des deux axes** | [DONE] 27/03/2026          | P1 : `users.age_group`, profil et API. P2 : `difficulty_tier` sur `exercises` et `logic_challenges`, reco exercices tier Ã‚Â±1 et scoring dÃƒÂ©fis par distance de tier. P3 : runtime exercice 4x3, bridges progression/diagnostic, personalization dÃƒÂ©fis IA, boundaries admin/API et documentation F42. | Dette assumÃƒÂ©e : les champs legacy (`difficulty`, `mastery_level`, `difficulty_rating`) restent comme couches de compatibilitÃƒÂ© et de stockage ; pas de migration de suppression ouverte. |
| **Leaderboard Ã¢â‚¬â€ filtre par groupe d'ÃƒÂ¢ge (utilisateur)**                      | Report 25/03/2026 (lot L1) | Le classement expose `limit` et des champs enrichis ; le paramÃƒÂ¨tre `age_group` a ÃƒÂ©tÃƒÂ© **retirÃƒÂ©** car il filtrait ÃƒÂ  tort sur `preferred_difficulty` (difficultÃƒÂ© easy/medium/hard Ã¢â€°Â  tranche d'ÃƒÂ¢ge).                                                                                 | DÃƒÂ©pend de F42 Phase 1 (colonne `age_group` sur `User`) puis F40.                                                                                                                           |
| F14 - Monitoring IA persistance DB                                                    | Code au 23/03/2026         | monitoring runtime, admin `/admin/ai-monitoring`, token tracker, generation metrics, persistance des runs harness                                                                                                                                                                                           | persistance DB complete des metriques runtime live                                                                                                                                            |
| F38 - Progression gamification compte coherente & historique des gains                | Code au 23/03/2026         | `point_events`, `GamificationService.apply_points`, calcul niveau/XP/rang, surfaces `/api/users/me`, `/api/badges/stats`, `/api/badges/user`, `/api/users/leaderboard`                                                                                                                                      | historique utilisateur dedie, agregats par source, UX compte lisible                                                                                                                          |

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

## 9. RÃƒÂ©fÃƒÂ©rences scientifiques {#9-rÃƒÂ©fÃƒÂ©rences-scientifiques}

| #   | RÃƒÂ©fÃƒÂ©rence                                                                                                                                                | Pertinence                                                            |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Hattie, J. (2009). _Visible Learning_. Routledge.                                                                                                              | MÃƒÂ©ta-analyse de rÃƒÂ©fÃƒÂ©rence Ã¢â‚¬â€ effets sur l'apprentissage |
| 2   | Cepeda, N.J. et al. (2006). Distributed practice in verbal recall tasks. _Psychological Bulletin_, 132(3).                                                     | Fondement rÃƒÂ©visions espacÃƒÂ©es (F04)                              |
| 3   | Hattie, J. & Timperley, H. (2007). The power of feedback. _Review of Educational Research_, 77(1).                                                             | Fondement feedback enrichi (F01)                                      |
| 4   | VanLehn, K. (2011). The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems. _Educational Psychologist_, 46(4). | Fondement tuteur IA (F24)                                             |
| 5   | Sweller, J. (1988). Cognitive load during problem solving. _Cognitive Science_, 12(2).                                                                         | Fondement charge cognitive, mise en forme (F01, F03)                  |
| 6   | Vygotsky, L.S. (1978). _Mind in Society_. Harvard University Press.                                                                                            | Fondement ZPD, adaptation difficultÃƒÂ© (F05)                         |
| 7   | Bjork, R.A. (1994). Memory and metamemory considerations in the training of human beings. In J. Metcalfe & A. Shimamura (Eds.), _Metacognition_.               | Fondement desirable difficulties, mode focus (F05, F10)               |
| 8   | Mayer, R.E. (2001). _Multimedia Learning_. Cambridge University Press.                                                                                         | Fondement rendu Markdown/KaTeX (F01)                                  |
| 9   | Deci, E.L. & Ryan, R.M. (2000). The 'what' and 'why' of goal pursuits. _Psychological Inquiry_, 11(4).                                                         | Fondement SDT, dÃƒÂ©fis optionnels (F02, F08)                         |
| 10  | Kivetz, R. et al. (2006). The goal-gradient hypothesis resurrected. _Journal of Marketing Research_, 43(1).                                                    | Fondement conditions badges visibles (F06)                            |
| 11  | Black, P. & Wiliam, D. (1998). Assessment and classroom learning. _Assessment in Education_, 5(1).                                                             | Fondement diagnostic initial (F03)                                    |
| 12  | Locke, E.A. & Latham, G.P. (1990). _A Theory of Goal Setting and Task Performance_. Prentice Hall.                                                             | Fondement objectifs personnalisÃƒÂ©s (F08)                            |
| 13  | Lave, J. & Wenger, E. (1991). _Situated Learning_. Cambridge University Press.                                                                                 | Fondement mode aventure (F28)                                         |
| 14  | Zimmerman, B.J. (2002). Becoming a self-regulated learner. _Theory into Practice_, 41(2).                                                                      | Fondement mÃƒÂ©tacognition, graphiques progression (F07, F12)         |
| 15  | Kornell, N. & Bjork, R.A. (2008). Learning concepts and categories. _Psychological Science_, 19(6).                                                            | Fondement rÃƒÂ©visions espacÃƒÂ©es + interleaving (F04, F32)          |
| 16  | Chase, C. et al. (2009). Teachable agents and the protÃƒÂ©gÃƒÂ© effect. _Journal of Science Education and Technology_, 18(4).                                  | Fondement Effet ProtÃƒÂ©gÃƒÂ© (F30)                                   |
| 17  | Rohrer, D. & Taylor, K. (2007). The shuffling of mathematics problems improves learning. _Instructional Science_, 35(6).                                       | Fondement Pratique EntrelacÃƒÂ©e (F32)                                |
| 18  | Sweller, J. & Cooper, G.A. (1985). The use of worked examples as a substitute for problem solving. _Cognition and Instruction_, 2(1).                          | Fondement Fading Effect, exemples rÃƒÂ©solus (F31)                    |
| 19  | Renkl, A. (1997). Learning from worked-out examples. _American Educational Research Journal_, 34(3).                                                           | Fondement fading progressif (F31)                                     |
| 20  | Dweck, C.S. (2006). _Mindset: The New Psychology of Success_. Random House.                                                                                    | Fondement Growth Mindset, feedback d'erreur (F33)                     |
| 21  | Yeager, D.S. et al. (2019). A national experiment reveals where a growth mindset improves achievement. _Nature_, 573.                                          | Fondement Growth Mindset appliquÃƒÂ© aux maths (F33)                  |

---

## Documents liÃƒÂ©s

> Note de rationalisation (28/03/2026) : les anciennes notes feature isolÃƒÂ©es encore utiles pour le contexte ont ÃƒÂ©tÃƒÂ© dÃƒÂ©placÃƒÂ©es dans `docs/03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/`. La vÃƒÂ©ritÃƒÂ© active reste portÃƒÂ©e par cette roadmap, les docs runtime actives et le code vivant.

| Sujet                                   | Document                                                                                                                                                                      |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Carte du dossier features               | [README.md](README.md)                                                                                                                                                        |
| SpÃƒÂ©cifications graphiques analytics  | [ANALYTICS_PROGRESSION.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ANALYTICS_PROGRESSION.md)                                                               |
| Fondements psychologiques badges        | [BADGES_AMELIORATIONS.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/BADGES_AMELIORATIONS.md)                                                                 |
| Workflow utilisateur complet            | [WORKFLOW_EDUCATION_REFACTORING.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/WORKFLOW_EDUCATION_REFACTORING.md)                                             |
| Normalisation difficultÃƒÂ©             | [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md) + [DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)   |
| Auth flow                               | [AUTH_FLOW.md](AUTH_FLOW.md)                                                                                                                                                  |
| Admin (pÃƒÂ©rimÃƒÂ¨tre, sÃƒÂ©curitÃƒÂ©) | [ADMIN_ESPACE_PROPOSITION.md](../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md), [ADMIN_FEATURE_SECURITE.md](ADMIN_FEATURE_SECURITE.md) |
| Analytics EdTech (implÃƒÂ©mentÃƒÂ©)     | [EDTECH_ANALYTICS.md](EDTECH_ANALYTICS.md)                                                                                                                                    |
| Endpoints API                           | [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)                                                                                                                              |
| ThÃƒÂ¨mes visuels                       | [THEMES.md](THEMES.md)                                                                                                                                                        |
| Internationalisation                    | [I18N.md](I18N.md)                                                                                                                                                            |
| Badges implÃƒÂ©mentÃƒÂ©s (archive)      | [AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md](../03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/PLAN_REFONTE_BADGES.md)                                              |
