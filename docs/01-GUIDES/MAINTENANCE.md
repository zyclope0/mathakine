# 🔧 GUIDE DE MAINTENANCE - MATHAKINE

**Version** : 1.0.0  
**Date** : 6 Décembre 2025  
**Audience** : DevOps, Développeurs, Mainteneurs

---

## 📋 TABLE DES MATIÈRES

1. [Vue d'ensemble](#vue-ensemble)
2. [Tests de charge réguliers](#load-tests)
3. [Vérifications de sécurité](#security-checks)
4. [Monitoring des performances](#performance-monitoring)
5. [Maintenance préventive](#preventive-maintenance)
6. [Procédures de dépannage](#troubleshooting)

---

## 🎯 VUE D'ENSEMBLE {#vue-ensemble}

Ce guide décrit les procédures de maintenance régulières pour assurer la stabilité, la sécurité et les performances de Mathakine.

### Fréquence recommandée

| Tâche | Fréquence | Criticité |
|-------|-----------|-----------|
| Tests de charge | Hebdomadaire | 🔴 Critique |
| Vérifications sécurité | Mensuelle | 🔴 Critique |
| **Revue documentation (vérité terrain)** | **Trimestrielle** | 🟡 Important |
| Review logs | Quotidienne | 🟡 Important |
| Optimisation DB | Trimestrielle | 🟢 Informatif |

> **Revue vérité terrain** : aligner README, README_TECH et docs de référence avec le code (routes API, versions, modèles). Voir [CONVENTION_DOCUMENTATION.md](../CONVENTION_DOCUMENTATION.md) §7.

---

## 📈 TESTS DE CHARGE RÉGULIERS {#load-tests}

### Objectif

Détecter les régressions de performance et valider la capacité de charge de l'application.

### Procédure hebdomadaire

#### 1. Préparer l'environnement

```bash
# Vérifier que le backend est démarré
curl http://localhost:10000/health

# Configurer les variables d'environnement
export BACKEND_URL=http://localhost:10000
export TEST_USERNAME=ObiWan
export TEST_PASSWORD=HelloThere123!
```

#### 2. Exécuter les tests standards

```bash
# Tests standards (recommandé)
python scripts/load/run_load_tests.py --level standard

# Ou avec PowerShell
.\scripts\load\run_load_tests.ps1 -Level standard
```

#### 3. Analyser les résultats

**Métriques à surveiller** :
- `http_req_duration` : Temps de réponse (p95 < 400ms pour auth, < 250ms pour refresh)
- `http_req_failed` : Taux d'échec (< 1%)
- `success_rate` : Taux de succès (> 99%)

**Actions si échec** :
1. Identifier le scénario en échec
2. Vérifier les logs du backend
3. Analyser les métriques système (CPU, mémoire)
4. Corriger les problèmes identifiés
5. Réexécuter les tests

### Tests mensuels complets

```bash
# Tests complets (tous les scénarios)
python scripts/load/run_load_tests.py --level full
```

**Durée** : ~5-10 minutes  
**Objectif** : Valider la capacité maximale de l'application

### Tests post-déploiement

Après chaque déploiement en production :

```bash
# Tests rapides sur production
BACKEND_URL=https://mathakine-backend.onrender.com \
python scripts/load/run_load_tests.py --level quick
```

**⚠️ Important** : Utiliser des comptes de test dédiés, pas des comptes utilisateurs réels.

---

## 🔒 VÉRIFICATIONS DE SÉCURITÉ {#security-checks}

### Scripts de vérification

Tous les scripts de sécurité sont dans `scripts/security/` :

```bash
# Vérifier les logs sensibles
python scripts/security/check_sensitive_logs.py

# Vérifier l'absence de fallback refresh token
python scripts/security/check_fallback_refresh.py

# Vérifier l'absence de localStorage pour refresh_token
python scripts/security/check_localstorage_refresh.py

# Vérifier le masquage des credentials démo
python scripts/security/check_demo_credentials.py

# Vérifier les migrations au boot
python scripts/security/check_startup_migrations.py
```

### Procédure mensuelle

```bash
# Exécuter tous les scripts de sécurité
for script in scripts/security/*.py; do
    echo "Exécution: $script"
    python "$script"
done
```

**Actions si échec** :
1. Consulter le rapport d'audit : `docs/03-PROJECT/AUDIT_SECURITE_PERFORMANCE_2025-11-30.md`
2. Vérifier le suivi d'implémentation : `docs/03-PROJECT/SUIVI_IMPLEMENTATION_SECURITE.md`
3. Corriger les vulnérabilités identifiées
4. Réexécuter les vérifications

---

## ⚡ MONITORING DES PERFORMANCES {#performance-monitoring}

### Métriques à surveiller

#### Backend

- **CPU** : < 75% en charge normale
- **Mémoire** : < 80% de la RAM disponible
- **Temps de réponse** :
  - Auth : p95 < 400ms
  - Refresh : p95 < 250ms
  - SSE : Latence stable, pas de drop

#### Database

- **Connexions actives** : < 80% du pool max
- **Requêtes lentes** : Identifier avec `pg_stat_statements`
- **Taille DB** : Surveiller la croissance

### Scripts de monitoring

```bash
# Benchmark de la liste des challenges
python scripts/performance/benchmark_challenges_list.py

# Vérifier les compteurs de challenges
python scripts/verify_migration_counters.py
```

### Alertes recommandées

Configurer des alertes pour :
- CPU > 80% pendant > 5 minutes
- Mémoire > 85% pendant > 5 minutes
- Taux d'erreur HTTP > 1%
- Temps de réponse p95 > seuils définis

---

## 🛡️ MAINTENANCE PRÉVENTIVE {#preventive-maintenance}

### Hebdomadaire

- [ ] Exécuter tests de charge standards
- [ ] Vérifier les logs d'erreur
- [ ] Surveiller les métriques de performance

### Mensuelle

- [ ] Exécuter tous les scripts de sécurité
- [ ] Review des logs d'accès
- [ ] Vérifier les variables d'environnement
- [ ] Tests de charge complets

### Trimestrielle

- [ ] Optimisation de la base de données
- [ ] Review des dépendances (mises à jour de sécurité)
- [ ] Audit de sécurité complet
- [ ] Review de la documentation

### Procédure de vérification pré-déploiement

Avant chaque déploiement :

```bash
# Vérification complète
python scripts/pre_deploy_check.py

# Inclut :
# - Build TypeScript
# - Tests Python critiques
# - Vérifications sécurité
# - Tests de charge rapides
```

**Résultat attendu** :
```
✅ Toutes les vérifications sont passées
```

Si échec :
```
❌ Déploiement bloqué (erreurs critiques)
```
→ Corriger les erreurs avant de déployer

---

## 🔍 PROCÉDURES DE DÉPANNAGE {#troubleshooting}

### Problème : Tests de charge échouent

**Symptômes** :
- `http_req_failed > 1%`
- `http_req_duration` p95 > seuils

**Diagnostic** :
```bash
# 1. Vérifier que le backend est démarré
curl http://localhost:10000/health

# 2. Vérifier les logs du backend
tail -f logs/app.log

# 3. Vérifier les ressources système
# CPU, mémoire, connexions DB
```

**Solutions** :
- Augmenter les ressources (CPU/RAM)
- Optimiser les requêtes DB lentes
- Vérifier la configuration du pool de connexions
- Review du code pour les goulots d'étranglement

### Problème : Scripts de sécurité échouent

**Symptômes** :
- Un script de sécurité retourne une erreur

**Diagnostic** :
```bash
# Exécuter le script avec verbose
python scripts/security/check_sensitive_logs.py -v

# Vérifier le code concerné
grep -r "logger.debug" app/
```

**Solutions** :
- Consulter `docs/03-PROJECT/SUIVI_IMPLEMENTATION_SECURITE.md`
- Appliquer les corrections recommandées
- Réexécuter les scripts

### Problème : Performance dégradée

**Symptômes** :
- Temps de réponse augmentent
- CPU/mémoire élevés

**Diagnostic** :
```bash
# Benchmark des endpoints critiques
python scripts/performance/benchmark_challenges_list.py

# Analyser les requêtes DB lentes
# (nécessite accès à la DB)
```

**Solutions** :
- Ajouter des index manquants
- Optimiser les requêtes N+1
- Mettre en cache les données fréquentes
- Scale up les ressources si nécessaire

---

## 📚 RESSOURCES

### Documentation

- [Guide de déploiement](DEPLOYMENT.md)
- [Architecture](../00-REFERENCE/ARCHITECTURE.md)
- [Audit sécurité](../03-PROJECT/AUDIT_SECURITE_PERFORMANCE_2025-11-30.md)
- [Suivi implémentation](../03-PROJECT/SUIVI_IMPLEMENTATION_SECURITE.md)

### Scripts

- `scripts/load/run_load_tests.py` : Tests de charge
- `scripts/pre_deploy_check.py` : Vérifications pré-déploiement
- `scripts/security/*.py` : Scripts de sécurité
- `scripts/performance/*.py` : Scripts de performance

### Outils externes

- [k6 Documentation](https://k6.io/docs/)
- [Render Monitoring](https://render.com/docs/monitoring)
- [PostgreSQL Monitoring](https://www.postgresql.org/docs/current/monitoring.html)

---

## 📝 CHECKLIST DE MAINTENANCE

### Hebdomadaire

- [ ] Tests de charge standards
- [ ] Review logs d'erreur
- [ ] Vérifier métriques de performance

### Mensuelle

- [ ] Tous les scripts de sécurité
- [ ] Tests de charge complets
- [ ] Review variables d'environnement
- [ ] Review logs d'accès

### Trimestrielle

- [ ] Optimisation DB
- [ ] Review dépendances
- [ ] Audit sécurité complet
- [ ] Mise à jour documentation

---

**Dernière mise à jour** : 6 Décembre 2025  
**Prochaine review** : 6 Janvier 2026

