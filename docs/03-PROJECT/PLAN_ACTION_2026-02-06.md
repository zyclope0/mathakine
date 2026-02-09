# 📋 Plan d'Action - Prochaines Étapes - 06/02/2026

> **⚠️ PARTIELLEMENT OBSOLETE** - Ce plan date du 06/02/2026. Plusieurs actions ont ete completees depuis :
> - ✅ 4.2 Mise a jour profil (implemente)
> - ✅ Widgets dashboard (testes et deployes)
> - ✅ Deploiement Render (valide)
> - ✅ Page settings complete (5 sections)
> - ✅ **08-09/02/2026** : Decorateurs auth (`@require_auth`, `@optional_auth`, `@require_auth_sse`)
> - ✅ **08-09/02/2026** : Vulnerabilites npm corrigees (0 vuln : jspdf v4.1.0, xlsx→exceljs)
> - ✅ **08/02/2026** : Dependabot configure (GitHub Actions + npm)
> - ✅ **08/02/2026** : CI fiabilise (continue-on-error retire, tests migres async)
> - ✅ **08/02/2026** : GitHub Actions mises a jour (checkout v6, artifacts v6/v7, codecov v5)
> 
> **Document de reference actuel** : [EVALUATION_PROJET_2026-02-07.md](EVALUATION_PROJET_2026-02-07.md)

## ✅ Contexte

**Déploiement complété** :
- ✅ Documentation rationalisée (-92%)
- ✅ 11 index DB créés (+30-50% perf estimé)
- ✅ Gitignore corrigé (3 problèmes critiques)
- ✅ Code nettoyé et archivé
- ✅ 3 nouveaux widgets dashboard
- ✅ Script Render corrigé (`start_render.sh`)

**Commits déployés** :
- `aea3bce` - Rationalisation docs + Index DB + Gitignore fixes
- `1d0cc69` - Nettoyage massif + Archive FastAPI + Nouveaux widgets
- `e9a3e8e` - Fix script start_render.sh

---

## 🔴 PRIORITÉ IMMÉDIATE (24-48h)

### 1. Valider Déploiement Render ⚡

**État actuel** : Script `start_render.sh` restauré et déployé

**Actions** :
```bash
# Vérifier logs Render
# Dashboard Render → mathakine-backend → Logs

# Attendu:
# ✅ "Application des migrations Alembic..."
# ✅ "Migrations appliquées avec succès"
# ✅ "Révision DB actuelle: 20260206_user_achv_idx"
# ✅ "Démarrage du serveur Starlette (port 10000)..."
```

**Si erreur** :
- Vérifier que `alembic` est dans `requirements.txt` ✅
- Vérifier que `migrations/` est bien commité ✅
- Consulter logs Render détaillés

**Temps estimé** : 10 minutes  
**Impact** : 🔴 CRITIQUE - Backend doit être fonctionnel

---

### 2. Mesurer Performance DB 📊

**Script à créer** : `scripts/test_performance_indexes.py`

```python
"""
Test performance des nouveaux index DB
Mesure le gain réel sur requêtes fréquentes
"""
import time
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.exercise import Exercise
from app.models.user import User

def benchmark_query(name, query_func):
    """Mesure temps d'exécution d'une requête"""
    db = SessionLocal()
    times = []
    
    for _ in range(10):  # 10 exécutions pour moyenne
        start = time.time()
        query_func(db)
        end = time.time()
        times.append((end - start) * 1000)
    
    db.close()
    avg_time = sum(times) / len(times)
    print(f"{name}: {avg_time:.2f}ms (avg)")
    return avg_time

# Test 1: Filtrage type + difficulté (index composite)
def test_type_difficulty(db):
    return db.execute(
        select(Exercise)
        .where(Exercise.exercise_type == 'ADDITION')
        .where(Exercise.difficulty == 'PADAWAN')
        .limit(100)
    ).scalars().all()

# Test 2: Tri chronologique (index created_at)
def test_recent_active(db):
    return db.execute(
        select(Exercise)
        .where(Exercise.is_active == True)
        .order_by(Exercise.created_at.desc())
        .limit(50)
    ).scalars().all()

# Test 3: Exercices d'un créateur (index composite)
def test_creator_active(db):
    return db.execute(
        select(Exercise)
        .where(Exercise.creator_id == 1)
        .where(Exercise.is_active == True)
        .limit(50)
    ).scalars().all()

# Test 4: Utilisateurs actifs récents (index users)
def test_users_active_recent(db):
    return db.execute(
        select(User)
        .where(User.is_active == True)
        .order_by(User.created_at.desc())
        .limit(20)
    ).scalars().all()

if __name__ == "__main__":
    print("🚀 Test Performance Index DB")
    print("=" * 50)
    
    t1 = benchmark_query("Test 1 (type + difficulty)", test_type_difficulty)
    t2 = benchmark_query("Test 2 (recent active)", test_recent_active)
    t3 = benchmark_query("Test 3 (creator + active)", test_creator_active)
    t4 = benchmark_query("Test 4 (users active)", test_users_active_recent)
    
    print("\n📊 Résumé:")
    print(f"  Exercises avg: {(t1 + t2 + t3) / 3:.2f}ms")
    print(f"  Users avg: {t4:.2f}ms")
    print("\n✅ Objectif gain: -30-50% vs baseline")
```

