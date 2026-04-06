# Neuro-inclusion EdTech - Verite active, backlog ouvert et plan d'implementation

> Mise a jour: 2026-04-06
> Statut: document actif
> Portee: ne garder que ce qui reste a faire
> Remplace le contenu historique de debat, les lots livres et les audits perimes

---

## 1. Objectif de ce document

Ce document n'est plus un compte-rendu de debat.

Il devient la reference active pour:

1. rappeler les contraintes produit deja arbitrees
2. consolider le diagnostic UX/UI/A11y/Learning Sciences encore valable
3. lister uniquement les sujets encore ouverts
4. prioriser un plan d'implementation detaille et executable

Tout ce qui est deja livre ou deja tranche n'est plus detaille ici sauf si cela conditionne un reste a faire.

---

## 2. Cadre produit actif a respecter

### 2.1 Regle de separation education / gamification

Decision produit explicite:

- les surfaces purement gamification peuvent assumer plus d'overdrive
- les surfaces ou zones 100 % education ne doivent pas utiliser ce langage visuel

Implications:

- `badges`, `leaderboard`, celebrations et certaines surfaces de recompense peuvent etre plus expressives
- `onboarding`, `diagnostic`, `exercise solver`, `challenge solver`, zones de lecture et de reponse doivent rester calmes, lisibles, peu distrayantes
- les surfaces hybrides doivent etre strictement bornees pour que la gamification n'ecrase jamais la tache cognitive

### 2.2 Regle sur la page de decouverte des defis

Decision produit explicite:

- la page de defis ne trouvera probablement pas un compromis parfait
- l'objectif n'est pas la purete abstraite
- l'objectif est un compromis efficace entre epuration, acces rapide et options utiles

Implications:

- il faut reduire le cout d'acces aux filtres et options
- sans retransformer la page en cockpit surcharge
- le succes sera un compromis "suffisamment bon", pas une perfection theorique

### 2.3 Ce document ne rouvre pas les decisions deja prises

Ne sont pas remises en cause ici:

- l'existence d'une couche apprenant dediee
- l'orientation neuro-inclusive des surfaces d'apprentissage
- la legitimite d'un registre visuel plus demonstratif sur les surfaces purement gamifiees

---

## 3. Hypotheses explicites utilisees pour le diagnostic

- Le support evalue est le code du frontend, pas une capture figee.
- Le perimetre prioritaire est: landing, onboarding, `Mon espace`, page defis, solveur de defi, widgets de progression.
- La cible provient de `docs/01-GUIDES/GUIDE_UTILISATEUR_MVP.md`: apprenants 5-20 ans, coeur de cible pratique 8-14 ans, autonomie variable, besoins potentiels TDAH, TSA, dyscalculie.
- Le job-to-be-done principal est: demarrer vite, faire une session courte utile, comprendre quoi faire ensuite, recevoir un feedback non punitif.
- L'objectif produit principal est: activation rapide, premiere pratique utile, retention par progression visible et revisions.
- Le typage front passe (`npx tsc --noEmit`).
- Le lint front n'est pas completement propre (`npm run lint:ci`): warnings React/perf mineurs et derive de formatage.
- Aucun test Axe ou assertion d'accessibilite automatisee n'a ete detecte dans `frontend/__tests__`.

---

## 4. Reformulation courte

- Cible: enfant ou adolescent apprenant, parfois accompagne d'un parent, avec besoin fort de clarte et de reassurance.
- Contexte: usage mobile, tablette ou desktop, a la maison ou en revision autonome.
- Objectif utilisateur: commencer rapidement, pratiquer sans friction, sentir qu'il progresse.
- Objectif business / integration: activer tot, faire revenir souvent, rendre la progression lisible sans stress.
- Maturite percue: produit serieux et pertinent sur le fond EdTech, mais encore inegal sur la finition systemique.

---

## 5. Diagnostic global

### 5.1 Verdict anti-patterns et "AI slop"

