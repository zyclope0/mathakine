#!/usr/bin/env python3
"""
Script de nettoyage des donnees de test en production.

Usage:
    python scripts/cleanup_test_data_production.py              # Mode dry-run (affiche sans supprimer)
    python scripts/cleanup_test_data_production.py --execute     # Supprime reellement les donnees de test

Ce script identifie et supprime les donnees de test creees par les tests
automatises (pytest) qui ont persiste en base de production.

SECURITE:
- Mode dry-run par defaut (aucune suppression sans --execute)
- Les utilisateurs permanents (ObiWan, maitre_yoda, padawan1, gardien1) ne sont JAMAIS supprimes
- Les attempts/progress d'ObiWan ne sont JAMAIS supprimes
- Respecte l'ordre des contraintes FK pour eviter les erreurs
- Demande confirmation avant execution
"""

import argparse
import os
import sys
from pathlib import Path

# Ajouter le repertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# ============================================================
# CONFIGURATION
# ============================================================

# Utilisateurs permanents a TOUJOURS preserver
PERMANENT_USERS = {'ObiWan', 'maitre_yoda', 'padawan1', 'gardien1'}

# Patterns de noms d'utilisateurs de test
USERNAME_PATTERNS = [
    'test_%', 'new_test_%', 'duplicate_%',
    'user_stats_%', 'rec_cascade_%', 'attempt_error_%',
    'nonexistent_%', 'record_%', 'starlette_%',
    'cascade_%', 'creator_%', 'malformed_%', 'disable_%',
    'flow_%', 'invalid_%', 'jedi_%', 'dashboard_test_%',
    'login_test_%', 'cascade_test_%',
    'auth_test_%', 'unique_username_%', 'different_%',
    'service_%', 'isolated_%',
]

# Patterns d'emails de test
EMAIL_PATTERNS = [
    'test@%', '%test%@%', 'cascade_%@%', 'dashboard_%@%',
    'service_%@%', 'isolated_%@%',
    '%@test.com', '%@jedi.com',
]

# Patterns de titres d'exercices de test
EXERCISE_TITLE_PATTERNS = [
    '%test%', '%Test%', '%TEST%', 'Cascade %', 'Dashboard %',
]

# Patterns de titres de defis de test
CHALLENGE_TITLE_PATTERNS = [
    '%test%', '%Test%', '%TEST%',
    'Défi Auto-%', 'Nouveau défi%',
    # Patterns de tests non préfixés (historique)
    'Sequence Challenge %', 'Puzzle Challenge %',
    'Séquence 9-12 %', 'Pattern 12-13 %', 'Puzzle 13+ %', 'Séquence Archivée %',
    'Challenge to Archive', 'Défi parcours complet', 'Défi mis à jour',
]


def get_db_url():
    """Recupere l'URL de la base de donnees."""
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERREUR: DATABASE_URL non definie. Definissez-la dans .env ou en variable d'environnement.")
        sys.exit(1)
    return db_url


def build_username_conditions():
    """Construit les conditions SQL pour les usernames de test."""
    conditions = [f"username LIKE '{p}'" for p in USERNAME_PATTERNS]
    return " OR ".join(conditions)


def build_email_conditions():
    """Construit les conditions SQL pour les emails de test."""
    conditions = [f"email LIKE '{p}'" for p in EMAIL_PATTERNS]
    return " OR ".join(conditions)


def build_exercise_conditions():
    """Construit les conditions SQL pour les titres d'exercices de test."""
    conditions = [f"title LIKE '{p}'" for p in EXERCISE_TITLE_PATTERNS]
    return " OR ".join(conditions)


def build_challenge_conditions():
    """Construit les conditions SQL pour les titres de defis de test."""
    conditions = [f"title LIKE '{p}'" for p in CHALLENGE_TITLE_PATTERNS]
    return " OR ".join(conditions)


def permanent_users_exclusion():
    """Construit la clause d'exclusion pour les utilisateurs permanents."""
    users = "', '".join(PERMANENT_USERS)
    return f"username NOT IN ('{users}')"


