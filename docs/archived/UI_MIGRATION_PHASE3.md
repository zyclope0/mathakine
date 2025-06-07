# Plan de Migration UI Phase 3 - Consolidation

## Objectif
Étendre les classes unifiées (`btn-unified`, `card-unified`) à tous les éléments de l'interface de manière progressive et sécurisée.

## Principes
1. **Aucune régression** : Tester après chaque changement
2. **Migration progressive** : Un template à la fois
3. **Conservation des styles existants** : Les classes unifiées s'ajoutent, ne remplacent pas
4. **Documentation** : Noter chaque changement

## État actuel
- ✅ `/login` : Bouton "Se connecter" a `btn-unified btn-primary`
- ✅ `/` : Première carte feature a `card-unified card-feature`
- ✅ `/exercises` : Bouton "Générer avec l'IA" a `btn-unified btn-secondary`

## Plan de migration par template

### 1. home.html (Page d'accueil)
**Boutons à migrer :**
- [ ] Ligne 52: `btn btn-large btn-primary cta-primary` → Ajouter `btn-unified`
- [ ] Ligne 56: `btn btn-large btn-ghost cta-secondary` → Ajouter `btn-unified`
- [ ] Ligne 165: `btn btn-primary` → Ajouter `btn-unified`

**Cartes à migrer :**
- [x] Ligne 76: `card feature-card` → Déjà migré
- [ ] Ligne 87: `card feature-card` → Ajouter `card-unified card-feature`
- [ ] Ligne 98: `card feature-card` → Ajouter `card-unified card-feature`
- [ ] Ligne 111: `card about-card` → Ajouter `card-unified`
- [ ] Ligne 178-202: `level-card` → Ajouter `card-unified`

### 2. dashboard.html (Tableau de bord)
**Boutons à migrer :**
- [ ] Ligne 149: `btn btn-outline-secondary` → Ajouter `btn-unified`

**Cartes à migrer :**
- [ ] Ligne 157, 165, 173: `card stats-card` → Ajouter `card-unified`
- [ ] Ligne 182, 189, 196: `card` → Ajouter `card-unified`
- [ ] Ligne 199, 207, 215, 223: `performance-card` → Ajouter `card-unified`
- [ ] Ligne 234, 239: `card` → Ajouter `card-unified`
- [ ] Ligne 255: `card recent-activity` → Ajouter `card-unified`

### 3. exercises.html (Liste des exercices)
**Boutons à migrer :**
- [ ] Ligne 46: `btn btn-primary compact-btn` → Ajouter `btn-unified`
- [x] Ligne 51: `btn compact-btn ai-btn` → Déjà migré
- [ ] Ligne 99: `btn btn-ghost btn-sm` → Ajouter `btn-unified`
- [x] Ligne 104: `btn btn-primary btn-sm` → Déjà migré
- [ ] Ligne 145, 150: `view-btn` → Ajouter `btn-unified` ?
- [ ] Ligne 245: `action-btn primary-action` → Ajouter `btn-unified btn-primary`
- [ ] Ligne 250: `action-btn secondary-action` → Ajouter `btn-unified btn-secondary`
- [ ] Ligne 256: `action-btn tertiary-action` → Ajouter `btn-unified btn-ghost`
- [ ] Ligne 286: `btn btn-primary btn-large` → Ajouter `btn-unified`
- [ ] Ligne 290: `btn btn-ghost` → Ajouter `btn-unified`
- [ ] Ligne 342: `btn btn-ghost` → Ajouter `btn-unified`
- [ ] Ligne 346: `btn btn-danger` → Ajouter `btn-unified`

**Cartes à migrer :**
- [ ] Ligne 134: `card enhanced-card` → Ajouter `card-unified`
- [ ] Ligne 183: `exercise-card enhanced-card` → Ajouter `card-unified`

### 4. exercise_simple.html & exercise_detail.html
**Boutons à migrer :**
- [ ] Ligne 25: `btn btn-outline-primary choice-btn` → Ajouter `btn-unified`
- [ ] Ligne 45: `btn btn-secondary` → Ajouter `btn-unified`
- [ ] Ligne 46: `btn btn-primary` → Ajouter `btn-unified`
- [ ] Ligne 351: `btn btn-secondary` → Ajouter `btn-unified`
- [ ] Ligne 419: `choice-btn` → Ajouter `btn-unified btn-outline`

**Cartes à migrer :**
- [ ] Ligne 6, 37: `card` → Ajouter `card-unified`
- [ ] Ligne 356: `card exercise-detail` → Ajouter `card-unified`

### 5. register.html & login.html
**Boutons à migrer :**
- [ ] Ligne 131 (register): `submit-button` → Ajouter `btn-unified btn-primary`
- [x] Ligne 98 (login): Déjà migré

**Cartes à migrer :**
- [ ] Ligne 9: `register-card` / `login-card` → Ajouter `card-unified`

### 6. profile.html
**Boutons à migrer :**
- [ ] Ligne 22: `avatar-edit-btn` → Ajouter `btn-unified btn-ghost`
- [ ] Ligne 97, 145: `save-btn` → Ajouter `btn-unified btn-primary`
- [ ] Ligne 160: `action-btn` → Ajouter `btn-unified btn-primary`
- [ ] Ligne 165: `action-btn secondary` → Ajouter `btn-unified btn-secondary`
- [ ] Ligne 170: `action-btn danger` → Ajouter `btn-unified btn-danger`
- [ ] Ligne 236: `btn-secondary` → Ajouter `btn-unified`
- [ ] Ligne 237: `btn-primary` → Ajouter `btn-unified`

**Cartes à migrer :**
- [ ] Ligne 13, 37, 105, 153, 178: `profile-card` → Ajouter `card-unified`

### 7. badges.html & about.html
**Boutons à migrer :**
- [ ] Ligne 645: `check-badges-btn` → Ajouter `btn-unified btn-primary`

**Cartes à migrer :**
- [ ] badges.html: `stat-card`, `badge-card` → Ajouter `card-unified`
- [ ] about.html: Toutes les cartes → Ajouter `card-unified`

## Ordre de migration recommandé
1. **home.html** - Cartes restantes (2e et 3e feature cards)
2. **dashboard.html** - Bouton refresh
3. **exercises.html** - Boutons de génération et filtres
4. **exercise_simple.html** - Boutons de choix
5. **profile.html** - Boutons d'action
6. **register.html** - Bouton de soumission
7. **badges.html & about.html** - Finalisation

## Tests à effectuer après chaque migration
1. Vérifier l'apparence visuelle
2. Tester les interactions (hover, click)
3. Vérifier la responsivité
4. Tester les animations
5. Vérifier l'accessibilité (focus) 