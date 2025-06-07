# 🎨 Guide Interface Utilisateur Mathakine

**Documentation complète UI/UX** - Version 3.0  
*Dernière mise à jour : 6 juin 2025*

---

## 🎯 Vue d'Ensemble de l'Interface

Mathakine propose une **interface immersive Star Wars** conçue spécifiquement pour l'apprentissage mathématique des enfants autistes. L'interface combine une esthétique galactique engageante avec des principes d'accessibilité avancés.

### Principes de Design
- **🌌 Immersion Star Wars** : Thème cohérent avec terminologie et visuels galactiques
- **♿ Accessibilité WCAG 2.1 AA** : Support complet des technologies d'assistance
- **📱 Mobile-First** : Conception responsive adaptative
- **🎮 Gamification** : Progression par rangs Jedi et récompenses visuelles
- **🧠 Adapté aux enfants autistes** : Animations douces, contrastes élevés, structure prévisible

---

## 🗺️ Architecture des Pages

### Pages Principales (14 routes)

#### 1. **Page d'Accueil** (`/`)
**Fonction** : Point d'entrée et présentation du projet  
**Composants** :
- **Hero Section** avec statistiques dorées
- **Fond d'étoiles animées** (50 étoiles scintillantes)
- **3 planètes flottantes** avec rotation
- **CTA principal** : "Commencer l'aventure" 🚀
- **Cartes de fonctionnalités** avec effets hover

```html
<section class="hero-section">
  <div class="stars-container">
    <!-- 50 étoiles générées en JavaScript -->
  </div>
  <div class="hero-card enhanced-card">
    <h1>Bienvenue dans la galaxie Mathakine</h1>
    <div class="hero-stats">
      <div class="stat-item">
        <span class="stat-number">150+</span>
        <span class="stat-label">Exercices</span>
      </div>
    </div>
    <a href="/exercises" class="cta-primary">
      <i class="fas fa-rocket"></i> Commencer l'aventure
    </a>
  </div>
</section>
```

#### 2. **Exercices** (`/exercises`)
**Fonction** : Hub central d'exercices mathématiques  
**Composants** :
- **Filtres dynamiques** : Type, difficulté, créateur
- **Vue grille/liste** avec basculement
- **Cartes d'exercices** avec badges colorés
- **Pagination avancée** avec ellipses
- **Génération IA** et standard
- **Modales de détails** et confirmation

#### 3. **Tableau de Bord** (`/dashboard`)
**Fonction** : Statistiques personnalisées utilisateur  
**Composants** :
- **Graphique de progression** (30 jours)
- **Métriques temps réel** (points, réussite, séries)
- **Rangs Jedi** avec progression visuelle
- **Recommandations personnalisées**
- **Historique des tentatives**

#### 4. **Défis Logiques** (`/challenges`)
**Fonction** : Énigmes spatiales thématiques  
**Composants** :
- **5 énigmes spatiales** (IDs 2292-2296)
- **Types variés** : SEQUENCE, PATTERN, PUZZLE, DEDUCTION
- **Données visuelles** adaptatives (ASCII, grilles, diagrammes)
- **Interface uniformisée** avec thème Star Wars
- **Résolution interactive** avec feedback immédiat

#### 5. **Profil Utilisateur** (`/profile`)
**Fonction** : Gestion du compte et préférences  
**Composants** :
- **Informations personnelles** modifiables
- **Préférences d'apprentissage** (niveau, style)
- **Paramètres d'accessibilité** (4 modes)
- **Historique complet** des activités
- **Badge de progression** Jedi

#### 6. **Page À Propos** (`/about`)
**Fonction** : Histoire inspirante du projet  
**Composants** :
- **Histoire personnelle** : Création pour Anakin
- **Mission éducative** : Apprentissage adaptatif
- **Valeurs du projet** : Inclusion et accessibilité
- **Équipe et vision** future

### Pages d'Authentification

#### 7. **Connexion** (`/login`)
**Fonction** : Authentification utilisateur  
**Composants** :
- **Formulaire simplifié** (username/password)
- **Remplissage automatique** pour tests (ObiWan)
- **Messages d'erreur** contextuels
- **Lien mot de passe oublié**
- **Design cohérent** avec thème Star Wars

