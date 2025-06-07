# 📚 Documentation Mathakine

Bienvenue dans la documentation de **Mathakine**, plateforme éducative mathématique pour enfants autistes avec thème Star Wars immersif.

## 🎯 **Vue d'Ensemble du Projet**

**Mathakine** = Plateforme éducative mathématique pour enfants autistes avec interface Star Wars
- **Mission** : Apprentissage adaptatif pour enfants 6-16 ans avec besoins spéciaux
- **Thème** : Univers Star Wars complet avec progression Jedi
- **Architecture** : Dual-backend FastAPI + Starlette avec PostgreSQL
- **Status** : ✅ **Version stable 1.5.0** - 9 types d'exercices opérationnels

---

## 📚 **Structure de la Documentation**

### 🏗️ **Architecture Technique**
- [Architecture Globale](architecture/README.md) - Vue d'ensemble et composants
- [Backend](architecture/backend.md) - FastAPI + Starlette dual-backend
- [Base de Données](architecture/database.md) - PostgreSQL/SQLite compatibility
- [Sécurité](architecture/security.md) - JWT, CORS, protection des données
- [Transactions](architecture/transactions.md) - Système transactionnel unifié

### 📡 **API et Intégrations**
- [API Complète](api/api.md) - 40+ endpoints documentés avec exemples
- [Authentification](../docs/ARCHIVE/2025/AUTH_GUIDE.md) - JWT et cookies sécurisés
- [Gestion d'erreurs](api/api.md#codes-derreur) - Codes d'erreur standardisés

### 🎨 **Interface Utilisateur**  
- [Guide UI/UX Complet](ui-ux/ui-ux.md) - Interface Star Wars et accessibilité
- [Composants](ui-ux/ui-ux.md#composants-ui-réutilisables) - Boutons, cartes, modales
- [Thème Star Wars](ui-ux/ui-ux.md#thème-star-wars-immersif) - Couleurs, animations, effets

### ✨ **Fonctionnalités**
- [Fonctionnalités Principales](features/README.md) - 9 types d'exercices + défis logiques
- [Système de Badges](features/BADGE_SYSTEM.md) - Progression et récompenses
- [Tableau de Bord](features/README.md#suivi-de-progression) - Statistiques temps réel

### 👨‍💻 **Développement**
- [Guide Développeur](development/README.md) - Setup, architecture, tests (916 lignes)
- [Tests](development/testing.md) - 4 niveaux avec classification intelligente
- [Contribution](development/contributing.md) - Workflow Git et standards
- [Opérations](development/operations.md) - Maintenance et monitoring

### 🚀 **Démarrage**
- [Installation Rapide](getting-started/README.md) - Guide complet de setup
- [Configuration](getting-started/README.md#configuration-base-de-données) - SQLite/PostgreSQL
- [Premiers Pas](getting-started/README.md#premiers-pas) - Navigation et fonctions

### 📊 **Gestion de Projet**
- [Statut Projet](project/README.md) - État fonctionnalités et roadmap
- [Roadmap](project/roadmap.md) - Vision 2025-2026
- [Glossaire](GLOSSARY.md) - Terminologie technique et métier

---

## 🔍 **Navigation Rapide**

### **🆕 Nouveaux Utilisateurs**
1. [Guide de démarrage](getting-started/README.md) - Installation et premiers pas
2. [Fonctionnalités](features/README.md) - Découverte des capacités
3. [Interface](ui-ux/ui-ux.md) - Guide de l'interface utilisateur

### **👨‍💻 Développeurs**
1. [Guide développeur](development/README.md) - Setup et architecture complète
2. [API](api/api.md) - Documentation des 40+ endpoints
3. [Architecture](architecture/README.md) - Composants techniques détaillés
4. [Tests](development/testing.md) - Système de tests à 4 niveaux

### **🏗️ Architectes**
1. [Architecture](architecture/README.md) - Vue d'ensemble technique
2. [Base de données](architecture/database.md) - Modélisation et migrations  
3. [Sécurité](architecture/security.md) - Standards et implémentation
4. [Transactions](architecture/transactions.md) - Gestion ACID

### **📊 Gestionnaires de Projet**
1. [Statut projet](project/README.md) - État des fonctionnalités
2. [Roadmap](project/roadmap.md) - Planification future
3. [Rapport](rapport/rapport-mise-a-jour.md) - Dernière mise à jour complète

---

## 📈 **Métriques du Projet**

### **Fonctionnalités Opérationnelles** (Version 1.5.0)
- ✅ **9 types d'exercices** : Addition, Soustraction, Multiplication, Division, Mixte, Fractions, Géométrie, Texte, Divers
- ✅ **Interface Star Wars** : Thème immersif avec 14 pages
- ✅ **Authentification** : JWT + cookies sécurisés
- ✅ **Tableau de bord** : Statistiques temps réel corrigées
- ✅ **Tests** : 6/6 fonctionnels passent (100%)
- ✅ **Accessibilité** : WCAG 2.1 AA avec barre d'outils 4 modes

### **Architecture Technique**
- **Backend** : FastAPI 0.115.12 + Starlette 0.31.1
- **Base de données** : PostgreSQL (prod) / SQLite (dev) avec Alembic
- **Frontend** : Templates Jinja2 + CSS/JS modulaire
- **Tests** : 52%+ couverture avec classification intelligente

### **Documentation**
- **107 fichiers .md** organisés et maintenus
- **23 documents principaux** mis à jour
- **7 nouveaux guides** créés en juin 2025

---

## 🔄 **Dernières Mises à Jour** (Juin 2025)

### **Nouveautés Majeures**
- ✨ **Documentation API complète** : [api/api.md](api/api.md) - 40+ endpoints
- ✨ **Guide UI/UX exhaustif** : [ui-ux/ui-ux.md](ui-ux/ui-ux.md) - Interface Star Wars
- ✨ **Rapport de mise à jour** : [rapport/rapport-mise-a-jour.md](rapport/rapport-mise-a-jour.md) - Audit complet

### **Extensions Fonctionnelles** (Mai 2025)
- 🎯 **3 nouveaux types d'exercices** : Fractions, Géométrie, Divers
- 📊 **Corrections critiques** : Tableau de bord et authentification
- 🔧 **12/12 tests réussis** : Migration générateurs d'exercices

---

## 📞 **Support et Contributions**

### **Documentation**
- **Mise à jour** : Documentation vivante mise à jour régulièrement
- **Contributions** : Suivre le [guide de contribution](development/contributing.md)
- **Standards** : Respecter la structure et le style existants

### **Contact**
- **Issues GitHub** : Pour bugs et demandes de fonctionnalités
- **Pull Requests** : Pour contributions de code ou documentation
- **Discussions** : Pour questions et suggestions

---

**Que la Force de la Documentation soit avec vous !** 📚⭐

*Documentation Mathakine - Maintenue avec ❤️ par l'équipe de développement*