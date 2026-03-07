#!/usr/bin/env python3
"""
Vérifie qu'un utilisateur supprimé (ex: Luc2) n'existe plus et qu'il n'y a pas d'enregistrements orphelins.

Usage:
  python scripts/verify_user_deletion.py Luc2
  python scripts/verify_user_deletion.py  # utilise Luc2 par défaut
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

# Éviter d'utiliser la base de test
if "TESTING" not in os.environ:
    os.environ["TESTING"] = "false"


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "Luc2"
    print(f"\n=== Vérification suppression utilisateur '{username}' ===\n")

    from sqlalchemy import create_engine, text
    from app.core.config import settings

    url = settings.SQLALCHEMY_DATABASE_URL
    engine = create_engine(url)

    with engine.connect() as conn:
        # 1. L'utilisateur n'existe plus
        r = conn.execute(text("SELECT id, username FROM users WHERE username = :u"), {"u": username})
        rows = r.fetchall()
        if rows:
            print(f"  ERREUR: L'utilisateur '{username}' existe encore (id={rows[0][0]})")
            return 1
        print(f"  OK: L'utilisateur '{username}' n'existe plus dans users")

        # 2. Entrée dans l'audit log
        r = conn.execute(
            text("""
                SELECT id, action, resource_type, resource_id, details, created_at
                FROM admin_audit_logs
                WHERE action = 'user_delete'
                AND details::text LIKE :pattern
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"pattern": f"%{username}%"},
        )
        audit = r.fetchone()
        if audit:
            print(f"  OK: Action user_delete enregistrée dans l'audit (id={audit[0]}, {audit[5]})")
        else:
            print(f"  INFO: Aucune entrée audit user_delete trouvée pour '{username}' (peut-être supprimé avant l'audit)")

        # 3. Pas d'enregistrements orphelins (user_id non NULL mais inexistant dans users)
        # Note: feedback_reports et edtech_events ont ON DELETE SET NULL → user_id=NULL est voulu
        tables = [
            ("attempts", "user_id"),
            ("progress", "user_id"),
            ("user_sessions", "user_id"),
            ("user_achievements", "user_id"),
            ("recommendations", "user_id"),
            ("daily_challenges", "user_id"),
            ("logic_challenge_attempts", "user_id"),
            ("feedback_reports", "user_id"),  # nullable, ON DELETE SET NULL
            ("notifications", "user_id"),
            ("edtech_events", "user_id"),  # nullable, ON DELETE SET NULL
            ("diagnostic_results", "user_id"),
        ]
        orphans = []
        for table, col in tables:
            try:
                r = conn.execute(
                    text(f"""
                        SELECT COUNT(*) FROM {table} t
                        WHERE t.{col} IS NOT NULL
                        AND NOT EXISTS (SELECT 1 FROM users u WHERE u.id = t.{col})
                    """)
                )
                count = r.scalar()
                if count and count > 0:
                    orphans.append((table, count))
            except Exception:
                pass  # table peut ne pas exister

        if orphans:
            print(f"  ERREUR: Enregistrements orphelins détectés:")
            for t, c in orphans:
                print(f"    - {t}: {c} enregistrement(s)")
            return 1
        print(f"  OK: Aucun enregistrement orphelin (cascade correcte)")

    print("\n=== Vérification OK ===\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