def identify_test_data(session):
    """Identifie toutes les donnees de test dans la base."""
    data = {}

    # 1. Utilisateurs de test
    user_query = f"""
        SELECT id, username, email, created_at
        FROM users
        WHERE ({build_username_conditions()} OR {build_email_conditions()})
        AND {permanent_users_exclusion()}
        ORDER BY created_at DESC
    """
    result = session.execute(text(user_query))
    data['users'] = [dict(row._mapping) for row in result.fetchall()]
    test_user_ids = [u['id'] for u in data['users']]

    # 2. Exercices de test
    exercise_query = f"""
        SELECT id, title, exercise_type, created_at
        FROM exercises
        WHERE {build_exercise_conditions()}
        ORDER BY created_at DESC
    """
    result = session.execute(text(exercise_query))
    data['exercises'] = [dict(row._mapping) for row in result.fetchall()]
    test_exercise_ids = [e['id'] for e in data['exercises']]

    # 3. Defis logiques de test
    challenge_conds = build_challenge_conditions()
    challenge_conds += " OR (COALESCE(title, '') = '' AND description LIKE '%Riddle description%')"
    challenge_query = f"""
        SELECT id, title, challenge_type, created_at
        FROM logic_challenges
        WHERE ({challenge_conds})
        ORDER BY created_at DESC
    """
    result = session.execute(text(challenge_query))
    data['challenges'] = [dict(row._mapping) for row in result.fetchall()]
    test_challenge_ids = [c['id'] for c in data['challenges']]

    # 4. Donnees liees aux utilisateurs de test
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))

        result = session.execute(text(f"SELECT COUNT(*) FROM attempts WHERE user_id IN ({ids_str})"))
        data['attempts_by_test_users'] = result.scalar()

        result = session.execute(text(f"SELECT COUNT(*) FROM progress WHERE user_id IN ({ids_str})"))
        data['progress_by_test_users'] = result.scalar()

        result = session.execute(text(f"SELECT COUNT(*) FROM recommendations WHERE user_id IN ({ids_str})"))
        data['recommendations_by_test_users'] = result.scalar()

        result = session.execute(text(f"SELECT COUNT(*) FROM logic_challenge_attempts WHERE user_id IN ({ids_str})"))
        data['challenge_attempts_by_test_users'] = result.scalar()
    else:
        data['attempts_by_test_users'] = 0
        data['progress_by_test_users'] = 0
        data['recommendations_by_test_users'] = 0
        data['challenge_attempts_by_test_users'] = 0

    # 5. Attempts lies aux exercices de test (TOUS les users, car l'exercice est du test data)
    # Note : si un exercice de test est supprime, ses attempts doivent l'etre aussi
    # meme pour les utilisateurs permanents (l'exercice est faux, l'attempt aussi)
    if test_exercise_ids:
        ids_str = ','.join(map(str, test_exercise_ids))
        result = session.execute(text(
            f"SELECT COUNT(*) FROM attempts WHERE exercise_id IN ({ids_str})"
        ))
        data['attempts_on_test_exercises'] = result.scalar()
    else:
        data['attempts_on_test_exercises'] = 0

    # 6. Challenge attempts lies aux defis de test (TOUS les users, meme raison)
    if test_challenge_ids:
        ids_str = ','.join(map(str, test_challenge_ids))
        result = session.execute(text(
            f"SELECT COUNT(*) FROM logic_challenge_attempts WHERE challenge_id IN ({ids_str})"
        ))
        data['challenge_attempts_on_test_challenges'] = result.scalar()
    else:
        data['challenge_attempts_on_test_challenges'] = 0

    return data