#### 8. **Inscription** (`/register`)
**Fonction** : Création de nouveau compte  
**Composants** :
- **Formulaire complet** avec validation temps réel
- **Choix niveau** et préférences
- **Confirmation mot de passe**
- **Acceptation conditions** d'utilisation

#### 9. **Mot de Passe Oublié** (`/forgot-password`)
**Fonction** : Récupération de compte  
**Composants** :
- **Saisie email** avec validation
- **Instructions envoi** email
- **Formulaire reset** avec token
- **Confirmation succès**

### Pages Spécialisées

#### 10. **Exercice Détaillé** (`/exercise/{id}`)
**Fonction** : Résolution d'exercice individuel  
**Composants** :
- **Énoncé formaté** avec choix multiples
- **Timer visuel** optionnel
- **Validation réponse** avec feedback
- **Solution détaillée** après tentative
- **Navigation exercice** suivant/précédent

#### 11. **Défi Logique** (`/logic-challenge/{id}`)
**Fonction** : Interface résolution énigmes  
**Composants** :
- **Affichage adaptatif** selon type de données visuelles
- **Zone de réponse** interactive
- **Système d'indices** progressifs (3 niveaux)
- **Solution explicative** complète
- **Retour défis** avec historique

#### 12. **Archives du Temple** (`/archives`)
**Fonction** : Gestion exercices archivés (admin)  
**Composants** :
- **Liste exercices** archivés avec filtres
- **Actions groupées** (restaurer, supprimer définitivement)
- **Historique archivage** avec logs
- **Interface admin** sécurisée par rôles

#### 13. **Debug** (`/debug`) 
**Fonction** : Outils développement (dev uniquement)  
**Composants** :
- **Tests fonctionnalités** rapides
- **Logs système** en temps réel  
- **Métriques performance**
- **Reset données** de test

#### 14. **Page d'Erreur 404** (`/error`)
**Fonction** : Gestion erreurs navigation  
**Composants** :
- **Message thématique** Star Wars
- **Navigation retour** vers accueil
- **Suggestions pages** populaires
- **Design cohérent** avec site

### Pages Spécialisées Avancées

#### 15. **Galerie de Badges** (`/badges`)
**Fonction** : Affichage collection badges utilisateur  
**Composants** :
- **Statistiques utilisateur** (badges gagnés, progression Jedi)
- **Grille badges** par catégories (exercices, défis, accomplissements)
- **Barres de progression** animées vers prochains badges
- **Rangs Jedi** avec système de couleurs (Youngling → Grand Master)
- **Effets visuels** Star Wars (glow, gradients, animations)

#### 16. **Centre de Contrôle Parental** (`/control-center`)
**Fonction** : Interface parentale de supervision  
**Composants** :
- **Profil enfant** avec avatar et progression
- **Préférences sensorielles** (hypersensible/hyposensible)
- **Gestion difficulté** (mode auto/manuel/assisté)
- **Statistiques apprentissage** avec rapport téléchargeable
- **Contrôles temps** (durée sessions, pauses, rappels)
- **Paramètres sécurité** et restrictions

#### 17. **Créateur d'Exercices** (`/new-exercise`)
**Fonction** : Interface création exercices par enseignants  
**Composants** :
- **Formulaire structuré** (titre, type, difficulté)
- **Éditeur questions** avec formatage riche
- **Générateur choix multiples** avec validation
- **Prévisualisation temps réel** avant publication
- **Système explicatifs** pour solutions
- **Sauvegarde brouillons** automatique

#### 18. **Paramètres Utilisateur** (`/settings`)
**Fonction** : Configuration personnalisée compte  
**Composants** :
- **Onglets organisés** (Général, Accessibilité, Notifications, Confidentialité)
- **Préférences thème** (Star Wars, Océan, Forêt, Espace)
- **Options audio** (sons/musique/effets)
- **Profil sensoriel** avec modes adaptatifs
- **Paramètres accessibilité** (contraste, texte, mouvement)
- **Gestion notifications** et rappels

