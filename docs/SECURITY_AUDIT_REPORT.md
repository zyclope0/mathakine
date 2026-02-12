# Rapport d'audit de sécurité — Mathakine

**Date :** 12 février 2026

---

## 1. Vulnérabilités de l'audit initial

### Next.js (CVE-2025-59471, CVE-2025-59472, CVE-2026-23864)

| Élément        | Statut |
|----------------|--------|
| Version actuelle | **16.1.6** |
| Version minimale recommandée | 16.1.5+ |
| Résultat       | OK — version déjà corrigée |

### Requests (CVE-2024-47081)

| Élément        | Statut |
|----------------|--------|
| Version actuelle | **2.32.5** |
| Version minimale recommandée | 2.32.4+ |
| Résultat       | OK — version déjà corrigée |

### Jinja2

| Élément        | Statut |
|----------------|--------|
| Version actuelle | **3.1.6** |
| Version minimale recommandée | 3.1.6 |
| Résultat       | OK — version déjà corrigée |

---

## 2. npm audit (frontend)

```
found 0 vulnerabilities
```

Aucune vulnérabilité détectée dans les dépendances npm.

---

## 3. pip-audit (backend Python)

**Vulnérabilités supplémentaires détectées :**

| Package      | Version actuelle | CVE           | Correction |
|--------------|------------------|---------------|------------|
| cryptography | 46.0.3           | CVE-2026-26007 | 46.0.5+    |
| ecdsa        | 0.19.1           | CVE-2024-23342 | —          |
| pillow       | 12.1.0           | CVE-2026-25990 | 12.1.1+    |
| pip          | 25.2             | CVE-2025-8869, CVE-2026-1703 | 25.3+ ou 26.0 |
| pyasn1       | 0.6.1            | CVE-2026-23490 | 0.6.2+     |

*Note : `cryptography`, `ecdsa` et `pyasn1` sont des dépendances transitives (ex. via `python-jose`).*

---

## Actions recommandées

1. Next.js, Requests, Jinja2 : aucune action requise.
2. Mettre à jour `pillow` dans `requirements.txt` : `pillow>=12.1.1`.
3. Mettre à jour `pip` : `pip install --upgrade pip`.
4. Pour les dépendances transitives : vérifier les mises à jour de `python-jose` / `cryptography`.
