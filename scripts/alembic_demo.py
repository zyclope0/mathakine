#!/usr/bin/env python
"""
Script de démonstration du processus de migration Alembic.
Ce script:
1. Vérifie l'état actuel des migrations
2. Génère une migration de test (ajout d'une colonne à la table results)
3. Applique la migration
4. Vérifie le nouvel état
5. Annule la migration
"""
import os
import sys
import subprocess
import time

# Ajouter le répertoire parent au sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from loguru import logger
import typer

app = typer.Typer()

def run_command(command):
    """Exécuter une commande Shell et retourner la sortie"""
    logger.info(f"Exécution de: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution de la commande: {e}")
        logger.error(f"Sortie standard: {e.stdout}")
        logger.error(f"Sortie d'erreur: {e.stderr}")
        return None

@app.command()
def demo():
    """Démonstration du processus de migration complet"""
    # 1. Vérifier l'état actuel
    logger.info("1. Vérification de l'état actuel des migrations")
    run_command("alembic current")
    
    # 2. Générer une migration de test
    logger.info("2. Génération d'une migration de test")
    migration_name = f"test_migration_{int(time.time())}"
    run_command(f"python {os.path.join(BASE_DIR, 'scripts', 'generate_migration.py')} {migration_name}")
    
    # 3. Modifier la migration pour ajouter une colonne de test
    # Trouver le dernier fichier de migration
    versions_dir = os.path.join(BASE_DIR, "migrations", "versions")
    migration_files = sorted(
        [f for f in os.listdir(versions_dir) if f.endswith('.py') and not f.startswith('__')],
        key=lambda x: os.path.getmtime(os.path.join(versions_dir, x))
    )
    
    if not migration_files:
        logger.error("Aucun fichier de migration trouvé")
        return
    
    latest_migration = os.path.join(versions_dir, migration_files[-1])
    logger.info(f"Dernier fichier de migration: {os.path.basename(latest_migration)}")
    
    # Modifier le fichier de migration pour ajouter une colonne test_column à la table results
    with open(latest_migration, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer la fonction upgrade vide par l'ajout d'une colonne
    content = content.replace(
        "def upgrade() -> None:\n    pass",
        """def upgrade() -> None:
    # Ajouter une colonne de test à la table results
    op.add_column('results', sa.Column('test_column', sa.String(50), nullable=True))"""
    )
    
    # Remplacer la fonction downgrade vide par la suppression de la colonne
    content = content.replace(
        "def downgrade() -> None:\n    pass",
        """def downgrade() -> None:
    # Supprimer la colonne de test de la table results
    op.drop_column('results', 'test_column')"""
    )
    
    with open(latest_migration, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.success(f"Migration modifiée pour ajouter une colonne 'test_column' à la table 'results'")
    
    # 4. Appliquer la migration
    logger.info("4. Application de la migration")
    run_command("alembic upgrade head")
    
    # 5. Vérifier le nouvel état
    logger.info("5. Vérification du nouvel état des migrations")
    run_command("alembic current")
    
    # Attendre que l'utilisateur examine les résultats
    logger.info("Migration appliquée avec succès!")
    input("Appuyez sur Entrée pour annuler la migration et revenir à l'état initial...")
    
    # 6. Annuler la migration
    logger.info("6. Annulation de la migration")
    run_command("alembic downgrade -1")
    
    # 7. Vérifier l'état final
    logger.info("7. Vérification de l'état final")
    run_command("alembic current")
    
    logger.success("Démonstration terminée!")
    logger.info("Cette démonstration a montré comment:")
    logger.info("1. Vérifier l'état des migrations")
    logger.info("2. Générer une nouvelle migration")
    logger.info("3. Appliquer une migration (ajout d'une colonne)")
    logger.info("4. Annuler une migration (suppression de la colonne)")

if __name__ == "__main__":
    logger.info("Démarrage du script de démonstration Alembic")
    app() 