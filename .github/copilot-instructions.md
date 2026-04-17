# Mathakine — instructions pour assistants IA (UI / frontend)

Ce fichier aligne **Copilot**, **Cursor**, **Claude** et tout assistant sur les **contraintes EdTech et neuro-inclusives** du projet. Il duplique la section **Design Context** de `.impeccable.md` (source de vérité à la racine).

**Ne pas** proposer de layouts génériques type dashboard SaaS (Vercel / Stripe / Linear) ni des grilles de cartes bordées + ombres si une mise en page plus simple par **espacement** suffit.

---

## Design Context

### Users

- **Apprenants (enfants / collégiens)** : exercices et défis au centre ; charge cognitive **minimale**.
- **Adultes (parents / enseignants)** : efficacité et clarté, **sans** “grid of boxes” façon B2B.
- **Administrateurs (`/admin/*`)** — **pas** apprenants ni parents : retours, modération, comptes = **triage / ops** ; clarté opérationnelle et actions explicites OK ; toujours sobre + WCAG (voir `.impeccable.md`).
- **Multilingue fr/en** ; patterns maintenables.

### Brand Personality (3 mots)

1. **Apaisant** — zéro surcharge sensorielle ; charge cognitive minimale.
2. **Évident** — navigation tubulaire ; pas de menus cachés ; **boring but obvious**.
3. **Constructif** — erreur = partie de l’apprentissage ; feedback **doux, non punitif**.

### Aesthetic Direction

**Références** : Gov.uk (clarté cognitive + accessibilité), Khan Academy (whitespace), Duolingo **uniquement** pour la mécanique streak / gamification, avec **~80 % de bruit visuel en moins**.

**Anti-références** : dashboards B2B SaaS (style Vercel, Stripe, Linear). **Interdiction** du “Grid of Boxes” (cartes `border` + `shadow-sm` partout). Séparer par **padding / gap**, pas par lignes ou cadres systématiques.

**Constellation vs streak** : constellation = arc **persistant** (niveaux / paliers), motif géométrique sobre ; streak = indicateur **séparé**, pas le même motif ; pas deux constellations sans rôle distinct sur une même vue.

### Thème clair / sombre

- **Égale importance.** Le sombre est une **nécessité d’accessibilité** (hypersensibilité visuelle).
- **Mode clair** : **jamais** de fond de page blanc pur (`#FFFFFF` / `bg-white`) — halo / éblouissement délétère pour TSA/TDAH. Fonds **muted** (ex. `slate-50`, `zinc-50`).

### Palette “Muted”

- Fond principal : gris-bleu très clair — thème spatial par défaut : fond teinté via tokens (ex. `#f0f4ff`), pas blanc pur ; équivalents sémantiques possibles (`slate-50` / `zinc-50`).
- Cartes : surfaces discrètes, peu de contraste avec le fond ; **pas** d’ombres décoratives type grille SaaS — ombres **minimales** seulement pour hiérarchie / état (focus, survol).
- Erreurs : pas de rouge vif (`bg-red-500`) ; tons doux (ex. `rose-100` / `rose-800`).
- Succès : vert doux (ex. `emerald-100` / `emerald-800`).

### Accessibilité

- **WCAG AA minimum** (contrastes typo).
- **COGA** : divulgation progressive, **pas d’autoplay**, `prefers-reduced-motion` **strict** — animations de récompense **désactivables instantanément**.
- Cibles **≥ 44×44 px**.

### Design Principles (rappel pour auto-complétions)

1. Cognitive load first — l’exercice prime ; pas d’animation décorative pendant la réflexion.
2. Évidence avant fioriture — pas de pattern caché “pour le style”.
3. Feedback constructif — pas punitif ; gamification discrète.
4. **Espace > bordures** — pas de grille de cartes ombrées par défaut.
5. **Pas de blanc pur** en fond page (clair) ; dark aussi important.
6. WCAG AA + COGA + reduced-motion respectés dans les suggestions de code.
7. Constellation (motif) = progression persistante uniquement ; streak hors de ce motif.

---

**Typo / code** : **Nunito** (UI), **JetBrains Mono** (code) via `next/font` dans `frontend/app/layout.tsx`.

Pour le détail et l’historique des décisions, voir `.impeccable.md` à la racine du dépôt.