Verdict: `Fail` au niveau systeme, `Pass` local sur certaines surfaces educatives.

Nuance importante:

- ce verdict ne condamne pas les surfaces purement gamification, puisque leur niveau d'expressivite est assume par la strategie produit
- ce verdict sanctionne surtout le fait que des signaux visuels generiques ou artificiels restent portes par la couche partagee et reapparaissent dans des surfaces mixtes ou semi-educatives

Preuves principales:

- glassmorphism shared UI dans `frontend/app/globals.css`
- carte "spatial depth" avec lift et sweep dans `frontend/app/globals.css`
- CTA glow dans `frontend/app/globals.css`
- gradient text sur le niveau dans `frontend/components/dashboard/LevelIndicator.tsx`
- suggestions IA cliches dans `frontend/components/shared/AIGeneratorBase.tsx`
- styles hardcodes violets sur le solveur de defi dans `frontend/components/challenges/ChallengeSolver.tsx`

Contrepoids reel:

- `frontend/app/home-learner/page.tsx` est sensiblement plus calme, plus lineaire, plus coherent avec la cible
- `LearnerLayout` et `LearnerCard` reinstaurent une vraie grammaire "apprentissage d'abord"

### 5.2 Scores de synthese

- Score UI: `6/10`
- Score UX: `6/10`
- Score Learning Fit: `6/10`
- Score A11y: `5/10`
- Score Product Integration Fit: `7/10`

### 5.3 Conclusion courte

Le produit est bon sur l'intention pedagogique et sur certaines boucles de feedback.
Il reste penalise par:

- un cold start encore trop couteux
- des compromis de decouverte encore instables sur la page defis
- une frontiere education / gamification pas encore assez enforcee par le design system
- un socle tactile et A11y en dessous du niveau attendu pour la cible

---

## 6. Audit technique `/20`

| Dimension | Score /4 | Probleme principal |
| --- | ---: | --- |
| Accessibilite | 2 | Cibles tactiles sous 44x44 sur plusieurs primitives, couverture A11y automatisee absente |
| Performance percue et technique front | 2 | Systeme global de blur/lift/animation trop large, plus un `setState` synchrone dans un effect |
| Responsive / touch-first | 2 | Primitives trop compactes, widget defis en 3 colonnes fixes, toolbar IA serree |
| Theming / coherence des tokens / contraste | 3 | Base de tokens solide, mais plusieurs couleurs et traitements restent hardcodes |
| Anti-patterns UI | 2 | Les effets "AI-ish" restent visibles dans la couche commune meme si l'overdrive gamification est assume |
| **Total** | **11/20** | **Acceptable** |

Rating:

- `11/20` = `Acceptable`

Lecture:

- la base n'est pas mauvaise
- mais elle n'est pas encore assez stable ni assez propre pour une experience EdTech vraiment haut de gamme

---

## 7. Heuristiques UX `/40`

| # | Heuristique | Score /4 | Probleme principal |
| --- | --- | ---: | --- |
| 1 | Visibilite de l'etat du systeme | 3 | Bons loaders et skeletons, mais onboarding sans progression explicite |
| 2 | Correspondance systeme / monde reel | 3 | Microcopy globalement simple, mais certains codes visuels restent trop "produit" pour un enfant |
| 3 | Controle et liberte | 2 | Onboarding sans vraie echappatoire ni relache du tunnel |
| 4 | Coherence et standards | 2 | Bonne intention de separation, enforcement encore imparfait en shared UI |
| 5 | Prevention des erreurs | 3 | Garde-fous corrects, prevention faible de la surcharge decisionnelle |
| 6 | Reconnaissance plutot que rappel | 3 | CTA et reperes visibles, mais le cout de decouverte des defis reste trop eleve |
| 7 | Flexibilite et efficacite | 1 | Peu d'accelerateurs, peu de fast path expert, compromis encore couteux |
| 8 | Design esthetique et minimaliste | 2 | Tres correct sur les surfaces calmes, faible sur les surfaces mixtes |
| 9 | Diagnostic et recuperation d'erreur | 2 | Fallbacks presents mais parfois generiques; global error hors systeme |
| 10 | Aide et documentation | 2 | Hints et docs existent, mais l'aide contextuelle manque aux moments d'hesitation |
| **Total** |  | **23/40** | **Acceptable** |

