# Normalisation des niveaux de difficulté

> **Date** : 27/02/2026  
> **Statut** : À faire — Souhait produit  
> **Priorité** : Moyenne (amélioration UX, pas bloquant)

---

## Contexte

Le système actuel utilise une nomenclature **Star Wars** pour les niveaux de difficulté des exercices :

| Valeur actuelle   | Signification      | Groupe d'âge |
|-------------------|-------------------|--------------|
| INITIE            | Facile            | 6-8 ans      |
| PADAWAN           | Moyen             | 9-11 ans     |
| CHEVALIER         | Difficile         | 12-14 ans    |
| MAITRE            | Très difficile    | 15-17 ans    |
| GRAND_MAITRE      | Expert            | Adultes      |

**Problème** : Cette logique n'est pas forcément claire pour tous les utilisateurs (enfants, parents, enseignants) qui ne connaissent pas l'univers Star Wars ou la hiérarchie Jedi.

---

## Objectif

Normaliser les niveaux de difficulté pour sortir de la logique Star Wars et proposer des libellés plus universels et compréhensibles.

### Pistes envisagées

1. **Niveaux numériques** : 1, 2, 3, 4, 5 (avec libellés optionnels : débutant, élémentaire, intermédiaire, avancé, expert)
2. **Libellés directs** : Facile, Moyen, Difficile, Très difficile, Expert
3. **Alignement scolaire** : CP-CE2, CM1-6e, 5e-3e, Lycée, Adulte
4. **Médaille / étoiles** : Bronze, Argent, Or… (déjà partiellement utilisé pour les badges)

---

## Périmètre technique

| Zone                 | Fichiers / modèle                         | Impact |
|----------------------|-------------------------------------------|--------|
| Modèle Exercise      | `app/models/exercise.py` — enum DifficultyLevel | Migration enum + données |
| Constantes           | `app/core/constants.py` — DifficultyLevels | Mapping, aliases |
| Schémas              | `app/schemas/exercise.py` — validateurs   | Validation |
| Admin                | `app/services/admin_service.py`, handlers | Création / édition |
| Recommandations      | `app/services/recommendation_service.py` | Filtres, progression |
| Générateur exercices  | `server/exercise_generator*.py`            | Génération IA |
| Frontend             | Composants admin, exercices, badges       | Affichage, sélecteurs |
| Base de données      | Colonne `difficulty` (exercises, etc.)    | Migration de données |

---

## À faire

- [ ] Choisir la nomenclature cible (produit / design)
- [ ] Définir le mapping ancien → nouveau (rétrocompatibilité)
- [ ] Migration enum + données
- [ ] Mise à jour schémas, services, admin
- [ ] Mise à jour frontend
- [ ] Tests de non-régression

---

## Référence

- Inventaire actuel : `app/models/exercise.py` (lignes 19-26)
- Constantes : `app/core/constants.py` (DifficultyLevels, ALL_LEVELS)
- Voir aussi : `docs/03-PROJECT/PLACEHOLDERS_ET_TODO.md` § Normalisation difficulté