#### 19. **Défis Hybrides** (`/challenges-hybrid`)
**Fonction** : Interface défis combinés maths+logique  
**Composants** :
- **Sections typées** (Exercices, Logique, Hybrides)
- **Cartes défis** avec bordures colorées par type
- **Badges progression** et récompenses
- **Stories thématiques** Star Wars par défi
- **Système points** et classements
- **Interface adaptative** selon type de données

#### 20. **Base Template** (`base.html`)
**Fonction** : Template maître pour toutes les pages  
**Composants** :
- **Architecture HTML5** sémantique complète
- **Système CSS** modulaire et optimisé
- **Navigation unifiée** (3 éléments max)
- **Barre accessibilité** avec 4 modes
- **Performance optimisée** (preload, DNS prefetch)
- **Meta tags** SEO et accessibility complets

#### 21. **Résolution Exercice** (`/exercise/{id}`)
**Fonction** : Interface résolution exercice simple  
**Composants** :
- **Question formatée** avec styling thématique
- **Grille choix** responsive (2 colonnes)
- **Feedback visuel** immédiat (correct/incorrect)
- **Navigation séquentielle** (suivant/précédent)
- **Animations Star Wars** et effets visuels
- **Timer optionnel** et compteur points

---

## 🎨 Système de Design

### Palette de Couleurs Star Wars

#### Couleurs Principales
```css
:root {
  /* Couleurs Star Wars */
  --sw-blue: #4f9eed;        /* Bleu lightsaber Luke */
  --sw-green: #5cb85c;       /* Vert lightsaber Yoda */
  --sw-gold: #f1c40f;        /* Or droïdes et accents */
  --sw-purple: #8b5cf6;      /* Violet Mace Windu */
  --sw-red: #e74c3c;         /* Rouge Sith/danger */
  
  /* Neutres galactiques */
  --space-black: #0a0a0a;    /* Noir spatial profond */
  --space-dark: #1a1a1a;     /* Gris foncé stations */
  --space-medium: #2a2a2a;   /* Gris moyen interfaces */
  --space-light: #f8f9fa;    /* Blanc textes clairs */
  
  /* Gradients */
  --gradient-space: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
  --gradient-hero: linear-gradient(135deg, #4f9eed 0%, #8b5cf6 100%);
}
```

#### Couleurs Sémantiques
```css
:root {
  /* États fonctionnels */
  --success: var(--sw-green);
  --warning: var(--sw-gold);
  --error: var(--sw-red);
  --info: var(--sw-blue);
  
  /* Badges exercices */
  --badge-addition: #4ade80;      /* Vert clair */
  --badge-soustraction: #f59e0b;  /* Orange */
  --badge-multiplication: #3b82f6; /* Bleu */
  --badge-division: #8b5cf6;      /* Violet */
  --badge-fractions: #ec4899;     /* Rose */
  --badge-geometrie: #06b6d4;     /* Cyan */
  --badge-divers: #84cc16;        /* Lime */
}
```

### Typographie

#### Familles de Polices
```css
:root {
  /* Polices principales */
  --font-primary: 'Roboto', 'Segoe UI', system-ui, sans-serif;
  --font-secondary: 'Arial', sans-serif;
  --font-monospace: 'Consolas', 'Monaco', monospace;
  
  /* Polices spécialisées */
  --font-dyslexia: 'OpenDyslexic', sans-serif; /* Mode dyslexie */
  --font-display: 'Star Jedi', fantasy;        /* Titres Star Wars */
}
```

