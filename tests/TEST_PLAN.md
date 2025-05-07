# PLAN DE TEST MATHAKINE (API REBELLE)

Ce document de recette détaille tous les scénarios de test pour valider le fonctionnement complet du projet Mathakine. Il sert de référence pour les tests manuels et automatisés et doit être mis à jour à chaque évolution majeure du projet.

## ORGANISATION DES TESTS

Les tests sont organisés en 4 catégories principales, reflétant la structure du dossier `/math-trainer-backend/tests/` :

1. **Tests unitaires** : Validation des composants individuels
2. **Tests API** : Validation des endpoints de l'API Rebelle
3. **Tests d'intégration** : Validation de l'interaction entre composants
4. **Tests fonctionnels** : Validation des fonctionnalités complètes

## MATRICE DE COUVERTURE

| Domaine | Composants | Couverture tests unitaires | Couverture tests API | Couverture tests d'intégration | Couverture tests fonctionnels |
|---------|------------|----------------------------|----------------------|--------------------------------|-------------------------------|
| Modèles | Énumérations | ✅ | N/A | N/A | N/A |
| Modèles | Modèles | ✅ | N/A | ✅ | N/A |
| Exercices | Génération | ✅ | ✅ | ✅ | ✅ |
| Exercices | Validation | ✅ | ✅ | ✅ | ✅ |
| API | Endpoints de base | N/A | ✅ | N/A | N/A |
| API | Endpoints exercices | N/A | ✅ | ✅ | N/A |
| API | Authentification | N/A | ✅ | ✅ | N/A |
| Utilisateurs | Flux utilisateur | N/A | ✅ | ✅ | N/A |
| Défis logiques | Génération | ✅ | N/A | N/A | ✅ |
| Défis logiques | Validation | ✅ | N/A | N/A | ✅ |

## 1. TESTS UNITAIRES

### 1.1 Tests des énumérations
- **Objectif**: Vérifier que toutes les énumérations sont correctement définies et fonctionnent comme attendu
- **Localisation**: `/math-trainer-backend/tests/unit/test_enum.py`
- **Scénarios**:
  - ✅ Vérifier les valeurs des types de défis logiques
  - ✅ Vérifier les valeurs des groupes d'âge
  - ✅ Vérifier que toutes les énumérations sont des chaînes de caractères

### 1.2 Tests des modèles
- **Objectif**: Vérifier que les modèles de données fonctionnent correctement
- **Localisation**: `/math-trainer-backend/tests/unit/test_models.py`
- **Scénarios**:
  - ✅ Créer et valider un modèle utilisateur
  - ✅ Créer et valider un modèle exercice
  - ✅ Créer et valider un modèle tentative
  - ✅ Vérifier la relation entre utilisateur et tentatives
  - ✅ Vérifier la relation entre exercice et tentatives

### 1.3 Tests des exercices
- **Objectif**: Vérifier la génération et validation des exercices
- **Localisation**: `/math-trainer-backend/tests/unit/test_exercise.py`
- **Scénarios**:
  - ✅ Générer un exercice d'addition facile
  - ✅ Générer un exercice de soustraction moyen
  - ✅ Générer un exercice de multiplication difficile
  - ✅ Générer un exercice de division très difficile
  - ✅ Vérifier la validation des réponses correctes
  - ✅ Vérifier la validation des réponses incorrectes

## 2. TESTS API

### 2.1 Tests des endpoints de base
- **Objectif**: Vérifier les endpoints fondamentaux de l'API
- **Localisation**: `/math-trainer-backend/tests/api/test_base_endpoints.py`
- **Scénarios**:
  - ✅ Vérifier la réponse de l'endpoint racine (/)
  - ✅ Vérifier la réponse de l'endpoint info (/api/info)
  - ✅ Vérifier la réponse de l'endpoint debug (/debug)
  - ✅ Vérifier la gestion d'un endpoint inexistant

### 2.2 Tests des endpoints d'exercices
- **Objectif**: Vérifier les endpoints liés aux exercices
- **Localisation**: `/math-trainer-backend/tests/api/test_exercise_endpoints.py`
- **Scénarios**:
  - ✅ Récupérer la liste des exercices
  - ✅ Récupérer un exercice spécifique
  - ✅ Créer un nouvel exercice
  - ✅ Mettre à jour un exercice existant
  - ✅ Supprimer un exercice
  - ✅ Tester la validation des données d'entrée
  - ✅ Vérifier les contraintes d'autorisation
  - ✅ Soumettre une réponse à un exercice
  - ✅ Vérifier le traitement des réponses correctes et incorrectes

## 3. TESTS D'INTÉGRATION

