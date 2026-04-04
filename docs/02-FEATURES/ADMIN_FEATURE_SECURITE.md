# Feature Admin — Exigences de sécurité (RBAC)

> **Date** : 15/02/2026  
> **À consulter** avant toute implémentation d'endpoints admin

---

## 1. Contexte

La feature **Admin** est prévue dans la roadmap. Les endpoints admin exposent des actions sensibles (gestion utilisateurs, modération, statistiques globales, etc.). Ils **doivent** être protégés par un contrôle d'accès basé sur les rôles (RBAC).

---

## 2. Obligation : décorateur `require_role` / `require_admin`

**Pour tout endpoint admin ajouté à l'avenir**, il faudra impérativement :

1. **Appliquer** `@require_admin` (ou `@require_role("admin")`) sur chaque handler admin
2. **Ne jamais** se fier uniquement à `@require_auth` pour les routes admin

> **Note** : Le contrat admin canonique expose le role `admin`.
> La base conserve encore l'alias legacy `archiviste` pendant la migration,
> mais les handlers et payloads doivent raisonner en role canonique.

### Exemple à suivre

```python
# server/auth.py
from app.utils.error_handler import api_error_response

def require_role(role: str):
    """Decorateur qui exige un role canonique specifique (ex: admin)."""
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            current_user = await get_current_user(request)
            if not current_user or not current_user.get("is_authenticated"):
                return api_error_response(401, "Authentification requise")
            if current_user.get("role") != role:
                return api_error_response(403, "Droits insuffisants")
            request.state.user = current_user
            return await handler(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage
@require_auth
@require_admin
async def admin_promote_user(request):
    ...
```

---

## 3. État actuel

| Élément                 | Statut                                                                                                                |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `require_auth`          | ✅ Existe (auth basique)                                                                                              |
| `require_role`          | ✅ Implémenté dans `server/auth.py`                                                                                   |
| `require_admin`         | ✅ Alias `require_role("admin")`                                                                                      |
| Modèle `User.role`      | ✅ DB legacy `padawan, maitre, gardien, archiviste` + exposition canonique `apprenant, enseignant, moderateur, admin` |
| Vérification rôle admin | ✅ Appliquée sur tous les endpoints `/api/admin/*`                                                                    |

---

## 4. Référence

- **Proposition détaillée** : [ADMIN_ESPACE_PROPOSITION.md](ADMIN_ESPACE_PROPOSITION.md) — Benchmark, périmètre, plan d'implémentation
- Audit sécurité : Validation & Input Sanitization (2.2 RBAC)
- Nomenclature canonique : `docs/00-REFERENCE/USER_ROLE_NOMENCLATURE.md`
- Modèle : `app/models/user.py` → `UserRole` (stockage legacy), normalisé par `app/core/user_roles.py`
- Auth : `server/auth.py`
