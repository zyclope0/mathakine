# Normalisation des niveaux de difficultÃ©

> **Date** : 27/02/2026  
> **Statut** : Ã€ faire â€” Souhait produit  
> **PrioritÃ©** : Moyenne (amÃ©lioration UX, pas bloquant)

---

## Contexte

Le systÃ¨me actuel utilise une nomenclature **Star Wars** pour les niveaux de difficultÃ© des exercices :

| Valeur actuelle   | Signification      | Groupe d'Ã¢ge |
|-------------------|-------------------|--------------|
| INITIE            | Facile            | 6-8 ans      |
| PADAWAN           | Moyen             | 9-11 ans     |
| CHEVALIER         | Difficile         | 12-14 ans    |
| MAITRE            | TrÃ¨s difficile    | 15-17 ans    |
| GRAND_MAITRE      | Expert            | Adultes      |

**ProblÃ¨me** : Cette logique n'est pas forcÃ©ment claire pour tous les utilisateurs (enfants, parents, enseignants) qui ne connaissent pas l'univers Star Wars ou la hiÃ©rarchie Jedi.

---

## Objectif

Normaliser les niveaux de difficultÃ© pour sortir de la logique Star Wars et proposer des libellÃ©s plus universels et comprÃ©hensibles.

### Pistes envisagÃ©es

1. **Niveaux numÃ©riques** : 1, 2, 3, 4, 5 (avec libellÃ©s optionnels : dÃ©butant, Ã©lÃ©mentaire, intermÃ©diaire, avancÃ©, expert)
2. **LibellÃ©s directs** : Facile, Moyen, Difficile, TrÃ¨s difficile, Expert
3. **Alignement scolaire** : CP-CE2, CM1-6e, 5e-3e, LycÃ©e, Adulte
4. **MÃ©daille / Ã©toiles** : Bronze, Argent, Orâ€¦ (dÃ©jÃ  partiellement utilisÃ© pour les badges)

---

## PÃ©rimÃ¨tre technique

| Zone                 | Fichiers / modÃ¨le                         | Impact |
|----------------------|-------------------------------------------|--------|
| ModÃ¨le Exercise      | `app/models/exercise.py` â€” enum DifficultyLevel | Migration enum + donnÃ©es |
| Constantes           | `app/core/constants.py` â€” DifficultyLevels | Mapping, aliases |
| SchÃ©mas              | `app/schemas/exercise.py` â€” validateurs   | Validation |
| Admin                | `app/services/admin_content_service.py`, `app/services/admin_stats_service.py`, handlers | CrÃ©ation / Ã©dition |
| Recommandations      | `app/services/recommendation_service.py` | Filtres, progression |
| Generateur exercices  | `app/generators/exercise_generator.py` + `app/utils/exercise_generator_*.py` | Generation et validation (avec compatibilite `server/exercise_generator*.py`) |
| Frontend             | Composants admin, exercices, badges       | Affichage, sÃ©lecteurs |
| Base de donnÃ©es      | Colonne `difficulty` (exercises, etc.)    | Migration de donnÃ©es |

---

## Ã€ faire

- [ ] Choisir la nomenclature cible (produit / design)
- [ ] DÃ©finir le mapping ancien â†’ nouveau (rÃ©trocompatibilitÃ©)
- [ ] Migration enum + donnÃ©es
- [ ] Mise Ã  jour schÃ©mas, services, admin
- [ ] Mise Ã  jour frontend
- [ ] Tests de non-rÃ©gression

---

## RÃ©fÃ©rence

- Inventaire actuel : `app/models/exercise.py` (lignes 19-26)
- Constantes : `app/core/constants.py` (DifficultyLevels, ALL_LEVELS)
- Voir aussi : `docs/03-PROJECT/PLACEHOLDERS_ET_TODO.md` Â§ Normalisation difficultÃ©

