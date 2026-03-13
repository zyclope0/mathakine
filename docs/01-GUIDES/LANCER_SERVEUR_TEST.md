# LANCER LE SERVEUR EN MODE TEST - MATHAKINE

> Guide rapide pour verifier manuellement un changement backend/local
> Mise a jour : 13/03/2026

## Usage

Ce guide sert a demarrer le backend localement pour un controle manuel.
Il ne remplace pas les gates backend documentees dans `TESTING.md`.

## Demarrage rapide

### Backend

```bash
venv\Scripts\activate
python enhanced_server.py
```

Backend par defaut: `http://localhost:8000`

### Variables utiles

```powershell
$env:MATH_TRAINER_DEBUG="true"
$env:RUN_STARTUP_MIGRATIONS="true"
$env:PORT="8000"
python enhanced_server.py
```

## Verifications manuelles utiles

### Auth

1. ouvrir `http://localhost:3000/login`
2. verifier login nominal
3. verifier refresh apres navigation
4. verifier logout

### Reset password

1. lancer le flow `forgot-password`
2. reinitialiser le mot de passe
3. verifier qu'un autre onglet doit se reconnecter a la prochaine navigation protegee

### Exercise / challenge generation

1. verifier `POST /api/exercises/generate`
2. verifier les flux SSE si le lot touche la generation IA
3. verifier qu'aucun contrat JSON ou statut HTTP n'a derive

## Verification rapide backend

```bash
pytest -q --maxfail=20 --ignore=tests/api/test_admin_auth_stability.py
```

## Problemes frequents

### Port `8000` deja utilise

```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### PostgreSQL local indisponible

```bash
python scripts/check_local_db.py
```

### Backend inaccessible depuis le frontend

Verifier `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## References

- [TESTING.md](TESTING.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [../00-REFERENCE/GETTING_STARTED.md](../00-REFERENCE/GETTING_STARTED.md)
