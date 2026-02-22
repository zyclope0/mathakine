# Politique de redaction PII et secrets dans les logs

**Date :** 22/02/2026  
**Objectif :** Formaliser les règles pour éviter les fuites de données sensibles dans les logs.

---

## 1. Données à ne jamais logger en clair

| Catégorie | Exemples | Action |
|-----------|----------|--------|
| **Mots de passe** | `password`, `hashed_password`, `new_password` | Ne jamais logger, même hashés |
| **Tokens** | `access_token`, `refresh_token`, `csrf_token`, `email_verification_token` | Remplacer par `[REDACTED]` ou les 4 derniers caractères seulement |
| **Secrets** | `SECRET_KEY`, clés API (OpenAI, SendGrid) | Ne jamais logger |
| **PII identifiantes** | `email`, `full_name` complets | Préférer `user_id` ou `username` pour corrélation ; si email nécessaire, masquer : `j***@example.com` |

---

## 2. Règles par contexte

| Contexte | Règle |
|----------|-------|
| **Exceptions** | `str(e)` ou `traceback` : ne pas inclure si contient body de requête, tokens, ou PII. Utiliser `logger.exception()` sans message détaillé en prod. |
| **Requêtes HTTP** | Ne pas logger le body entier (peut contenir password). Logger path, method, status. |
| **Utilisateur** | Logger `user_id` ou `username` pour corrélation ; éviter `email` en clair. |

---

## 3. Configuration actuelle

- **Sentry** : `send_default_pii=False` (monitoring.py) — aucun PII envoyé par défaut.
- **Loguru** : pas de filtre automatique — discipline manuelle et revue de code.
- **Corrélation** : `request_id` par requête (RequestIdMiddleware) — tag Sentry + header `X-Request-ID` + logs. Permet de retrouver logs associés à un event Sentry.

---

## 4. Checklist revue de code

Avant de merger du code qui ajoute des `logger.*` :

- [ ] Aucun `password`, `hashed_password`, `token` dans le message ou les arguments
- [ ] Aucun `email` ou `full_name` en clair (préférer `user_id`/`username`)
- [ ] Les exceptions loguées ne contiennent pas de body/token dans leur détail

---

## 5. Référence

- OWASP Logging Cheat Sheet : https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- RGPD : minimiser les données personnelles dans les logs