#### Échelle Typographique
```css
:root {
  /* Tailles responsive avec clamp() */
  --text-xs: clamp(0.75rem, 2vw, 0.875rem);    /* 12-14px */
  --text-sm: clamp(0.875rem, 2.5vw, 1rem);     /* 14-16px */
  --text-base: clamp(1rem, 3vw, 1.125rem);     /* 16-18px */
  --text-lg: clamp(1.125rem, 3.5vw, 1.25rem);  /* 18-20px */
  --text-xl: clamp(1.25rem, 4vw, 1.5rem);      /* 20-24px */
  --text-2xl: clamp(1.5rem, 5vw, 2rem);        /* 24-32px */
  --text-3xl: clamp(2rem, 6vw, 2.5rem);        /* 32-40px */
  
  /* Hauteurs de ligne */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### Système d'Espacement

#### Base Mathématique 8px
```css
:root {
  /* Unité de base */
  --space-unit: 8px;
  
  /* Échelle d'espacement */
  --space-xs: calc(var(--space-unit) * 0.5);   /* 4px */
  --space-sm: var(--space-unit);               /* 8px */
  --space-md: calc(var(--space-unit) * 2);     /* 16px */
  --space-lg: calc(var(--space-unit) * 3);     /* 24px */
  --space-xl: calc(var(--space-unit) * 4);     /* 32px */
  --space-2xl: calc(var(--space-unit) * 6);    /* 48px */
  --space-3xl: calc(var(--space-unit) * 8);    /* 64px */
}
```

#### Grille Responsive
```css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-md);
}

.grid {
  display: grid;
  gap: var(--space-md);
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

/* Breakpoints */
@media (max-width: 768px) {
  .container { padding: 0 var(--space-sm); }
  .grid { gap: var(--space-sm); }
}
```

---

## 🧩 Composants UI Réutilisables

### Boutons (4 Variants)

#### 1. **Bouton Primaire** (CTA principal)
```css
.cta-primary {
  background: linear-gradient(135deg, var(--sw-blue) 0%, var(--sw-purple) 100%);
  color: white;
  padding: var(--space-sm) var(--space-md);
  border-radius: 8px;
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(79, 158, 237, 0.3);
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(79, 158, 237, 0.4);
}

.cta-primary:active {
  transform: translateY(0);
}
```

#### 2. **Bouton Secondaire** (Actions secondaires)
```css
.cta-secondary {
  background: transparent;
  color: var(--sw-blue);
  border: 2px solid var(--sw-blue);
  padding: var(--space-sm) var(--space-md);
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.cta-secondary:hover {
  background: var(--sw-blue);
  color: white;
}
```

#### 3. **Bouton Outline** (Actions tertiaires)
```css
.btn-outline {
  background: transparent;
  color: var(--space-light);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: var(--space-xs) var(--space-sm);
  border-radius: 6px;
  font-size: var(--text-sm);
}
```

#### 4. **Bouton Texte** (Actions discrètes)
```css
.btn-text {
  background: none;
  border: none;
  color: var(--sw-blue);
  padding: var(--space-xs);
  text-decoration: underline;
  cursor: pointer;
}
```

### Cartes (Enhanced Cards)

#### Structure de Base
```css
.enhanced-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: var(--space-lg);
  transition: all 0.4s ease;
  position: relative;
  overflow: hidden;
}

.enhanced-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.6s ease;
}

.enhanced-card:hover::before {
  left: 100%;
}

.enhanced-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}
```

#### Cartes d'Exercices
```css
.exercise-card {
  position: relative;
  background: var(--gradient-space);
  border-radius: 12px;
  padding: var(--space-md);
  overflow: hidden;
}

.exercise-card .badge {
  position: absolute;
  top: var(--space-sm);
  right: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: 20px;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
}

.badge-addition { background: var(--badge-addition); }
.badge-fractions { background: var(--badge-fractions); }
.badge-geometrie { background: var(--badge-geometrie); }
```

### Modales

#### Structure Modale Unifiée
```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: var(--space-dark);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: var(--space-xl);
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.modal-close {
  background: none;
  border: none;
  color: var(--space-light);
  font-size: var(--text-xl);
  cursor: pointer;
  padding: var(--space-xs);
}
```

#### Animation d'Entrée/Sortie
```css
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-content {
  animation: modalFadeIn 0.3s ease-out;
}
```

### Formulaires

#### Champs de Saisie
```css
.form-field {
  margin-bottom: var(--space-md);
}

.form-label {
  display: block;
  color: var(--space-light);
  font-weight: 500;
  margin-bottom: var(--space-xs);
}

