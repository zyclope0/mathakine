# Guide utilisateur MVP — Mathakine

> **Objectif** : Documentation utilisateur MVP (= **version minimale** de la doc : le strict nécessaire pour démarrer) avec réflexion sur la cible, la rétention et l’adaptation psychologique.

**Date** : Février 2026

> 📌 **Version en ligne** : ce guide est intégré au site sur `/docs`. Le présent fichier est la source détaillée pour l'équipe (personas, analyse psychologique, post-MVP).

---

## 1. Cible utilisateur

### 1.1 Profil principal

| Critère | Cible |
|---------|--------|
| **Âge** | 5 à 20 ans |
| **Usage** | Apprentissage des mathématiques |
| **Particularités** | Enfants/ados, possiblement TSA, TDAH ou besoins en accessibilité |
| **Décideur** | Parent ou tuteur (création du compte, suivi) |

### 1.2 Personas MVP

**Persona A — Lucas, 8 ans (TDAH)**  
- Besoin de courtes sessions, feedback visuel fort, renforcements fréquents  
- Risque de décrochage si trop long ou trop difficile  

**Persona B — Emma, 14 ans (dyscalculie)**  
- Besoin de progression très progressive, moins de pression, formats visuels  
- Peur de l’échec, besoin de voir les progrès  

**Persona C — Parent (Marine)**  
- Veut voir la progression, comprendre comment l’enfant utilise l’app  
- Cherche une solution simple, adaptée et sérieuse  

---

## 2. Analyse psychologique et adaptation

### 2.1 Motivations

- **Compétence** : sentiment de progresser, maîtriser de nouveaux sujets  
- **Autonomie** : choisir ce qu’on fait, à son rythme  
- **Lien** : badges, série, progression (effet “collection”)  
- **Réduction d’anxiété** : pas de note, pas de jugement public, erreurs encouragées  

### 2.2 Freins potentiels

- **Surcharge cognitive** : trop d’infos, trop de choix → simplifier les parcours  
- **Frustration** : difficulté mal calibrée → adapter la difficulté et rassurer  
- **Perte de motivation** : objectif trop lointain → objectifs courts et visibles  
- **Découragement après erreur** : feedback négatif ressenti fortement → valoriser l’effort  

### 2.3 Principes d’adaptation UX

1. **Feedback immédiat et positif** : même en cas d’erreur  
2. **Progression visible** : badges, série, graphiques simples  
3. **Sessions courtes** : 5–15 min par défaut, proposer de continuer ou s’arrêter  
4. **Choix et contrôle** : catégories, types d’exercices  
5. **Pas de punition** : pas de “mauvaise note”, plutôt “tu peux réessayer”  

---

## 3. Stratégie de rétention

### 3.1 Levers (leviers) MVP

| Levier | Implémentation actuelle | Amélioration possible |
|--------|-------------------------|------------------------|
| **Habitude** | Exercices quotidiens possibles | Streak, rappel quotidien |
| **Progression** | Badges, dashboard | Série quotidienne, objectifs courts |
| **Propriété** | Profil, badges | Personnalisation (avatar, thème) |
| **Réciprocité** | App gratuite en partie | Contenu premium, partage des progrès |
| **Engagement** | Défis IA, exercices variés | Défis du jour, variété des formats |

### 3.2 Points d’accroche

- **Premier jour** : onboarding simple, premier badge rapide  
- **J+7** : objectif “7 jours”, renforcement positif  
- **J+30** : rétrospective de progression (graphique, badges débloqués)  

---

## 4. Guide utilisateur — Parcours MVP

> Ce parcours est reflété sur la page `/docs` du site (version grand public).

### 4.1 Démarrer (Parent ou grand enfant)

