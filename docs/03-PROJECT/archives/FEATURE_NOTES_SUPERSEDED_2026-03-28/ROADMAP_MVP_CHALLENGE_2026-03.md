# Roadmap Challenge — Vision Solo Founder
> Créé : 2026-03-23 | Challenger de ROADMAP_FONCTIONNALITES.md
> **Hypothèse centrale** : Un solo founder peut livrer 1 à 2 features significatives par mois.
> À ce rythme, le backlog actuel (34+ items) représente 2+ ans de travail minimum.
> Ce document recentre sur ce qui doit exister pour qu'**un parent sorte sa carte bancaire**.

---

## Ce qui change vs la roadmap actuelle

| Aspect | Roadmap actuelle | Cette version |
|--------|-----------------|---------------|
| Structure | P0→P4 par score | 3 horizons temporels |
| Horizon de planification | Open-ended | 12 mois max |
| Features listées | 34+ | 15 prioritaires |
| Logique de coupe | Score composite | "Est-ce bloquant pour payer ?" |
| F04 révisions espacées | P0 non impl. | **H1 bloquant absolu** |
| Dashboard parent | P1 (enfouie) | **H1 priorité revenue** |
| Analytics admin | "manquante" | Déjà implémentée — retirée |
| Onboarding | "à faire" | Déjà en place — à optimiser |

---

## État réel de la plateforme (2026-03-23)

### Ce qui est solide et en production

- Exercices adaptatifs (F05) ✅
- Défis quotidiens (F02) ✅
- Diagnostic initial F03 ✅ (1m30-2m30, objectif atteint)
- Onboarding ✅ : inscription → préférences → mail validation → 45min full accès → puis accès exercices sans validation, défis/dashboard après validation
- Analytics admin ✅ (page `/admin/analytics` existante — perfectible mais fonctionnelle)
- Gamification : moteur persistant ✅, ledger ✅, badges ✅
- IA génération exercices + défis ✅
- Rendu math KaTeX ✅, Growth Mindset ✅, Interleaving ✅
- Auth JWT + sessions ✅

### Ce qui est cassé ou absent (P0 réels)

- `apply_points` exercices : **corrigé lot 2** ✅ (en cours)
- Race condition gamification : **corrigé lot 1** ✅
- Révisions espacées SM-2 (F04) : **non implémenté** — seul vrai P0 restant
- Dashboard parent (F09) : absent — **bloquant revenue**
- IP Star Wars (F39) : dette légale — **bloquant avant scale**

---

## Horizon 1 — MVP Payant (0-3 mois)
> **Objectif** : Avoir un premier parent qui paye.
> Ces features sont des prérequis à toute commercialisation sérieuse.

### H1.1 — F04 : Révisions espacées SM-2 ⚡ BLOQUANT ABSOLU

**Pourquoi en premier** : C'est la promesse centrale de la plateforme — "apprends mieux, retiens plus longtemps". Sans ça, Mathakine est une plateforme d'exercices aléatoires comme beaucoup d'autres. Avec ça, c'est un système d'apprentissage adaptatif différenciant.

**Ce que ça débloque** : F23 (exercices adaptatifs SR+IA, score 17.1) — le produit le plus différenciant du backlog.

**Périmètre minimal** :
- File de révision par utilisateur (calcul intervalles SM-2 basique)
- Badge / rappel "à réviser aujourd'hui"
- Intégration dans les recommandations existantes
- **Ne pas sur-ingéniérer** : SM-2 basique > rien, même si imparfait

**Effort estimé** : 3-5 jours

---

### H1.2 — F09 : Dashboard parent minimal 💰 BLOQUANT REVENUE

**Pourquoi** : C'est la première brique payante. Sans dashboard parent, il n'y a rien à vendre. Un parent paie pour **voir ce que fait son enfant**, pas pour que l'enfant joue gratuitement.

**MVP strict (ce qui fait payer) :**
- Vue "mon enfant" : temps passé cette semaine, exercices complétés, score moyen
- Indicateur de régularité (pratique 3j/7 = bonne semaine)
- 1 graphe simple : évolution sur 30 jours
- Email hebdomadaire automatique (résumé)
- **Pas besoin de** : comparaison avec d'autres élèves, export PDF, multi-enfants (V2)

**Modèle d'accès** : Compte parent lié à un compte enfant. L'enfant garde son accès gratuit. Le parent paie pour la visibilité.

**Effort estimé** : 5-8 jours

---

### H1.3 — F39 : Suppression IP Star Wars ⚖️ BLOQUANT LÉGAL

**Pourquoi maintenant** : Dès qu'il y a de l'argent qui rentre, la plateforme devient une cible légale. Disney/Lucasfilm ne tolèrent pas l'utilisation commerciale de leurs marques sans licence. À faire avant la première campagne ou article de presse.

**Périmètre** :
- Renommer `jedi_rank` → `rank_title` (migration DB)
- Remplacer les valeurs Padawan/Jedi/Maître dans le code et les traductions
- Choisir un thème original (recommandé : thème mathématique pur ou exploration spatiale sans Star Wars)
- Étendre à F20 (niveaux de difficulté) dans le même lot pour ne faire la migration qu'une fois

