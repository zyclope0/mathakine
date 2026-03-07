#!/usr/bin/env python3
"""
Nettoie les données aberrantes dans edtech_events (timeToFirstAttemptMs < 0).

Les événements first_attempt avec un temps négatif sont corrigés en retirant
la clé timeToFirstAttemptMs du payload (l'événement reste, seule la métrique invalide est supprimée).

Usage:
  python scripts/cleanup_edtech_aberrant_data.py           # dry-run, affiche ce qui serait modifié
  python scripts/cleanup_edtech_aberrant_data.py --apply   # applique les modifications
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

if "TESTING" not in os.environ:
    os.environ["TESTING"] = "false"


def main():
    apply_changes = "--apply" in sys.argv
    if not apply_changes:
        print("\n=== Mode dry-run (ajoutez --apply pour exécuter) ===\n")

    from sqlalchemy import create_engine, text
    from app.core.config import settings

    url = settings.SQLALCHEMY_DATABASE_URL
    # Afficher la cible (sans mot de passe)
    from urllib.parse import urlparse
    parsed = urlparse(url)
    target = f"{parsed.hostname or 'localhost'}:{parsed.port or 5432}/{parsed.path.lstrip('/') or '?'}"
    print(f"Base ciblée : {target}\n")

    engine = create_engine(url)

    with engine.connect() as conn:
        # Diagnostic : compter les first_attempt avec timeToFirstAttemptMs
        r = conn.execute(
            text("""
                SELECT COUNT(*) FROM edtech_events
                WHERE event = 'first_attempt' AND payload ? 'timeToFirstAttemptMs'
            """)
        )
        total_with_time = r.scalar() or 0
        print(f"Événements first_attempt avec timeToFirstAttemptMs : {total_with_time}")

        # Échantillon des valeurs (pour diagnostic)
        r2 = conn.execute(
            text("""
                SELECT payload->>'timeToFirstAttemptMs' as val
                FROM edtech_events
                WHERE event = 'first_attempt' AND payload ? 'timeToFirstAttemptMs'
                ORDER BY created_at DESC
                LIMIT 10
            """)
        )
        samples = [row[0] for row in r2.fetchall()]
        if samples:
            print(f"Échantillon (10 derniers) : {samples}")

        # Trouver les événements first_attempt avec timeToFirstAttemptMs < 0
        r = conn.execute(
            text("""
                SELECT id, user_id, event, payload, created_at
                FROM edtech_events
                WHERE event = 'first_attempt'
                AND payload ? 'timeToFirstAttemptMs'
                AND (payload->>'timeToFirstAttemptMs')::numeric < 0
                ORDER BY id
            """)
        )
        rows = r.fetchall()

        if not rows:
            print("Aucune donnée aberrante trouvée (timeToFirstAttemptMs < 0).")
            return 0

        print(f"Événements first_attempt avec temps négatif : {len(rows)}")
        for row in rows:
            print(f"  id={row[0]} user_id={row[1]} payload={row[3]} created_at={row[4]}")

        if apply_changes:
            # Retirer la clé timeToFirstAttemptMs du payload
            result = conn.execute(
                text("""
                    UPDATE edtech_events
                    SET payload = payload - 'timeToFirstAttemptMs'
                    WHERE event = 'first_attempt'
                    AND payload ? 'timeToFirstAttemptMs'
                    AND (payload->>'timeToFirstAttemptMs')::numeric < 0
                """)
            )
            conn.commit()
            print(f"\n{result.rowcount} enregistrement(s) corrigé(s).")
        else:
            print(f"\nPour corriger ces {len(rows)} enregistrement(s), relancez avec --apply")

    return 0


if __name__ == "__main__":
    sys.exit(main())