Rating:

- `23/40` = `Acceptable`

---

## 8. Learning Sciences et charge cognitive

### 8.1 Analyse des 3 charges

#### Charge intrinseque

Niveau: `modere`

Motif:

- l'apprentissage des mathematiques et des defis logiques demande deja un effort cognitif reel
- ce n'est pas supprimable
- il faut donc surtout limiter la charge parasite

#### Charge extrinseque

Niveau: `trop eleve`

Sources principales:

- onboarding trop dense
- page defis avec compromis encore couteux entre acces rapide et options
- shared UI avec effets visuels trop demonstratifs dans certaines surfaces mixtes
- primitives compactes qui ralentissent l'interaction sur mobile

#### Charge germane

Niveau: `partiellement bien soutenu`

Points positifs:

- feedback de correction constructif
- revisions visibles et actionnables
- progression lisible
- ton general plutot rassurant

### 8.2 Checklist charge cognitive

| Item | Verdict | Note |
| --- | --- | --- |
| Focus unique | Echec | correct sur les solvers, insuffisant sur onboarding et decouverte des defis |
| Chunking | Echec | onboarding encore trop monobloc |
| Regroupement visuel | Reussi | bon sur `Mon espace`, plus inegal ailleurs |
| Hierarchie claire | Echec | surfaces mixtes encore en concurrence interne |
| Une decision a la fois | Echec | onboarding et certaines zones de decouverte demandent trop d'arbitrages |
| Nombre de choix limite | Reussi partiel | bien sur les CTA principaux, moins bon sur les surfaces d'exploration |
| Faible dependance a la memoire de travail | Reussi | peu de memorisation cross-screen |
| Progressive disclosure | Reussi partiel | bonne direction, compromis encore imparfait sur la page defis |

Resultat:

- `4 echecs sur 8`
- Niveau de charge cognitive: `critique`

### 8.3 Lecture pedagogique

L'interface aide reellement l'apprentissage quand elle:

- canalise l'attention sur une seule action
- donne un feedback immediat
- n'humilie pas l'erreur
- montre une progression courte et lisible

Elle cesse d'aider quand elle:

- fait negocier trop de choix avant la premiere valeur
- demande d'explorer l'interface avant d'apprendre
- reutilise un langage visuel spectaculaire dans des zones de lecture ou de reponse

---

## 9. Adequation a la cible

### 9.1 Reponse courte

- Cette interface est-elle adaptee a la cible precise ? `Partiellement`
- Le ton, la densite informationnelle et les interactions correspondent-ils a son niveau ? `Oui sur certaines surfaces, non de facon uniforme`
- Les moments de friction sont-ils tolerables ? `Pas toujours`
- Les feedbacks renforcent-ils l'apprentissage ? `Oui, globalement oui`

### 9.2 Lecture detaillee

Ce qui correspond a la cible:

- ton rassurant
- feedback non punitif
- progression visible
- `Mon espace` plus lisible et plus lineaire

Ce qui correspond moins:

- onboarding trop exigeant trop tot
- primitives encore trop petites pour tablette / mobile
- decouverte des defis encore couteuse en clics et en arbitrage
- shared UI qui laisse encore entrer des signaux trop "produit demonstratif"

---

## 10. Integration produit

### 10.1 Ce que l'interface soutient bien

- retention via revisions
- progression pedagogique via feedback et niveau
- engagement via routines et challenge board
- sentiment de progression visible

### 10.2 Ce qu'elle soutient moins bien

- onboarding / activation initiale
- passage inscription -> premiere valeur
- decouverte recurrente efficace des defis
- coherence de promesse entre neuro-inclusion affichee et shared UI effectivement calme