.form-input {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: var(--space-sm);
  color: var(--space-light);
  font-size: var(--text-base);
  transition: all 0.3s ease;
}

.form-input:focus {
  border-color: var(--sw-blue);
  box-shadow: 0 0 0 3px rgba(79, 158, 237, 0.2);
  outline: none;
}

.form-input.error {
  border-color: var(--error);
}

.form-error {
  color: var(--error);
  font-size: var(--text-sm);
  margin-top: var(--space-xs);
}
```

#### Validation Temps Réel
```javascript
function validateField(input) {
  const value = input.value.trim();
  const errorElement = input.nextElementSibling;
  
  if (input.type === 'email') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showError(input, 'Format d\'email invalide');
      return false;
    }
  }
  
  clearError(input);
  return true;
}

function showError(input, message) {
  input.classList.add('error');
  const errorElement = input.nextElementSibling;
  if (errorElement && errorElement.classList.contains('form-error')) {
    errorElement.textContent = message;
  }
}
```

---

## 🌌 Thème Star Wars Immersif

### Effets Visuels Spéciaux

#### Fond d'Étoiles Animées
```javascript
class StarField {
  constructor(container, starCount = 50) {
    this.container = container;
    this.starCount = starCount;
    this.stars = [];
    this.init();
  }
  
  init() {
    for (let i = 0; i < this.starCount; i++) {
      this.createStar();
    }
  }
  
  createStar() {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.cssText = `
      position: absolute;
      width: ${Math.random() * 3 + 1}px;
      height: ${Math.random() * 3 + 1}px;
      background: white;
      border-radius: 50%;
      top: ${Math.random() * 100}%;
      left: ${Math.random() * 100}%;
      animation: twinkle ${Math.random() * 3 + 2}s infinite;
    `;
    this.container.appendChild(star);
    this.stars.push(star);
  }
}

// CSS Animation
@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}
```

#### Planètes Flottantes
```css
.planet {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ffd700, #ff8c00);
  animation: float 6s ease-in-out infinite;
}

.planet-1 {
  width: 60px;
  height: 60px;
  top: 20%;
  right: 10%;
  animation-delay: 0s;
}

.planet-2 {
  width: 40px;
  height: 40px;
  top: 60%;
  left: 5%;
  background: radial-gradient(circle at 30% 30%, #4169e1, #1e90ff);
  animation-delay: 2s;
}

.planet-3 {
  width: 30px;
  height: 30px;
  top: 80%;
  right: 30%;
  background: radial-gradient(circle at 30% 30%, #32cd32, #228b22);
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-10px) rotate(90deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
  75% { transform: translateY(-10px) rotate(270deg); }
}
```

#### Particules Lumineuses
```javascript
class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.mouse = { x: 0, y: 0 };
    
    this.resize();
    this.createParticles();
    this.animate();
    
    window.addEventListener('resize', () => this.resize());
    canvas.addEventListener('mousemove', (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });
  }
  
  createParticles() {
    for (let i = 0; i < 30; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        radius: Math.random() * 2 + 1,
        alpha: Math.random() * 0.5 + 0.2
      });
    }
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    this.particles.forEach(particle => {
      particle.x += particle.vx;
      particle.y += particle.vy;
      
      // Rebond sur les bords
      if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
      if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
      
      // Dessiner particule
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
      this.ctx.fillStyle = `rgba(79, 158, 237, ${particle.alpha})`;
      this.ctx.fill();
    });
    
    requestAnimationFrame(() => this.animate());
  }
}
```

### Terminologie Star Wars

#### Labels d'Interface
```javascript
const starWarsLabels = {
  // Niveaux de difficulté
  difficulties: {
    'initie': '🌱 Youngling',
    'padawan': '⚔️ Padawan', 
    'chevalier': '🛡️ Chevalier Jedi',
    'maitre': '👑 Maître Jedi'
  },
  
  // Types d'exercices
  exerciseTypes: {
    'addition': 'Sommes Galactiques',
    'soustraction': 'Retraits Spatiaux',
    'multiplication': 'Produits Stellaires',
    'division': 'Partages Cosmiques',
    'fractions': 'Fragments d\'Étoiles',
    'geometrie': 'Formes Planétaires',
    'divers': 'Défis Variés'
  },
  
  // Messages d'encouragement
  feedback: {
    correct: [
      "Que la Force soit avec toi ! 🌟",
      "Un vrai Jedi des mathématiques ! ⚡",
      "Excellent travail, jeune Padawan ! 🏆",
      "Tu maîtrises cette technique ! 💫"
    ],
    incorrect: [
      "N'abandonne pas, jeune Padawan ! 💪",
      "Même les Maîtres Jedi apprennent ! 📚",
      "La persévérance mène à la maîtrise ! ⭐",
      "Réessaye, tu es sur la bonne voie ! 🎯"
    ]
  }
};
```

#### Breadcrumbs Thématiques
```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) 0;
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.7);
}

