# 📈 Tests de Charge k6 - Mathakine

Ce répertoire contient les scénarios de tests de charge pour valider les performances et la robustesse de l'application Mathakine.

## 🎯 Objectifs

Les tests de charge visent à valider :
- **Performance** : Temps de réponse sous charge
- **Robustesse** : Comportement sous stress
- **Sécurité** : Pas de régression après corrections (fallback, localStorage, etc.)

## 📋 Scénarios Disponibles

### 1. `auth_burst.js` - Burst d'authentification
- **Objectif** : 300 connexions/min sur `POST /api/auth/login`
- **KPI** : p95 < 400ms, taux succès > 99%
- **Usage** :
  ```bash
  k6 run --vus 5 --duration 60s auth_burst.js
  ```

### 2. `refresh_storm.js` - Tempête de refresh
- **Objectif** : 150 req/min sur `POST /api/auth/refresh`
- **KPI** : p95 < 250ms, aucun 5xx, invalid token → 401
- **Usage** :
  ```bash
  k6 run --vus 3 --duration 60s refresh_storm.js
  ```

### 3. `sse_ia_challenges.js` - Connexions SSE IA
- **Objectif** : 200 connexions simultanées `GET /api/challenges/generate-ai-stream`
- **KPI** : CPU < 75%, queue OpenAI stable, 0 drop SSE
- **Usage** :
  ```bash
  k6 run --vus 200 --duration 60s sse_ia_challenges.js
  ```

### 4. `mix_auth_sse.js` - Mix authentification + SSE
- **Objectif** : 100 utilisateurs authentifiés déclenchent SSE après login
- **KPI** : Pas de fuite mémoire, latence stable
- **Usage** :
  ```bash
  k6 run --vus 100 --duration 120s mix_auth_sse.js
  ```

## 🚀 Installation

### Windows (via winget)
```powershell
winget install k6
```

### macOS (via Homebrew)
```bash
brew install k6
```

### Linux
```bash
# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## ⚙️ Configuration

### Variables d'environnement

Les scénarios utilisent des variables d'environnement pour la configuration :

```bash
# URL du backend (défaut: http://localhost:10000)
export BACKEND_URL=http://localhost:10000

# Credentials de test (défaut: ObiWan/HelloThere123!)
export TEST_USERNAME=ObiWan
export TEST_PASSWORD=HelloThere123!
```

### Windows PowerShell
```powershell
$env:BACKEND_URL="http://localhost:10000"
$env:TEST_USERNAME="ObiWan"
$env:TEST_PASSWORD="HelloThere123!"
k6 run auth_burst.js
```

### Linux/macOS
```bash
BACKEND_URL=http://localhost:10000 TEST_USERNAME=ObiWan TEST_PASSWORD=HelloThere123! k6 run auth_burst.js
```

## 📊 Exécution des Tests

### Test individuel
```bash
cd scripts/load/k6
k6 run auth_burst.js
```

### Tous les scénarios (script à créer)
```bash
# À créer : scripts/load/k6/run_all.sh ou run_all.ps1
```

### Avec options personnalisées
```bash
# Plus de VU, durée plus longue
k6 run --vus 10 --duration 120s auth_burst.js

# Mode cloud k6 (nécessite compte)
k6 cloud auth_burst.js
```

## 📈 Interprétation des Résultats

### Métriques importantes

- **http_req_duration** : Temps de réponse des requêtes
  - `p(95)` : 95ème percentile (95% des requêtes sont plus rapides)
  - `p(99)` : 99ème percentile
  
- **http_req_failed** : Taux d'échec des requêtes
  - Doit être < 1% pour les scénarios critiques

- **success_rate** : Taux de succès personnalisé (métrique custom)

### Exemple de sortie

```
✓ status is 200
✓ has access_token
✓ response time < 400ms

checks.........................: 100.00% ✓ 300      ✗ 0
data_received..................: 450 KB  7.5 kB/s
data_sent......................: 90 KB   1.5 kB/s
http_req_duration..............: avg=120ms min=50ms med=110ms max=380ms p(95)=350ms
http_req_failed................: 0.00%   ✓ 0       ✗ 300
success_rate...................: 100.00% ✓ 300      ✗ 0
vus............................: 5       min=5      max=5
```

## 🔍 Validation des Corrections de Sécurité

Les scénarios valident également les corrections de sécurité :

### ✅ SEC-1.2 : Pas de fallback refresh token
- `refresh_storm.js` teste que les tokens invalides retournent 401
- Vérifie qu'aucun nouveau refresh_token n'est créé avec un access_token expiré

### ✅ SEC-1.3 : Cookies HTTP-only uniquement
- Tous les scénarios utilisent uniquement les cookies pour l'authentification
- Aucun refresh_token n'est envoyé dans le body JSON

### ✅ SEC-1.4 : Authentification SSE
- `sse_ia_challenges.js` vérifie que les endpoints SSE nécessitent une authentification
- Vérifie qu'aucun 401 n'est retourné pour les utilisateurs authentifiés

## 📝 Notes Importantes

1. **Comptes de test** : Utilisez des comptes de test dédiés, pas des comptes de production
2. **Environnement** : Testez d'abord en développement/staging avant la production
3. **Ressources** : Les tests SSE peuvent être intensifs en CPU/mémoire
4. **Monitoring** : Surveillez les métriques serveur pendant les tests (CPU, mémoire, DB)

## 🐛 Dépannage

### k6 non trouvé
```bash
# Vérifier l'installation
k6 version

# Ajouter au PATH si nécessaire
# Windows: Ajouter C:\Program Files\k6 au PATH système
```

### Erreurs de connexion
- Vérifier que le backend est démarré
- Vérifier l'URL dans `BACKEND_URL`
- Vérifier les credentials dans `TEST_USERNAME` / `TEST_PASSWORD`

### Timeouts SSE
- Augmenter le timeout dans `sse_ia_challenges.js` (ligne `timeout: '60s'`)
- Vérifier que le backend peut gérer plusieurs connexions SSE simultanées

## 📚 Ressources

- [Documentation k6](https://k6.io/docs/)
- [k6 Cloud](https://app.k6.io/)
- [Plan d'Action Sécurité](docs/03-PROJECT/PLAN_ACTION_SECURITE_PERFORMANCE.md)
- [Audit Sécurité](docs/03-PROJECT/AUDIT_SECURITE_PERFORMANCE_2025-11-30.md)

