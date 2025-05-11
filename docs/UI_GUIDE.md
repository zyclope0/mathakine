# Guide de l'Interface Graphique de Mathakine

Ce guide détaille l'interface graphique de Mathakine, son architecture, et comment la personnaliser.

## Vue d'ensemble

L'application Mathakine dispose désormais d'une interface graphique moderne avec un thème spatial inspiré de l'univers Star Wars. Cette interface est construite avec :

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
- Visualiser les exercices disponibles sous forme de cartes
- Générer de nouveaux exercices
- Commencer un exercice ou voir ses détails via un modal
- Supprimer un exercice avec confirmation

#### Fonctionnalités d'interface avancées
- **Modal de détails** : Un clic sur le bouton "Détails" ouvre une fenêtre modale présentant les informations de l'exercice sans afficher la réponse correcte
- **Chargement asynchrone** : Les informations du modal sont chargées à la demande via l'API
- **Suppression avec confirmation** : Un clic sur l'icône de suppression ouvre un modal de confirmation

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

---

*Dernière mise à jour : Mai 2025* 