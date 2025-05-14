# Guide de l'Interface Graphique de Mathakine

Ce guide détaille l'interface graphique de Mathakine, son architecture, et comment la personnaliser.

## Vue d'ensemble

L'application Mathakine dispose d'une interface graphique moderne avec un thème spatial inspiré de l'univers Star Wars. Cette interface est construite avec :

- Starlette pour le backend (enhanced_server.py)
- Jinja2 pour les templates HTML
- CSS moderne avec variables et animations
- JavaScript pour les interactions côté client

## Architecture des fichiers

### Structure des dossiers

```
mathakine/
├── app/                       # Code de l'application standard FastAPI (API sans UI)
│   └── main.py                # Point d'entrée de l'API standard
├── enhanced_server.py         # Serveur amélioré avec interface graphique
├── static/                    # Fichiers statiques
│   ├── style.css              # Styles de base
│   ├── space-theme.css        # Thème spatial
│   ├── home-styles.css        # Styles spécifiques à la page d'accueil
│   └── img/                   # Images
│       ├── mathakine-logo.svg # Logo de l'application
│       └── favicon.svg        # Favicon
├── templates/                 # Templates HTML
│   ├── base.html              # Template de base avec structure commune
│   ├── home.html              # Page d'accueil
│   ├── exercises.html         # Page des exercices
│   ├── exercise_detail.html   # Page de détail d'un exercice
│   └── dashboard.html         # Tableau de bord
├── mathakine_cli.py           # Interface en ligne de commande pour lancer l'application
└── check_ui_setup.py          # Utilitaire pour vérifier la configuration de l'interface
```

## Pages principales

### 1. Page d'accueil (home.html)

