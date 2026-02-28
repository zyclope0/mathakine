"""
Tests unitaires pour le module queries.py.
Ce module vérifie que les requêtes SQL sont correctement définies.
"""

import re

import pytest
from sqlalchemy import text

from app.db.queries import (
    ExerciseQueries,
    ResultQueries,
    SettingQueries,
    UserQueries,
    UserStatsQueries,
)
from app.utils.db_helpers import get_enum_value


def test_exercise_queries_defined():
    """Vérifie que toutes les requêtes pour les exercices sont définies"""
    # Vérifier que les attributs attendus existent
    assert hasattr(ExerciseQueries, "CREATE_TABLE")
    assert hasattr(ExerciseQueries, "GET_ALL")
    assert hasattr(ExerciseQueries, "GET_BY_ID")
    assert hasattr(ExerciseQueries, "GET_BY_TYPE")
    assert hasattr(ExerciseQueries, "GET_BY_DIFFICULTY")
    assert hasattr(ExerciseQueries, "GET_BY_TYPE_AND_DIFFICULTY")
    assert hasattr(ExerciseQueries, "GET_RANDOM")
    assert hasattr(ExerciseQueries, "GET_RANDOM_BY_TYPE")
    assert hasattr(ExerciseQueries, "GET_RANDOM_BY_DIFFICULTY")
    assert hasattr(ExerciseQueries, "GET_RANDOM_BY_TYPE_AND_DIFFICULTY")
    assert hasattr(ExerciseQueries, "INSERT")
    assert hasattr(ExerciseQueries, "UPDATE")
    assert hasattr(ExerciseQueries, "ARCHIVE")
    assert hasattr(ExerciseQueries, "ACTIVATE")
    assert hasattr(ExerciseQueries, "DEACTIVATE")
    assert hasattr(ExerciseQueries, "DELETE")
    assert hasattr(ExerciseQueries, "DELETE_PERMANENT")


def test_result_queries_defined():
    """Vérifie que toutes les requêtes pour les résultats sont définies"""
    # Vérifier que les attributs attendus existent
    assert hasattr(ResultQueries, "CREATE_TABLE")
    assert hasattr(ResultQueries, "GET_BY_USER")
    assert hasattr(ResultQueries, "GET_BY_EXERCISE")
    assert hasattr(ResultQueries, "GET_BY_USER_AND_EXERCISE")
    assert hasattr(ResultQueries, "INSERT")


def test_user_stats_queries_defined():
    """Vérifie que toutes les requêtes pour les statistiques utilisateur sont définies"""
    # Vérifier que les attributs attendus existent
    assert hasattr(UserStatsQueries, "GET_USER_STATS")
    assert hasattr(UserStatsQueries, "GET_USER_STATS_BY_TYPE")
    assert hasattr(UserStatsQueries, "GET_USER_STATS_BY_DIFFICULTY")
    assert hasattr(UserStatsQueries, "GET_USER_PROGRESS_BY_DAY")


def test_user_queries_defined():
    """Vérifie que toutes les requêtes pour les utilisateurs sont définies"""
    # Vérifier que les attributs attendus existent
    assert hasattr(UserQueries, "CREATE_TABLE")
    assert hasattr(UserQueries, "GET_ALL")
    assert hasattr(UserQueries, "GET_BY_ID")
    assert hasattr(UserQueries, "GET_BY_USERNAME")
    assert hasattr(UserQueries, "GET_BY_EMAIL")
    assert hasattr(UserQueries, "INSERT")
    assert hasattr(UserQueries, "UPDATE")
    assert hasattr(UserQueries, "UPDATE_PASSWORD")
    assert hasattr(UserQueries, "DELETE")


def test_setting_queries_defined():
    """Vérifie que toutes les requêtes pour les paramètres sont définies"""
    # Vérifier que les attributs attendus existent
    assert hasattr(SettingQueries, "CREATE_TABLE")
    assert hasattr(SettingQueries, "GET_ALL")
    assert hasattr(SettingQueries, "GET_BY_KEY")
    assert hasattr(SettingQueries, "INSERT")
    assert hasattr(SettingQueries, "UPDATE")
    assert hasattr(SettingQueries, "DELETE")


def test_exercise_queries_syntax():
    """Vérifie la syntaxe des requêtes pour les exercices"""
    # Vérifier que les requêtes contiennent les mots-clés SQL attendus
    assert "CREATE TABLE" in ExerciseQueries.CREATE_TABLE
    assert "SELECT" in ExerciseQueries.GET_ALL
    assert "WHERE id = %s" in ExerciseQueries.GET_BY_ID
    assert "ORDER BY RANDOM()" in ExerciseQueries.GET_RANDOM
    assert "INSERT INTO exercises" in ExerciseQueries.INSERT
    assert "UPDATE exercises" in ExerciseQueries.UPDATE
    assert "SET is_archived = true" in ExerciseQueries.ARCHIVE
    assert "DELETE FROM exercises" in ExerciseQueries.DELETE_PERMANENT


def test_result_queries_syntax():
    """Vérifie la syntaxe des requêtes pour les résultats"""
    # Vérifier que les requêtes contiennent les mots-clés SQL attendus
    assert "CREATE TABLE" in ResultQueries.CREATE_TABLE
    assert "SELECT" in ResultQueries.GET_BY_USER
    assert "WHERE exercise_id = %s" in ResultQueries.GET_BY_EXERCISE
    assert "INSERT INTO results" in ResultQueries.INSERT


