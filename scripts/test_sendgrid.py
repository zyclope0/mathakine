#!/usr/bin/env python3
"""
Script de vérification SendGrid - Envoie un email de test.
Usage:
  python scripts/test_sendgrid.py [email]              # Email simple
  python scripts/test_sendgrid.py [email] --verify     # Template vérification inscription
  python scripts/test_sendgrid.py [email] --reset      # Template mot de passe oublié
"""

import os
import sys
from pathlib import Path

# Charger .env depuis la racine du projet
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
env_path = root / ".env"
if env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(env_path, override=False)

api_key = os.getenv("SENDGRID_API_KEY")
from_email = os.getenv("SENDGRID_FROM_EMAIL", "no-reply@mathakine.fun")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

args = [a for a in sys.argv[1:] if a.startswith("--")]
plain_args = [a for a in sys.argv[1:] if not a.startswith("--")]
to_email = plain_args[0] if plain_args and "@" in plain_args[0] else from_email
template = "--verify" in args or "--reset" in args

if not api_key:
    print("ERREUR: SENDGRID_API_KEY non definie dans .env")
    sys.exit(1)

if "@" not in to_email:
    print(
        "Usage: python scripts/test_sendgrid.py ton_email@example.com [--verify|--reset]"
    )
    sys.exit(1)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail

    from app.services.email_service import EmailService

    if template:
        token = "test_token_preview_123"
        username = "PadawanTest"
        if "--reset" in args:
            sent = EmailService.send_password_reset_email(
                to_email, username, token, frontend_url
            )
            print("OK - Email reset-password envoye" if sent else "ECHEC")
        else:
            sent = EmailService.send_verification_email(
                to_email, username, token, frontend_url
            )
            print("OK - Email verification envoye" if sent else "ECHEC")
        print(f"   À: {to_email}")
        print(f"   Template: thème Jedi unifié")
    else:
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject="Test SendGrid - Mathakine",
            plain_text_content="Email de test. Si tu reçois ce message, la configuration fonctionne.",
        )
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        print(f"OK - Email envoye (status {response.status_code})")
        print(f"   De: {from_email}")
        print(f"   A: {to_email}")
except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
