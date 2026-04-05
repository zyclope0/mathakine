# Dashboard parent et gestion des enfants

> Statut : spec active
> Updated : 2026-04-05
> Priorite produit : prochain ajout cible apres stabilisation de `3.6.0-alpha.1`

---

## Objectif

Cadrer le prochain lot produit autour de l'audience `parent`, sans melanger :

- le lot deja livre `roles canoniques + NI-13`
- la migration SQL legacy encore en attente
- les besoins distincts `enseignant` vs `parent`

Ce document ne signifie pas que `parent` est deja implemente.
Il fixe seulement **ou** et **comment** l'implementer ensuite.

---

## Positionnement

`parent` est le prochain role metier cible apres stabilisation de `3.6.0-alpha.1`.

Il ne doit pas etre traite comme un synonyme de :

- `enseignant`
- `moderateur`
- `admin`

Le besoin produit vise une surface de suivi domestique simple :

- voir un ou plusieurs enfants lies
- comprendre rapidement leur progression
- relancer un parcours utile sans entrer dans un dashboard analytique trop dense

---

## Perimetre phase 1

Le lot vise un **MVP parent** avec 3 briques :

1. **Role canonique `parent`**
   - ajoute au contrat applicatif/API
   - traite comme role adulte non-staff

2. **Liens parent-enfant**
   - relation persistante parent <-> enfant
   - lecture d'une liste d'enfants lies
   - selection d'un enfant actif cote UI

3. **Surface parent dediee**
   - `/parent/dashboard`
   - `/parent/child/[id]`

Le lot n'inclut pas :

- espace enseignant multi-classe complet
- moderation
- admin
- partage public sans compte

Le partage simple vers parents reste documente separement dans `F11`.

---

## Regles UX

Le dashboard parent ne doit pas etre une copie du dashboard adulte actuel.

Contraintes :

- un enfant actif a la fois par defaut
- priorite a la comprehension rapide, pas a l'exhaustivite
- zero grille de 16 widgets
- CTA explicites :
  - voir les revisions a faire
  - voir les progres recents
  - voir les badges proches

Lecture recommandee :

1. enfant selectionne
2. etat du jour
3. progression recente
4. actions ou encouragements utiles

---

## Architecture cible

### Role

Role canonique futur :

- `parent`

Compatibilite :

- a introduire **apres** le lot roles canoniques actuel
- sans reintroduire de strings legacy dans le frontend actif

### Donnees

Table minimale cible :

```sql
parent_child_links (
  id SERIAL PRIMARY KEY,
  parent_user_id INTEGER NOT NULL REFERENCES users(id),
  child_user_id INTEGER NOT NULL REFERENCES users(id),
  relationship_label VARCHAR(50) NULL,
  permissions JSONB NULL,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
)
```

Principes :

- un parent peut avoir plusieurs enfants lies
- un enfant peut etre visible par plusieurs adultes si le produit l'autorise plus tard
- la phase 1 peut commencer avec des permissions simples en lecture

### Routes cibles

- `/parent/dashboard`
- `/parent/child/[id]`

### Boundary

Politique cible :

- `parent` -> home par defaut `/parent/dashboard`
- `parent` n'entre pas dans `/home-learner`
- `parent` n'entre pas dans `/admin`
- `parent` n'est pas confondu avec `enseignant`

---

## Sequencage recommande

### Phase 1 - fondation role + liens

- ajouter `parent` au modele canonique
- ajouter la persistance `parent_child_links`
- ajouter les contracts API minimaux

### Phase 2 - surface parent

- creer `/parent/dashboard`
- creer `/parent/child/[id]`
- definir une navigation parent dediee

### Phase 3 - enrichissements

- notifications parent
- partage simple / lecture seule
- vues comparees si plusieurs enfants

---

## Source de verite associee

- roadmap : [ROADMAP_FONCTIONNALITES.md](ROADMAP_FONCTIONNALITES.md)
- roles : [../00-REFERENCE/USER_ROLE_NOMENCLATURE.md](../00-REFERENCE/USER_ROLE_NOMENCLATURE.md)
- surfaces UX : [../04-FRONTEND/UX_SURFACES.md](../04-FRONTEND/UX_SURFACES.md)
- modele de donnees : [../00-REFERENCE/DATA_MODEL.md](../00-REFERENCE/DATA_MODEL.md)
