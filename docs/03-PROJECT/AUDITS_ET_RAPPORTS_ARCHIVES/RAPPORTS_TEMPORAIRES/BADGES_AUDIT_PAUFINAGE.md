# Audit page Badges — Avant paufinage

> **Date** : 16/02/2026  
> **Contexte** : Lot A terminé, écran 2560×1440  
> **Bases** : Rétention, gamification, ergonomie (interface uniquement)

---

## 1. Synthèse des remarques utilisateur

| Zone | Problème observé |
|------|------------------|
| **Ma collection** | Espace vide à droite, icône sigma/coche peu claire, « 7X Padawan » ambigu |
| **Badges en cours** | Large bande vide à droite (~60–70 % écran), badges « 0/0 » démotivants, cartes monotones sans icône |
| **À débloquer** | Texte de progression peu contrasté, barres quasi invisibles, pas de feedback pour les streaks |
| **Stats / Profil** | Icône cadenas sur badge obtenu (« Mois Parfait ») — incohérence visuelle |

---

## 2. Analyse ergonomique (écran 2560×1440)

### 2.1 Utilisation de l’écran

| Constat | Impact | Recommandation |
|--------|--------|----------------|
| **Contenu centré, marges larges** | Sous‑utilisation de l’espace horizontal | Largeur max du contenu (max-w-7xl) à augmenter ou colonnes latérales |
| **Grille 3 colonnes fixe** | Beaucoup d’espace vide au‑delà de 1200px | Grille responsive : 4–5 colonnes sur très grand écran |
| **Section « Badges en cours » étroite** | Perte de lisibilité et d’impact | Largeur alignée sur la grille principale ou layout 2 colonnes |

### 2.2 Lisibilité et contraste

| Constat | Impact | Recommandation |
|--------|--------|----------------|
| **Texte progression (bleu clair sur fond sombre)** | Contraste faible, lecture pénible | `text-muted-foreground` plus soutenu ou `text-foreground` pour X/Y |
| **Barres de progression fines** | Peu visibles quand &lt;20 % | Hauteur 8–10px, contour ou fond plus marqué |
| **« 19/50 » en bleu léger** | Peu mis en évidence | Typo plus forte, couleur primaire ou accent |

### 2.3 Incohérences visuelles

| Constat | Correction proposée |
|--------|---------------------|
| **Cadenas sur badge obtenu** | N’afficher le cadenas que sur badges verrouillés |
| **Icône sigma + coche** | Remplacer par CheckCircle ou trophée pour les badges obtenus |
| **« 7X Padawan »** | Clarifier : niveau, rang ou multiplicateur — libellé unique |

---

## 3. Analyse rétention (best practices)

### 3.1 Goal-Gradient — Progression vers l’objectif

| Problème | Effet rétention | Piste |
|----------|------------------|-------|
| **Badges « 0/0 »** | Perte de sens (pas de cible claire) | Afficher « Non démarré » ou masquer tant que conditions non remplies |
| **Barres presque invisibles** | Peu de renforcement visuel | Barres plus visibles + message « Plus que X » dès 50 % |
| **Pas de streak actuel** (ex. Maître des Divisions) | Impossible de mesurer l’avancement | Indicateur « Série actuelle : 5/15 » si calculable côté backend |

### 3.2 Clarté des objectifs

| Problème | Effet | Piste |
|----------|-------|------|
| **Cartes « Badges en cours » trop uniformes** | Difficile de prioriser | Icônes, différenciation par catégorie/difficulté |
| **Conditions uniquement en texte** | Charge cognitive plus élevée | Compléter par X/Y ou petite barre pour les badges mesurables |
| **Bouton « Vérifier les badges »** | Rôle peu évident | Label « Actualiser » ou info‑bulle explicative |

### 3.3 Renforcement positif

| Élément OK | Suggestion |
|------------|------------|
| « X % ont débloqué » (preuve sociale) | Garder, éventuellement mettre en avant pour les badges rares |
| Date d’obtention | OK, renforce l’ownership |
| Stats Performance | OK, feedback immédiat utile |
| Badges par catégorie | OK, aide à explorer et à se fixer des objectifs |

---

## 4. Analyse gamification (interface)

### 4.1 Hiérarchie et récompenses

| Problème | Impact | Piste |
|----------|--------|-------|
| **Visuel identique pour tous les badges** | Peu de valorisation des badges difficiles | Bordure/glow pour or/légendaire, différenciation par difficulté |
| **Points peu mis en avant** | Moins de clarté sur la récompense | Renforcer la zone pts (taille, couleur) |
| **Pas de célébration visuelle au déblocage** | Moins de « moment fort » | Animation légère, confettis ou toast au déblocage |

### 4.2 Motivation et rareté

| Élément | État | Piste |
|--------|------|-------|
| Badge « Rare » | Présent | Bien, à garder |
| Rareté visuelle par difficulté | Partiel | Renforcer pour gold/légendaire |
| « Proches du déblocage » | Filtre présent | Mettre en avant en haut ou avec un bandeau |

### 4.3 Endowment (effet de dotation)

| Élément | État |
|--------|------|
| Ma collection en premier | OK |
| Option épingler | OK |
| Visuel distinct obtenu vs verrouillé | À vérifier (cadenas incohérent) |

---

## 5. Priorisation pour le paufinage

### P0 — Corrections rapides

1. **Cadenas sur badges obtenus** — Ne pas afficher le cadenas quand le badge est débloqué.
2. **Contraste progression** — Texte X/Y et barres plus lisibles.
3. **Badges « 0/0 »** — Gérer l’affichage (masquer, « Non démarré » ou message explicatif).

### P1 — Ergonomie grand écran

4. **Grille responsive** — 4–5 colonnes au‑delà de ~1400px.
5. **Largeur max contenu** — Augmenter sur 2560px.
6. **Section « Badges en cours »** — Adapter la largeur au reste de la page.

### P2 — Rétention / gamification

7. **Barres de progression** — Hauteur et visibilité augmentées.
8. **Streaks** — Afficher « Série actuelle : X/Y » quand le backend le permet.
9. **Icône obtention** — Remplacer sigma/coche par une icône plus explicite.
10. **Clarifier « 7X Padawan »** — Libellé et design univoques.

### P3 — Polish

11. **Célébration au déblocage** — Toast ou animation.
12. **Hiérarchie visuelle or/légendaire** — Bordure ou effet pour les badges prestigieux.
13. **Badges en cours** — Icônes par catégorie ou difficulté pour réduire la monotonie.

---

## 6. Références

- **Goal-Gradient** : Clark Hull 1932, Kivetz — barres de progression +40–60 % d’engagement.
- **Endowment** : Thaler, Kahneman — ownership augmente la valeur perçue.
- **Scarcity** : Cialdini — rareté augmente la motivation.
- **Social proof** : Cialdini — « X % l’ont » renforce le désir.
- **NN/G** : Utilisation de l’écran, contraste, hiérarchie visuelle.
- **Long-Term Gamification Survey** (Springer 2024) : ownership, communauté, objectifs évolutifs.

---

*Document préparatoire pour les itérations de paufinage de la page badges.*
