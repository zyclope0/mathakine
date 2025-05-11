#!/usr/bin/env python
"""
Script pour nettoyer la base de données des données de test
"""
import os
import psycopg2
import sqlite3
import sys

# Déterminer le type de base de données à utiliser
DATABASE_URL = os.environ.get("DATABASE_URL", "")
USE_POSTGRES = bool(DATABASE_URL)

print("Nettoyage de la base de données...")
print(f"Mode Base de données: {'PostgreSQL' if USE_POSTGRES else 'SQLite'}")

try:
    if USE_POSTGRES:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
    else:
        # Connexion à SQLite
        conn = sqlite3.connect("database.db")
        # Activer les foreign keys pour SQLite
        conn.execute("PRAGMA foreign_keys = ON")
    
    cursor = conn.cursor()
    
    # 1. Supprimer les résultats existants
    print("Suppression des résultats existants...")
    cursor.execute("DELETE FROM results")
    
    # 2. Réinitialiser les statistiques utilisateur
    print("Réinitialisation des statistiques utilisateur...")
    cursor.execute("DELETE FROM user_stats")
    
    # 3. Supprimer les tentatives (attempts)
    print("Suppression des tentatives existantes...")
    cursor.execute("DELETE FROM attempts")
    
    # 4. Supprimer tous les exercices
    print("Suppression des exercices existants...")
    cursor.execute("DELETE FROM exercises")
    
    # 5. Réinitialiser les séquences d'ID pour PostgreSQL
    if USE_POSTGRES:
        print("Réinitialisation des séquences d'ID...")
        cursor.execute("ALTER SEQUENCE exercises_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE results_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE user_stats_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE attempts_id_seq RESTART WITH 1")
    
    # Valider les modifications
    conn.commit()
    print("Base de données nettoyée avec succès!")
    
except Exception as e:
    print(f"Erreur lors du nettoyage de la base de données: {e}")
    if conn:
        conn.rollback()
    sys.exit(1)
    
finally:
    if conn:
        conn.close()

print("Opération terminée.") 