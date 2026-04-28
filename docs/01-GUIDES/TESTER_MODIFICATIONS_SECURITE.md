# TESTER LES MODIFICATIONS DE SECURITE - MATHAKINE

> Mise a jour : 18/03/2026
> Objectif : verifier localement les flux auth/session/cookies sans faux positifs de methode

## Portee

Ce guide couvre les controles manuels utiles apres une modification de securite sur:
- login / logout
- cookies auth
- refresh token
- reset password
- changement de mot de passe
- revocation de session

Il ne remplace pas les tests backend standard.

## Preparation

### Backend

```powershell
venv\Scripts\activate
python enhanced_server.py
```

### Frontend

```powershell
cd frontend
npm run dev
```

### Base locale

Si PostgreSQL local n'est pas pret:

```powershell
python scripts/check_local_db.py
```

## Checks manuels recommandes

### 1. Login nominal

1. ouvrir `/login`
2. se connecter avec un utilisateur valide
3. verifier la redirection vers la zone protegee
4. verifier qu'un refresh navigateur conserve la session

Attendu:
- `access_token` et `refresh_token` geres en cookies
- `GET /api/users/me` reste coherent apres refresh

### 2. Logout

1. se connecter
2. lancer logout
3. verifier qu'une page protegee force le retour login

### 3. Forgot / reset password

1. lancer `forgot-password`
2. utiliser un token valide de reset
3. reinitialiser le mot de passe
4. verifier qu'un autre onglet ouvert semble encore connecte jusqu'a la prochaine navigation protegee
5. verifier qu'a la prochaine requete protegee cet onglet est force a se reconnecter

Attendu:
- anciens tokens rejetes
- anciennes sessions revoquees
- pas de fuite d'information sur l'existence d'un email dans le message forgot/resend

### 4. Changement de mot de passe depuis le profil

1. se connecter
2. aller dans les settings
3. changer le mot de passe
4. verifier qu'un ancien onglet ou ancien token est invalide a la prochaine navigation protegee

### 5. Cookies et stockage navigateur

Verifier dans DevTools:
- presence des cookies auth attendus
- absence de `refresh_token` en `localStorage`
- comportement CSRF conforme aux flux frontend habituels

## Headers de securite (ENVIRONMENT=production)

Pour tester les headers de securite HTTP (HSTS, CSP, X-Frame-Options, etc.), le backend doit etre lance avec `ENVIRONMENT=production` :

```powershell
$env:ENVIRONMENT="production"
python enhanced_server.py
```

Verifier la presence des headers sur une reponse :
```bash
curl -I http://localhost:10000/live
```

## Politique PII dans les logs

La politique de redaction des PII dans les logs est appliquee depuis le commit `9cf2504` :
- `user_id` (entier) dans les logs — PAS le `username` ni l'email
- voir `docs/03-PROJECT/POLITIQUE_REDACTION_LOGS_PII.md`

## Checks automatiques a relancer

```powershell
pytest -q tests/api/test_auth_flow.py tests/integration/test_auth_cookies_only.py tests/integration/test_auth_no_fallback.py tests/unit/test_auth_service.py --maxfail=20 --no-cov
black app/ server/ tests/ --check
isort app/ server/ tests/ --check-only --diff
```

Si le changement touche aussi `user`:

```powershell
pytest -q tests/api/test_user_endpoints.py tests/unit/test_user_service.py --maxfail=20 --no-cov
```

## Faux positifs a eviter

- ne pas utiliser `tests/api/test_admin_auth_stability.py` comme gate standard
- ne pas conclure a un bug runtime si plusieurs `pytest-cov` ont ete lances en parallele sur Windows et qu'un lock `.coverage` apparait
- ne pas confondre un onglet deja rendu avec une session encore valide apres reset password

## References

- [TESTING.md](TESTING.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../02-FEATURES/AUTH_FLOW.md](../02-FEATURES/AUTH_FLOW.md)
- [../../README_TECH.md](../../README_TECH.md)
