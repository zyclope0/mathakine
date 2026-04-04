# Nomenclature des roles utilisateur

> Statut : reference active
> Date : 2026-04-04
> Scope : roles utilisateur uniquement

---

## Objectif

Ce document fixe la verite du domaine "roles utilisateur" pendant la migration
des anciennes valeurs Star Wars vers des noms metier lisibles.

Ce chantier concerne uniquement :

- l'application backend
- les schemas API
- le frontend
- les guards d'acces et la navigation

Ce chantier ne renomme pas :

- les niveaux de difficulte
- les rangs de gamification
- les badges et codes badges
- les documents d'archives historiques

---

## Roles canoniques

Les roles applicatifs et API sont des identifiants canoniques en ASCII :

- `apprenant`
- `enseignant`
- `moderateur`
- `admin`

Libelles UI stables :

- `Apprenant`
- `Enseignant`
- `Moderateur`
- `Admin`

`parent` n'est pas implemente dans ce lot.
Il reste un role metier cible de phase 2.

---

## Mapping legacy

La base conserve encore l'enum legacy `UserRole`.
Le mapping de compatibilite est :

- `padawan -> apprenant`
- `maitre -> enseignant`
- `gardien -> moderateur`
- `archiviste -> admin`

Regles de migration phase 1 :

- lecture DB/API legacy -> normalisation canonique immediate
- sortie API -> role canonique uniquement
- entree admin/API -> role canonique ou alias legacy acceptes temporairement
- ecriture DB -> valeur legacy compatible ORM tant que l'enum SQL n'est pas migre

---

## Boundary NI-13

Le boundary apprenant/adulte s'appuie sur ces roles canoniques :

- `/home-learner` = surface apprenant principale
- `/dashboard` = surface analytique adulte, mais accessible de maniere secondaire a l'apprenant
- `apprenant` est redirige vers `/home-learner` apres login
- `apprenant` peut encore ouvrir `/dashboard` depuis une entree discrete du menu profil
- `enseignant`, `moderateur`, `admin` conservent l'acces normal au dashboard

L'implementation active utilise un guard partage et type cote frontend,
pas une redirection ad hoc locale a la page.

---

## Hors scope explicite

Les references suivantes peuvent encore exister sans contradiction :

- `padawan`, `chevalier`, `maitre`, `grand_maitre` dans les difficultes
- `padawan`, `knight`, `master` dans les rangs gamification legacy
- `padawan_path`, `maitre_jedi`, etc. dans les codes de badges
- citations historiques dans les archives projet

---

## Fichiers de verite

- Backend : `app/core/user_roles.py`
- Frontend : `frontend/lib/auth/userRoles.ts`
- Boundary apprenant/adulte : `frontend/components/auth/ProtectedRoute.tsx`
- Doc securite admin : `docs/02-FEATURES/ADMIN_FEATURE_SECURITE.md`
- Modele de donnees : `docs/00-REFERENCE/DATA_MODEL.md`
