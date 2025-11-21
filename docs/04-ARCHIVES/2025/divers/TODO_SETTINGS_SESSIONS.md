# TODO - Gestion des Sessions Actives

**Statut** : ⏳ En attente (non critique pour MVP)  
**Priorité** : Moyenne  
**Complexité** : Élevée

## 📋 Description

Implémenter la gestion complète des sessions actives pour permettre aux utilisateurs de :
- Voir toutes leurs sessions actives sur différents appareils
- Révoquer des sessions individuelles
- Révoquer toutes les autres sessions

## 🔧 Fonctionnalités Requises

### Backend

1. **Créer/modifier le modèle UserSession**
   - Vérifier si le modèle existe déjà (`app/models/user_session.py`)
   - S'assurer que les champs nécessaires sont présents :
     - `device_info` (JSON) : navigateur, OS, appareil
     - `ip_address` : Adresse IP
     - `location_data` (JSON) : ville, pays (optionnel via géolocalisation IP)
     - `last_activity` : Dernière activité
     - `is_active` : Session active ou non
     - `expires_at` : Date d'expiration

2. **Créer les endpoints API**
   - `GET /api/users/me/sessions` : Liste toutes les sessions actives de l'utilisateur
   - `DELETE /api/users/me/sessions/{session_id}` : Révoquer une session spécifique
   - `DELETE /api/users/me/sessions` : Révoquer toutes les autres sessions (sauf la session actuelle)

3. **Intégrer la création de sessions**
   - Modifier le processus de login pour créer une session dans `user_sessions`
   - Stocker les informations de l'appareil (user-agent, IP)
   - Optionnel : Géolocalisation IP pour `location_data`

4. **Gérer l'expiration des sessions**
   - Nettoyer automatiquement les sessions expirées
   - Mettre à jour `last_activity` à chaque requête authentifiée

### Frontend

1. **Mettre à jour `useSettings.ts`**
   - Implémenter `getSessions()` pour appeler l'endpoint
   - Implémenter `revokeSession()` pour révoquer une session
   - Ajouter `revokeAllSessions()` pour révoquer toutes les autres sessions

2. **Améliorer l'UI des sessions**
   - Afficher les informations de l'appareil de manière lisible
   - Indiquer la session actuelle
   - Ajouter un bouton "Révoquer toutes les autres sessions"

## 📝 Notes Techniques

- Le modèle `UserSession` existe déjà dans `app/models/user_session.py`
- La table `user_sessions` doit être créée via migration Alembic si elle n'existe pas
- Pour la géolocalisation IP, on peut utiliser un service externe (ex: ipapi.co) ou simplement stocker l'IP
- Les sessions doivent être liées aux tokens JWT pour pouvoir les révoquer

## 🎯 Estimation

- **Temps estimé** : 4-6 heures
- **Difficulté** : Moyenne-Élevée
- **Dépendances** : Modèle UserSession, système de tokens JWT

## ✅ Prérequis

- [ ] Migration Alembic pour table `user_sessions` (si nécessaire)
- [ ] Modèle `UserSession` vérifié et fonctionnel
- [ ] Système de création de sessions au login
- [ ] Tests unitaires pour les endpoints

