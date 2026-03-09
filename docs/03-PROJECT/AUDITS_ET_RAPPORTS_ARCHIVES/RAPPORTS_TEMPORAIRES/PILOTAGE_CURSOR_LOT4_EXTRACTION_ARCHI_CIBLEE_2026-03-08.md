# Pilotage Cursor - Lot 4 - Extraction Architecture Ciblee

> Date : 08/03/2026
> Type : dette structurelle ciblee
> Risque accepte : moyen

---

## 1. Mission

Reduire la dette structurelle sur un seul hotspot backend, sans ouvrir une
refonte globale.

---

## 2. Objectif de sortie

En fin de lot :

- un seul hotspot a ete traite
- le comportement fonctionnel reste identique
- les tests caracterisation protegeant l'extraction sont verts
- le diff reste lisible et explicable

---

## 3. Cible du cycle

Pour ce cycle, la cible recommandee est :

- `app/services/challenge_validator.py`

Raison :

- fichier tres volumineux
- couverture faible
- risque de regression implicite si on le laisse grossir

Ne pas traiter `badge_service.py` dans le meme lot.

---

## 4. Fichiers a lire avant toute modification

- `app/services/challenge_validator.py`
- tests associes au validator / challenges
- documents d'architecture pertinents

---

## 5. Scope autorise

- extraction d'une seule seam claire
- deplacement de fonctions pures ou de logique lisiblement isolable
- ajout de tests de caracterisation avant extraction si necessaire
- renommage minimal pour clarifier la responsabilite

---

## 6. Scope interdit

- pas de changement de contrat API
- pas de modification de logique fonctionnelle voulue
- pas de traitement simultane de plusieurs hotspots
- pas de "clean architecture" generale

---

## 7. Strategie d'extraction

Ordre impose :

1. identifier une seam unique dans `challenge_validator.py`
2. ecrire ou renforcer les tests qui figent son comportement
3. extraire seulement cette seam
4. rerouter le code appelant sans changer le comportement
5. executer les checks

Exemples de seams acceptables :

- normalisation pure
- regles de validation sans acces IO
- comparaisons ou transformations pures

Exemples de seams refusees pour ce lot :

- redecoupage complet du service
- redesign du domaine challenge
- changement de format de reponse

---

## 8. Verification attendue

- tests backend cibles sur le validator / challenges
- `pytest -q --maxfail=20`
- `black app/ server/ tests/ --check`

Si de nouveaux modules sont crees, verifier aussi les imports et la lisibilite
du diff.

---

## 9. Stop conditions

Cursor doit s'arreter si :

- aucune seam simple n'est extractible sans gros redesign
- le lot commence a toucher plusieurs domaines metier
- l'extraction exige une reecriture du comportement
- les tests caracterisation manquent au point de rendre l'extraction aveugle

Dans ce cas, convertir le lot en lot de cartographie et ne pas coder plus loin.

---

## 10. Definition of done

- une seule seam extraite proprement
- tests verts avant et apres
- comportement stable
- diff comprehensible en revue

---

## 11. Compte-rendu demande

Cursor doit retourner :

1. la seam choisie
2. pourquoi elle etait le bon premier decoupage
3. les tests de caracterisation relies a cette extraction
4. les checks executes
5. ce qui reste explicitement hors scope pour le prochain cycle