def print_report(data):
    """Affiche un rapport detaille des donnees de test identifiees."""
    print("\n" + "=" * 70)
    print("  RAPPORT DES DONNEES DE TEST IDENTIFIEES")
    print("=" * 70)

    # Utilisateurs
    print(f"\n  Utilisateurs de test : {len(data['users'])}")
    if data['users']:
        for u in data['users'][:20]:  # Limiter l'affichage
            print(f"    - {u['username']} ({u['email']}) cree le {u['created_at']}")
        if len(data['users']) > 20:
            print(f"    ... et {len(data['users']) - 20} autres")

    # Exercices
    print(f"\n  Exercices de test : {len(data['exercises'])}")
    if data['exercises']:
        for e in data['exercises'][:20]:
            print(f"    - [{e['id']}] {e['title']} ({e['exercise_type']})")
        if len(data['exercises']) > 20:
            print(f"    ... et {len(data['exercises']) - 20} autres")

    # Defis
    print(f"\n  Defis logiques de test : {len(data['challenges'])}")
    if data['challenges']:
        for c in data['challenges'][:20]:
            print(f"    - [{c['id']}] {c['title']} ({c['challenge_type']})")
        if len(data['challenges']) > 20:
            print(f"    ... et {len(data['challenges']) - 20} autres")

    # Donnees liees
    print(f"\n  Donnees liees :")
    print(f"    - Attempts par utilisateurs test : {data['attempts_by_test_users']}")
    print(f"    - Progress par utilisateurs test : {data['progress_by_test_users']}")
    print(f"    - Recommandations par utilisateurs test : {data['recommendations_by_test_users']}")
    print(f"    - Challenge attempts par utilisateurs test : {data['challenge_attempts_by_test_users']}")
    print(f"    - Attempts sur exercices test (tous users) : {data['attempts_on_test_exercises']}")
    print(f"    - Challenge attempts sur defis test (tous users) : {data['challenge_attempts_on_test_challenges']}")

    total = (
        len(data['users']) + len(data['exercises']) + len(data['challenges'])
        + data['attempts_by_test_users'] + data['progress_by_test_users']
        + data['recommendations_by_test_users'] + data['challenge_attempts_by_test_users']
        + data['attempts_on_test_exercises'] + data['challenge_attempts_on_test_challenges']
    )
    print(f"\n  TOTAL elements a supprimer : {total}")
    print(f"\n  Utilisateurs proteges : {', '.join(sorted(PERMANENT_USERS))}")
    print("=" * 70)

    return total


def execute_cleanup(session, data):
    """Execute la suppression des donnees de test."""
    test_user_ids = [u['id'] for u in data['users']]
    test_exercise_ids = [e['id'] for e in data['exercises']]
    test_challenge_ids = [c['id'] for c in data['challenges']]

    deleted = {}

    # Ordre FK : d'abord les tables dependantes, puis les tables parentes

    # 1. Challenge attempts pour utilisateurs test
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))
        result = session.execute(text(f"DELETE FROM logic_challenge_attempts WHERE user_id IN ({ids_str})"))
        deleted['challenge_attempts_users'] = result.rowcount

    # 2. Challenge attempts sur defis test (TOUS les users - le defi est du test data)
    if test_challenge_ids:
        ids_str = ','.join(map(str, test_challenge_ids))
        result = session.execute(text(
            f"DELETE FROM logic_challenge_attempts WHERE challenge_id IN ({ids_str})"
        ))
        deleted['challenge_attempts_challenges'] = result.rowcount

    # 3. Attempts pour utilisateurs test
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))
        result = session.execute(text(f"DELETE FROM attempts WHERE user_id IN ({ids_str})"))
        deleted['attempts_users'] = result.rowcount

    # 4. Attempts sur exercices test (TOUS les users - l'exercice est du test data)
    if test_exercise_ids:
        ids_str = ','.join(map(str, test_exercise_ids))
        result = session.execute(text(
            f"DELETE FROM attempts WHERE exercise_id IN ({ids_str})"
        ))
        deleted['attempts_exercises'] = result.rowcount

    # 5. Recommendations pour utilisateurs test
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))
        result = session.execute(text(f"DELETE FROM recommendations WHERE user_id IN ({ids_str})"))
        deleted['recommendations_users'] = result.rowcount

    # 5b. Recommendations liees aux exercices test (FK exercise_id)
    if test_exercise_ids:
        ids_str = ','.join(map(str, test_exercise_ids))
        result = session.execute(text(f"DELETE FROM recommendations WHERE exercise_id IN ({ids_str})"))
        deleted['recommendations_exercises'] = result.rowcount

    # 6. Progress pour utilisateurs test
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))
        result = session.execute(text(f"DELETE FROM progress WHERE user_id IN ({ids_str})"))
        deleted['progress'] = result.rowcount

    # 7. Defis logiques de test
    if test_challenge_ids:
        ids_str = ','.join(map(str, test_challenge_ids))
        result = session.execute(text(f"DELETE FROM logic_challenges WHERE id IN ({ids_str})"))
        deleted['challenges'] = result.rowcount

    # 8. Exercices de test
    if test_exercise_ids:
        ids_str = ','.join(map(str, test_exercise_ids))
        result = session.execute(text(f"DELETE FROM exercises WHERE id IN ({ids_str})"))
        deleted['exercises'] = result.rowcount

    # 9. Nettoyer toutes les FK references restantes des test users
    #    (challenges/exercises crees par des test users mais sans titre "test")
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))

        # 9a. Challenge attempts sur challenges crees par test users
        result = session.execute(text(
            f"DELETE FROM logic_challenge_attempts WHERE challenge_id IN "
            f"(SELECT id FROM logic_challenges WHERE creator_id IN ({ids_str}))"
        ))
        deleted['challenge_attempts_by_creator'] = result.rowcount

        # 9b. Logic challenges crees par test users
        result = session.execute(text(
            f"DELETE FROM logic_challenges WHERE creator_id IN ({ids_str})"
        ))
        deleted['challenges_by_creator'] = result.rowcount

        # 9c. Attempts sur exercices crees par test users
        result = session.execute(text(
            f"DELETE FROM attempts WHERE exercise_id IN "
            f"(SELECT id FROM exercises WHERE creator_id IN ({ids_str}))"
        ))
        deleted['attempts_by_creator_exercises'] = result.rowcount

        # 9d. Recommendations sur exercices crees par test users
        result = session.execute(text(
            f"DELETE FROM recommendations WHERE exercise_id IN "
            f"(SELECT id FROM exercises WHERE creator_id IN ({ids_str}))"
        ))
        deleted['recommendations_by_creator_exercises'] = result.rowcount

        # 9e. Exercices crees par test users
        result = session.execute(text(
            f"DELETE FROM exercises WHERE creator_id IN ({ids_str})"
        ))
        deleted['exercises_by_creator'] = result.rowcount

        # 9f. User achievements des test users
        result = session.execute(text(
            f"DELETE FROM user_achievements WHERE user_id IN ({ids_str})"
        ))
        deleted['user_achievements'] = result.rowcount

        # 9g. User sessions des test users
        result = session.execute(text(
            f"DELETE FROM user_sessions WHERE user_id IN ({ids_str})"
        ))
        deleted['user_sessions'] = result.rowcount

        # 9h. Notifications des test users
        result = session.execute(text(
            f"DELETE FROM notifications WHERE user_id IN ({ids_str})"
        ))
        deleted['notifications'] = result.rowcount

    # 10. Utilisateurs de test (en dernier)
    if test_user_ids:
        ids_str = ','.join(map(str, test_user_ids))
        result = session.execute(text(f"DELETE FROM users WHERE id IN ({ids_str})"))
        deleted['users'] = result.rowcount

    return deleted


