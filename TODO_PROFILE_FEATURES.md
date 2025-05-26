# 📋 TODO - Fonctionnalités Page Profil Mathakine

## 🎯 Vue d'ensemble
La page de profil a été créée avec l'interface complète mais plusieurs fonctionnalités backend doivent encore être implémentées pour la rendre pleinement fonctionnelle.

## ✅ Déjà Implémenté
- Interface utilisateur complète et moderne
- Design cohérent avec le thème Star Wars
- Structure responsive
- Formulaires avec validation côté client
- Intégration du système de notifications
- Chargement des statistiques de base

## 🚀 Fonctionnalités à Implémenter

### 1. **Gestion de l'Avatar** 🖼️
- **Endpoint** : `POST /api/users/me/avatar`
- **Fonctionnalités** :
  - Upload d'image (formats : JPG, PNG, GIF)
  - Redimensionnement automatique (200x200px)
  - Stockage sécurisé (local ou cloud)
  - Limite de taille (5MB max)
  - Avatar par défaut selon le rôle (Padawan, Chevalier, etc.)
- **Tables DB** : Ajouter champ `avatar_url` dans la table `users`

### 2. **Mise à jour du Profil** 📝
- **Endpoint** : `PUT /api/users/me` (partiellement existant)
- **Champs manquants** :
  - `learning_style` (enum : visual, auditory, kinesthetic, mixed)
  - `preferred_difficulty` (enum : initie, padawan, chevalier, maitre)
  - `preferred_theme` (enum : space, nature, ocean, fantasy)
- **Validation** :
  - Email unique
  - Format email valide
  - Nom complet : max 100 caractères

### 3. **Changement de Mot de Passe** 🔐
- **Endpoint** : `POST /api/users/me/change-password`
- **Payload** :
  ```json
  {
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Règles de sécurité** :
  - Minimum 8 caractères
  - Au moins 1 majuscule
  - Au moins 1 chiffre
  - Au moins 1 caractère spécial
  - Différent des 3 derniers mots de passe
- **Fonctionnalités** :
  - Vérification du mot de passe actuel
  - Hashage bcrypt du nouveau mot de passe
  - Email de confirmation
  - Déconnexion des autres sessions

### 4. **Export des Données Utilisateur** 📥
- **Endpoint** : `GET /api/users/me/export`
- **Format** : ZIP contenant :
  - `profile.json` : Informations personnelles
  - `progress.json` : Statistiques et progression
  - `attempts.csv` : Historique des tentatives
  - `achievements.json` : Badges et accomplissements
- **Conformité RGPD** : Droit à la portabilité des données

### 5. **Suppression de Compte** ⚠️
- **Endpoint** : `DELETE /api/users/me`
- **Processus** :
  1. Vérification du mot de passe
  2. Email de confirmation avec lien temporaire
  3. Période de grâce de 30 jours
  4. Anonymisation des données (pas de suppression physique)
- **Options** :
  - Suppression immédiate
  - Désactivation temporaire
  - Anonymisation complète

### 6. **Statistiques Avancées** 📊
- **Endpoints à créer** :
  - `GET /api/users/me/stats/detailed` : Stats complètes
  - `GET /api/users/me/activity` : Historique d'activité
  - `GET /api/users/me/badges` : Badges obtenus
- **Métriques** :
  - Jours d'activité consécutifs
  - Badges obtenus et progression
  - Temps moyen par exercice
  - Points de maîtrise par catégorie

### 7. **Préférences d'Accessibilité** ♿
- **Champs à ajouter** :
  - Police dyslexique
  - Taille de texte
  - Contraste élevé
  - Réduction des animations
- **Stockage** : JSON dans `accessibility_settings`

### 8. **Notifications et Alertes** 🔔
- **Préférences** :
  - Notifications email (quotidien, hebdomadaire, désactivé)
  - Rappels d'entraînement
  - Nouvelles fonctionnalités
  - Achievements débloqués

### 9. **Sessions et Sécurité** 🛡️
- **Fonctionnalités** :
  - Liste des sessions actives
  - Déconnexion à distance
  - Authentification 2FA (optionnelle)
  - Historique de connexion

### 10. **Intégration Sociale** 👥
- **Future feature** :
  - Partage de profil public
  - Comparaison avec amis
  - Défis entre utilisateurs
  - Tableau des leaders

## 📊 Priorités d'Implémentation

### Phase 1 (Critique)
1. ✅ Interface de base (FAIT)
2. Mise à jour profil complet
3. Changement de mot de passe
4. Avatar upload

### Phase 2 (Important)
5. Export de données
6. Statistiques détaillées
7. Préférences d'accessibilité

### Phase 3 (Nice to have)
8. Suppression de compte
9. Gestion des sessions
10. Notifications avancées

## 🛠️ Stack Technique Recommandée

### Backend
- **FastAPI** : Endpoints REST
- **SQLAlchemy** : ORM et migrations
- **Pillow** : Traitement d'images
- **python-multipart** : Upload de fichiers
- **celery** : Tâches asynchrones (export, emails)

### Stockage
- **Local** : Dossier `uploads/avatars/`
- **Cloud** : AWS S3 ou Cloudinary (futur)
- **Cache** : Redis pour les stats

### Sécurité
- **bcrypt** : Hashage mots de passe
- **JWT** : Tokens d'authentification
- **rate-limiting** : Protection API
- **CORS** : Configuration stricte

## 📝 Notes d'Implémentation

### Modèle User à Étendre
```python
class User(Base):
    # Champs existants...
    
    # Nouveaux champs
    avatar_url = Column(String(255), nullable=True)
    learning_style = Column(Enum(LearningStyle), nullable=True)
    preferred_difficulty = Column(Enum(Difficulty), nullable=True)
    preferred_theme = Column(Enum(Theme), default='space')
    accessibility_settings = Column(JSON, default={})
    notification_preferences = Column(JSON, default={})
    last_password_change = Column(DateTime, nullable=True)
    deletion_requested_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
```

### Endpoints Prioritaires
```python
# 1. Upload avatar
@router.post("/users/me/avatar")
async def upload_avatar(file: UploadFile = File(...)):
    # Validation et traitement
    pass

# 2. Changer mot de passe
@router.post("/users/me/change-password")
async def change_password(data: PasswordChangeRequest):
    # Vérification et mise à jour
    pass

# 3. Export données
@router.get("/users/me/export")
async def export_user_data():
    # Génération ZIP async
    pass
```

## 🎯 Objectif Final
Créer une expérience utilisateur complète et sécurisée permettant aux utilisateurs de :
- Personnaliser entièrement leur profil
- Gérer leur sécurité et confidentialité
- Suivre leur progression en détail
- Adapter l'application à leurs besoins

## 📅 Timeline Estimée
- **Phase 1** : 2-3 semaines
- **Phase 2** : 3-4 semaines
- **Phase 3** : 4-6 semaines

**Total** : 2-3 mois pour l'implémentation complète 