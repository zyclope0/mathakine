# Analyse dépendances — 20/02/2026

## Dependabot (config actuelle)

- **pip** : hebdo, lundi, max 5 PR ouvertes
- **npm** (frontend) : hebdo, lundi, max 5 PR, groupes `react` et `next`
- **github-actions** : mensuel

⚠️ **Dependabot ne se lance pas manuellement** — il s'exécute selon le schedule GitHub. Prochain cycle : lundi.

**État** : 0 PR Dependabot ouvertes (37 fermées/mergées).

---

## Backend (pip) — pip-audit

| Package | Version | CVE | Fix |
|---------|---------|-----|-----|
| cryptography | 46.0.3 | CVE-2026-26007 | 46.0.5 |
| ecdsa | 0.19.1 | CVE-2024-23342 | (vérifier) |
| pillow | 12.1.0 | CVE-2026-25990 | 12.1.1 ✅ dans requirements |
| pyasn1 | 0.6.1 | CVE-2026-23490 | 0.6.2 |

**Actions** : `pip install --upgrade cryptography pillow pyasn1` puis mettre à jour requirements.txt si versions fixées.

---

## Frontend (npm) — npm audit

**34 vulnérabilités** (1 modérée, 33 élevées).

### Corrections possibles sans breaking

| Package | Problème | Action |
|---------|----------|--------|
| jspdf | ≤4.1.0 — PDF Injection, DoS | `npm audit fix` (met à jour jspdf) |

### Dépendances transitives (complexes)

- **ajv** (ReDoS) — via eslint, typescript-eslint. Fix = downgrade eslint → breaking.
- **minimatch** (ReDoS) — Sentry, eslint-config-next, next-pwa, exceljs. Pas de fix direct.
- **glob** — idem, chaîne longue.

### Recommandation MVP

1. **Immédiat** : `npm audit fix` (jspdf uniquement, sans --force)
2. **Surveiller** : GitHub Dependabot (onglet Security → Dependabot alerts)
3. **Post-MVP** : Évaluer migration next-pwa → alternative ou attente fix workbox

---

## Priorité par risque

| Priorité | Domaine | Action |
|----------|---------|--------|
| P1 | pip: cryptography, pyasn1 | Mise à jour manuelle |
| P2 | npm: jspdf | `npm audit fix` |
| P3 | pip: ecdsa | Vérifier correctif dispo |
| P4 | npm: chaîne eslint/minimatch | Attendre Dependabot ou correctifs upstream |
