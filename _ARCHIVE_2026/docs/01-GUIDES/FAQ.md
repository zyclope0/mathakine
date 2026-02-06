# ❓ FAQ - MATHAKINE

**Version** : 2.0.0  
**Date** : 20 novembre 2025

---

## 🎯 GÉNÉRAL

### Qu'est-ce que Mathakine ?
Mathakine est une plateforme éducative mathématique conçue pour les enfants autistes (6-16 ans), offrant une expérience d'apprentissage personnalisée et engageante.

### Pour qui est-ce conçu ?
- **Primaire** : Enfants autistes 6-16 ans
- **Secondaire** : Enseignants, parents, thérapeutes

### Est-ce gratuit ?
Oui, Mathakine est open-source et gratuit.

---

## 🏗️ ARCHITECTURE

### Quelle est l'architecture ?
```
Frontend Next.js (port 3000)
    ↓ REST API
Backend Starlette (port 8000)
    ↓ SQLAlchemy ORM
PostgreSQL Database
```

### Pourquoi deux frameworks backend (FastAPI + Starlette) ?
- **Starlette** : Backend API principal (37 routes JSON)
- **FastAPI** : Documentation OpenAPI uniquement

Post-Phase 2, le backend est 100% API JSON (aucune route HTML).

### Peut-on utiliser SQLite au lieu de PostgreSQL ?
Oui pour **développement** :
```bash
# .env
DATABASE_URL=sqlite:///./mathakine.db
```

Non pour **production** (utiliser PostgreSQL).

---

## 💻 INSTALLATION

### Prérequis minimums ?
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ (ou SQLite pour dev)
- 4GB RAM
- 2GB disque

### Temps d'installation ?
- **Backend** : 5 min
- **Frontend** : 3 min
- **Total** : ~10 min

### Comment installer ?
Voir [Getting Started](../00-REFERENCE/GETTING_STARTED.md)

---

## 🔐 AUTHENTIFICATION

### Comment fonctionne l'auth ?
- **JWT** stocké dans cookies HTTP-only
- **Expiration** : 30 min
- **Refresh token** : Disponible
- **Sécurité** : HTTPS en production

### Comment tester l'auth en local ?
```bash
# Créer utilisateur test
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123","role":"student"}'

# Se connecter
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

---

## 🎯 CHALLENGES

### Quels types de challenges ?
- **SEQUENCE** : Suites numériques
- **PATTERN** : Reconnaissance motifs
- **PUZZLE** : Énigmes logiques
- **CALCULATION** : Calcul mental
- **CHESS** : Stratégie échecs

### Comment créer un challenge ?
```python
# Backend
from app.services import challenge_service
from app.schemas.logic_challenge import LogicChallengeCreate

data = LogicChallengeCreate(
    title="Suite de Fibonacci",
    description="Trouvez le prochain nombre",
    challenge_type="SEQUENCE",
    age_group="GROUP_10_12",
    correct_answer="13",
    solution_explanation="..."
)

challenge = challenge_service.create_challenge(db, data)
```

### Comment filtrer les challenges ?
```typescript
// Frontend
const { data: challenges } = useChallenges({
  challengeType: 'SEQUENCE',
  ageGroup: 'GROUP_10_12',
  difficultyMin: 1.0,
  difficultyMax: 3.0,
});
```

---

## 📝 EXERCISES

### Différence entre Exercise et Challenge ?
- **Exercise** : Exercice math simple (addition, multiplication, etc.)
- **Challenge** : Défi logique complexe (patterns, puzzles, etc.)

### Génération IA disponible ?
Oui, via OpenAI :
```bash
# .env
OPENAI_API_KEY=sk-...
```

Streaming SSE :
```
GET /api/exercises/generate-ai-stream?type=ADDITION&difficulty=MEDIUM
GET /api/challenges/generate-ai-stream?type=SEQUENCE&difficulty=HARD
```

---

## 🧪 TESTS

### Comment lancer les tests ?
```bash
# Backend - tous les tests
pytest tests/ -v

# Backend - critiques uniquement
pytest tests/ -v -m critical

# Backend - avec coverage
pytest tests/ --cov --cov-report=html

