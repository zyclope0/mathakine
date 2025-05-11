"""
Script pour corriger la séquence d'auto-incrémentation de la table attempts
Ce script détecte et restaure la séquence PostgreSQL pour le champ id de la table attempts.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv
from loguru import logger

# Ajouter le répertoire parent au chemin
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration du logger
logger.remove()
logger.add(sys.stderr, level="INFO")

# Charger les variables d'environnement
load_dotenv()



def fix_attempts_sequence():
    """Corrige la séquence d'auto-incrémentation de la table attempts"""
    # Récupérer l'URL de connexion à la base de données
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.error("La variable d'environnement DATABASE_URL n'est pas définie")
        return False

    logger.info(f"Connexion à PostgreSQL: {database_url.split('@')[1]}")

    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Vérifier si la table existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name
            = 'attempts')")
        table_exists = cursor.fetchone()[0]

        if not table_exists:
            logger.error("La table 'attempts' n'existe pas")
            return False

        # 1. Vérifier si la séquence existe déjà
        cursor.execute("SELECT EXISTS (SELECT FROM pg_sequences WHERE sequencename
            = 'attempts_id_seq')")
        sequence_exists = cursor.fetchone()[0]

        if not sequence_exists:
            logger.warning("La séquence 'attempts_id_seq' n'existe pas, création...")

            # Créer la séquence
            cursor.execute("CREATE SEQUENCE attempts_id_seq")

            # Modifier la colonne id pour utiliser la séquence
            cursor.execute("ALTER TABLE attempts ALTER COLUMN id SET DEFAULT nextval('attempts_id_seq')")

            logger.success("Séquence 'attempts_id_seq' créée avec succès")
        else:
            logger.info("La séquence 'attempts_id_seq' existe déjà")

        # 2. Trouver la valeur maximale actuelle de l'id
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM attempts")
        max_id = cursor.fetchone()[0]

        # 3. Réinitialiser la séquence à cette valeur
        cursor.execute(f"ALTER SEQUENCE attempts_id_seq RESTART WITH {max_id + 1}")

        # 4. Confirmer les changements
        conn.commit()

        logger.success(f"Séquence 'attempts_id_seq' réinitialisée à {max_id + 1}")

        # Vérification additionnelle si la colonne id est correctement configurée
        cursor.execute("SELECT column_default FROM information_schema.columns WHERE table_name
            = 'attempts' AND column_name = 'id'")
        column_default = cursor.fetchone()[0]

        if column_default is None or 'nextval' not in str(column_default):
            logger.warning("Configuration de l'auto-incrémentation pour la colonne id...")

            # Modifier la colonne id pour utiliser la séquence
            cursor.execute("ALTER TABLE attempts ALTER COLUMN id SET DEFAULT nextval('attempts_id_seq')")
            conn.commit()

            logger.success("Colonne id configurée pour utiliser la séquence")
        else:
            logger.info(f"La colonne id est correctement configurée avec: {column_default}")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la correction de la séquence: {e}")
        return False


if __name__ == "__main__":
    logger.info("Correction de la séquence d'auto-incrémentation de la table attempts")

    if fix_attempts_sequence():
        logger.success("Correction terminée avec succès")
        sys.exit(0)
    else:
        logger.error("La correction a échoué")
        sys.exit(1)
