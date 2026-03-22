# Convention de documentation Mathakine

> Regles de nommage, structure et maintenance des documents projet
> **Version :** 1.1 - 22/03/2026

---

## Recapitulatif - Ou mettre quel document ?

| Type | Emplacement | Exemple |
|------|-------------|---------|
| **Audit - toutes recos appliquees** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` | ANALYSE_THEMES_UX |
| **Audit - recos partielles** | `03-PROJECT/` (racine) | AUDIT_DASHBOARD |
| **Rapport situationnel** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` | DEPLOIEMENT_2026, MISSION_COMPLETE |
| **Reference actuelle / CI-CD** | `03-PROJECT/` (racine) | EVALUATION_PROJET, CICD_DEPLOY |
| **Reference transversale runtime / gouvernance** | `00-REFERENCE/` | AI_MODEL_GOVERNANCE |
| **A faire / TODO** | `03-PROJECT/` (racine) | ENDPOINTS_NON_INTEGRES |

---

## 1. Structure des dossiers

```text
docs/
|-- 00-REFERENCE/       # Reference technique vivante
|-- 01-GUIDES/          # Guides pratiques (dev, test, deploiement)
|-- 02-FEATURES/        # Documentation fonctionnalites
|-- 03-PROJECT/         # Gestion projet - audits, rapports, evaluations
|-- 06-WIDGETS/         # Widgets dashboard
|-- INDEX.md            # Point d'entree unique
`-- CONVENTION_DOCUMENTATION.md   # Ce document
```

### 03-PROJECT - Taxonomie

| Dossier / Emplacement | Contenu |
|-----------------------|---------|
| Racine `03-PROJECT/` | Documents actifs : reference, audits partiels, TODO, historique recent |
| `AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` | Audits dont **toutes** les recommandations sont appliquees |
| `AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` | Rapports situationnels, plans contextuels, recap de mission |
| `RAPPORTS_TEMPORAIRES/PHASES/` | Documentation de phases historiques |

---

## 2. Convention de nommage

### Prefixes par type de document

| Prefixe | Usage | Exemple |
|---------|-------|---------|
| `AUDIT_` | Audit technique (qualite, securite, performance) | `AUDIT_DASHBOARD_2026-02.md` |
| `ANALYSE_` | Analyse thematique (DRY, UX, themes) | `ANALYSE_THEMES_UX_2026-02.md` |
| `RAPPORT_` | Rapport situationnel, verification | `RAPPORT_VERIFICATION_CHALLENGES.md` |
| `EVALUATION_` | Evaluation globale, etat des lieux | `EVALUATION_PROJET_2026-02-07.md` |
| `INDEX_` | Index ou inventaire | `INDEX_DB_MANQUANTS_2026-02-06.md` |
| `PLAN_` | Plan d'action | `PLAN_ACTION_2026-02-06.md` |
| `RECAP_` | Recapitulatif | `RECAP_FINAL_2026-02-06.md` |

### Format de la date

- suffixe : `_YYYY-MM` ou `_YYYY-MM-DD`
- exemples : `AUDIT_DASHBOARD_2026-02.md`, `EVALUATION_PROJET_2026-02-07.md`

### Regles generales

- snake_case ou majuscules a underscore selon la convention deja dominante du dossier
- pas d'espaces dans les noms
- nom descriptif et stable

---

## 3. En-tete des documents

Chaque document projet devrait inclure en en-tete :

```markdown
# Titre du document

**Date :** Mois Annee
**Type :** Audit | Analyse | Rapport | Evaluation | Reference
**Statut :** Actif | Implemente | Archive | Obsolete | Historique

