# Guide de Sécurité - Mathakine

## Table des matières
- [Introduction](#introduction)
- [Authentification](#authentification)
- [Autorisation](#autorisation)
- [Protection des données](#protection-des-données)
- [Sécurité de l'API](#sécurité-de-lapi)
- [Bonnes pratiques](#bonnes-pratiques)
- [Audit de sécurité](#audit-de-sécurité)

## Introduction

Ce guide détaille les mesures de sécurité implémentées dans Mathakine et les bonnes pratiques à suivre.

## Authentification

### JWT (JSON Web Tokens)
- Durée de validité : 1 heure pour le token d'accès, 30 jours pour le refresh token
- Stockage sécurisé des tokens dans des cookies HTTP-only
- Protection CSRF avec SameSite=Lax
- Refresh tokens avec rotation automatique
- Validation des tokens avec vérification du rôle utilisateur

### Mots de passe
- Hachage avec bcrypt
- Règles de complexité minimale
- Protection contre les attaques par force brute
- Réinitialisation sécurisée

### Middleware d'authentification
- Vérification automatique des tokens pour les routes protégées
- Redirection vers la page de connexion pour les utilisateurs non authentifiés
- Routes publiques configurées (/, /login, /register, /api/auth/login, /api/users/, /static, /exercises)
- Journalisation des tentatives d'accès non autorisées

### Cookies sécurisés
- access_token : Token d'accès principal (1 heure)
- refresh_token : Token de rafraîchissement (30 jours)
- Configuration sécurisée :
  - httponly=True
  - secure=True
  - samesite="lax"
  - max_age configuré selon le type de token

## Autorisation

### Rôles utilisateur
- Administrateur
- Enseignant
- Élève
- Parent

### Permissions
- Granularité fine par ressource
- Vérification systématique
- Journalisation des accès

## Protection des données

### Données sensibles
- Chiffrement en base de données
- Masquage des données sensibles dans les logs
- Suppression sécurisée

### RGPD
- Consentement explicite
- Droit à l'oubli
- Export des données
- Journalisation des accès

## Sécurité de l'API

### Protection des endpoints
- Rate limiting
- Validation des entrées
- Protection CSRF
- En-têtes de sécurité

### Bonnes pratiques
- Validation Pydantic
- Échappement des données
- Prévention des injections SQL
- Protection XSS

## Bonnes pratiques

### Développement
```python
# Exemple de validation d'entrée
from pydantic import BaseModel, constr

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: constr(min_length=8)
```

### Configuration
```python
# Exemple de configuration sécurisée
SECURITY_CONFIG = {
    'JWT_SECRET_KEY': os.environ['JWT_SECRET_KEY'],
    'JWT_ALGORITHM': 'HS256',
    'JWT_EXPIRATION_DELTA': timedelta(hours=24),
    'PASSWORD_RESET_TIMEOUT': 3600,
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_TIME': 300
}
```

### Déploiement
```bash
# Vérification des vulnérabilités
safety check

# Scan des dépendances
pip-audit

# Test de pénétration
owasp-zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true'
```

## Audit de sécurité

### Checklist de sécurité
- [ ] Mise à jour des dépendances
- [ ] Scan de vulnérabilités
- [ ] Test de pénétration
- [ ] Revue de code sécurité
- [ ] Vérification des logs

### Outils recommandés
- Safety (vulnérabilités Python)
- Bandit (analyse statique)
- OWASP ZAP (test de pénétration)
- SQLMap (test injection SQL)

### Procédures d'incident
1. Détection et alerte
2. Évaluation et triage
3. Confinement
4. Éradication
5. Récupération
6. Leçons apprises

## Ressources

### Documentation
- [OWASP Top 10](https://owasp.org/Top10/)
- [RGPD](https://www.cnil.fr/fr/rgpd)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

### Contact sécurité
- Email : security@mathakine.fr
- Bug Bounty : [huntr.dev/mathakine](https://huntr.dev/mathakine)

---

*Dernière mise à jour : 15 juin 2025* 