.breadcrumb-item {
  position: relative;
}

.breadcrumb-item:not(:last-child)::after {
  content: '▶';
  margin-left: var(--space-sm);
  color: var(--sw-gold);
  font-size: var(--text-xs);
}

.breadcrumb-item.active {
  color: var(--sw-gold);
  font-weight: 600;
}
```

---

## ♿ Accessibilité WCAG 2.1 AA

### Barre d'Outils d'Accessibilité

#### Structure HTML
```html
<div id="accessibility-toolbar" class="a11y-toolbar">
  <button class="a11y-btn" data-feature="contrast" title="Mode contraste élevé (Alt+C)">
    <i class="fas fa-adjust"></i>
    <span>Contraste</span>
  </button>
  <button class="a11y-btn" data-feature="text-size" title="Texte plus grand (Alt+T)">
    <i class="fas fa-text-height"></i>
    <span>Taille</span>
  </button>
  <button class="a11y-btn" data-feature="animations" title="Réduire animations (Alt+M)">
    <i class="fas fa-play-circle"></i>
    <span>Animations</span>
  </button>
  <button class="a11y-btn" data-feature="dyslexia" title="Mode dyslexie (Alt+D)">
    <i class="fas fa-brain"></i>
    <span>Dyslexie</span>
  </button>
</div>
```

#### Fonctionnalités JavaScript
```javascript
class AccessibilityManager {
  constructor() {
    this.features = {
      contrast: false,
      textSize: false,
      animations: false,
      dyslexia: false
    };
    
    this.init();
  }
  
  init() {
    // Charger préférences sauvegardées
    this.loadPreferences();
    
    // Raccourcis clavier
    this.setupKeyboardShortcuts();
    
    // Boutons toolbar
    this.setupToolbarButtons();
    
    // Respect des préférences système
    this.respectSystemPreferences();
  }
  
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.altKey) {
        switch (e.key.toLowerCase()) {
          case 'c': this.toggleContrast(); break;
          case 't': this.toggleTextSize(); break;
          case 'm': this.toggleAnimations(); break;
          case 'd': this.toggleDyslexia(); break;
        }
      }
    });
  }
  
  toggleContrast() {
    this.features.contrast = !this.features.contrast;
    document.body.classList.toggle('high-contrast', this.features.contrast);
    this.savePreferences();
    this.announceChange('Contraste élevé ' + (this.features.contrast ? 'activé' : 'désactivé'));
  }
  
  toggleTextSize() {
    this.features.textSize = !this.features.textSize;
    document.body.classList.toggle('large-text', this.features.textSize);
    this.savePreferences();
    this.announceChange('Texte agrandie ' + (this.features.textSize ? 'activé' : 'désactivé'));
  }
  
  toggleAnimations() {
    this.features.animations = !this.features.animations;
    document.body.classList.toggle('reduced-motion', !this.features.animations);
    this.savePreferences();
    this.announceChange('Animations ' + (this.features.animations ? 'activées' : 'réduites'));
  }
  
  toggleDyslexia() {
    this.features.dyslexia = !this.features.dyslexia;
    document.body.classList.toggle('dyslexia-font', this.features.dyslexia);
    this.savePreferences();
    this.announceChange('Mode dyslexie ' + (this.features.dyslexia ? 'activé' : 'désactivé'));
  }
  
  announceChange(message) {
    // Annonce pour lecteurs d'écran
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.textContent = message;
    document.body.appendChild(announcement);
    
    setTimeout(() => document.body.removeChild(announcement), 1000);
  }
}
```

#### Styles d'Accessibilité
```css
/* Mode contraste élevé */
.high-contrast {
  --space-black: #000000;
  --space-light: #ffffff;
  --sw-blue: #0066cc;
  --sw-green: #008800;
  --error: #cc0000;
}