def test_user_stats_queries_syntax():
    """Vérifie la syntaxe des requêtes pour les statistiques utilisateur"""
    # Vérifier que les requêtes contiennent les mots-clés SQL attendus
    assert "SELECT" in UserStatsQueries.GET_USER_STATS
    assert "COUNT(*)" in UserStatsQueries.GET_USER_STATS
    assert "GROUP BY e.exercise_type" in UserStatsQueries.GET_USER_STATS_BY_TYPE
    assert "GROUP BY e.difficulty" in UserStatsQueries.GET_USER_STATS_BY_DIFFICULTY
    assert "DATE(r.created_at)" in UserStatsQueries.GET_USER_PROGRESS_BY_DAY


def test_user_queries_syntax():
    """Vérifie la syntaxe des requêtes pour les utilisateurs"""
    # Vérifier que les requêtes contiennent les mots-clés SQL attendus
    assert "CREATE TABLE" in UserQueries.CREATE_TABLE
    assert "SELECT" in UserQueries.GET_ALL
    assert "WHERE id = %s" in UserQueries.GET_BY_ID
    assert "INSERT INTO users" in UserQueries.INSERT
    assert "UPDATE users" in UserQueries.UPDATE
    assert "SET hashed_password = %s" in UserQueries.UPDATE_PASSWORD


def test_setting_queries_syntax():
    """Vérifie la syntaxe des requêtes pour les paramètres"""
    # Vérifier que les requêtes contiennent les mots-clés SQL attendus
    assert "CREATE TABLE" in SettingQueries.CREATE_TABLE
    assert "SELECT" in SettingQueries.GET_ALL
    assert "WHERE key = %s" in SettingQueries.GET_BY_KEY
    assert "INSERT INTO settings" in SettingQueries.INSERT
    assert "UPDATE settings" in SettingQueries.UPDATE


def test_sql_injection_prevention():
    """Vérifie que les requêtes utilisent des paramètres pour éviter les injections SQL"""
    # Liste des requêtes qui devraient utiliser des paramètres
    parameterized_queries = [
        ExerciseQueries.GET_BY_ID,
        ExerciseQueries.GET_BY_TYPE,
        ExerciseQueries.GET_BY_DIFFICULTY,
        ExerciseQueries.GET_BY_TYPE_AND_DIFFICULTY,
        ExerciseQueries.GET_RANDOM_BY_TYPE,
        ExerciseQueries.GET_RANDOM_BY_DIFFICULTY,
        ExerciseQueries.GET_RANDOM_BY_TYPE_AND_DIFFICULTY,
        ExerciseQueries.INSERT,
        ExerciseQueries.UPDATE,
        ExerciseQueries.ARCHIVE,
        ResultQueries.GET_BY_USER,
        ResultQueries.GET_BY_EXERCISE,
        ResultQueries.GET_BY_USER_AND_EXERCISE,
        ResultQueries.INSERT,
        UserStatsQueries.GET_USER_STATS,
        UserStatsQueries.GET_USER_STATS_BY_TYPE,
        UserStatsQueries.GET_USER_STATS_BY_DIFFICULTY,
        UserStatsQueries.GET_USER_PROGRESS_BY_DAY,
        UserQueries.GET_BY_ID,
        UserQueries.GET_BY_USERNAME,
        UserQueries.GET_BY_EMAIL,
        UserQueries.INSERT,
        UserQueries.UPDATE,
        UserQueries.UPDATE_PASSWORD,
        SettingQueries.GET_BY_KEY,
        SettingQueries.INSERT,
        SettingQueries.UPDATE,
    ]

    # Vérifier que chaque requête utilise au moins un paramètre %s
    for query in parameterized_queries:
        assert "%s" in query, f"La requête {query} devrait utiliser des paramètres (%s)"


def test_query_validity_with_sqlalchemy():
    """Vérifie que les requêtes peuvent être validées par SQLAlchemy"""
    # Liste des requêtes à tester
    queries_to_test = [
        ExerciseQueries.GET_ALL,
        ExerciseQueries.GET_BY_ID,
        ExerciseQueries.GET_RANDOM,
        ResultQueries.GET_BY_USER,
        UserQueries.GET_ALL,
        SettingQueries.GET_ALL,
    ]

    # Tester que chaque requête peut être convertie en objet SQLAlchemy text
    for query in queries_to_test:
        try:
            sql_text = text(query)
            assert sql_text is not None
        except Exception as e:
            pytest.fail(f"La requête '{query}' n'est pas valide: {str(e)}")


def test_create_table_queries_contain_required_fields():
    """Vérifie que les requêtes CREATE TABLE contiennent les champs requis"""
    # Liste des requêtes CREATE TABLE
    create_table_queries = [
        ExerciseQueries.CREATE_TABLE,
        ResultQueries.CREATE_TABLE,
        UserQueries.CREATE_TABLE,
        SettingQueries.CREATE_TABLE,
    ]

    # Listes des champs requis pour chaque table
    required_fields = {
        "exercises": [
            "id",
            "title",
            "exercise_type",
            "difficulty",
            "question",
            "correct_answer",
        ],
        "results": ["id", "exercise_id", "is_correct"],
        "users": ["id", "username", "email", "hashed_password"],
        "settings": ["id", "key", "value"],
    }

    # Vérifier que chaque requête CREATE TABLE contient les champs requis
    for query in create_table_queries:
        table_name = re.search(r"CREATE TABLE IF NOT EXISTS (\w+)", query)
        if not table_name:
            continue

        table_name = table_name.group(1)
        if table_name not in required_fields:
            continue

        for field in required_fields[table_name]:
            assert (
                field in query
            ), f"Le champ '{field}' devrait être présent dans la requête CREATE TABLE de {table_name}"