### 10.3 Ruptures UX detectees

- l'onboarding demande trop avant d'apporter une recompense
- la page defis reste un compromis encore couteux
- la frontiere education / gamification n'est pas encore assez outillee techniquement

### 10.4 Gamification decorative vs utile

Gamification utile:

- progression visible
- streak
- revisions priorisees
- challenge board si bien borne au contexte

Gamification decorative ou risquee:

- tout effet shared UI qui fuit vers les surfaces educatives
- tout code visuel fort qui concurrence une phase de lecture ou de reponse

---

## 11. Forces reelles a preserver

- `frontend/app/home-learner/page.tsx` est la surface la plus convaincante du perimetre
- le ton pedagogique reste majoritairement juste et non punitif
- la boucle feedback -> tentative -> explication -> progression existe reellement
- le design system theming et l'architecture front ne sont pas improvises
- la decision produit de separer education et gamification est saine et doit etre consolidee, pas abandonnee

---

## 12. Faiblesses ouvertes prioritaires

### [P1] Cold start encore trop couteux

- **Probleme exact**
  - l'onboarding demande trop d'informations avant d'apporter une premiere valeur
  - reference: `frontend/app/onboarding/page.tsx:95-227`
- **Pourquoi c'est un probleme pour cette cible**
  - enfant hesitant ou parent presse doit remplir plusieurs decisions avant de comprendre le benefice
- **Risque pedagogique / produit**
  - abandon avant premiere pratique
  - baisse d'activation
- **Recommandation concrete**
  - reduire l'onboarding initial a 1-2 decisions essentielles
  - decaler objectif et rythme apres la premiere pratique ou apres le diagnostic

### [P1] Decouverte des defis: compromis encore insuffisamment efficace

- **Probleme exact**
  - la page a deja ete epuree, mais l'acces aux filtres et options reste encore trop couteux pour certains usages
  - references:
    - `frontend/app/challenges/page.tsx:167-209`
    - `frontend/components/shared/ContentListProgressiveFilterToolbar.tsx`
- **Pourquoi c'est un probleme pour cette cible**
  - le cout de clic et d'exploration reste sensible pour retrouver rapidement un contenu pertinent
- **Risque pedagogique / produit**
  - friction sur la decouverte recurrente
  - fatigue d'usage
- **Recommandation concrete**
  - viser un compromis "good enough"
  - une action principale immediate
  - un acces aux filtres avances en une seule ouverture
  - pas de retour a un header surcharge

### [P1] Frontiere education / gamification encore trop dependante de la discipline humaine

- **Probleme exact**
  - la regle produit est bonne, mais la couche commune continue de porter des effets visuels trop demonstratifs
  - references:
    - `frontend/app/globals.css:1793-1838`
    - `frontend/app/globals.css:1977-2017`
    - `frontend/app/globals.css:2066-2114`
- **Pourquoi c'est un probleme pour cette cible**
  - si la frontiere n'est pas techniquement outillee, l'overdrive fuit vers les surfaces mixtes
- **Risque pedagogique / produit**
  - dilution de la promesse neuro-inclusive
  - perception de produit composite
- **Recommandation concrete**
  - definir et enforced 3 contextes:
    - `Education Core`
    - `Hybrid`
    - `Gamification Shell`

### [P1] Socle tactile et A11y insuffisant

- **Probleme exact**
  - tailles de controles trop petites sur plusieurs primitives
  - references:
    - `frontend/components/ui/button.tsx:21-27`
    - `frontend/components/ui/select.tsx:33-35`
    - `frontend/components/ui/switch.tsx:13-23`
    - `frontend/components/shared/AIGeneratorBase.tsx:151-185`
- **Pourquoi c'est un probleme pour cette cible**
  - usage mobile / tablette, motricite variable, fatigue visuelle
- **Risque pedagogique / produit**
  - erreurs de tap
  - lenteur percue
  - frustration mobile