**À décider avant de coder** : le nouveau thème des rangs — voir les options dans F39 (ROADMAP_FONCTIONNALITES.md).

**Effort estimé** : 3-5 jours (migration + frontend + i18n)

---

### H1.4 — Onboarding : micro-optimisations (pas une refonte)

L'onboarding est en place et fonctionnel (45min full accès, diagnostic 1m30-2m30). Ce n'est **pas** un chantier H1.

**Seuls ajustements utiles à ce stade** :
- Vérifier le taux de complétion du diagnostic (analytics admin)
- Un seul message de relance si le mail n'est pas validé après 24h (F19 léger)
- Ajouter l'accès au dashboard parent dans le flow d'inscription si compte parent

---

## Horizon 2 — Rétention et croissance (3-9 mois)
> **Objectif** : Les enfants reviennent. Les parents renouvellent. Premiers enseignants intéressés.

| Feature | Pourquoi H2 | Effort |
|---------|-------------|--------|
| **F23 — Exercices adaptatifs SR+IA** | Débloqué par F04, produit le plus différenciant (score 17.1) | 2-3 semaines |
| **F38 — Widget progression gamification** | Exploite le ledger déjà implémenté, rend les points visibles | 2-4 jours |
| **F13 — Déblocage badges temps réel** | Quick win rétention, UX de récompense immédiate | 1-2 jours |
| **F16 — Heatmap d'activité** | Visible par parent ET enfant, renforce le dashboard parent | 2-3 jours |
| **F19 — Notification email** | Streak en danger, badge proche — rétention passive | 3-5 jours |
| **F08 — Objectifs personnalisés** | Donne une direction à l'enfant, réduit le churn | 3-5 jours |
| **F39b — Refonte rangs (+ de paliers)** | Après avoir choisi le thème en H1, enrichir le système | 1-2 jours |

**Ce qu'on ne touche pas en H2 :**
- F18 (ligues) — compétition entre élèves, risque de démotivation des moins bons
- F28 (mode aventure) — effort massif, à réserver après traction confirmée
- F24 (tuteur IA contextuel) — 2-4 semaines, trop lourd sans équipe

---

## Horizon 3 — Scale (9-12+ mois)
> **Objectif** : Ouvrir le canal B2B (écoles, collèges). Nécessite traction B2C confirmée.

| Feature | Note |
|---------|------|
| **F25 — Mode classe / enseignant** | La plus grande feature du backlog. Ne pas commencer sans revenus récurrents. |
| **F24 — Tuteur IA contextuel** | Différenciant fort mais 2-4 semaines minimum. H3 au plus tôt. |
| **F04b — SM-2 avancé** | Après le MVP SM-2 de H1, affiner l'algorithme avec les données réelles. |
| **F11 — Partage progression → parents** | Lien de partage public, outil d'acquisition organique. |
| **F23b — SR+IA avancé** | Itérations sur la V1 de H2, avec feedback loop réel. |

---

## Ce qui sort du backlog actif

Ces features ont un score correct mais ne sont **jamais une priorité solo** :

| Feature | Raison de la sortie |
|---------|-------------------|
| F18 — Ligues hebdomadaires | Risque pédagogique (compétition négative), effort non justifié au stade actuel |
| F28 — Mode aventure / histoire | 5+ semaines pour un solo — à revoir après levée ou croissance équipe |
| F29 — Personnalisation avatar | Plaisant mais sans impact sur apprentissage ou revenue |
| F34 — Module Sciences | Hors scope maths — à ouvrir après consolidation du cœur de métier |
| F26 — Filtres tri badges | La page badges fonctionne — optimisation cosmétique |
| F27 — Optimisation re-renders | Uniquement si mesure de dégradation réelle en prod |

---

## Séquence recommandée (12 mois)

```
M1-M2  : F04 SM-2 minimal + F39 IP cleanup + choix thème rangs
M3-M4  : F09 Dashboard parent minimal + infrastructure paiement (Stripe)
M5     : Lancement offre payante parent · Mesurer conversion
M6-M7  : F23 exercices adaptatifs SR+IA (H2 principal)
M8     : F38 widget progression + F13 badges temps réel
M9     : F19 notifications email + F08 objectifs personnalisés
M10-12 : Selon traction — F25 mode classe si B2B ou F24 tuteur IA si B2C fort
```

---

## Principe directeur

> **Ne pas construire pour la plateforme que tu voudrais avoir.
> Construire pour le parent qui sortira sa carte dans 3 mois.**

Chaque feature doit répondre à l'une de ces trois questions :
1. Est-ce qu'un enfant apprend mieux avec ? (EdTech)
2. Est-ce qu'un parent voit la valeur et paie pour ça ? (Revenue)
3. Est-ce que ça empêche la plateforme de mourir légalement ou techniquement ? (Risque)

Si la réponse est non aux trois : H3 ou hors scope.

---

*Ce document est un challenger opinionné — il ne remplace pas ROADMAP_FONCTIONNALITES.md
qui reste la source de vérité détaillée. Il sert à la décision de priorisation.*
