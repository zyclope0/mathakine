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

**État au 12/02/2026 — corrections appliquées le 15/02/2026 :**

| Package      | Version actuelle | CVE           | Correction | Statut     |
|--------------|------------------|---------------|------------|------------|
| cryptography | 46.0.3           | CVE-2026-26007 | 46.0.5+    | À vérifier |
| ecdsa        | 0.19.1           | CVE-2024-23342 | —          | Transitive |
| pillow       | 12.1.1           | CVE-2026-25990 | 12.1.1+    | ✅ Corrigé |
| pip          | (env)            | CVE-2025-8869, CVE-2026-1703 | 25.3+ | CI : `pip install --upgrade pip` |
| pyasn1       | 0.6.1            | CVE-2026-23490 | 0.6.2+     | Transitive |

*Note : `cryptography`, `ecdsa` et `pyasn1` sont des dépendances transitives (ex. via `python-jose`). pip n'est pas dans requirements.txt ; la CI exécute `pip install --upgrade pip` avant chaque build.*

---

## Actions recommandées

1. Next.js, Requests, Jinja2 : aucune action requise. ✅
2. ~~Pillow~~ : `pillow==12.1.1` déjà dans `requirements.txt`. ✅
3. pip : version variable selon l'environnement (Render, CI). S'assurer que les images de build utilisent `pip install --upgrade pip` (déjà en place en CI).
4. Pour les dépendances transitives : vérifier les mises à jour de `python-jose` / `cryptography`.
