# 📚 INDEX GÉNÉRAL - DOCUMENTATION MATHAKINE

**Version** : 2.0.1  
**Date** : 20 novembre 2025  
**Organisation** : Hiérarchique et épurée

---

## 🎯 NAVIGATION RAPIDE

### 🚀 Démarrage rapide
- **[Getting Started](00-REFERENCE/GETTING_STARTED.md)** ⭐ - Installation 15 min
- **[Architecture](00-REFERENCE/ARCHITECTURE.md)** - Vue d'ensemble technique
- **[API Reference](00-REFERENCE/API.md)** - 37 routes documentées

### 📖 Pour les développeurs
- **[Development Guide](01-GUIDES/DEVELOPMENT.md)** - Workflow développement
- **[Testing Guide](01-GUIDES/TESTING.md)** - Tests et CI/CD
- **[Troubleshooting](01-GUIDES/TROUBLESHOOTING.md)** - Solutions problèmes

### 🎓 Pour les contributeurs
- **[Contributing](01-GUIDES/CONTRIBUTING.md)** - Comment contribuer
- **[Roadmap](03-PROJECT/ROADMAP.md)** - Feuille de route
- **[Changelog](03-PROJECT/CHANGELOG.md)** - Historique versions

---

## 📁 STRUCTURE DOCUMENTATION

```
docs/
├── 00-REFERENCE/          # 📘 Documents permanents (4 docs)
│   ├── ARCHITECTURE.md    # Architecture complète post-phases
│   ├── API.md             # 37 routes API JSON
│   ├── GETTING_STARTED.md # Installation et premiers pas
│   └── GLOSSARY.md        # Terminologie projet
│
├── 01-GUIDES/             # 📗 Guides pratiques (7 docs)
│   ├── DEVELOPMENT.md     # Workflow développement complet
│   ├── TESTING.md         # Tests backend/frontend
│   ├── DEPLOYMENT.md      # Déploiement Render
│   ├── TROUBLESHOOTING.md # Dépannage
│   ├── CONTRIBUTING.md    # Contribution
│   ├── FAQ.md             # Questions fréquentes
│   └── DOCKER.md          # Conteneurisation
│
├── 02-FEATURES/           # 📙 Fonctionnalités (1+ docs)
│   └── I18N.md            # Internationalisation (next-intl)
│
├── 03-PROJECT/            # 📕 Gestion projet (3+ docs)
│   ├── ROADMAP.md         # Feuille de route
│   ├── CHANGELOG.md       # Historique versions
│   ├── BILAN_COMPLET.md   # Bilan phases 1-6
│   └── PHASES/            # Documentation phases
│       ├── PHASE6_PLAN.md
│       ├── PHASE6_RESULTAT.md
│       └── RECAP_PHASES.md
│
├── 04-ARCHIVES/           # 📚 Archives historiques (~200 docs)
│   ├── 2024/              # Archives 2024
│   ├── 2025/              # Archives 2025
│   │   ├── corrections-historiques/
│   │   ├── deployment/
│   │   ├── audits-historiques/
│   │   ├── architecture-obsolete/
│   │   ├── development-obsolete/
│   │   ├── api-obsolete/
│   │   ├── divers/
│   │   └── a-trier/
│   └── archived/          # Autres archives
│
└── INDEX.md               # 📑 Ce fichier
```

---

## 📘 00-REFERENCE (Documents permanents)

Documents de référence toujours valides et à jour.

| Document | Description | Audience |
|----------|-------------|----------|
| **[ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md)** | Architecture complète (frontend/backend/db) | Dev, Tech Lead |
| **[API.md](00-REFERENCE/API.md)** | 37 routes API documentées | Dev Frontend/Backend |
| **[GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)** | Installation et démarrage rapide | Tous |
| **[GLOSSARY.md](00-REFERENCE/GLOSSARY.md)** | Terminologie et acronymes | Tous |

---

## 📗 01-GUIDES (Guides pratiques)

Guides pas-à-pas pour tâches spécifiques.