La page d'accueil présente l'application avec :
- Une bannière (hero section) compacte et horizontale avec trois composants clés:
  - **Contenu textuel**: Message d'accueil et explication concise
  - **Statistiques**: Affichage des métriques principales (nombre d'exercices, niveaux, possibilités)
  - **Illustration spatiale**: Représentation visuelle de l'univers Star Wars avec animation
- Un unique bouton d'appel à l'action (CTA) principal qui réduit les redondances avec la barre de navigation
- Des cartes de fonctionnalités expliquant les capacités de l'application
- Une section sur la progression avec les différents niveaux disponibles

#### Structure de la Hero Section
```html
<div class="hero-section">
    <div class="stars-container">
        <!-- Étoiles générées par JavaScript -->
    </div>
    
    <div class="card hero-card">
        <div class="hero-flex">
            <div class="hero-content">
                <h2>Bienvenue dans la galaxie Mathakine</h2>
                <p class="hero-subtitle">Embarquez pour un voyage stellaire...</p>
                
                <div class="hero-stats">
                    <div class="stat-item">
                        <div class="stat-number"><i class="fas fa-calculator"></i> 150+</div>
                        <div class="stat-label">Exercices</div>
                    </div>
                    <!-- Autres statistiques -->
                </div>
                
                <a href="/api/exercises/generate?ai=true" class="btn big-btn primary-btn">
                    <i class="fas fa-jedi"></i> Commencer l'aventure
                </a>
            </div>
            <div class="hero-image">
                <div class="space-object"></div>
            </div>
        </div>
    </div>
</div>
```

#### Design responsive
La hero section utilise un layout flexible qui s'adapte aux différentes tailles d'écran:
- Sur desktop: Affichage horizontal avec contenu à gauche et image à droite
- Sur mobile: Bascule vers un affichage vertical avec image en haut et contenu en dessous
- Optimisation de l'espace tout en conservant l'expérience immersive Star Wars

#### Bonnes pratiques implémentées
- **Réduction des redondances UI**: Suppression des boutons duplicatifs avec la navigation
- **Hiérarchie visuelle claire**: Un seul CTA principal qui guide l'utilisateur
- **Métrique de conversion**: Mise en avant des statistiques pour engager l'utilisateur
- **Équilibre texte/visuel**: Combinaison efficace d'informations textuelles et d'éléments visuels
- **Animations subtiles**: Effet de pulsation et rotation sur l'objet spatial pour attirer l'attention sans distraire

### 2. Page des exercices (exercises.html)

La page des exercices permet aux utilisateurs de :
- Filtrer les exercices par type et difficulté
- Visualiser les exercices disponibles sous forme de cartes (vues grille ou liste)
- Générer de nouveaux exercices (standard ou avec IA)
- Naviguer entre les pages d'exercices avec la pagination
- Commencer un exercice ou voir ses détails via un modal
- Supprimer un exercice avec confirmation

#### Fonctionnalités d'interface avancées
- **Système de pagination amélioré** : Navigation intuitive entre les pages avec numéros de page, boutons précédent/suivant et ellipses pour les grandes plages
- **Double vue** : Basculement entre vue en grille (par défaut) et vue en liste avec persistance du choix via localStorage
- **Modals interactifs** : 
  - Modal de détails avec chargement asynchrone des informations de l'exercice
  - Modal de confirmation pour la suppression sécurisée
- **Animations optimisées** : Apparition séquentielle des cartes d'exercices avec délais progressifs
- **Cache et performance** :
  - Mécanisme de "force redraw" pour éviter les problèmes de cache lors du changement de vue
  - Prévention du défilement automatique indésirable lors du basculement entre vues grille/liste

#### Badges et indicateurs
- **Badges de type d'exercice** : Identification visuelle rapide par code couleur (Addition en vert, Soustraction en orange, etc.)
- **Badges de difficulté** : Indication claire du niveau (Initié, Padawan, Chevalier, Maître) par couleur
- **Badge IA** : Identification des exercices générés par IA avec une icône de robot

#### Code JavaScript clé
Le JavaScript de la page implémente des fonctionnalités importantes :
```javascript
// Pagination avec prévention du défilement automatique indésirable
function goToPage(page, skipScroll = false) {
    // ... logique de pagination ...
    
    // Scroll en haut de la liste uniquement si skipScroll est false
    if (!skipScroll) {
        setTimeout(() => {
            const exerciseList = document.querySelector('.exercise-list');
            if (exerciseList) {
                exerciseList.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    }
}

// Bascule entre vue grille et vue liste avec persistance
function applyViewMode(mode) {
    if (mode === 'list') {
        exerciseList.classList.add('list-view');
        // ... configuration vue liste ...
    } else {
        exerciseList.classList.remove('list-view');
        // ... configuration vue grille ...
    }
    
    // Force redraw pour éviter les problèmes de cache
    exerciseList.style.display = 'none';
    setTimeout(() => {
        exerciseList.style.display = mode === 'list' ? 'flex' : 'grid';
    }, 10);
}
```

### 3. Page de détail d'exercice (exercise_detail.html)

La page de détail d'un exercice permet à l'utilisateur de :
- Voir l'énoncé de l'exercice et sa difficulté
- Choisir parmi les réponses proposées
- Recevoir un feedback immédiat sur sa réponse
- Consulter l'explication de l'exercice

### 4. Tableau de bord (dashboard.html)

Le tableau de bord affiche :
- Les statistiques de l'utilisateur (exercices résolus, taux de réussite, points d'expérience)
- Des graphiques de progression
- Le niveau actuel et la progression vers le niveau suivant
- L'activité récente

## Lancement de l'application avec interface graphique

### Méthode 1 : Utilisation de mathakine_cli.py (recommandé)

```bash
python mathakine_cli.py run
```

L'interface graphique est maintenant lancée par défaut. Si vous souhaitez uniquement l'API sans interface, utilisez :

```bash
python mathakine_cli.py run --api-only
```

### Méthode 2 : Lancement direct du serveur amélioré

```bash
python enhanced_server.py
```

## Personnalisation

### Structure CSS normalisée

L'interface de Mathakine utilise une structure CSS normalisée pour améliorer la maintenabilité et la cohérence du code :

#### 1. Organisation des fichiers CSS

Les fichiers CSS sont organisés comme suit :

- **normalize.css** - Réinitialisation CSS standardisée qui normalise le rendu entre navigateurs
- **variables.css** - Variables CSS globales (couleurs, espacements, typographie, etc.)
- **utils.css** - Classes utilitaires réutilisables (marges, paddings, alignements, etc.)
- **style.css** - Styles principaux de l'application (importe normalize.css, variables.css et utils.css)
- **space-theme.css** - Styles spécifiques au thème Star Wars
- **home-styles.css** - Styles spécifiques à la page d'accueil