# Frontend
cd frontend
npm run test
```

### Coverage actuel ?
- **Backend** : 60%+
- **Frontend** : En développement
- **Objectif** : 70%+

### CI/CD configuré ?
Oui, GitHub Actions :
- Tests auto sur push/PR
- PostgreSQL service
- Coverage upload (Codecov)

---

## 🚀 DÉPLOIEMENT

### Où déployer ?
**Recommandé** : Render
- Frontend : Static Site
- Backend : Web Service
- Database : PostgreSQL

Voir [Deployment Guide](DEPLOYMENT.md)

### URLs production ?
- **Frontend** : https://mathakine-frontend.onrender.com
- **Backend** : https://mathakine-backend.onrender.com

### Coût hébergement ?
- **Render Free Tier** : Gratuit avec limitations
- **Render Starter** : $7/mois backend + $15/mois DB
- **Total** : ~$22/mois pour production stable

---

## 🐛 DEBUGGING

### Backend ne démarre pas ?
Voir [Troubleshooting](TROUBLESHOOTING.md#backend-ne-démarre-pas)

### Frontend ne charge pas ?
Voir [Troubleshooting](TROUBLESHOOTING.md#frontend-ne-charge-pas)

### Erreurs CORS ?
```python
# enhanced_server.py
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://mathakine-frontend.onrender.com"
]
```

### Tests échouent ?
```bash
# Vérifier environnement
pytest --collect-only

# Relancer avec verbosité
pytest tests/ -vv

# Debugger test spécifique
pytest tests/api/test_auth.py::test_login -vv -s
```

---

## 📊 PERFORMANCE

### Backend lent ?
1. **Ajouter indexes**
```python
op.create_index('idx_challenges_type', 'logic_challenges', ['challenge_type'])
```

2. **Utiliser eager loading**
```python
from sqlalchemy.orm import joinedload
challenges = db.query(Challenge).options(joinedload(Challenge.user)).all()
```

3. **Cache**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_challenge_types():
    return CHALLENGE_TYPES_DB
```

### Frontend lent ?
1. **Code splitting**
```typescript
import dynamic from 'next/dynamic';
const HeavyComponent = dynamic(() => import('./Heavy'));
```

2. **Memoization**
```typescript
const value = useMemo(() => compute(data), [data]);
```

3. **Images optimisées**
```typescript
import Image from 'next/image';
<Image src="..." width={800} height={600} loading="lazy" />
```

---

## 🔧 DÉVELOPPEMENT

### Conventions de code ?
- **Backend** : `snake_case`, type hints, docstrings
- **Frontend** : `camelCase`, TypeScript strict, interfaces
- Voir [Development Guide](DEVELOPMENT.md)

### Comment contribuer ?
Voir [Contributing Guide](CONTRIBUTING.md)

### Workflow Git ?
```bash
git checkout -b feature/ma-feature
# développer
git commit -m "feat: Add feature"
git push origin feature/ma-feature
# Ouvrir PR sur GitHub
```

---

## 📚 DOCUMENTATION

### Où trouver la doc ?
- **Index** : [docs/INDEX.md](../INDEX.md)
- **Architecture** : [docs/00-REFERENCE/ARCHITECTURE.md](../00-REFERENCE/ARCHITECTURE.md)
- **API** : [docs/00-REFERENCE/API.md](../00-REFERENCE/API.md)
- **Getting Started** : [docs/00-REFERENCE/GETTING_STARTED.md](../00-REFERENCE/GETTING_STARTED.md)

### Doc à jour ?
Oui, 100% à jour (post-phases 1-6, 20 nov 2025).

---

## 🤝 SUPPORT

### Comment obtenir de l'aide ?
1. **Documentation** : Consulter guides
2. **FAQ** : Ce document
3. **Issues GitHub** : Signaler bugs
4. **Discussions GitHub** : Questions générales

### Temps de réponse ?
- **Issues critiques** : 24-48h
- **Questions** : 2-5 jours
- **Feature requests** : Variable

---

## 📈 ROADMAP

### Prochaines features ?
Voir [Roadmap](../03-PROJECT/ROADMAP.md)

**Q1 2026** :
- Amélioration IA génération
- Modes multi-joueurs
- Analytics avancées
- Mobile apps natives

---

## 🎓 APPRENTISSAGE

### Ressources pour débuter ?
1. [Getting Started](../00-REFERENCE/GETTING_STARTED.md) (15 min)
2. [Architecture](../00-REFERENCE/ARCHITECTURE.md) (30 min)
3. [Development Guide](DEVELOPMENT.md) (45 min)

### Exemples de code ?
Tous les guides contiennent des exemples :
- [Development Guide](DEVELOPMENT.md) - Workflow complet
- [Testing Guide](TESTING.md) - Tests exemples
- [API Reference](../00-REFERENCE/API.md) - Requêtes exemples

---

**Autres questions ?** Ouvrez une [Discussion](https://github.com/yourusername/mathakine/discussions) !