1. **Inscription** : [mathakine.fun/register](https://mathakine.fun/register)  
   - Nom d’utilisateur, email, mot de passe  
   - Vérifier l’email (lien envoyé)  

2. **Connexion** : [mathakine.fun/login](https://mathakine.fun/login)  
   - Identifiants créés à l’inscription  
   - Option “Mot de passe oublié” si besoin  

3. **Premier contact**  
   - Page d’accueil → **Exercices** ou **Défis**  
   - Choix de la catégorie (addition, soustraction, etc.) ou du type de défi  

### 4.2 Utilisation quotidienne

| Action | Où | Description |
|--------|-----|-------------|
| **Faire des exercices** | `/exercises` | Choisir une catégorie, lancer un exercice, répondre |
| **Lancer un défi** | `/challenges` | Types variés (patterns, énigmes, graphes, etc.) |
| **Voir sa progression** | `/dashboard` | Graphiques, précision, activité récente |
| **Consulter ses badges** | `/badges` | Badges débloqués, objectifs |
| **Paramètres** | `/settings` | Langue, thème, accessibilité (contraste, police, animations) |

### 4.3 Mode accessibilité

Dans **Paramètres** ou via la barre d’accessibilité :

- **Contraste élevé** : Alt+C  
- **Texte agrandi** : Alt+T  
- **Animations réduites** : Alt+M  
- **Mode dyslexie** : Alt+D  
- **Mode Focus TSA/TDAH** : Alt+F  

### 4.4 Fonctionnement des exercices

1. Choisir une **catégorie** (ex. Addition)  
2. Choisir un **niveau de difficulté** (Découverte, Apprenti, Confirmé, Avancé)  
3. Lire l’énoncé et répondre dans le champ prévu  
4. Valider → Feedback immédiat (correct / incorrect)  
5. Possibilité de passer à l’exercice suivant  

### 4.5 Fonctionnement des défis

1. Choisir un **type** de défi (pattern, énigme, graphe, etc.)  
2. Lire la consigne et résoudre  
3. Répondre dans le format demandé (texte, nombre, etc.)  
4. Valider et voir le feedback  

### 4.6 Export des données

Sur le **Dashboard** :  
- **Exporter en PDF** ou **Excel** pour garder une trace de la progression  

---

## 5. FAQ MVP

### Inscription et compte

**Comment créer un compte ?**  
→ Aller sur **S’inscrire**, remplir le formulaire, vérifier l’email et se connecter.

**Je n’ai pas reçu l’email de vérification.**  
→ Vérifier les spams. Si besoin : page **Vérification email** → “Pas reçu ?” → renvoyer.

**J’ai oublié mon mot de passe.**  
→ **Connexion** → “Mot de passe oublié” → indiquer l’email pour recevoir un lien de réinitialisation.

### Exercices et défis

**Où sont les exercices ?**  
→ Menu **Exercices** ou bouton sur la page d’accueil.

**Comment choisir la difficulté ?**  
→ Lors du choix d’un exercice : Découverte, Apprenti, Confirmé ou Avancé selon le niveau proposé à l’écran.

**Les défis sont-ils notés ?**  
→ Non. L’objectif est de s’entraîner et de progresser, pas d’être noté.

### Progression et badges

**Où voir ma progression ?**  
→ **Dashboard** : graphiques, précision par catégorie, activité récente.

**Comment obtenir des badges ?**  
→ En réalisant des actions (exercices réussis, défis complétés, etc.). Ils s’affichent sur la page **Badges**.

### Accessibilité et paramètres

**L’interface est trop chargée.**  
→ **Paramètres** → Mode Focus (TSA/TDAH) ou réduction des animations.

**Je préfère un thème sombre.**  
→ **Paramètres** → Thème : Clair / Sombre / Système.

**L’app fonctionne-t-elle hors ligne ?**  
→ Oui, en PWA : installation depuis le navigateur puis utilisation hors ligne pour certaines parties.

---

## 6. Prochaines étapes (post-MVP)

- [ ] Video tutoriel court (2–3 min)  
- [ ] Guide parent (suivi, interprétation des graphiques)  
- [ ] FAQ enrichie (vidéos, captures d’écran)  
- [ ] Onboarding interactif au premier login  
- [ ] Rappels / notifications pour la rétention  

---

## 7. Références

- [ROADMAP_FONCTIONNALITES.md](../02-FEATURES/ROADMAP_FONCTIONNALITES.md) — Évolutions fonctionnelles  
- [ACCESSIBILITY_GUIDE.md](../../frontend/docs/ACCESSIBILITY_GUIDE.md) — Détails accessibilité  
- [README.md](../../README.md) — Présentation du projet  