- **Recommandation concrete**
  - imposer un minimum 44x44 sur toutes les primitives interactives
  - revalider les toolbars compactes

### [P2] Fallbacks et resilience encore inegaux

- **Probleme exact**
  - certains fallbacks sont corrects localement, mais `global-error` sort completement du design system
  - reference: `frontend/app/global-error.tsx:17-35`
- **Pourquoi c'est un probleme pour cette cible**
  - en cas de rupture, le produit perd sa tonalite rassurante
- **Risque pedagogique / produit**
  - perte de confiance
  - stress
- **Recommandation concrete**
  - realigner `global-error`
  - ajouter des error boundaries localisees sur les surfaces critiques

### [P2] Dette performance et motion dans la couche commune

- **Probleme exact**
  - transitions et effets globaux trop larges
  - warning React/perf dans `frontend/lib/hooks/useCountUp.ts:33-64`
- **Pourquoi c'est un probleme pour cette cible**
  - jank et bruit visuel sur appareils modestes
- **Risque pedagogique / produit**
  - perte de calme
  - baisse de fluidite
- **Recommandation concrete**
  - budget motion par contexte
  - correction des warnings React significatifs

### [P2] Generateur IA encore trop ambitieux visuellement et ergonomiquement dans le contexte de decouverte

- **Probleme exact**
  - suggestions narratives cliches + toolbar compacte dense
  - reference: `frontend/components/shared/AIGeneratorBase.tsx:31-37`, `141-254`
- **Pourquoi c'est un probleme pour cette cible**
  - l'outil parait plus demonstratif que guidant
- **Risque pedagogique / produit**
  - decouragement ou dispersion
- **Recommandation concrete**
  - replier davantage le generateur
  - reduire le bruit des suggestions
  - restaurer un vrai second niveau d'usage

### [P3] Some visual hardcodes still bypass tokens

- **Probleme exact**
  - certains styles utilisent encore des violets ou tons fixes
  - reference: `frontend/components/challenges/ChallengeSolver.tsx:376-383`
- **Pourquoi c'est un probleme**
  - coherence theming moins fiable
- **Risque**
  - rendu moins propre sur certains themes
- **Recommandation concrete**
  - passer ces styles par tokens semantiques

### [P3] Absence de preuve A11y automatisee

- **Probleme exact**
  - aucun test Axe detecte
- **Pourquoi c'est un probleme**
  - le niveau A11y ne peut pas etre defendu de facon fiable dans la duree
- **Risque**
  - regressions silencieuses
- **Recommandation concrete**
  - ajouter une couverture minimale Axe sur onboarding, `Mon espace`, page defis et solveurs

---

## 13. Persona red flags

### Jordan - first-timer

- casse sur l'onboarding trop dense
- ne comprend pas pourquoi il doit fournir autant avant de pratiquer
- risque d'interpreter certaines zones grisees ou compactes comme des bugs

### Casey - mobile distrait

- casse sur la taille de plusieurs controles
- paie trop cher l'acces aux options utiles sur la page defis
- supporte mal les toolbars compactes quand l'attention est basse

### Sam - accessibilite dependante

- beneficie de plusieurs bonnes intentions de structure
- mais reste penalise par la taille des cibles, l'absence de preuve Axe et les effets partages trop larges

### Riley - stress tester

- verra immediatement que la separation education / gamification existe en intention
- mais que la couche commune n'interdit pas encore assez les fuites entre contextes

---

## 14. Plan de priorites d'implementation

## Priorite 1 - Activation, acces direct et socle tactile

### 14.1 Chantier A - Simplifier l'onboarding de premiere valeur

**Objectif**

Reduire la friction avant premiere pratique.

**Resultat attendu**

L'utilisateur comprend en moins de 10 secondes:

- ce qu'il doit faire
- pourquoi on lui demande une information
- ce qu'il obtient juste apres

**Implementation cible**

1. Redefinir le parcours:
   - etape 1: classe / systeme scolaire
   - etape 2: go diagnostic ou go premiere pratique
