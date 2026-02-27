# Convention de documentation Mathakine

> Règles de nommage, structure et maintenance des documents projet  
> **Version :** 1.0 — 15/02/2026

---

## Récapitulatif — Où mettre quel document ?

| Type | Emplacement | Exemple |
|------|-------------|---------|
| **Audit — toutes recos appliquées** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` | ANALYSE_THEMES_UX |
| **Audit — recos partielles** | `03-PROJECT/` (racine) | AUDIT_DASHBOARD |
| **Rapport situationnel** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` | DEPLOIEMENT_2026, MISSION_COMPLETE |
| **Référence actuelle / CI-CD** | `03-PROJECT/` (racine) | EVALUATION_PROJET, CICD_DEPLOY |
| **À faire / TODO** | `03-PROJECT/` (racine) | ENDPOINTS_NON_INTEGRES |

---

## 1. Structure des dossiers

```
docs/
├── 00-REFERENCE/       # Référence technique (installation, etc.)
├── 01-GUIDES/          # Guides pratiques (dev, test, déploiement)
├── 02-FEATURES/        # Documentation fonctionnalités
├── 03-PROJECT/         # Gestion projet — audits, rapports, évaluations
├── 06-WIDGETS/         # Widgets dashboard
├── INDEX.md            # Point d'entrée unique
└── CONVENTION_DOCUMENTATION.md   # Ce document
```

### 03-PROJECT — Taxonomie

| Dossier / Emplacement | Contenu |
|-----------------------|---------|
| Racine `03-PROJECT/` | Documents actifs : référence, audits partiels, à faire, historique |
| `AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` | Audits dont **toutes** les recommandations sont appliquées |
| `AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` | Rapports situationnels (récaps mission, plans contextuels) |
| `RAPPORTS_TEMPORAIRES/PHASES/` | Documentation phases historiques |

---

## 2. Convention de nommage

### Préfixes par type de document

| Préfixe | Usage | Exemple |
|---------|-------|---------|
| `AUDIT_` | Audit technique (qualité, sécurité, performance) | `AUDIT_DASHBOARD_2026-02.md` |
| `ANALYSE_` | Analyse thématique (DRY, UX, thèmes) | `ANALYSE_THEMES_UX_2026-02.md` |
| `RAPPORT_` | Rapport situationnel, vérification | `RAPPORT_VERIFICATION_CHALLENGES.md` |
| `EVALUATION_` | Évaluation globale, état des lieux | `EVALUATION_PROJET_2026-02-07.md` |
| `INDEX_` | Index ou inventaire (ex. DB) | `INDEX_DB_MANQUANTS_2026-02-06.md` |
| `PLAN_` | Plan d'action | `PLAN_ACTION_2026-02-06.md` |
| `RECAP_` | Récapitulatif | `RECAP_FINAL_2026-02-06.md` |

### Format de la date

- Suffixe : `_YYYY-MM` ou `_YYYY-MM-DD`
- Exemples : `AUDIT_DASHBOARD_2026-02.md`, `EVALUATION_PROJET_2026-02-07.md`

### Règles générales

- **Snake_case** pour les noms de fichiers
- **Pas d'espaces** dans les noms
- **Descriptif** : le nom doit indiquer le sujet

---

## 3. En-tête des documents (front matter)

Chaque document projet devrait inclure en en-tête :

```markdown
# Titre du document

**Date :** Mois Année (ex. Février 2026)
**Type :** Audit | Analyse | Rapport | Évaluation
**Statut :** Actif | Implémenté | Archivé | Obsolète

---
```

---

## 4. Déplacement des documents

### Quand archiver dans AUDITS_IMPLEMENTES ?

- Toutes les recommandations de l'audit ont été appliquées
- Le document sert de trace/historique

### Quand garder en racine 03-PROJECT ?

- Audit avec recommandations partielles
- Document de référence actuel
- À faire / TODO

### Quand mettre dans RAPPORTS_TEMPORAIRES ?

- Récap de mission, plan d'action ponctuel
- Rapport contextuel (ex. migration index DB)
- Contexte historique, pas de suivi actif

---

## 5. Liens internes

- Utiliser des **chemins relatifs** depuis le document courant
- Exemple depuis `RAPPORTS_TEMPORAIRES/` vers `03-PROJECT/` : `../../EVALUATION_PROJET_2026-02-07.md`
- Vérifier les liens après tout déplacement

---

## 6. Mise à jour

- **Document de référence** : mettre à jour dès qu'une action impactante est réalisée
- **Marquer obsolète** : si un document est remplacé, ajouter en en-tête :
  ```markdown
  > **⚠️ OBSOLÈTE** — Remplacé par [Nouveau document](lien)
  ```

---

## 7. Revue périodique — vérité terrain

L'accumulation de rapports historiques rend la maintenance difficile sans processus de revue. Pour garder la documentation alignée avec le code :

### Fréquence

- **Trimestrielle** : au minimum 1 revue par trimestre (Fév., Mai, Août, Nov.)
- **À la livraison** : vérifier les docs de référence après chaque release majeure

### Checklist (source de vérité = code)

| Point | Fichier source | Où corriger |
|-------|----------------|-------------|
| Nombre de routes API | `server/routes.py` (`get_routes()`) | README, README_TECH, docs référençant ce nombre |
| Versions frontend | `frontend/package.json` (react, @tanstack/react-query, next-intl, framer-motion) | README § Stack technique |
| Versions backend | `requirements.txt` (openai, sqlalchemy, starlette) | README, README_TECH |
| Modèles ORM | `app/models/all_models.py` | README § Structure (nombre d'entités) |
| Handlers | `server/handlers/` (fichiers .py) | README § Structure |

### Principe

**Le code prime sur la documentation.** En cas d'incohérence, corriger la doc pour refléter la réalité du code.

---

## 8. Index et navigation

- Chaque sous-dossier d'archives dispose d'un **INDEX.md** ou est décrit dans le **README** parent
- Le [INDEX.md](INDEX.md) principal pointe vers les entrées clés
- Le [03-PROJECT/README.md](03-PROJECT/README.md) est l'index maître des audits et rapports

---

## 9. Principe d'archivage — projet entier

**Règle :** Tout document d'audit, d'analyse ou de rapport **passé, obsolète ou entièrement implémenté** doit être rangé dans `AUDITS_ET_RAPPORTS_ARCHIVES` (et non laissé en racine).

### Où archiver ?

| Statut du document | Destination |
|-------------------|-------------|
| Audit — **toutes** les recommandations appliquées | `AUDITS_IMPLEMENTES/` |
| Rapport situationnel, plan exécuté, migration terminée | `RAPPORTS_TEMPORAIRES/` |
| Document remplacé par un autre (ex. PLAN_ACTION → EVALUATION_PROJET) | `RAPPORTS_TEMPORAIRES/` (marquer obsolète) |

### Application au reste du projet

- **02-FEATURES, 01-GUIDES, frontend/docs** : Pas de sous-dossier archives dédié. Les docs obsolètes :
  - Soit sont fusionnés/supprimés si redondants avec un doc unique (ex. README_TECH)
  - Soit déplacés vers `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` si ce sont des rapports ou audits projet
- **Principe unique** : Une seule source de vérité par sujet ; archives centralisées dans `03-PROJECT`.

### Fréquence de rangement

- À chaque livraison majeure : vérifier si des audits/plans peuvent être archivés
- Revue trimestrielle (§7) : identifier les docs obsolètes et les archiver
