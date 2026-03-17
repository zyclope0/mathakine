# Lot F1 - Residual Weak Contracts Elimination

> Iteration `F`
> Status: done

## Mission

Remove the most important remaining weak internal contracts left after `E`.

## Priority Targets

- residual weak tuples in `auth_service.py`
- weak internal results still crossing `admin_application_service.py`
- bounded mutation-result shapes in `admin_content_service.py`

## Success Criteria

- less tuple unpacking on critical flows
- more explicit typed results or business exceptions
- no HTTP contract redesign
- bounded blast radius

## F1 Result (2026-03-17)

**Cluster choisi** : `auth_service.py` (create_user, refresh_access_token, update_user_password, create_registered_user_with_verification)

**Retours faibles remplacés** :
- `create_user` : `(user, error_message, status_code)` → `CreateUserResult`
- `refresh_access_token` : `(token_data, error_message, status_code)` → `RefreshTokenResult`
- `update_user_password` : `(bool, Optional[str])` → `UpdatePasswordResult`
- `create_registered_user_with_verification` : `(user, error_message, status_code)` → `CreateUserResult`

**Hors scope** : `authenticate_user_with_session` reste en `Tuple` (non modifié). `admin_application_service` et `admin_content_service` non touchés.
