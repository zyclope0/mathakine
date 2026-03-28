# Normalisation des niveaux de difficulte

> Updated: 27/03/2026
> Statut: reference de compatibilite post-F42

---

## 1. Contexte

L'ancienne difficulte historique du projet reposait sur des valeurs comme :
- `INITIE`
- `PADAWAN`
- `CHEVALIER`
- `MAITRE`
- `GRAND_MAITRE`

Depuis F42, la normalisation ne consiste plus a renommer tous les enums en base.
La verite actuelle est plus precise :

`age_group + pedagogical_band -> difficulty_tier`

Et les surfaces visibles ont ete neutralisees pour ne plus afficher brutalement les labels legacy a l'utilisateur.

---

## 2. Ce qui est deja livre

### Produit visible

Les surfaces utilisateur principales n'utilisent plus les anciens labels comme vocabulaire public de difficulte :
- generateurs et libelles d'exercices neutralises
- recommandations et aides neutralisees
- progression publique neutralisee
- principaux restes visibles Star Wars retires

### Modele pedagogique

Le modele canonique de difficulte est maintenant :
- `age_group`
- `pedagogical_band`
- `difficulty_tier`

### Compatibilite

Les champs legacy restent presents dans le backend et certaines APIs :
- `difficulty`
- `mastery_level`
- `difficulty_rating`

Ils sont acceptes comme couches de compatibilite ou de stockage, pas comme verite fine unique.

---

## 3. Ce qui n'a pas ete fait volontairement

Le projet n'a pas cherche a :
- renommer tous les enums legacy en base
- migrer toutes les colonnes historiques
- supprimer tous les identifiants techniques anciens

Exemples de dettes legitimes encore presentes :
- `difficulty = INITIE/PADAWAN/...`
- `Progress.mastery_level = 1..5`
- `jedi_rank` comme nom de champ technique pour les rangs publics

Pourquoi c'est acceptable :
- la compatibilite de contrat est preservee
- le risque de migration est evite a court terme
- la verite canonique F42 est quand meme centralisee dans le runtime

---

## 4. Lecture correcte aujourd'hui

### A afficher a l'utilisateur

On affiche :
- un libelle neutre ou pedagogique
- une progression publique lisible
- une calibration produit sobre

On n'affiche pas en brut :
- `PADAWAN`
- `MAITRE`
- autres labels techniques legacy

### A utiliser pour la logique metier

Pour toute nouvelle logique fine, il faut partir de :
- `age_group`
- `pedagogical_band`
- `difficulty_tier`

### A conserver comme compatibilite

Les champs legacy sont autorises pour :
- stockage
- lecture de donnees anciennes
- fallback de compatibilite
- boundaries historiques qui n'ont pas encore besoin d'une migration

---

## 5. Si l'equipe veut aller plus loin un jour

Une normalisation plus forte deviendra pertinente seulement si l'on veut :
- supprimer les champs legacy des contrats
- persister plus largement le canon F42
- simplifier fortement le reporting et l'analytics

Ce serait alors un vrai chantier de migration, pas un simple lot de wording.

---

## 6. References

- [DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md](DIFFICULTE_PEDAGOGIQUE_ET_RANGS_GUIDE.md)
- [../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md](../00-REFERENCE/DIFFICULTY_AND_RANKS_MANIFEST.md)
- `app/core/difficulty_tier.py`
- `app/core/mastery_tier_bridge.py`