### 3.1 Tests du flux utilisateur-exercice
- **Objectif**: Vérifier l'interaction complète entre utilisateurs et exercices
- **Localisation**: `/math-trainer-backend/tests/integration/test_user_exercise_flow.py`
- **Scénarios**:
  - ✅ Création d'un utilisateur Padawan
  - ✅ Authentification de l'utilisateur
  - ✅ Récupération des exercices disponibles
  - ✅ Sélection d'un exercice
  - ✅ Soumission d'une réponse correcte
  - ✅ Vérification de la progression utilisateur
  - ✅ Déconnexion et suppression du compte

## 4. TESTS FONCTIONNELS

### 4.1 Tests des défis logiques
- **Objectif**: Vérifier le fonctionnement des défis logiques (Épreuves du Conseil Jedi)
- **Localisation**: `/math-trainer-backend/tests/functional/test_logic_challenge.py`
- **Scénarios**:
  - ✅ Récupérer la liste des défis logiques
  - ✅ Récupérer un défi spécifique par ID
  - ✅ Soumettre une réponse correcte à un défi
  - ✅ Soumettre une réponse incorrecte à un défi
  - ✅ Vérifier le feedback approprié selon la réponse

## PLAN D'EXÉCUTION DES TESTS

### Exécution automatisée complète
- **Commande**: `python math-trainer-backend/tests/run_tests.py --type all`
- **Fréquence**: Avant chaque fusion de branche et déploiement
- **Critère de succès**: Tous les tests passent sans erreur

### Exécution par catégorie
- **Tests unitaires**: `python math-trainer-backend/tests/run_tests.py --type unit`
- **Tests API**: `python math-trainer-backend/tests/run_tests.py --type api`
- **Tests d'intégration**: `python math-trainer-backend/tests/run_tests.py --type integration`
- **Tests fonctionnels**: `python math-trainer-backend/tests/run_tests.py --type functional`
- **Fréquence**: Lors du développement, avant de committer des changements
- **Critère de succès**: Tous les tests de la catégorie passent sans erreur

### Scripts d'exécution disponibles
- **Windows (Batch)**: `math-trainer-backend\run_tests.bat [--unit|--api|--integration|--functional|--all]`
- **Windows (PowerShell)**: `.\math-trainer-backend\Run-Tests.ps1 [-Type unit|api|integration|functional|all]`

## TESTS MANUELS ADDITIONNELS

En plus des tests automatisés, les tests manuels suivants doivent être effectués avant chaque release majeure :

### M1. Vérification de l'interface utilisateur
1. Vérifier l'affichage correct sur différentes résolutions d'écran
2. Vérifier l'accessibilité des éléments de l'interface
3. Vérifier la cohérence du thème Star Wars dans tous les écrans
4. Vérifier la réactivité de l'interface sur mobile

### M2. Tests de performance
1. Vérifier les temps de réponse de l'API sous charge
2. Vérifier la génération d'exercices en parallèle
3. Vérifier le comportement du système avec de nombreux utilisateurs simultanés

### M3. Tests de compatibilité
1. Vérifier le fonctionnement sur différents navigateurs
2. Vérifier le fonctionnement sur différents systèmes d'exploitation
3. Vérifier la compatibilité avec Python 3.8 à 3.13

## GESTION DES DÉFAUTS

Pour chaque test échoué, suivre la procédure suivante :

1. Documenter précisément le scénario qui échoue
2. Identifier les étapes pour reproduire le problème
3. Analyser les logs et messages d'erreur
4. Créer un ticket dans le système de suivi avec les éléments suivants :
   - Titre descriptif
   - Description détaillée
   - Environnement de test
   - Étapes de reproduction
   - Résultat attendu
   - Résultat observé
   - Sévérité (Bloquant, Critique, Majeur, Mineur, Cosmétique)
   - Priorité (Immédiate, Haute, Moyenne, Basse)

## VALIDATION DES FONCTIONNALITÉS MÉTIER

### V1. Fonctionnalités pédagogiques
1. Vérifier que les exercices sont adaptés aux enfants autistes
2. Vérifier que la difficulté est progressive et adaptative
3. Vérifier que le feedback est clair et encourageant
4. Vérifier que les explications sont compréhensibles pour le public cible

### V2. Thématique Star Wars
1. Vérifier la cohérence de la terminologie dans toute l'application
2. Vérifier que les éléments visuels sont conformes à la thématique
3. Vérifier que la thématique renforce l'engagement sans distraire

## MISE À JOUR DE LA RECETTE

Cette recette de tests doit être mise à jour dans les cas suivants :
1. Ajout d'une nouvelle fonctionnalité
2. Modification significative d'une fonctionnalité existante
3. Identification d'un nouveau scénario de test pertinent
4. Correction d'un bug majeur nécessitant un test spécifique

**Dernière mise à jour**: 07/05/2025

---

## SUIVI DES VERSIONS DE LA RECETTE

| Version | Date | Auteur | Description des modifications |
|---------|------|--------|-------------------------------|
| 1.0 | 07/05/2025 | Claude | Version initiale de la recette de tests | 