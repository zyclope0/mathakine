# Feature Admin - Exigences de securite (RBAC)

> Date : 2026-02-15
> A consulter avant toute implementation d'endpoint admin

---

## Contexte

La surface admin expose des operations sensibles :

- gestion utilisateurs
- moderation
- statistiques globales
- configuration

Ces endpoints doivent etre proteges par un controle d'acces par role.

---

## Regle obligatoire

Pour tout endpoint admin :

1. appliquer `@require_admin` ou `@require_role("admin")`
2. ne jamais se reposer uniquement sur `@require_auth`

Le role canonique cote frontend/backend est `admin`.
L'alias legacy `archiviste` peut encore exister en DB, mais il ne doit plus etre la verite de contrat.

---

## Etat actuel

| Element                 | Statut                                     |
| ----------------------- | ------------------------------------------ |
| `require_auth`          | existe                                     |
| `require_role`          | implemente dans `server/auth.py`           |
| `require_admin`         | alias `require_role("admin")`              |
| verification role admin | appliquee sur les endpoints `/api/admin/*` |

---

## Exemple

```python
@require_auth
@require_admin
async def admin_promote_user(request):
    ...
```

---

## References

- `server/auth.py`
- `app/core/user_roles.py`
- `app/models/user.py`
- `docs/00-REFERENCE/USER_ROLE_NOMENCLATURE.md`
- `../03-PROJECT/archives/FEATURE_NOTES_SUPERSEDED_2026-03-28/ADMIN_ESPACE_PROPOSITION.md`
