# Documentation des Nouveaux Types d'Exercices dans Mathakine

## Introduction

Mathakine a été enrichi avec trois nouveaux types d'exercices pour diversifier l'expérience d'apprentissage des mathématiques :

1. **Fractions** : Exercices sur les opérations avec fractions
2. **Géométrie** : Exercices sur les figures géométriques et leurs propriétés
3. **Divers (Problèmes)** : Exercices variés sous forme de problèmes à résoudre

Ces nouveaux types complètent les types existants (Addition, Soustraction, Multiplication, Division) et permettent d'explorer davantage de concepts mathématiques avec la même thématique Star Wars immersive.

## 1. Exercices de Fractions

### Description

Les exercices de fractions permettent aux élèves de pratiquer les opérations sur les fractions (addition, soustraction, multiplication, division) adaptées à leur niveau.

### Adaptation par niveau de difficulté

- **Initié** : 
  - Fractions simples avec dénominateurs faciles (2, 3, 4, 5)
  - Uniquement des additions
  - Numérateurs inférieurs aux dénominateurs (fractions propres)

- **Padawan** : 
  - Fractions avec dénominateurs intermédiaires (2-10)
  - Additions et soustractions
  - Fractions propres

- **Chevalier** : 
  - Fractions plus complexes avec dénominateurs jusqu'à 12
  - Additions, soustractions et multiplications
  - Introduction des fractions impropres

- **Maître** : 
  - Fractions avancées avec dénominateurs jusqu'à 20
  - Toutes les opérations (y compris la division)
  - Fractions impropres complexes

### Exemple d'exercice

```
Calcule la fraction 2/5 + 1/3
```

La résolution implique de trouver un dénominateur commun (15), puis d'effectuer l'addition:
```
2/5 = 6/15
1/3 = 5/15
6/15 + 5/15 = 11/15
```

### Choix et distracteurs

Les choix incluent la bonne réponse et des distracteurs basés sur des erreurs communes:
- Confusion des dénominateurs
- Inversion des fractions
- Addition des numérateurs et dénominateurs (erreur courante)

## 2. Exercices de Géométrie

### Description

Les exercices de géométrie permettent aux élèves de calculer différentes propriétés des figures géométriques (périmètre, aire, etc.) en fonction de leur niveau.

### Adaptation par niveau de difficulté

- **Initié** : 
  - Formes simples : carré ou rectangle
  - Calculs de périmètre ou d'aire

- **Padawan** : 
  - Ajout du triangle
  - Calculs de périmètre ou d'aire

- **Chevalier** : 
  - Ajout du cercle et du trapèze
  - Introduction de la diagonale

- **Maître** : 
  - Formes avancées incluant losange et hexagone
  - Propriétés avancées comme rayon et apothème

### Exemple d'exercice

```
Calcule le périmètre d'un rectangle avec longueur=8 et largeur=4
```

La résolution utilise la formule du périmètre d'un rectangle:
```
Périmètre = 2 × (longueur + largeur) = 2 × (8 + 4) = 2 × 12 = 24
```

### Choix et distracteurs

Les choix incluent la bonne réponse et des distracteurs basés sur des erreurs communes:
- Oubli du facteur 2 dans le périmètre
- Confusion avec la formule de l'aire
- Erreurs de calcul simples

## 3. Exercices Divers (Problèmes)

### Description

Cette catégorie propose des problèmes variés adaptés à l'âge et au niveau des élèves, couvrant différents domaines des mathématiques (monnaie, âge, vitesse, pourcentage, probabilité, etc.).

### Adaptation par niveau de difficulté

- **Initié** : 
  - Problèmes simples : monnaie, âge, vitesse simple
  - Nombres petits et calculs directs

- **Padawan** : 
  - Problèmes intermédiaires : ajout des pourcentages
  - Situations plus complexes

- **Chevalier** : 
  - Problèmes avancés : probabilités, mélanges
  - Résolutions multi-étapes

- **Maître** : 
  - Problèmes experts : algébriques, séquences
  - Raisonnement mathématique avancé

### Types de problèmes disponibles

1. **Monnaie** : Calcul de monnaie à rendre
2. **Âge** : Calcul d'âge futur ou passé
3. **Vitesse** : Calculs de distance, temps ou vitesse
4. **Pourcentage** : Applications des pourcentages
5. **Probabilité** : Calcul de probabilités simples
6. **Mélange** : Calcul de concentration d'un mélange
7. **Algébrique** : Résolution d'équations simples
8. **Séquence** : Identification du terme suivant

### Exemple d'exercice

```
Tu achètes un jouet qui coûte 12 euros. Tu paies avec un billet de 20 euros. Combien d'euros le vendeur doit-il te rendre?
```

La résolution est un simple calcul de soustraction:
```
20 - 12 = 8 euros
```

### Choix et distracteurs

Les choix varient selon le type de résultat:
- Pour les entiers: valeurs proches et le double
- Pour les décimaux: variations de pourcentage (±10%, ×2)
- Pour les fractions: variations sur le numérateur et le dénominateur

## Intégration dans le Système

Les nouveaux types d'exercices sont parfaitement intégrés dans l'application:

1. **Base de données**: Compatible avec le schéma existant
2. **API**: Accessible via les mêmes endpoints
3. **Interface utilisateur**: Affichage adapté dans l'interface existante
4. **Système de difficulté**: Adaptation en fonction du niveau du joueur

## Messages et Constantes

Les nouveaux types utilisent le système centralisé de messages et constantes:

- **Titres**: `TITLE_FRACTIONS`, `TITLE_GEOMETRIE`, `TITLE_DIVERS`
- **Questions**: `QUESTION_FRACTIONS`, `QUESTION_GEOMETRIE`, `QUESTION_DIVERS`
- **Explications**: Format standardisé pour chaque type

## Conclusion

Ces trois nouveaux types d'exercices enrichissent considérablement l'offre éducative de Mathakine en permettant d'explorer des concepts mathématiques plus variés, tout en conservant l'expérience immersive Star Wars qui caractérise l'application.

Les exercices s'adaptent automatiquement au niveau de l'élève, offrant une progression pédagogique cohérente du niveau Initié au niveau Maître. 