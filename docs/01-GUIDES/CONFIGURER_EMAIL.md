# 📧 Configurer l'envoi d'emails

Les workflows **inscription** (vérification email) et **mot de passe oublié** envoient des emails. Par défaut, sans configuration, ils sont **simulés** en développement (le flux fonctionne mais aucun mail n'est reçu).

Les emails utilisent un **template thème Jedi** unifié (`app/utils/email_templates.py`), ergonomique et adapté à tous les clients email.

---

## Parcours utilisateur (auth)

| Étape | Emails envoyés | Blocage |
|-------|----------------|---------|
| Inscription | Email de vérification avec lien `/verify-email?token=...` | — |
| Clic sur lien | — | Compte activé (`is_email_verified=true`) |
| Connexion | — | **Bloquée** si email non vérifié (403) |
| Mot de passe oublié | Email avec lien `/reset-password?token=...` | — |

Le lien de vérification est **idempotent** : cliquer plusieurs fois ou rafraîchir la page retourne un succès si le compte est déjà vérifié.

---

## Comportement par défaut

| Contexte       | SMTP/SendGrid configuré ? | Comportement                                      |
|----------------|---------------------------|---------------------------------------------------|
| Développement  | Non                       | Simulation : `True` retourné, aucun email envoyé  |
| Développement  | Oui                       | Emails envoyés                                    |
| Production     | Non                       | Erreur 500 : "Impossible d'envoyer l'email"       |
| Production     | Oui                       | Emails envoyés                                    |

---

## Option 1 : Gmail (rapide pour dev / petit volume)

1. Activer l’[authentification à deux facteurs](https://myaccount.google.com/security) sur ton compte Google.
2. Créer un [mot de passe d’application](https://myaccount.google.com/apppasswords) pour l’app.
3. Ajouter dans ton `.env` :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ton_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=ton_email@gmail.com
SMTP_USE_TLS=true
```

---

## Option 2 : SendGrid (recommandé pour production)

[SendGrid](https://sendgrid.com/) offre un forfait gratuit (≈ 100 emails/jour).

1. Créer un compte sur [sendgrid.com](https://sendgrid.com).
2. **Settings** → **API Keys** → **Create API Key** (avec droits d’envoi).
3. Vérifier / créer un **Sender** dans **Settings** → **Sender Authentication**.
4. Ajouter dans le `.env` :

```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@mathakine.com
```

> **Priorité** : Si `SENDGRID_API_KEY` est défini, SendGrid est utilisé. Sinon, le service bascule sur SMTP.

---

## Option 3 : Brevo (ex-Sendinblue)

[Brevo](https://www.brevo.com/) propose un forfait gratuit (≈ 300 emails/jour).

1. Créer un compte sur [brevo.com](https://www.brevo.com).
2. **SMTP & API** → récupérer les identifiants SMTP.
3. Ajouter dans le `.env` :

```env
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=ton_email@example.com
SMTP_PASSWORD=ta_cle_smtp_brevo
SMTP_FROM_EMAIL=noreply@mathakine.com
SMTP_USE_TLS=true
```

---

## Variables utilisées par le code

| Variable           | Obligatoire     | Description                           |
|-------------------|----------------|---------------------------------------|
| `SENDGRID_API_KEY`| Si SendGrid    | Clé API SendGrid                      |
| `SENDGRID_FROM_EMAIL` | Si SendGrid | Adresse d’expéditeur                  |
| `SMTP_HOST`       | Si SMTP        | Serveur (ex. `smtp.gmail.com`)        |
| `SMTP_PORT`       | Si SMTP        | Port (souvent `587`)                  |
| `SMTP_USER`       | Si SMTP        | Utilisateur SMTP                     |
| `SMTP_PASSWORD`   | Si SMTP        | Mot de passe ou mot de passe d’app    |
| `SMTP_FROM_EMAIL` | Optionnel      | Expéditeur (défaut : `SMTP_USER`)    |
| `SMTP_USE_TLS`    | Optionnel      | `true` (défaut) ou `false`           |

---

## Production (Render)

Sur **Render** → backend → **Environment**, ajouter les mêmes variables (SendGrid ou SMTP) selon ton choix, afin que les emails soient envoyés en production.

---

## Développement local (localhost)

Les liens dans les emails pointent vers `FRONTEND_URL` (souvent `http://localhost:3000`). Certains clients (ex. Gmail) **filtrent** les emails contenant des liens localhost. Si l’email n’arrive pas, le lien est affiché dans les logs du serveur (`[DEV] Si l'email n'arrive pas... copie ce lien : ...`). Alternative : utiliser [ngrok](https://ngrok.com) pour exposer le frontend et définir `FRONTEND_URL=https://xxx.ngrok.io`.

---

## Script de test

```bash
python scripts/test_sendgrid.py ton@email.com           # Email simple
python scripts/test_sendgrid.py ton@email.com --verify # Template inscription
python scripts/test_sendgrid.py ton@email.com --reset  # Template reset
```

## Vérification

Après configuration, redémarrer le serveur et tester le flux « mot de passe oublié » ou « inscription ». Les logs doivent afficher :

```
✅ Email envoyé via SMTP à xxx@example.com depuis ...
```
ou
```
Email envoyé via SendGrid à xxx@example.com
```