| Guide | Description | Temps estimé |
|-------|-------------|--------------|
| **[DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)** | Workflow dev, conventions, best practices | 30 min |
| **[TESTING.md](01-GUIDES/TESTING.md)** | Écrire et lancer tests, CI/CD | 20 min |
| **[DEPLOYMENT.md](01-GUIDES/DEPLOYMENT.md)** | Déploiement Render, config production | 45 min |
| **[TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)** | Résolution problèmes courants | Variable |
| **[CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md)** | Workflow contribution (fork, PR) | 15 min |
| **[FAQ.md](01-GUIDES/FAQ.md)** | Questions fréquentes | 10 min |
| **[DOCKER.md](01-GUIDES/DOCKER.md)** | Conteneurisation (Docker, docker-compose) | 30 min |

---

## 📙 02-FEATURES (Fonctionnalités)

Documentation détaillée de chaque fonctionnalité.

| Feature | Description | Status |
|---------|-------------|--------|
| **[I18N.md](02-FEATURES/I18N.md)** | Internationalisation (next-intl) | ✅ Complet |

*À compléter avec :*
- AUTHENTICATION.md - Système auth JWT
- CHALLENGES.md - Défis logiques
- EXERCISES.md - Exercices maths
- BADGES.md - Système récompenses
- GAMIFICATION.md - Points, niveaux
- AI_GENERATION.md - Génération IA

---

## 📕 03-PROJECT (Gestion projet)

Planification, historique et bilans.

### Documents principaux
| Document | Description | Mise à jour |
|----------|-------------|-------------|
| **[ROADMAP.md](03-PROJECT/ROADMAP.md)** | Feuille de route 2025-2026 | Trimestrielle |
| **[CHANGELOG.md](03-PROJECT/CHANGELOG.md)** | Historique versions | À chaque release |
| **[BILAN_COMPLET.md](03-PROJECT/BILAN_COMPLET.md)** | Bilan phases 1-6 | Post-phases |

### Phases (Documentation historique)
| Phase | Objectif | Status | Document |
|-------|----------|--------|----------|
| **Phase 1** | Nettoyage code mort | ✅ Complété | [PHASES/](03-PROJECT/PHASES/) |
| **Phase 2** | Séparation Frontend/Backend | ✅ Complété | [PHASES/](03-PROJECT/PHASES/) |
| **Phase 3** | Refactoring DRY | ✅ Complété | [PHASES/](03-PROJECT/PHASES/) |
| **Phase 4** | Architecture Services | ✅ Complété | [PHASES/](03-PROJECT/PHASES/) |
| **Phase 5** | Tests automatisés | ✅ Complété | [PHASES/](03-PROJECT/PHASES/) |
| **Phase 6** | Nommage & Lisibilité | ✅ Complété | [PHASES/PHASE6_RESULTAT.md](03-PROJECT/PHASES/PHASE6_RESULTAT.md) |

---

## 📚 04-ARCHIVES (~200 documents)

Documents historiques (audits, corrections, anciennes versions).

