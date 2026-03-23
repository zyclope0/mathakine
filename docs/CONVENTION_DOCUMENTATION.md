# Convention de documentation Mathakine

> Regles de structure, nommage et maintenance des documents projet
> Version : 1.2 - 23/03/2026

---

## 1. Taxonomie reelle du repo

```text
docs/
|-- 00-REFERENCE/        # References transversales vivantes
|-- 01-GUIDES/           # Guides pratiques (dev, test, deploiement, runbook)
|-- 02-FEATURES/         # Specs produit, references de feature, backlog
|-- 03-PROJECT/          # Pilotage, audits, bilans, suivi projet
|-- 04-FRONTEND/         # Documentation frontend vivante
|-- 05-ADR/              # Architecture Decision Records
|-- 06-WIDGETS/          # Compatibilite legacy - redirects uniquement
|-- assets/              # Artefacts documentaires non-Markdown
|-- INDEX.md             # Point d'entree global
`-- CONVENTION_DOCUMENTATION.md
```

### Hors `docs/`

Les workspaces de generation de livrables (ex: deck investisseurs, scripts PPTX, mini-projets Node) ne doivent pas vivre dans `docs/`.
Emplacement recommande : `presentations/`, `tools/` ou un dossier metier dedie.

---

## 2. Ou mettre quel document ?

| Type | Emplacement canonique | Exemple |
|------|------------------------|---------|
| Reference runtime transverse | `00-REFERENCE/` | `AI_MODEL_GOVERNANCE.md` |
| Guide operatoire / dev | `01-GUIDES/` | `TESTING.md`, `PRODUCTION_RUNBOOK.md` |
| Reference ou spec de feature | `02-FEATURES/` | `AUTH_FLOW.md`, `F02_DEFIS_QUOTIDIENS.md` |
| Pilotage / audit / bilan / suivi | `03-PROJECT/` | `PILOTAGE_*`, `AUDIT_*`, `BILAN_*`, `POINTS_*` |
| Reference frontend | `04-FRONTEND/` | `ARCHITECTURE.md`, `DASHBOARD_WIDGETS/` |
| Decision d'architecture | `05-ADR/` | `ADR-001-starlette-vs-fastapi.md` |
| Prototype ou asset de doc | `assets/` | `assets/prototypes/F34_SCIENCES_PROTOTYPE.html` |

### Cas legacy explicites

- `06-WIDGETS/` : ne sert plus qu'a rediriger vers `04-FRONTEND/DASHBOARD_WIDGETS/`
- `03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/` : collection legacy conservee pour compatibilite historique ; aucun nouveau document ne doit y etre cree
- archive canonique active : `03-PROJECT/archives/`

---

## 3. Nommage des documents

### Principe

La nomenclature doit refleter les familles reelles du repo. Ne pas imposer une liste de prefixes trop etroite si le projet utilise deja des familles stables plus larges.

### Familles courantes autorisees

| Prefixe | Usage |
|---------|-------|
| `README` | point d'entree local d'un dossier |
| `AUDIT_` | audit technique / qualite / securite |
| `ANALYSE_` | analyse thematique |
| `BILAN_` | recapitulatif d'etat ou de cloture |
| `CLOTURE_` | cloture de lot / audit |
| `IMPLEMENTATION_` | note d'implementation d'une feature |
| `PILOTAGE_` | pilotage de lot, sequence de travail, ledger projet |
| `POINTS_` | reste a faire / suivis residuels |
| `POLITIQUE_` | regle transverse durable |
| `RECOMMENDATION_` | sequence recommandation / iteration R |
| `ADR-` | decision d'architecture versionnee |

### Regles generales

- pas d'espaces dans les noms
- suffixe date recommande pour les snapshots ou bilans : `_YYYY-MM` ou `_YYYY-MM-DD`
- utiliser un nom descriptif stable plutot qu'un prefixe artificiel
- eviter les artefacts mal orthographies ou ambigus (`REFACTO_`, `REFACTO` vs `REFACTOR_`) pour les nouveaux documents

---

## 4. Archives projet

### Archive canonique

Le dossier canonique pour les archives projet est :
- `docs/03-PROJECT/archives/`

### Collection legacy

Le dossier suivant est conserve pour compatibilite historique :
- `docs/03-PROJECT/AUDITS_ET_RAPPORTS_ARCHIVES/`

Regle stricte :
- ne plus y creer de nouveaux documents
- si un nouveau document doit etre archive, il va dans `docs/03-PROJECT/archives/`

### Quand archiver ?

- audit entierement applique -> archive
- plan execute ou note ponctuelle close -> archive
- document remplace par une reference plus stable -> conserver si utile, mais marquer obsolete ou snapshot historique

---

## 5. Navigation

- chaque dossier vivant devrait idealement avoir un `README.md` si cela simplifie l'entree d'un lecteur externe
- `docs/INDEX.md` doit rester un portail de navigation, pas un journal de run local
- les details historiques et baselines de lot appartiennent a `docs/03-PROJECT/`
- les liens internes doivent etre relatifs au document courant

---

## 6. Mise a jour et verite terrain

- le code actif prime toujours sur la doc
- `server/routes/` reste la verite des endpoints actifs
- les references runtime transverses doivent vivre dans `00-REFERENCE/`
- les audits et code reviews remplaces par une reference plus stable doivent rester accessibles comme historique, avec un renvoi clair

---

## 7. Anti-patterns interdits

- stocker un mini-projet applicatif complet dans `docs/`
- laisser une structure de dossier fantome documentee mais vide sans le dire explicitement
- disperser la meme source de verite entre plusieurs dossiers concurrents
- garder un dossier legacy actif alors qu'un emplacement canonique le remplace deja
