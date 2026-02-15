# Feature Admin — Exigences de sécurité (RBAC)

> **Date** : 15/02/2026  
> **À consulter** avant toute implémentation d'endpoints admin

---

## 1. Contexte

La feature **Admin** est prévue dans la roadmap. Les endpoints admin exposent des actions sensibles (gestion utilisateurs, modération, statistiques globales, etc.). Ils **doivent** être protégés par un contrôle d'accès basé sur les rôles (RBAC).

---

## 2. Obligation : décorateur `require_role("admin")`

**Pour tout endpoint admin ajouté à l'avenir**, il faudra impérativement :

1. **Implémenter** un décorateur `require_role(role)` dans `server/auth.py`
2. **Appliquer** `@require_role("admin")` sur chaque handler admin
3. **Ne jamais** se fier uniquement à `@require_auth` pour les routes admin

### Exemple à suivre

```python
# server/auth.py
def require_role(role: str):
    """Décorateur qui exige un rôle spécifique (ex: admin)."""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            current_user = await get_current_user(request)
            if not current_user or not current_user.get("is_authenticated"):
                return JSONResponse(
                    {"error": "Authentification requise"},
                    status_code=401
                )
            if current_user.get("role") != role:
                return JSONResponse(
                    {"error": "Droits insuffisants"},
                    status_code=403
                )
            request.state.user = current_user
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@app.post("/api/admin/users/{user_id}/promote")
@require_auth
@require_role("admin")
async def admin_promote_user(request):
    ...
```

---

## 3. État actuel

| Élément                    | Statut                            |
|---------------------------|-----------------------------------|
| `require_auth`            | ✅ Existe (auth basique)          |
| `require_role`            | ❌ **À implémenter** avec la feature admin |
| Modèle `User.role`        | ✅ Existe (padawan, maitre, gardien, archiviste) |
| Vérification rôle admin   | ❌ Non utilisée actuellement      |

---

## 4. Référence

- **Proposition détaillée** : [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md) — Benchmark, périmètre, plan d'implémentation
- Audit sécurité : Validation & Input Sanitization (2.2 RBAC)
- Modèle : `app/models/user.py` → `UserRole` (archiviste = accès admin complet)
- Auth : `server/auth.py`
