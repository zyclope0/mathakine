# Analyse thèmes graphiques — Impact UX et qualité CSS

**Date :** Février 2026 
**Périmètre :** Thème graphique, impact utilisateur, architecture CSS  
**Dernière mise à jour :** Fév. 2026 — P0–P4 implémentés + 7 thèmes  
**Type :** Analyse (implémentée)  
**Statut :** ✅ Toutes recos appliquées

---

## 1. État actuel — Ce qui fonctionne bien

| Élément | Bilan |
|--------|-------|
| **7 thèmes cohérents** | Spatial, Minimaliste, Océan, Dune, Forêt, Lumière, Dinosaures — variables CSS bien isolées |
| **WCAG visé** | Contrastes AAA documentés (primary, muted-foreground, primary-text-on-dark) |
| **Accessibilité** | focus-mode (TSA/TDAH), high-contrast, reduced-motion, skip link |
| **Persistance** | Thème stocké en localStorage + profil utilisateur |
| **Architecture** | `@theme inline`, layers, `data-theme` sur `<html>` |

---

## 2. Problèmes à impact utilisateur

### 2.1 Thème par défaut = sombre (spatial)

**Constat :** Le thème spatial (fond #0a0a0f) est proposé par défaut. Cible : enfants 5–20 ans, parents, enseignants.

**Risque psycho/marketing :**
- Une majorité des visiteurs non inscrits préfèrent un fond clair.
- Un fond très sombre peut être perçu comme « jeu vidéo » ou peu rassurant pour les parents.
- Moindre confiance perçue sur un site éducatif en sombre par défaut.

**Options :**

| Option | Action | Avantage | Inconvénient |
|-------|--------|----------|--------------|
| A | Garder spatial par défaut | Cohérence actuelle | Risque de rebond sur public familial |
| B | Détecter `prefers-color-scheme` et l’utiliser pour le 1er chargement | Respect des préférences système | Spatial reste sombre pour ceux en dark system |
| C | Défaut « Minimaliste » (clair) pour les non connectés, spatial pour les connectés | Bon équilibre confiance/identité | Changement de thème à la connexion |

**Recommandation :** Option B à court terme (peu de code, gain de confiance). Option C si tu veux optimiser la conversion inscription.

**État :** ✅ **Implémenté (Option B)** — `Providers.tsx` : si aucune préférence stockée, détection de `prefers-color-scheme`. Si light → Minimaliste, si dark → Spatial.

---

### 2.2 Effets visuels (shimmer, sweep, orbit)

**Constat :** Boutons, cards et background ont des effets (shimmer, sweep, particules, planète). Ils respectent `prefers-reduced-motion`, mais le mode « normal » reste riche.

**Risque cognitif :**
- Public TSA/TDAH : le mode Focus masque beaucoup d’éléments, ce qui est bon.
- Pour les autres : risque de surcharge si trop d’effets sur une même page.
- Particules/planète/étoiles = ambiance « spatiale » alignée avec la marque, mais peuvent distraire pendant la résolution d’exercices.

**Recommandation :** Pas de changement majeur. Le focus-mode couvre déjà les cas sensibles. Si tu mesures du bounce élevé sur les pages exercices, envisager un mode « lecture » ou réduction d’effets sur ces écrans.

---

### 2.3 Hiérarchie des CTA

**Constat :** Boutons CTA utilisent `btn-cta-primary`, gradient hero `from-primary via-accent`, bonne lisibilité.

**Point d’attention :** ~~Couleurs codées en dur créaient des incohérences sur certains thèmes.~~ ✅ **Corrigé** — effets hover utilisent `var(--primary)`.

---

## 3. Problèmes CSS — Reproductibilité et maintenance

### 3.1 Couleurs codées en dur (violet spatial)

~~Les valeurs suivantes ne s'adaptaient pas aux autres thèmes~~ ✅ **Corrigé**

**Implémenté :** Remplacement par `color-mix(in srgb, var(--primary) X%, transparent)` dans `globals.css` :
- Boutons (hover, active) : box-shadow
- Cards `[data-slot="card"]` : ::before gradient, box-shadow, border-color
- Inputs/textarea/select : border-color hover

---

### 3.2 Duplication de code

- **@keyframes shimmer** — ✅ **Corrigé** : bloc dupliqué supprimé, une seule définition conservée.
- **`.text-muted-foreground`** : `opacity: 0.9` peut s’ajouter à une couleur déjà en `--muted-foreground` et compliquer le calcul de contraste.

**Corrigé (P4) :** L’`opacity: 0.9` sur `.text-muted-foreground` ne dégrade pas le contraste WCAG.

---

### 3.3 Règle `primary` en light mode

```css
:root:not(.dark) .text-primary { color: #6d28d9; }
```

**Constat :** Couleur fixe pour améliorer le contraste sur fond clair. Sur Minimaliste (light), c’est pertinent. Sur Spatial (déjà sombre), `:root` peut encore s’appliquer selon la structure du DOM. Dune, Forêt, Lumière, Dinosaures utilisent leur `--primary` natif.

**Action :** Cibler explicitement le thème Minimaliste en light :  
`[data-theme="minimalist"]:not(.dark) .text-primary`  
et éviter d’affecter Spatial si ce n’est pas voulu.

---

## 4. Synthèse des priorités

| Priorité | Action | Effort | Impact | État |
|----------|--------|--------|--------|------|
| **P0** | Remplacer les couleurs fixes par `var(--primary)` / `color-mix` | 1–2 h | Cohérence sur tous les thèmes | ✅ Fait |
| **P1** | Détecter `prefers-color-scheme` pour le thème initial | 1 h | Confiance, alignement préférences | ✅ Fait |
| **P2** | Supprimer la duplication de @keyframes shimmer | 15 min | Maintenance | ✅ Fait |
| **P3** | Affiner les règles `.text-primary` en light mode (ciblage par thème) | 30 min | Comportement prévisible | ✅ Fait |

---

## 5. Réalisé (implémenté)

| Priorité | Action | Fichiers modifiés |
|----------|--------|-------------------|
| **P0** | Couleurs fixes → `color-mix(in srgb, var(--primary) X%, transparent)` | `globals.css` — boutons, cards, inputs |
| **P1** | Détection `prefers-color-scheme` pour les nouveaux visiteurs | `Providers.tsx` |
| **P2** | Suppression duplication `@keyframes shimmer` | `globals.css` |
| **P3** | Règles `.text-primary` et `.text-muted-foreground` ciblées Minimaliste en light uniquement | `globals.css` |
| **P4** | Suppression `opacity: 0.9` sur `.text-muted-foreground` (dégradait le contraste) | `globals.css` |

---

## 6. Prochaines actions proposées

| Priorité | Action | Effort | Impact |
|----------|--------|--------|--------|
| ~~P4~~ | ~~Vérifier `.text-muted-foreground` + `opacity: 0.9`~~ | — | ✅ Fait |
| **P5** | Audit visuel : 7 thèmes sur accueil, exercices, inscription | ~1 h | Cohérence |
| **Option** | Option C : Minimaliste pour non connectés, Spatial pour connectés | ~1 h | Conversion inscription |

---

## 7. Checklist qualité CSS

- [x] Aucune couleur hex/rgba fixe pour primary/accent dans les effets globaux (boutons, cards, inputs)
- [x] Hover/focus des boutons et cards basés sur `var(--primary)`
- [x] Une seule définition de chaque @keyframes
- [x] `prefers-color-scheme` appliqué au premier chargement
- [x] Règles de contraste `.text-primary` ciblées par `[data-theme]` (P3)
- [x] `prefers-reduced-motion` vérifié sur tous les effets animés

---

## 8. Recommandations non prioritaires

- **AlphaBanner :** Amber convient pour une alerte. Garder tel quel.
- **Exo 2 :** Police adaptée, bonne lisibilité. Pas de changement.
- **Cards :** `card-spatial-depth` + `data-slot="card"` — structure claire. Couleurs adaptatives ✅ (P0).

---

## 9. Prochaines étapes suggérées (ordre de priorité)

| # | Action | Effort | Fichiers |
|---|--------|--------|----------|
| ~~1~~ | ~~P4 — .text-muted-foreground~~ | — | ✅ Fait |
| 2 | **P5** — Audit visuel : parcourir accueil, exercices, inscription sur les 7 thèmes | ~1 h | — |
| 3 | **Optionnel** — Option C (Minimaliste pour non connectés, Spatial pour connectés) si objectif conversion | ~1 h | `Providers.tsx`, logique auth |