#### 2. Bonnes pratiques

- Utiliser les variables CSS définies dans `variables.css` plutôt que des valeurs codées en dur
- Privilégier les classes utilitaires de `utils.css` plutôt que des styles en ligne
- Suivre l'ordre d'importation des fichiers CSS : normalize → variables → utils → style → theme
- Éviter d'ajouter des styles en ligne directement dans le HTML
- Utiliser les classes utilitaires pour les mises en page communes

#### 3. Classes utilitaires

Un système de classes utilitaires est disponible pour les besoins courants :

```html
<!-- Alignement de texte -->
<div class="text-center">Texte centré</div>
<div class="text-left">Texte aligné à gauche</div>

<!-- Marges -->
<div class="mt-3">Marge supérieure moyenne</div>
<div class="mb-4">Marge inférieure grande</div>

<!-- Display et Flexbox -->
<div class="d-flex justify-between">Conteneur flex avec espace entre</div>
<div class="d-none">Élément masqué</div>

<!-- Padding -->
<div class="p-3">Padding moyen sur tous les côtés</div>
```

#### 4. Script de normalisation

Un script utilitaire est disponible pour normaliser les styles en ligne existants :

```bash
python scripts/normalize_css.py
```

Ce script analyse les fichiers HTML dans le dossier templates et remplace les styles en ligne par des classes utilitaires appropriées.

### Styles CSS

L'interface utilise un système de variables CSS pour faciliter la personnalisation :

```css
:root {
  --sw-accent: #7765e3;     /* Couleur principale */
  --sw-blue: #3db4f2;       /* Couleur secondaire */
  --sw-gold: #ffd700;       /* Couleur d'accentuation */
  /* ... autres variables ... */
}
```

Pour modifier le thème, vous pouvez simplement ajuster ces variables dans `static/space-theme.css`.

### Templates HTML

Tous les templates héritent de `base.html` qui fournit :
- La structure HTML commune
- Le menu de navigation
- Les méta-données et liens CSS
- Les scripts JavaScript communs

Pour ajouter une nouvelle page, créez un nouveau template qui étend `base.html` :

```html
{% extends "base.html" %}

{% block title %}Titre de la page{% endblock %}

{% block content %}
  <!-- Contenu de la page -->
{% endblock %}

{% block scripts %}
  <!-- Scripts spécifiques à la page -->
{% endblock %}
```

### Composants réutilisables

Les composants réutilisables peuvent être définis dans des fichiers partiels et inclus dans les templates avec `{% include %}`.

### Modales et Interactions

L'interface utilise des fenêtres modales pour plusieurs fonctionnalités :
- Affichage des détails d'un exercice sans naviguer vers une nouvelle page
- Confirmation de suppression d'un exercice
- Affichage des messages d'erreur ou de succès

Exemple d'implémentation d'une modale :
```html
<!-- Structure HTML de la modale -->
<div id="detail-modal" class="modal">
  <div class="modal-content">
    <span class="close">&times;</span>
    <div id="modal-content">
      <!-- Contenu chargé dynamiquement -->
    </div>
  </div>
</div>

<!-- JavaScript pour gérer la modale -->
<script>
  // Ouvrir la modale
  document.querySelector('.show-details').addEventListener('click', function() {
    document.getElementById('detail-modal').style.display = 'block';
    // Charger le contenu via AJAX
    fetch('/api/exercises/123')
      .then(response => response.json())
      .then(data => {
        document.getElementById('modal-content').innerHTML = renderExerciseDetails(data);
      });
  });
  
  // Fermer la modale
  document.querySelector('.close').addEventListener('click', function() {
    document.getElementById('detail-modal').style.display = 'none';
  });
</script>
```

### Animations

L'interface utilise des animations CSS pour les transitions et les effets visuels. Pour les performances, les animations respectent la préférence `prefers-reduced-motion` :

```css
@media (prefers-reduced-motion: reduce) {
    .animation {
        animation: none;
    }
}
```