---
```

---

## 4. Deplacement des documents

### Quand archiver dans AUDITS_IMPLEMENTES ?

- toutes les recommandations de l'audit ont ete appliquees
- le document sert uniquement de trace historique

### Quand garder en racine 03-PROJECT ?

- audit avec recommandations partielles
- document de reference actuel
- TODO ou suivi encore vivant

### Quand mettre dans RAPPORTS_TEMPORAIRES ?

- recap de mission, plan d'action ponctuel
- rapport contextuel
- contexte historique sans suivi actif

---

## 5. Liens internes

- utiliser des chemins relatifs depuis le document courant
- verifier les liens apres tout deplacement
- pour une reference runtime transverse, ajouter un renvoi depuis `docs/INDEX.md`

---

## 6. Mise a jour

- **Document de reference** : mettre a jour des qu'une action impactante est realisee
- **Marquer obsolete** : si un document est remplace, ajouter en en-tete :
  ```markdown
  > ⚠️ OBSOLETE - Remplace par [Nouveau document](lien)
  ```
- **Reference runtime transverse** : si un document devient la source de verite multi-workloads ou multi-modules, il doit vivre dans `00-REFERENCE/` et citer le code avec des pointeurs `fichier:ligne`.
- **Snapshot de revue** : un audit ou une code review remplace par une reference stable ne doit pas etre supprime d'office ; il doit rester consultable comme historique et etre marque comme snapshot avec un renvoi explicite vers la reference active.

---

## 7. Revue periodique - verite terrain

### Frequence

- trimestrielle : au minimum 1 revue par trimestre
- a la livraison : verifier les docs de reference apres chaque release majeure

### Checklist (source de verite = code)

| Point | Fichier source | Ou corriger |
|-------|----------------|-------------|
| Nombre de routes API | `server/routes/` | README, README_TECH, docs referencant ce nombre |
| Versions frontend | `frontend/package.json` | README, README_TECH |
| Versions backend | `requirements.txt` | README, README_TECH |
| Modeles ORM | `app/models/` | README, docs de structure |
| Schemas Pydantic | `app/schemas/` | docs de structure |
| Handlers | `server/handlers/` | README, docs API |
| Gouvernance IA multi-workloads | `app/core/app_model_policy.py`, `app/core/ai_generation_policy.py`, `app/services/challenges/challenge_ai_model_policy.py`, `app/utils/token_tracker.py`, `app/utils/generation_metrics.py` | `00-REFERENCE/AI_MODEL_GOVERNANCE.md` |

### Principe

**Le code prime sur la documentation.** En cas d'incoherence, corriger la doc pour refleter la realite du code.

---

## 8. Index et navigation

- chaque sous-dossier d'archives dispose d'un `INDEX.md` ou est decrit dans le `README` parent
- `docs/INDEX.md` pointe vers les entrees cles
- `docs/03-PROJECT/README.md` est l'index maitre des audits et rapports

---

## 9. Principe d'archivage - projet entier

**Regle :** tout document d'audit, d'analyse ou de rapport passe, obsolete ou entierement implemente doit etre range dans `AUDITS_ET_RAPPORTS_ARCHIVES` ou marque explicitement historique s'il doit rester en racine pour contexte proche.

### Ou archiver ?

| Statut du document | Destination |
|-------------------|-------------|
| Audit - **toutes** les recommandations appliquees | `AUDITS_IMPLEMENTES/` |
| Rapport situationnel, plan execute, migration terminee | `RAPPORTS_TEMPORAIRES/` |
| Document remplace par une reference plus stable | garder si necessaire, mais marquer `⚠️ OBSOLETE` ou `snapshot historique` et renvoyer vers la reference active |

### Application au reste du projet

- `02-FEATURES`, `01-GUIDES`, `frontend/docs` : pas de sous-dossier archives dedie. Les docs obsoletees doivent etre soit fusionnees, soit marquees comme remplacees.
- principe unique : une seule source de verite par sujet ; les archives restent centralisees dans `03-PROJECT`.

### Frequence de rangement

- a chaque livraison majeure : verifier si des audits/plans peuvent etre archives
- revue trimestrielle : identifier les docs obsoletees et les classer correctement