2. Deplacer `learningGoal` et `practiceRhythm` dans un moment ulterieur:
   - apres premiere pratique
   - ou dans le profil
3. Ajouter une trace de progression visible:
   - titre d'etape
   - phrase de reassurance
   - resultat immediat attendu
4. Ajouter un message de valeur avant soumission:
   - "on adapte tes premiers exercices"

**Fichiers probables**

- `frontend/app/onboarding/page.tsx`
- `frontend/messages/fr.json`
- `frontend/messages/en.json`

**Criteres d'acceptation**

- maximum 2 decisions obligatoires avant la premiere valeur
- aucun champ secondaire ne bloque l'entree dans le produit
- feedback explicite apres validation

### 14.2 Chantier B - Stabiliser le compromis de la page defis

**Objectif**

Obtenir une page defis efficace, sans viser un ideal impossible.

**Resultat attendu**

L'utilisateur peut:

- lancer un defi vite
- ouvrir les filtres avances sans friction excessive
- comprendre la logique de la page sans surcharge

**Implementation cible**

1. Confirmer un fast path principal:
   - un contenu recommande
   - ou une action principale unique
2. Garder les filtres avances accessibles en une seule ouverture
3. Eviter tout doublonnage entre:
   - type chips
   - toolbar
   - AI generator
   - liste
4. Replier davantage le generateur IA si besoin
5. Mesurer la page sur un critere pragmatique:
   - nombre d'actions pour atteindre un filtre utile
   - nombre d'actions pour lancer un defi

**Fichiers probables**

- `frontend/app/challenges/page.tsx`
- `frontend/components/shared/ContentListProgressiveFilterToolbar.tsx`
- `frontend/components/challenges/AIGenerator.tsx`
- `frontend/components/shared/AIGeneratorBase.tsx`

**Criteres d'acceptation**

- acces aux options utiles en une seule ouverture de panneau maximum
- page lisible sans avoir a comprendre toute la toolbox
- pas de retour a une densite type cockpit

### 14.3 Chantier C - Elever les primitives a 44x44 minimum

**Objectif**

Rendre le socle tactile compatible avec la cible EdTech.

**Implementation cible**

1. Revoir `Button`:
   - `default`, `sm`, `lg`, `icon` au-dessus ou egal a 44px sur mobile
2. Revoir `SelectTrigger`
3. Revoir `Switch`
4. Revoir les toolbars compactes qui forcent des hauteurs plus basses
5. Revalider les pages:
   - onboarding
   - home learner
   - challenges
   - solver

**Fichiers probables**

- `frontend/components/ui/button.tsx`
- `frontend/components/ui/select.tsx`
- `frontend/components/ui/switch.tsx`
- `frontend/components/shared/AIGeneratorBase.tsx`

**Criteres d'acceptation**

- toutes les cibles interactives principales atteignent 44x44
- aucune regression severe de layout mobile

---

## Priorite 2 - Enforcer la frontiere education / gamification

### 14.4 Chantier D - Formaliser les contextes visuels

**Objectif**

Arreter de compter sur la seule vigilance manuelle.

**Implementation cible**

Definir trois contextes:

1. `Education Core`
   - pas de blur decoratif
   - pas de gradient text heroique
   - pas de glow CTA
   - pas de lift non essentiel
2. `Hybrid`
   - expressivite limitee
   - aucune concurrence avec lecture / reponse
3. `Gamification Shell`
   - overdrive autorise
   - celebrations, ranking, badges, rewards

**Actions**

1. Auditer les classes shared UI existantes
2. Reclasser chaque classe dans un contexte autorise
3. Renommer ou segreguer les utilitaires
4. Interdire l'import / usage de certains styles dans les surfaces `Education Core`

**Fichiers probables**

- `frontend/app/globals.css`
- `frontend/components/shared/ContentCardBase.tsx`
- `frontend/components/dashboard/LevelIndicator.tsx`
- `frontend/components/dashboard/StudentChallengesBoard.tsx`

