# Audit commit fixes frontend — 20/02/2026

## Contexte

Après merges Dependabot et problèmes en dev local (Turbopack, framer-motion, motion-dom), modifications locales pour stabiliser. La prod fonctionne. Ce document audite chaque changement avant commit pour garantir zéro régression.

---

## Modifications package.json

| Modification | Impact prod | Justification |
|--------------|-------------|---------------|
| `"dev": "next dev --webpack"` | **AUCUN** | Script dev uniquement. `npm run build` inchangé. |
| `@alloc/quick-lru` ajouté | Positif | Dépendance de @tailwindcss/postcss. Absence causait erreur build. |
| `framer-motion`: `^12.34.0` → `12.33.2` | **Correction** | 12.34.0 = paquet npm incomplet (proxy.mjs manquant). 12.33.2 = dernière version complète. |
| `motion-dom` en dep directe | Positif | Était transitive. Résolution Webpack plus fiable en dép directe. |
| ~~`@next/swc-win32-x64-msvc`~~ | **RETIRÉ** | Binaire Windows. Prod = Linux. Éviter bloat inutile. |

---

## Modifications next.config.ts

| Modification | Impact prod | Justification |
|--------------|-------------|---------------|
| `turbopack.root: path.resolve(__dirname)` | Neutre / positif | Build utilise Webpack. Si Turbopack utilisé un jour, root explicite évite bugs d'inférence. |
| Retrait `framer-motion` de `optimizePackageImports` | **Correction** | L'optimisation cassait la résolution de motion-dom. Retrait = stabilité. Léger impact bundle possible (quelques KB). |

---

## Dépendances : obsolètes ?

- **framer-motion 12.33.2** : Publié fév 2026. Version mineure avant 12.34.0 (cassée). **PAS obsolète**.
- **motion-dom ^12.34.3** : Aligné avec framer-motion 12.x. **PAS obsolète**.
- **@alloc/quick-lru ^5.2.0** : Utilisé par Tailwind. Actif. **PAS obsolète**.

---

## Checklist avant commit

- [ ] `npm ci` réussit
- [ ] `npm run build` réussit (simulation prod)
- [ ] Aucune dépendance obsolète introduite
- [ ] @next/swc-win32 retiré (Windows-only)