.high-contrast .enhanced-card {
  background: #ffffff;
  color: #000000;
  border: 2px solid #000000;
}

/* Texte agrandi */
.large-text {
  font-size: 120%;
}

.large-text .text-sm {
  font-size: 1.1rem;
}

.large-text .text-base {
  font-size: 1.3rem;
}

/* Animations réduites */
@media (prefers-reduced-motion: reduce), .reduced-motion {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Police dyslexie */
.dyslexia-font {
  font-family: 'OpenDyslexic', sans-serif;
  letter-spacing: 0.1em;
  line-height: 1.6;
}
```

### Navigation Clavier

#### Skip Links
```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 8px;
  background: var(--sw-blue);
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 1001;
  transition: top 0.3s;
}

.skip-link:focus {
  top: 8px;
}
```

#### Focus Management
```css
:focus-visible {
  outline: 3px solid var(--sw-gold);
  outline-offset: 2px;
}

.modal-open {
  overflow: hidden;
}

/* Focus trap dans modales */
.modal-content:focus {
  outline: none;
}
```

#### ARIA Labels Complets
```html
<!-- Exemple exercice -->
<article class="exercise-card" 
         role="article"
         aria-labelledby="exercise-12-title"
         aria-describedby="exercise-12-desc">
  <h3 id="exercise-12-title">Fractions : Addition Niveau Padawan</h3>
  <p id="exercise-12-desc">Exercice d'addition de fractions avec dénominateurs différents</p>
  <button aria-label="Commencer l'exercice Fractions Addition Niveau Padawan">
    Commencer
  </button>
</article>

<!-- Status live region pour feedback -->
<div id="status" aria-live="polite" aria-atomic="true" class="sr-only"></div>
```

---

## 📱 Design Responsive et Mobile

### Breakpoints Standards
```css
:root {
  /* Breakpoints */
  --mobile: 480px;
  --tablet: 768px;
  --desktop: 1024px;
  --wide: 1200px;
}

/* Mobile first approach */
@media (min-width: 480px) { /* Tablet */ }
@media (min-width: 768px) { /* Desktop */ }
@media (min-width: 1024px) { /* Wide */ }
```

### Touch Targets (44px minimum)
```css
/* Boutons et liens tactiles */
.btn, button, a[role="button"] {
  min-height: 44px;
  min-width: 44px;
  padding: var(--space-sm);
}

/* Zones cliquables agrandies sur mobile */
@media (max-width: 768px) {
  .exercise-card {
    padding: var(--space-lg);
  }
  
  .modal-close {
    padding: var(--space-md);
    font-size: 1.5rem;
  }
}
```

### Navigation Mobile
```css
/* Menu hamburger */
.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--space-light);
  font-size: 1.5rem;
  padding: var(--space-sm);
}

