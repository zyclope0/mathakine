# TROUBLESHOOTING GUIDE - MATHAKINE

> Problemes courants et diagnostics utiles
> Mise a jour : 13/03/2026

## Backend ne demarre pas

### Port `8000` deja utilise

```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Ou lancer sur un autre port:

```bash
$env:PORT="8001"
python enhanced_server.py
```

### Dependances Python manquantes

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Variables d'environnement absentes

Verifier au minimum:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mathakine
SECRET_KEY=<secret>
ALLOWED_ORIGINS=http://localhost:3000
```

## PostgreSQL local indisponible

Symptome typique:
- `psycopg2.OperationalError`
- `connection refused localhost:5432`

Verification rapide:

```bash
python scripts/check_local_db.py
```

Si PostgreSQL n'est pas demarre, option Docker rapide:

```bash
docker run -d --name pg-mathakine -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

## Les tests backend refusent de demarrer

### `TEST_DATABASE_URL` manquant ou incorrect

Les tests backend ne doivent pas utiliser la base de dev/production.

A verifier:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mathakine
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/test_mathakine
TESTING=true
```

Preparation recommandee:

```bash
python scripts/check_local_db.py
```

### Lock `.coverage` sur Windows

Symptome:
- `PermissionError` ou echec aleatoire sur `.coverage`
- surtout quand plusieurs commandes `pytest` avec couverture tournent en parallele

Cause:
- faux positif tooling `pytest-cov` / verrouillage de fichier

Correctif:
- ne pas lancer plusieurs `pytest` avec couverture en parallele
- relancer une seule commande `pytest`
- ne pas conclure a une regression runtime sans reproduction sur run serialise

### `tests/api/test_admin_auth_stability.py`

Ce test n'est pas un gate standard. Il ne doit pas servir a invalider un lot normal tant qu'il execute `pytest` dans `pytest`.

## Un test est vert seul mais rouge dans une batterie mixte

Interpretation correcte:
- ce n'est pas forcement un bug runtime
- cela peut etre une vraie flakiness de test ou un couplage a l'etat global de la DB

Exemple traite pendant la cloture Runtime:
- `tests/unit/test_exercise_service.py::test_list_exercises` et `tests/unit/test_badge_requirement_engine.py::TestCheckRequirementsMinPerType::test_min_per_type_satisfied` ont illustre ce type de symptome
- dans les deux cas, la bonne approche a ete de prouver la cause de test ou de namespace, pas d'incriminer a tort `coverage`

## Frontend ne demarre pas

### Backend introuvable

Verifier:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Puis demarrer le backend:

```bash
python enhanced_server.py
```

### Erreurs de format/lint frontend

```bash
cd frontend
npm run format
npm run lint
npm run format:check
```

### Hydration mismatch

Causes frequentes:
- branchement conditionnel `typeof window`
- `Date.now()` ou `Math.random()` pendant le rendu SSR
- lecture d'un etat navigateur uniquement disponible cote client
- extension navigateur qui injecte des attributs dans le DOM

Approche:
- garder le rendu SSR deterministe
- deplacer la logique navigateur dans `useEffect`
- verifier d'abord si le warning disparait sans extension navigateur

## Auth et sessions

### Apres reset password, un autre onglet semble encore connecte

Comportement attendu:
- l'onglet deja ouvert peut afficher temporairement son etat courant
- des la prochaine navigation ou requete protegee, les anciens tokens sont rejetes et l'utilisateur doit se reconnecter

Ce comportement est compatible avec la revocation par `password_changed_at` + comparaison `iat`.

## References

- [TESTING.md](TESTING.md)
- [CREATE_TEST_DATABASE.md](CREATE_TEST_DATABASE.md)
- [../../README_TECH.md](../../README_TECH.md)