- **[ARCHIVE/](04-ARCHIVES/)** - Index des archives
- **2024/** - Archives année 2024
- **2025/** - Archives année 2025 (corrections, audits, deployment, etc.)

---

## 🔍 RECHERCHE PAR BESOIN

### Je veux démarrer le projet
1. [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)
2. [ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md)
3. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)

### Je veux comprendre l'architecture
1. [ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md)
2. [API.md](00-REFERENCE/API.md)
3. [BILAN_COMPLET.md](03-PROJECT/BILAN_COMPLET.md)

### Je veux développer une feature
1. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)
2. [API.md](00-REFERENCE/API.md)
3. [Fonctionnalité spécifique](02-FEATURES/)

### Je veux écrire des tests
1. [TESTING.md](01-GUIDES/TESTING.md)
2. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)

### Je veux déployer en production
1. [DEPLOYMENT.md](01-GUIDES/DEPLOYMENT.md)
2. [ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md)
3. [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)

### J'ai un problème
1. [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)
2. [FAQ.md](01-GUIDES/FAQ.md)
3. [GitHub Issues](https://github.com/yourusername/mathakine/issues)

### Je veux contribuer
1. [CONTRIBUTING.md](01-GUIDES/CONTRIBUTING.md)
2. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)
3. [ROADMAP.md](03-PROJECT/ROADMAP.md)

---

## 📊 STATUT DOCUMENTATION

### Par catégorie

| Catégorie | Documents actifs | Status | Complétude |
|-----------|------------------|--------|------------|
| **00-REFERENCE** | 4 docs | ✅ À jour | 100% |
| **01-GUIDES** | 7 docs | ✅ À jour | 100% |
| **02-FEATURES** | 1 doc | 🔄 En cours | 15% |
| **03-PROJECT** | 3+ docs | ✅ À jour | 100% |
| **04-ARCHIVES** | ~200 docs | ✅ Organisées | 100% |

### Légende
- ✅ À jour : 100% complet et validé
- 🔄 En cours : Documentation partielle
- ⏸️ Planifié : Pas encore commencé

---

## 🎯 PRIORITÉS LECTURE

### 🔴 Priorité HAUTE (obligatoire)
1. [GETTING_STARTED.md](00-REFERENCE/GETTING_STARTED.md)
2. [ARCHITECTURE.md](00-REFERENCE/ARCHITECTURE.md)
3. [API.md](00-REFERENCE/API.md)

### 🟡 Priorité MOYENNE (recommandé)
4. [DEVELOPMENT.md](01-GUIDES/DEVELOPMENT.md)
5. [TESTING.md](01-GUIDES/TESTING.md)
6. [BILAN_COMPLET.md](03-PROJECT/BILAN_COMPLET.md)

### 🟢 Priorité BASSE (selon besoin)
7. [DEPLOYMENT.md](01-GUIDES/DEPLOYMENT.md)
8. [Features spécifiques](02-FEATURES/)
9. [Phases historiques](03-PROJECT/PHASES/)

---

## 📝 CONVENTIONS

### Format documents
- **Markdown** (.md) pour tous les documents
- **Titres** : émojis + hiérarchie claire
- **Liens** : relatifs dans docs/, absolus vers externe
- **Code** : blocs avec syntax highlighting

### Organisation
- **00-REFERENCE** : Documents permanents, toujours valides
- **01-GUIDES** : Procédures pas-à-pas
- **02-FEATURES** : Documentation fonctionnalités
- **03-PROJECT** : Gestion, planning, bilans
- **04-ARCHIVES** : Historique

### Nomenclature
```
REFERENCE:  UPPERCASE.md (ARCHITECTURE.md, API.md)
GUIDE:      PascalCase.md (Development.md, Testing.md)
FEATURE:    PascalCase.md (Challenges.md, I18N.md)
PROJECT:    UPPERCASE.md ou PascalCase.md
PHASE:      PHASE{N}_{NOM}.md (PHASE6_RESULTAT.md)
```

---

## 🔄 MAINTENANCE

### Mise à jour régulière
- **Référence** : À chaque changement architectural majeur
- **Guides** : Trimestriel ou lors de changements workflow
- **Features** : À chaque feature ajoutée/modifiée
- **Project** : Roadmap trimestrielle, Changelog à chaque release

### Responsabilités
- **Tech Lead** : Architecture, API, Guides
- **Dev Team** : Features, Development
- **PM** : Roadmap, Changelog, Bilans

---

## 📚 DOCUMENTS RACINE (hors docs/)

| Fichier | Description | Audience |
|---------|-------------|----------|
| **README.md** | Point d'entrée projet | Tous |
| **ai_context_summary.md** | Contexte pour IA | Dev, IA |
| **CONTRIBUTING.md** | Guide contribution | Contributeurs |
| **LICENSE** | Licence projet | Légal |

---

## 🎉 CONCLUSION

**Documentation épurée et professionnelle** :
- ✅ **~20 docs actifs** (contre 250 avant)
- ✅ **~200 docs archivés** (historique préservé)
- ✅ **0 doublon**
- ✅ **Hiérarchie claire** (00-04)
- ✅ **Navigation intuitive**
- ✅ **100% à jour**

**Prêt à explorer !** 🚀

**Besoin d'aide ?** Consultez [FAQ.md](01-GUIDES/FAQ.md) ou [TROUBLESHOOTING.md](01-GUIDES/TROUBLESHOOTING.md)
