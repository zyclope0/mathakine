# Diagrammes d'Architecture - Mathakine

Ce document présente l'architecture de Mathakine à travers différents diagrammes.

## Architecture Globale

```mermaid
graph TB
    Client[Client Web/Mobile]
    API[API FastAPI]
    Auth[Service Auth]
    DB[(Base de données)]
    Cache[(Cache Redis)]
    Queue[File de tâches]
    
    Client --> API
    API --> Auth
    API --> DB
    API --> Cache
    API --> Queue
    Queue --> DB
```

## Structure des Services

```mermaid
graph LR
    A[API Gateway] --> B[Service Exercices]
    A --> C[Service Utilisateurs]
    A --> D[Service Progression]
    A --> E[Service Analytics]
    
    B --> DB[(PostgreSQL)]
    C --> DB
    D --> DB
    E --> Cache[(Redis)]
```

## Flux d'Authentification

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant A as API
    participant Auth as Service Auth
    participant DB as Base de données
    
    U->>A: Connexion
    A->>Auth: Vérification
    Auth->>DB: Validation
    DB-->>Auth: Données utilisateur
    Auth-->>A: Token JWT
    A-->>U: Session active
```

## Modèle de Données

```mermaid
erDiagram
    UTILISATEUR ||--o{ PROGRESSION : réalise
    UTILISATEUR {
        int id
        string email
        string nom
        string role
    }
    EXERCICE ||--o{ PROGRESSION : contient
    EXERCICE {
        int id
        string type
        int niveau
        json contenu
    }
    PROGRESSION {
        int id
        int score
        datetime date
        int temps
    }
```

## Pipeline de Déploiement

```mermaid
graph LR
    A[Code] -->|Push| B[Tests]
    B -->|Success| C[Build]
    C -->|Docker| D[Staging]
    D -->|Validation| E[Production]
```

## Architecture des Tests

```mermaid
graph TB
    A[Tests Unitaires] --> D[Coverage Report]
    B[Tests d'Intégration] --> D
    C[Tests E2E] --> D
    D --> E[Quality Gate]
```

## Monitoring et Métriques

```mermaid
graph LR
    A[Application] -->|Métriques| B[Prometheus]
    B -->|Visualisation| C[Grafana]
    A -->|Logs| D[ELK Stack]
```

## Notes sur les Diagrammes

- Les diagrammes sont générés avec Mermaid
- Ils sont automatiquement mis à jour avec le code
- La documentation est versionnée avec le code

## Légende

- 🟦 Services principaux
- 🟨 Services auxiliaires
- 🟩 Bases de données
- 🟥 Points critiques
- ⚡ Flux de données

## Maintenance

Ces diagrammes sont maintenus par l'équipe d'architecture. Pour proposer des modifications :

1. Créer une issue avec le label `documentation`
2. Joindre le diagramme modifié
3. Expliquer les changements proposés

## Versions

- v1.0 : Architecture initiale
- v1.1 : Ajout du cache Redis
- v1.2 : Mise à jour du pipeline CI/CD
- v1.3 : Ajout du monitoring

# Diagrammes et visuels d'architecture

## Vue d'ensemble du système

```mermaid
graph TD
    A[Interface Web Starlette] --> B[enhanced_server.py]
    C[API REST FastAPI] --> D[app/main.py]
    B --> E[Services métier]
    D --> E
    E --> F[Base de données]
    G[Interface CLI] --> E
```

## Flux de données

```mermaid
sequenceDiagram
    participant U as Utilisateur
    participant W as Web UI
    participant A as API
    participant S as Services
    participant DB as Base de données

    U->>W: Résout exercice
    W->>A: POST /api/exercises/{id}/submit
    A->>S: ExerciseService.submit_answer()
    S->>DB: Enregistre résultat
    DB-->>S: Confirme
    S-->>A: Retourne résultat
    A-->>W: Affiche feedback
```

## Architecture des composants

```mermaid
graph LR
    A[Templates] --> B[enhanced_server.py]
    C[Static Files] --> B
    B --> D[Services]
    E[API Endpoints] --> D
    D --> F[Models]
    F --> G[Database]
```

## Structure de la base de données

```mermaid
erDiagram
    USERS ||--o{ EXERCISES : creates
    USERS ||--o{ ATTEMPTS : makes
    EXERCISES ||--o{ ATTEMPTS : has
    USERS ||--o{ PROGRESS : tracks
    EXERCISES ||--o{ STATISTICS : generates
```

## Captures d'écran de l'interface

### Interface principale
![Interface principale](../assets/images/main_interface.png)
*L'interface principale avec le thème Star Wars*

### Tableau de bord
![Tableau de bord](../assets/images/dashboard.png)
*Le tableau de bord avec les statistiques*

### Exercice type
![Exercice type](../assets/images/exercise.png)
*Un exercice avec le design holographique*

## Flux d'utilisation typiques

### 1. Création d'un exercice
```mermaid
graph LR
    A[Accès interface] --> B[Nouveau exercice]
    B --> C[Remplir formulaire]
    C --> D[Validation]
    D --> E[Enregistrement]
    E --> F[Publication]
```

### 2. Résolution d'exercice
```mermaid
graph LR
    A[Sélection exercice] --> B[Affichage]
    B --> C[Résolution]
    C --> D[Soumission]
    D --> E[Feedback]
    E --> F[Statistiques]
```

### 3. Suivi de progression
```mermaid
graph LR
    A[Tableau de bord] --> B[Vue statistiques]
    B --> C[Analyse progrès]
    C --> D[Recommandations]
```

## Notes d'implémentation

1. **Interface utilisateur**
   - Composants Starlette pour le rendu
   - Templates Jinja2 pour les vues
   - CSS modulaire pour le thème

2. **API REST**
   - FastAPI pour les endpoints
   - Pydantic pour la validation
   - OpenAPI pour la documentation

3. **Base de données**
   - SQLAlchemy pour l'ORM
   - Alembic pour les migrations
   - PostgreSQL/SQLite pour le stockage

---

*Dernière mise à jour : 15 juin 2025* 