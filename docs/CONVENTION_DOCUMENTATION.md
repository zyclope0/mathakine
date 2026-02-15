# Convention de documentation Mathakine

> Règles de nommage, structure et maintenance des documents projet  
> **Version :** 1.0 — 15/02/2026

---

## Récapitulatif — Où mettre quel document ?

| Type | Emplacement | Exemple |
|------|-------------|---------|
| **Audit — toutes recos appliquées** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/AUDITS_IMPLEMENTES/` | ANALYSE_THEMES_UX |
| **Audit — recos partielles** | `03-PROJECT/` (racine) | AUDIT_DASHBOARD |
| **Rapport situationnel** | `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/RAPPORTS_TEMPORAIRES/` | MISSION_COMPLETE |
| **Référence actuelle** | `03-PROJECT/` (racine) | EVALUATION_PROJET |
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
| `PHASES/` | Documentation phases historiques |

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

## 7. Index et navigation

- Chaque sous-dossier d'archives dispose d'un **INDEX.md** ou est décrit dans le **README** parent
- Le [INDEX.md](INDEX.md) principal pointe vers les entrées clés
- Le [03-PROJECT/README.md](03-PROJECT/README.md) est l'index maître des audits et rapports