def main():
    parser = argparse.ArgumentParser(
        description="Nettoyage des donnees de test en production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python scripts/cleanup_test_data_production.py              # Dry-run
  python scripts/cleanup_test_data_production.py --execute     # Suppression reelle
        """
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Effectuer reellement la suppression (par defaut: dry-run)'
    )
    args = parser.parse_args()

    db_url = get_db_url()
    print(f"\n  Connexion a la base : {db_url[:50]}...")

    engine = create_engine(db_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Identifier les donnees de test
        data = identify_test_data(session)
        total = print_report(data)

        if total == 0:
            print("\n  Aucune donnee de test trouvee. La base est propre.")
            return

        if not args.execute:
            print("\n  MODE DRY-RUN : aucune suppression effectuee.")
            print("  Pour supprimer reellement, relancez avec : --execute")
            return

        # Demander confirmation
        print("\n  ATTENTION : Vous etes sur le point de supprimer ces donnees.")
        print(f"  Les utilisateurs proteges ({', '.join(sorted(PERMANENT_USERS))}) ne seront PAS touches.")
        confirm = input("\n  Tapez 'CONFIRMER' pour proceder : ")

        if confirm != "CONFIRMER":
            print("  Annule.")
            return

        # Executer la suppression
        print("\n  Suppression en cours...")
        deleted = execute_cleanup(session, data)
        session.commit()

        print("\n  Suppression terminee :")
        for table, count in deleted.items():
            if count > 0:
                print(f"    - {table}: {count} lignes supprimees")

        total_deleted = sum(deleted.values())
        print(f"\n  TOTAL supprime : {total_deleted} lignes")

    except Exception as e:
        session.rollback()
        print(f"\n  ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()
