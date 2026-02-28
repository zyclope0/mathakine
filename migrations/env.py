import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ajouter le répertoire parent au sys.path pour pouvoir importer l'app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Import de configuration et modèles de notre application
from app.core.config import settings
from app.db.base import Base
from app.models.achievement import Achievement, UserAchievement
from app.models.attempt import Attempt
from app.models.edtech_event import EdTechEvent
from app.models.exercise import Exercise
from app.models.feedback_report import FeedbackReport
from app.models.legacy_tables import Results, SchemaVersion, Statistics, UserStats
from app.models.logic_challenge import LogicChallenge
from app.models.notification import Notification
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.models.setting import Setting
from app.models.user import User
from app.models.user_session import UserSession

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Définir l'URL : TEST_DATABASE_URL si TESTING=true, sinon DATABASE_URL
# Permet de migrer la base de test avec: TESTING=true alembic upgrade head
db_url = settings.SQLALCHEMY_DATABASE_URL
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Liste des tables à ignorer lors des migrations (ne pas les supprimer)
# Ces tables sont gérées manuellement
tables_to_keep = {"results", "statistics", "user_stats", "schema_version"}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Paramètres de connexion spécifiques pour SQLite
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Ne pas générer de changements de valeurs par défaut pour les colonnes existantes
            render_item=render_item,
            # Ignorer certaines tables qui pourraient poser problème
            include_schemas=True,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


# Fonction pour personnaliser le rendu des éléments dans les migrations
def render_item(type_, obj, autogen_context):
    """Personnaliser le rendu des éléments dans les migrations."""
    if type_ == "table" and obj.name == "alembic_version":
        return False
    return True


# Fonction pour déterminer quelles tables et objets inclure dans les migrations
def include_object(object, name, type_, reflected, compare_to):
    """
    Détermine si un objet doit être inclus dans les migrations.
    Exclut les tables spécifiées dans tables_to_keep de la suppression.
    """
    # Ne jamais supprimer les tables que nous voulons conserver
    if type_ == "table" and name in tables_to_keep and not compare_to:
        # Si compare_to est None, cela signifie que l'objet n'existe pas dans le modèle
        # donc Alembic essaierait de le supprimer
        return False

    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
