"""
Templates emails Mathakine — thème spatial sobre.
Design unifié, ergonomique et accessible pour tous les clients email.
"""

# Couleurs du thème (compatible clients email)
THEME = {
    "bg_dark": "#0f172a",  # Fond header
    "bg_content": "#ffffff",  # Corps du message
    "accent": "#06b6d4",  # Cyan accent
    "accent_hover": "#0891b2",
    "gold": "#f59e0b",  # Mise en avant secondaire
    "text_dark": "#1e293b",
    "text_light": "#e2e8f0",
    "text_muted": "#64748b",
    "border": "#e2e8f0",
}


def _base_styles() -> str:
    """Styles de base partagés."""
    return f"""
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: {THEME["text_dark"]}; margin: 0; padding: 0; -webkit-text-size-adjust: 100%; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, {THEME["bg_dark"]} 0%, #1e293b 100%); color: {THEME["text_light"]}; padding: 32px 24px; text-align: center; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: 0.05em; }}
        .header .subtitle {{ margin: 8px 0 0; font-size: 14px; opacity: 0.9; }}
        .content {{ background: {THEME["bg_content"]}; padding: 32px 24px; border: 1px solid {THEME["border"]}; border-top: none; border-radius: 0 0 12px 12px; }}
        .content p {{ margin: 0 0 16px; }}
        .cta-wrapper {{ text-align: center; margin: 28px 0; }}
        .cta {{ display: inline-block; padding: 14px 32px; background: {THEME["accent"]}; color: white !important; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; }}
        .link-fallback {{ margin: 20px 0; padding: 12px; background: #f8fafc; border-radius: 6px; word-break: break-all; font-size: 13px; color: {THEME["accent"]}; }}
        .expiry {{ color: {THEME["gold"]}; font-weight: 600; }}
        .footer {{ margin-top: 24px; padding-top: 20px; border-top: 1px solid {THEME["border"]}; font-size: 12px; color: {THEME["text_muted"]}; text-align: center; }}
    """


def _wrapper(header_title: str, header_subtitle: str, body_html: str) -> str:
    """Enveloppe commune HTML."""
    return f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{header_title}</title>
    <style>{_base_styles()}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Mathakine</h1>
            <p class="subtitle">{header_subtitle}</p>
        </div>
        <div class="content">
            {body_html}
        </div>
    </div>
    <div class="container">
        <div class="footer">
            <p>© 2026 Mathakine — Plateforme d'apprentissage des mathématiques</p>
        </div>
    </div>
</body>
</html>
"""


def verification_email_html(username: str, verification_link: str) -> str:
    """
    Email de vérification à l'inscription.
    Ton accueillant, clair, CTA prominent.
    """
    body = f"""
            <p>Bonjour <strong>{username}</strong>,</p>
            <p>Bienvenue sur Mathakine ! 🌟</p>
            <p>Ton inscription est presque terminée. Clique sur le bouton ci-dessous pour activer ton compte et commencer à t'entraîner.</p>
            <div class="cta-wrapper">
                <a href="{verification_link}" class="cta">Activer mon compte</a>
            </div>
            <p>Le lien ne fonctionne pas ? Copie-colle cette adresse dans ton navigateur :</p>
            <div class="link-fallback">{verification_link}</div>
            <p class="expiry">⏱ Ce lien expire dans 24 heures.</p>
            <p style="margin-top: 24px; font-size: 14px; color: {THEME["text_muted"]};">Tu ne t'es pas inscrit ? Tu peux ignorer cet email en toute sécurité.</p>
        """
    return _wrapper(
        header_title="Bienvenue — Mathakine",
        header_subtitle="Vérification de ton adresse email",
        body_html=body,
    )


def verification_email_text(username: str, verification_link: str) -> str:
    """Version texte brute de l'email de vérification."""
    return f"""Bonjour {username},

Bienvenue sur Mathakine !

Ton inscription est presque terminée. Active ton compte en cliquant sur ce lien :
{verification_link}

Ce lien expire dans 24 heures.

Tu ne t'es pas inscrit ? Tu peux ignorer cet email.

© 2026 Mathakine — Plateforme d'apprentissage des mathématiques"""


def password_reset_email_html(username: str, reset_link: str) -> str:
    """
    Email de réinitialisation mot de passe.
    Ton rassurant, urgence claire, CTA évident.
    """
    body = f"""
            <p>Bonjour <strong>{username}</strong>,</p>
            <p>Une demande de réinitialisation de mot de passe a été faite pour ton compte Mathakine.</p>
            <p>Clique sur le bouton ci-dessous pour définir un nouveau mot de passe :</p>
            <div class="cta-wrapper">
                <a href="{reset_link}" class="cta">Réinitialiser mon mot de passe</a>
            </div>
            <p>Le bouton ne fonctionne pas ? Copie cette adresse :</p>
            <div class="link-fallback">{reset_link}</div>
            <p class="expiry">⏱ Ce lien expire dans 1 heure.</p>
            <p style="margin-top: 24px; font-size: 14px; color: {THEME["text_muted"]};">Tu n'as pas demandé ce changement ? Ignore cet email — ton mot de passe restera inchangé.</p>
        """
    return _wrapper(
        header_title="Réinitialisation — Mathakine",
        header_subtitle="Réinitialisation de mot de passe",
        body_html=body,
    )


def password_reset_email_text(username: str, reset_link: str) -> str:
    """Version texte brute de l'email de reset password."""
    return f"""Bonjour {username},

Une demande de réinitialisation de mot de passe a été faite pour ton compte Mathakine.

Clique sur ce lien pour définir un nouveau mot de passe :
{reset_link}

Ce lien expire dans 1 heure.

Tu n'as pas demandé ce changement ? Ignore cet email.

© 2026 Mathakine — Plateforme d'apprentissage des mathématiques"""