## Intégration avec l'API

L'interface communique avec l'API via des requêtes fetch JavaScript :

```javascript
fetch('/api/exercises')
    .then(response => response.json())
    .then(data => {
        // Traitement des données
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
```

## Routes principales dans l'interface

| URL | Description |
|-----|-------------|
| `/` | Page d'accueil |
| `/exercises` | Liste des exercices disponibles |
| `/exercise/{id}` | Détail d'un exercice spécifique |
| `/dashboard` | Tableau de bord de l'utilisateur |
| `/debug` | Page de débogage (uniquement en mode développement) |
| `/api/exercises` | API pour récupérer la liste des exercices |
| `/api/exercises/{id}` | API pour récupérer les détails d'un exercice spécifique |
| `/api/exercises/generate` | API pour générer un nouvel exercice |
| `/api/submit-answer` | API pour soumettre une réponse (POST) |

## Bonnes pratiques

1. **Performance** :
   - Minimisez les requêtes HTTP en regroupant les ressources
   - Utilisez `preload` pour les ressources critiques
   - Chargez les polices et icônes avec `media="print" onload="this.media='all'"`
   - Utilisez des modales pour afficher des informations sans recharger la page

2. **Accessibilité** :
   - Utilisez des attributs alt pour les images
   - Assurez un bon contraste de couleurs
   - Permettez la navigation au clavier
   - Assurez-vous que les modales sont utilisables au clavier (focus trap)

3. **Responsive design** :
   - Utilisez des media queries pour adapter l'interface à différentes tailles d'écran
   - Implémentez une approche "mobile-first"
   - Assurez-vous que les modales s'affichent correctement sur mobile

## Accessibilité

### Barre d'outils d'accessibilité

Une barre d'outils d'accessibilité flottante est disponible sur toutes les pages de l'application. Elle propose les fonctionnalités suivantes :

- **Mode contraste élevé** (Alt+C) : Augmente le contraste des couleurs pour améliorer la lisibilité
- **Texte plus grand** (Alt+T) : Augmente la taille du texte de 20%
- **Réduction des animations** (Alt+M) : Désactive les animations qui pourraient poser problème aux utilisateurs photosensibles
- **Mode dyslexie** (Alt+D) : Utilise une police adaptée aux personnes dyslexiques et améliore l'espacement des lettres

Les préférences d'accessibilité sont enregistrées dans le stockage local du navigateur et automatiquement restaurées lors des visites ultérieures.

### Accessibilité de l'interface holographique

L'interface holographique Star Wars a été conçue pour être entièrement conforme aux normes WCAG 2.1 AA :

- Les effets visuels sont désactivés automatiquement lorsque `prefers-reduced-motion` est activé
- En mode contraste élevé, les effets holographiques sont simplifiés pour maximiser la lisibilité
- Tous les éléments interactifs sont accessibles au clavier avec un focus visible
- Des attributs ARIA sont utilisés pour informer les lecteurs d'écran du rôle et de l'état des composants
- Des messages audio peuvent être désactivés selon les préférences utilisateur

### Compatibilité avec les technologies d'assistance

- **Lecteurs d'écran** : Structure sémantique avec landmarks, headings et attributs ARIA appropriés
- **Navigation au clavier** : Ordre de tabulation logique et focus visible pour tous les éléments interactifs
- **Préférences système** : Respect des préférences système via les media queries (`prefers-contrast`, `prefers-reduced-motion`)
- **Zoom** : Interface entièrement fonctionnelle jusqu'à 400% de zoom sans perte de contenu ou de fonctionnalité

## Lien avec d'autres documents

Pour plus d'informations sur l'architecture technique et l'API sous-jacente, consultez :
- [Core/ARCHITECTURE.md](ARCHITECTURE.md) pour la structure technique globale
- [Core/DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) pour les détails sur l'API et les services
- [Tech/TRANSACTION_SYSTEM.md](../Tech/TRANSACTION_SYSTEM.md) pour la gestion des données
- [Core/PROJECT_STATUS.md](PROJECT_STATUS.md) pour l'état actuel du projet et les améliorations planifiées

---

*Dernière mise à jour : 12 juin 2025* 