**Actions** :
1. Créer le script
2. Exécuter en local
3. Comparer avec baseline (si disponible)
4. Documenter résultats dans `INDEX_DB_MANQUANTS_2026-02-06.md`

**Temps estimé** : 30 minutes  
**Impact** : 🔴 HAUTE - Valider optimisations

---

### 3. Tester Widgets Dashboard 🎨

**URL** : http://localhost:3000/dashboard (ou prod)

**Checklist** :
- [ ] `StreakWidget` charge et affiche série actuelle
- [ ] `ChallengesProgressWidget` affiche défis complétés
- [ ] `CategoryAccuracyChart` affiche précision par type (addition, multiplication, etc.)
- [ ] **Multi-thème** : Basculer clair ↔ sombre fonctionne
- [ ] **Animations** : Smooth et respecte `prefers-reduced-motion`
- [ ] **Responsive** : Widgets s'adaptent mobile/tablette
- [ ] **Traductions** : FR/EN fonctionnent (exercices.types.addition, etc.)

**Si bug** : Consulter `docs/06-WIDGETS/CORRECTIONS_WIDGETS.md`

**Temps estimé** : 15 minutes  
**Impact** : 🔴 HAUTE - UX dashboard

---

## 🟡 PRIORITÉ MOYENNE (Cette semaine)

### 4. Implémenter Endpoints Prioritaires 🔧

Voir `docs/03-PROJECT/PLACEHOLDERS_ET_TODO.md`

#### 4.1 Mot de passe oublié (P1 - HAUTE)

**Endpoint** : `POST /api/auth/forgot-password`

**Fichiers** :
- `server/handlers/auth_handlers.py` (handler)
- `app/services/auth_service.py` (logique)
- `app/services/email_service.py` (email reset)

**Flow** :
```
1. User POST email → endpoint
2. Génère token reset (UUID)
3. Sauvegarde token en DB (expires_at)
4. Envoie email avec lien
5. Returns 200 OK
```

**Temps estimé** : 2h  
**Impact** : 🟡 MOYENNE - UX importante

---

#### 4.2 Mise à jour profil (P1 - HAUTE)

**Endpoint** : `PUT /api/users/me`

**Fichiers** :
- `server/handlers/user_handlers.py` (handler)
- `app/services/user_service.py` (update_user)
- `frontend/app/profile/page.tsx` (UI)

**Champs modifiables** :
- `full_name`, `grade_level`, `learning_style`, `preferred_difficulty`, `preferred_theme`

**Temps estimé** : 1h  
**Impact** : 🟡 MOYENNE - UX dashboard

---

#### 4.3 Refresh token (P2 - MOYENNE)

**Endpoint** : `POST /api/auth/refresh`

**Fichiers** :
- `server/handlers/auth_handlers.py`
- `app/services/auth_service.py`

**Flow** :
```
1. User POST refresh_token
2. Valide token (JWT decode)
3. Génère nouveau access_token
4. Returns new tokens
```

**Temps estimé** : 1h  
**Impact** : 🟢 BASSE - Sécurité (les cookies fonctionnent déjà)

---

### 5. Optimiser Imports Lazy ⚡

**Fichiers concernés** : `server/handlers/*.py` (~50 occurrences)

**Avant** :
```python
def get_exercises(request: Request):
    from app.services.exercise_service import ExerciseService  # ❌ Lazy
    from app.schemas.exercise import ExerciseOut
    ...
```

**Après** :
```python
from app.services.exercise_service import ExerciseService  # ✅ Top
from app.schemas.exercise import ExerciseOut

def get_exercises(request: Request):
    ...
```

**Gain estimé** : -10ms par requête  
**Temps estimé** : 2h (remonter 50 imports)  
**Impact** : 🟡 MOYENNE - Performance

**Doc** : README_TECH.md section 9 (INC-B6)

---

## 🟢 PRIORITÉ BASSE (Quand tu veux)

### 6. Monitoring Production 📈

**Outils suggérés** :
- **Sentry** (déjà intégré) : Erreurs et exceptions
- **Prometheus** (déjà dans requirements) : Métriques custom
- **Grafana** (optionnel) : Dashboards

**Métriques à tracker** :
- Temps réponse API (p50, p95, p99)
- Taux erreur 4xx/5xx
- Slow queries DB (> 100ms)
- Utilisation CPU/RAM