**Criteres d'acceptation**

- un composant educatif ne peut plus heriter par accident d'un style overdrive
- la shared UI expose explicitement ce qui est reserve a la gamification

### 14.5 Chantier E - Nettoyer les styles shared UI trop demonstratifs

**Objectif**

Supprimer les effets systemiques qui rendent le produit composite.

**Actions**

1. Revoir `card-spatial-depth`
2. Revoir `dashboard-card-surface`
3. Revoir `btn-cta-primary`
4. Revoir les gradients et glows du niveau
5. Passer les hardcodes couleur sur tokens

**Criteres d'acceptation**

- les surfaces educatives restent stables quel que soit le theme
- les surfaces gamification gardent le droit a l'expressivite sans contaminer le reste

---

## Priorite 3 - Resilience, preuve A11y et dette technique

### 14.6 Chantier F - Refaire les fallbacks critiques

**Objectif**

Rendre les etats d'erreur coherents avec la promesse produit.

**Actions**

1. Refaire `frontend/app/global-error.tsx`
2. Verifier `error.tsx`
3. Ajouter des error boundaries localisees sur:
   - onboarding
   - challenges
   - solveurs

**Criteres d'acceptation**

- aucun fallback critique n'utilise d'inline style hors systeme
- le ton reste rassurant et actionnable

### 14.7 Chantier G - Ajouter la preuve A11y automatisee

**Objectif**

Sortir de l'opinion et verrouiller les regressions.

**Actions**

1. Ajouter Axe a la suite de tests front
2. Couvrir au minimum:
   - onboarding
   - `Mon espace`
   - page defis
   - challenge solver
3. Ajouter un seuil de non-regression simple en CI

**Criteres d'acceptation**

- au moins un test Axe par surface critique
- les regressions majeures deviennent visibles avant merge

### 14.8 Chantier H - Corriger les warnings React/performance utiles

**Objectif**

Nettoyer les points qui degradent la fluidite ou la robustesse.

**Actions**

1. Corriger `useCountUp`
2. supprimer les vars inutilisees detectees par lint
3. remettre le formatage des fichiers critiques au niveau

**Criteres d'acceptation**

- plus de warning React significatif sur la couche critique
- base de travail plus stable avant la suite des retouches UX

---

## 15. Ordre recommande d'execution

### Sprint 1 - Obligatoire

1. Simplification onboarding
2. Rehausse des primitives a 44x44
3. Ajustement page defis pour compromis plus efficace

### Sprint 2 - Structurant

1. Formalisation des contextes visuels
2. Nettoyage shared UI
3. Hardcodes couleur vers tokens

### Sprint 3 - Consolidation

1. Refonte `global-error`
2. Couverture Axe minimale
3. Nettoyage lint/perf

---

## 16. Definition of done

Ce document pourra etre considere comme clos quand les conditions suivantes seront vraies:

1. l'onboarding ne demande plus plus de 2 decisions obligatoires avant la premiere valeur
2. la page defis atteint un compromis d'acces juge efficace par l'equipe produit
3. toutes les primitives principales respectent 44x44 en contexte mobile
4. la separation `Education Core / Hybrid / Gamification Shell` est outillee dans la shared UI
5. `global-error` est aligne sur le design system
6. une couverture Axe minimale existe sur les surfaces critiques
7. les warnings React/performance significatifs de la couche critique sont nettoyes

---

## 17. Resume executif

Ce qui reste vraiment a faire n'est pas un grand reset visuel.

C'est un travail de precision sur 4 axes:

1. raccourcir le chemin vers la premiere valeur
2. rendre les controles reellement adaptables a la cible mobile / neuro-inclusive
3. transformer la frontiere education / gamification en regle technique, pas seulement en intention
4. fiabiliser la preuve A11y et les fallbacks

Le produit est deja credible sur le fond pedagogique.
Le prochain saut de qualite viendra d'une meilleure discipline systemique, pas d'une nouvelle couche decorative.