@media (max-width: 768px) {
  .mobile-menu-toggle {
    display: block;
  }
  
  .main-nav {
    position: fixed;
    top: 0;
    left: -100%;
    width: 80%;
    height: 100vh;
    background: var(--space-dark);
    transition: left 0.3s ease;
    z-index: 999;
  }
  
  .main-nav.open {
    left: 0;
  }
}
```

### Grilles Adaptatives
```css
.exercise-grid {
  display: grid;
  gap: var(--space-md);
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

@media (max-width: 768px) {
  .exercise-grid {
    grid-template-columns: 1fr;
    gap: var(--space-sm);
  }
}

@media (min-width: 1200px) {
  .exercise-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

---

## 📸 Captures d'Écran et Wireframes

### Emplacements des Captures
```
docs/ui-ux/screenshots/
├── desktop/
│   ├── homepage-hero.png
│   ├── exercises-grid-view.png
│   ├── dashboard-stats.png
│   ├── challenges-spatial.png
│   └── profile-settings.png
├── mobile/
│   ├── homepage-mobile.png
│   ├── exercises-mobile.png
│   ├── navigation-mobile.png
│   └── accessibility-toolbar.png
└── wireframes/
    ├── user-flow-diagram.png
    ├── homepage-wireframe.png
    └── exercise-resolution-flow.png
```

### Guide Capture d'Écran
```javascript
// Script automatique pour captures
const captureScreenshots = async () => {
  const pages = [
    { url: '/', name: 'homepage' },
    { url: '/exercises', name: 'exercises' },
    { url: '/dashboard', name: 'dashboard' },
    { url: '/challenges', name: 'challenges' },
    { url: '/profile', name: 'profile' }
  ];
  
  for (const page of pages) {
    await capturePageScreenshot(page.url, page.name);
  }
};

async function capturePageScreenshot(url, name) {
  // Implementation avec Puppeteer
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Desktop
  await page.setViewport({ width: 1200, height: 800 });
  await page.goto(`http://localhost:8000${url}`);
  await page.screenshot({ 
    path: `docs/ui-ux/screenshots/desktop/${name}-desktop.png` 
  });
  
  // Mobile
  await page.setViewport({ width: 375, height: 667 });
  await page.screenshot({ 
    path: `docs/ui-ux/screenshots/mobile/${name}-mobile.png` 
  });
  
  await browser.close();
}
```

---

## 🔧 Performance et Optimisations

### Chargement CSS Optimisé
```html
<!-- Critical CSS inline -->
<style>
  /* CSS critique pour rendu initial */
  body { margin: 0; font-family: Roboto, sans-serif; }
  .hero-section { min-height: 100vh; }
</style>

<!-- CSS non-critique en différé -->
<link rel="preload" href="/static/styles/critical.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<link rel="stylesheet" href="/static/styles/enhanced.css" media="print" onload="this.media='all'">
```

### Lazy Loading Images
```javascript
// Intersection Observer pour lazy loading
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      imageObserver.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  imageObserver.observe(img);
});
```

### Service Worker Cache
```javascript
// Cache pour performance offline
const CACHE_NAME = 'mathakine-v1';
const urlsToCache = [
  '/',
  '/static/styles/critical.css',
  '/static/js/main.js',
  '/static/fonts/roboto.woff2'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
```

---

## 🎯 Métriques UX et Tests

### Core Web Vitals Cibles
- **LCP (Largest Contentful Paint)** : < 2.5s
- **FID (First Input Delay)** : < 100ms  
- **CLS (Cumulative Layout Shift)** : < 0.1

### Tests d'Accessibilité
```javascript
// Tests automatisés avec axe-core
const runAccessibilityTests = async () => {
  const results = await axe.run();
  
  if (results.violations.length > 0) {
    console.error('Violations d\'accessibilité:', results.violations);
  } else {
    console.log('✅ Tous les tests d\'accessibilité passent');
  }
  
  return results;
};

// Tests manuels recommandés
const manualTests = [
  'Navigation complète au clavier uniquement',
  'Test avec lecteur d\'écran (NVDA/JAWS)',
  'Validation contraste couleurs (ratio 4.5:1)',
  'Test responsive sur appareils réels',
  'Validation formulaires sans JavaScript'
];
```

### Métriques de Conversion
```javascript
// Tracking événements UX
const trackUXEvent = (category, action, value) => {
  // Google Analytics ou autre
  gtag('event', action, {
    event_category: category,
    event_label: window.location.pathname,
    value: value
  });
};

// Exemples d'événements
trackUXEvent('Engagement', 'exercise_started', exerciseId);
trackUXEvent('Accessibility', 'feature_used', 'high_contrast');
trackUXEvent('Performance', 'page_load_time', loadTime);
```

---

**Interface conçue pour l'apprentissage inclusif et l'engagement maximum** 🎨✨

*Guide UI/UX complet - Version 3.0 - Documentation vivante mise à jour en continu* 