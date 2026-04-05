# UX Surfaces - Mathakine

> Statut : reference active
> Updated : 2026-04-05
> Scope : surfaces frontend visibles, audience, navigation et boundary NI-13

---

## Objectif

Ce document fixe la verite des surfaces UX visibles apres :

- la refonte neuro-inclusive
- la creation de `/home-learner`
- la normalisation des roles canoniques
- le durcissement serveur + client de `NI-13`

---

## Audiences et surfaces

| Audience     | Home par defaut | Surfaces principales                                   | Surfaces secondaires             |
| ------------ | --------------- | ------------------------------------------------------ | -------------------------------- |
| Visiteur     | `/`             | home publique, contenu public, changelog               | login, register                  |
| `apprenant`  | `/home-learner` | home apprenant, exercices, defis, badges, classement   | `/dashboard` via entree discrete |
| `enseignant` | `/dashboard`    | dashboard adulte, exercices, defis, badges, classement | pas de `home-learner`            |
| `moderateur` | `/dashboard`    | dashboard adulte + moderation selon droits             | pas de `home-learner`            |
| `admin`      | `/dashboard`    | dashboard adulte + `/admin`                            | pas de `home-learner`            |

`parent` n'est pas implemente dans cette phase.

Surface cible suivante apres stabilisation :

| Audience cible | Home par defaut     | Surfaces principales                  | Notes                                            |
| -------------- | ------------------- | ------------------------------------- | ------------------------------------------------ |
| `parent`       | `/parent/dashboard` | dashboard parent + detail d'un enfant | prochain ajout produit, distinct de `enseignant` |

---

## Navigation visible

### Apprenant

Navigation principale :

- `Mon espace`
- `Exercices`
- `Defis`
- `Badges`
- `Classement`

Entree secondaire :

- `Tableau de bord` reste disponible dans le menu profil, pas dans la nav principale

### Roles adultes

Navigation principale :

- `Tableau de bord`
- `Exercices`
- `Defis`
- `Badges`
- `Classement`

Entree admin :

- visible dans le menu profil pour `admin`

### Phase suivante - parent

Navigation cible minimale :

- `Tableau parent`
- `Mes enfants`
- acces detail par enfant

Le parent ne doit pas reutiliser tel quel le dashboard analytique adulte actuel.

---

## NI-13 - Boundary actif

Le boundary est maintenant **serveur + client** :

- serveur : `frontend/proxy.ts`
- client : `frontend/components/auth/ProtectedRoute.tsx`
- politique partagee : `frontend/lib/auth/routeAccess.ts`

Regles :

- `/home-learner`
  - autorise pour `apprenant`
  - redirige les roles adultes vers `/dashboard`
- `/dashboard`
  - autorise pour `apprenant` et roles adultes avec acces complet
  - reste secondaire pour `apprenant`
- `/admin`
  - autorise uniquement pour `admin`
  - verite backend requise sur la route serveur

---

## Principes UX livres

### Surface apprenant

- structure lineaire
- zero onglets
- actions immediates
- progression visible sans surcharge analytique
- feedback explicite
- neutralisation des distractions visuelles via `data-learner-context`

### Surface dashboard

- lecture analytique
- widgets plus denses
- charts et exports
- acceptable pour `apprenant` en secondaire, cible principale adulte

---

## Composants structurants

- `LearnerLayout`
- `LearnerCard`
- `ProtectedRoute`
- `Header`
- `SpacedRepetitionSummaryWidget`
- `StudentChallengesBoard`

---

## Liens de verite

- Roles : [../00-REFERENCE/USER_ROLE_NOMENCLATURE.md](../00-REFERENCE/USER_ROLE_NOMENCLATURE.md)
- Architecture : [ARCHITECTURE.md](ARCHITECTURE.md)
- Accessibilite : [ACCESSIBILITY.md](ACCESSIBILITY.md)
- Themes : [../02-FEATURES/THEMES.md](../02-FEATURES/THEMES.md)
- Parent spec : [../02-FEATURES/PARENT_DASHBOARD_AND_CHILD_LINKS.md](../02-FEATURES/PARENT_DASHBOARD_AND_CHILD_LINKS.md)
