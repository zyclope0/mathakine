#!/usr/bin/env python3
"""Script safe avec timeout pour eviter blocage"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import signal
from contextlib import contextmanager
from dotenv import load_dotenv

# Charger .env
load_dotenv()

# Timeout handler
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Script timeout apres 30 secondes")

@contextmanager
def time_limit(seconds):
    """Context manager pour limiter le temps d'execution"""
    if sys.platform == 'win32':
        # Sur Windows, pas de signal.SIGALRM, on skip le timeout
        yield
    else:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)

def main():
    print("=== NETTOYAGE ET SEED SECURISE ===\n")
    
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import NullPool
    import os
    
    # Connexion sans pool pour eviter les verrous
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERREUR: DATABASE_URL non definie")
        return 1
    
    # SÉCURITÉ : Vérifier qu'on n'est pas en production
    is_production = (
        os.getenv("NODE_ENV") == "production" or 
        os.getenv("ENVIRONMENT") == "production" or
        os.getenv("MATH_TRAINER_PROFILE") == "prod" or
        "render.com" in database_url.lower() or
        "production" in database_url.lower()
    )
    
    if is_production:
        print("🚨 ATTENTION: Ce script ne peut pas être exécuté en production!")
        print(f"   DATABASE_URL={database_url[:50]}...")
        print("   Pour forcer l'exécution, définir FORCE_CLEAN=true")
        if os.getenv("FORCE_CLEAN", "").lower() != "true":
            return 1
    
    print(f"Connexion a: {database_url[:50]}...")
    
    # Creer engine sans pool
    engine = create_engine(
        database_url,
        poolclass=NullPool,  # Pas de pool, connexion directe
        connect_args={
            "connect_timeout": 10,
            "options": "-c statement_timeout=10000"  # 10s max par requete
        }
    )
    
    SessionLocal = sessionmaker(bind=engine)
    
    try:
        with time_limit(30):  # 30 secondes max
            db = SessionLocal()
            
            try:
                print("[1/4] Test connexion...")
                result = db.execute(text("SELECT 1")).scalar()
                print(f"  OK: {result}")
                
                print("\n[2/4] Comptage avant nettoyage...")
                ex_before = db.execute(text("SELECT COUNT(*) FROM exercises")).scalar()
                ch_before = db.execute(text("SELECT COUNT(*) FROM logic_challenges")).scalar()
                att_before = db.execute(text("SELECT COUNT(*) FROM attempts")).scalar()
                ch_att_before = db.execute(text("SELECT COUNT(*) FROM logic_challenge_attempts")).scalar()
                print(f"  Exercises: {ex_before}")
                print(f"  Challenges: {ch_before}")
                print(f"  Attempts: {att_before}")
                print(f"  Challenge attempts: {ch_att_before}")
                
                print("\n[3/4] Nettoyage...")
                db.execute(text("DELETE FROM attempts"))
                db.execute(text("DELETE FROM logic_challenge_attempts"))
                db.execute(text("DELETE FROM exercises"))
                db.execute(text("DELETE FROM logic_challenges"))
                db.commit()
                print("  Suppression terminee")
                
                print("\n[4/4] Verification finale...")
                ex_after = db.execute(text("SELECT COUNT(*) FROM exercises")).scalar()
                ch_after = db.execute(text("SELECT COUNT(*) FROM logic_challenges")).scalar()
                print(f"  Exercises: {ex_after}")
                print(f"  Challenges: {ch_after}")
                
                print("\n[SUCCES] Base nettoyee!")
                return 0
                
            except Exception as e:
                print(f"\n[ERREUR OPERATION] {e}")
                db.rollback()
                return 1
            finally:
                db.close()
                print("\n[INFO] Session fermee")
                
    except TimeoutException as e:
        print(f"\n[TIMEOUT] {e}")
        return 1
    except Exception as e:
        print(f"\n[ERREUR CONNEXION] {e}")
        return 1
    finally:
        engine.dispose()
        print("[INFO] Engine dispose")

if __name__ == "__main__":
    exit_code = main()
    print(f"\n=== FIN (code: {exit_code}) ===")
    sys.exit(exit_code)