**Temps estimé** : 4h  
**Impact** : 🟢 BASSE - Observabilité

---

### 7. Tests E2E Widgets 🧪

**Framework** : Playwright (déjà configuré)

**Tests à créer** :
```typescript
// frontend/__tests__/e2e/dashboard.spec.ts
test('Dashboard widgets load correctly', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Vérifier widgets présents
  await expect(page.locator('[data-testid="streak-widget"]')).toBeVisible();
  await expect(page.locator('[data-testid="challenges-widget"]')).toBeVisible();
  await expect(page.locator('[data-testid="category-chart"]')).toBeVisible();
});
```

**Temps estimé** : 2h  
**Impact** : 🟢 BASSE - Qualité

---

### 8. Documentation Continue 📝

**Actions** :
- [ ] Créer CHANGELOG.md (historique versions)
- [ ] Capturer screenshots widgets pour docs
- [ ] Mettre à jour INDEX.md si nouveaux docs
- [ ] Documenter nouveaux endpoints implémentés

**Temps estimé** : 1h  
**Impact** : 🟢 BASSE - Maintenance

---

## 📊 Résumé Priorisation

| Tâche | Priorité | Temps | Impact Business | Complexité |
|-------|----------|-------|----------------|------------|
| **1. Valider Render** | 🔴 IMMÉDIATE | 10 min | Production bloquée | Faible |
| **2. Mesurer perf DB** | 🔴 IMMÉDIATE | 30 min | Validation optimisation | Moyenne |
| **3. Tester widgets** | 🔴 IMMÉDIATE | 15 min | UX dashboard | Faible |
| **4.1 Forgot password** | 🟡 HAUTE | 2h | UX importante | Moyenne |
| **4.2 Update profil** | 🟡 HAUTE | 1h | UX dashboard | Faible |
| **5. Imports lazy** | 🟡 MOYENNE | 2h | Performance -10ms | Moyenne |
| **4.3 Refresh token** | 🟢 BASSE | 1h | Sécurité (non bloquant) | Faible |
| **6. Monitoring** | 🟢 BASSE | 4h | Observabilité | Élevée |
| **7. Tests E2E** | 🟢 BASSE | 2h | Qualité | Moyenne |
| **8. Docs continue** | 🟢 BASSE | 1h | Maintenance | Faible |

> **Mise a jour 09/02/2026** : Le monitoring (point 6) reste a faire (Sentry SDK installe mais `sentry_sdk.init()` non appele). Les imports lazy (point 5) restent a optimiser. Les points 1-3 sont valides.

---

## 🎯 Parcours Recommandé

### Aujourd'hui (1h)
1. ✅ Vérifier logs Render (déploiement OK)
2. ✅ Tester widgets dashboard local
3. ✅ Créer script `test_performance_indexes.py`
4. ✅ Mesurer gain performance

### Cette semaine (5h)
5. Implémenter `POST /api/auth/forgot-password` (2h)
6. Implémenter `PUT /api/users/me` (1h)
7. Optimiser imports lazy (2h)

### Plus tard (quand besoin)
8. Monitoring production
9. Tests E2E widgets
10. Documentation continue

---

## 📝 Quick Wins (30 min chacun)

Si tu veux des petites victoires rapides :

1. **Script performance** → Confirme gain +30-50%
2. **Test widgets** → Valide UX dashboard
3. **Update profil** → Endpoint simple, impact UX direct
4. **Screenshot widgets** → Documentation visuelle

---

## 🚀 Action Immédiate Suggérée

**SI TU AS 15 MIN MAINTENANT** :

```bash
# 1. Vérifier Render déployé
# Aller sur: https://dashboard.render.com/
# Logs → mathakine-backend → Vérifier "Migrations appliquées"

# 2. Tester dashboard local
cd d:\Mathakine
python enhanced_server.py  # Terminal 1
cd frontend && npm run dev  # Terminal 2
# Ouvrir: http://localhost:3000/dashboard

# 3. Valider widgets
# Série, Défis, Précision → Tout s'affiche ?
```

---

## 📄 Documents de Référence

| Document | Utilité |
|----------|---------|
| `docs/03-PROJECT/PLACEHOLDERS_ET_TODO.md` | 13 endpoints à implémenter |
| `docs/03-PROJECT/INDEX_DB_MANQUANTS_2026-02-06.md` | Détails index DB + script perf |
| `docs/06-WIDGETS/INTEGRATION_PROGRESSION_WIDGETS.md` | Guide widgets dashboard |
| `docs/06-WIDGETS/DESIGN_SYSTEM_WIDGETS.md` | Design system patterns |
| `README_TECH.md` | Référence technique (47 endpoints) |

---

**Date** : 06/02/2026  
**Statut** : ✅ Déploiement complété, plan d'action prêt  
**Prochaine action recommandée** : Valider Render (10 min) 🚀
