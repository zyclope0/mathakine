import pytest
from unittest.mock import patch, MagicMock, call
from sqlalchemy.orm import Session
import app.services.db_init_service as db_init_service
from app.models.user import User, UserRole
from app.models.exercise import Exercise, ExerciseType, DifficultyLevel
from app.models.attempt import Attempt
from app.models.logic_challenge import LogicChallenge, LogicChallengeType, AgeGroup
from app.models.progress import Progress
from app.models.recommendation import Recommendation
from app.utils.db_helpers import get_enum_value

@pytest.fixture
def mock_db_session():
    """Fixture pour créer un mock de session de base de données"""
    mock_session = MagicMock(spec=Session)
    return mock_session

def test_create_tables():
    """Test la création des tables"""
    with patch('app.services.db_init_service.Base.metadata.create_all') as mock_create_all:
        db_init_service.create_tables()
        mock_create_all.assert_called_once()

# Tests avec des mocks pour vérifier l'appel des fonctions sans affecter la base de données réelle
def test_create_test_users(mock_db_session):
    """Test la création des utilisateurs de test avec des mocks"""
    # Simuler qu'aucun utilisateur n'existe
    mock_db_session.query().count.return_value = 0

    # Appeler la fonction de création d'utilisateurs
    with patch('app.services.db_init_service.User') as mock_user:
        db_init_service.create_test_users(mock_db_session)

        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()

        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_exercises(mock_db_session):
    """Test la création des exercices de test avec des mocks"""
    # Simuler qu'aucun exercice n'existe
    mock_db_session.query().count.return_value = 0

    # Simuler que l'utilisateur Yoda existe
    mock_yoda = MagicMock()
    mock_yoda.id = 1
    mock_db_session.query().filter().first.return_value = mock_yoda

    # Appeler la fonction de création d'exercices
    with patch('app.services.db_init_service.Exercise') as mock_exercise:
        db_init_service.create_test_exercises(mock_db_session)

        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()

        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_logic_challenges(mock_db_session):
    """Test la création des défis logiques de test avec des mocks"""
    # Simuler qu'aucun défi logique n'existe
    mock_db_session.query().count.return_value = 0

    # Simuler que l'utilisateur Yoda existe
    mock_yoda = MagicMock()
    mock_yoda.id = 1
    mock_db_session.query().filter().first.return_value = mock_yoda

    # Appeler la fonction de création de défis logiques
    with patch('app.services.db_init_service.LogicChallenge') as mock_challenge:
        db_init_service.create_test_logic_challenges(mock_db_session)

        # Vérifier que add_all est appelé
        mock_db_session.add_all.assert_called_once()

        # Vérifier que flush est appelé
        mock_db_session.flush.assert_called_once()

def test_create_test_attempts(mock_db_session):
    """Test la création des tentatives de test avec des mocks"""
    # Simuler qu'aucune tentative n'existe
    mock_db_session.query().count.return_value = 0

    # Simuler que l'utilisateur Padawan existe
    mock_padawan = MagicMock()
    mock_padawan.id = 2

    # Simuler que les exercices existent
    mock_exercise = MagicMock()
    mock_exercise.id = 1
    mock_exercise.correct_answer = "4"
    mock_exercise.choices = ["2", "3", "4", "5"]

    # Configurer les retours des requêtes
    mock_db_session.query().filter().first.return_value = mock_padawan
    mock_db_session.query().all.return_value = [mock_exercise]

    # Appeler la fonction de création de tentatives
    with patch('app.services.db_init_service.Attempt') as mock_attempt:
        db_init_service.create_test_attempts(mock_db_session)

        # Vérifier que add est appelé (au moins deux fois, pour les tentatives réussies et échouées)
        assert mock_db_session.add.call_count >= 2

        # Vérifier que flush est appelé au moins deux fois (une fois par tentative)
        assert mock_db_session.flush.call_count >= 2

def test_initialize_database():
    """Test l'initialisation complète de la base de données"""
    # Patcher les fonctions du module
    with patch('app.services.db_init_service.create_tables') as mock_create_tables, \
         patch('app.services.db_init_service.populate_test_data') as mock_populate_test_data:

        # Appeler la fonction d'initialisation
        db_init_service.initialize_database()

        # Vérifier que chaque fonction est appelée
        mock_create_tables.assert_called_once()
        mock_populate_test_data.assert_called_once()

# Tests d'intégration avec une vraie session de base de données
def test_create_test_users_integration(db_session):
    """Test la création des utilisateurs de test avec une vraie session de base de données"""
    # Nettoyage préalable (dans le bon ordre pour éviter les violations de contrainte)
    db_session.query(Attempt).delete()
    db_session.query(Progress).delete()  # Suppression des progressions avant les utilisateurs
    db_session.query(Recommendation).delete()  # Suppression des recommandations
    db_session.query(Exercise).delete()
    db_session.query(LogicChallenge).delete()
    db_session.query(User).delete()
    db_session.commit()
    
    # Appeler la fonction de création d'utilisateurs
    db_init_service.create_test_users(db_session)
    
    # Vérifier que des utilisateurs ont été créés
    users = db_session.query(User).all()
    assert len(users) > 0, "Des utilisateurs devraient être créés"
    
    # Vérifier qu'il y a un utilisateur avec le rôle Maître
    maitre_users = [u for u in users if u.role == UserRole.MAITRE]
    assert len(maitre_users) > 0, "Au moins un utilisateur Maître devrait être créé"
    
    # Vérifier qu'il y a un utilisateur avec le nom 'maitre_yoda'
    yoda = db_session.query(User).filter(User.username == "maitre_yoda").first()
    assert yoda is not None, "L'utilisateur maitre_yoda devrait être créé"
    assert yoda.role == UserRole.MAITRE, "maitre_yoda devrait avoir le rôle MAITRE"

def test_create_test_exercises_integration(db_session):
    """Test la création des exercices de test avec une vraie session de base de données"""
    # Créer d'abord un utilisateur Maître si nécessaire
    if not db_session.query(User).filter(User.username == "maitre_yoda").first():
        db_init_service.create_test_users(db_session)
    
    # Nettoyer les exercices existants (et les entités dépendantes)
    db_session.query(Attempt).delete()
    db_session.query(Progress).delete()
    db_session.query(Exercise).delete()
    db_session.commit()
    
    # Appeler la fonction de création d'exercices
    db_init_service.create_test_exercises(db_session)
    
    # Vérifier que des exercices ont été créés
    exercises = db_session.query(Exercise).all()
    assert len(exercises) > 0, "Des exercices devraient être créés"
    
    # Vérifier la diversité des exercices
    exercise_types = set(ex.exercise_type for ex in exercises)
    assert len(exercise_types) > 1, "Différents types d'exercices devraient être créés"
    
    # Vérifier la présence de niveaux de difficulté différents
    difficulty_levels = set(ex.difficulty for ex in exercises)
    assert len(difficulty_levels) > 1, "Différents niveaux de difficulté devraient être créés"

def test_create_test_logic_challenges_integration(db_session):
    """Test la création des défis logiques de test avec une vraie session de base de données"""
    # Créer d'abord un utilisateur Maître si nécessaire
    if not db_session.query(User).filter(User.username == "maitre_yoda").first():
        db_init_service.create_test_users(db_session)
    
    # Nettoyer les défis logiques existants
    db_session.query(LogicChallenge).delete()
    db_session.commit()
    
    # Appeler la fonction de création de défis logiques
    db_init_service.create_test_logic_challenges(db_session)
    
    # Vérifier que des défis logiques ont été créés
    challenges = db_session.query(LogicChallenge).all()
    assert len(challenges) > 0, "Des défis logiques devraient être créés"
    
    # Vérifier la diversité des défis
    challenge_types = set(c.challenge_type for c in challenges)
    assert len(challenge_types) > 1, "Différents types de défis devraient être créés"
    
    # Vérifier la présence de différents groupes d'âge
    age_groups = set(c.age_group for c in challenges)
    assert len(age_groups) > 0, "Au moins un groupe d'âge devrait être défini"

def test_create_test_attempts_integration(db_session):
    """Test la création des tentatives de test avec une vraie session de base de données"""
    # S'assurer que les utilisateurs et exercices existent
    if db_session.query(User).count() == 0:
        db_init_service.create_test_users(db_session)
    
    if db_session.query(Exercise).count() == 0:
        db_init_service.create_test_exercises(db_session)
    
    # Nettoyer les tentatives existantes
    db_session.query(Attempt).delete()
    db_session.commit()
    
    # Appeler la fonction de création de tentatives
    db_init_service.create_test_attempts(db_session)
    
    # Vérifier que des tentatives ont été créées
    attempts = db_session.query(Attempt).all()
    assert len(attempts) > 0, "Des tentatives devraient être créées"
    
    # Vérifier qu'il y a des tentatives réussies et échouées
    successful_attempts = [a for a in attempts if a.is_correct]
    failed_attempts = [a for a in attempts if not a.is_correct]
    
    assert len(successful_attempts) > 0, "Des tentatives réussies devraient être créées"
    assert len(failed_attempts) > 0, "Des tentatives échouées devraient être créées"

def test_populate_test_data_integration(db_session):
    """Test l'intégration complète du remplissage de données de test"""
    # Nettoyer la base de données dans l'ordre correct pour respecter les contraintes de clé étrangère
    db_session.query(Attempt).delete()
    db_session.query(Progress).delete()
    db_session.query(Recommendation).delete()
    db_session.query(Exercise).delete()
    db_session.query(LogicChallenge).delete()
    db_session.query(User).delete()
    db_session.commit()
    
    # Patcher la fonction get_db pour retourner notre session de test
    with patch('app.services.db_init_service.get_db', return_value=iter([db_session])):
        # Appeler la fonction de remplissage
        db_init_service.populate_test_data()
    
    # Vérifier que toutes les entités ont été créées
    assert db_session.query(User).count() > 0, "Des utilisateurs devraient être créés"
    assert db_session.query(Exercise).count() > 0, "Des exercices devraient être créés"
    assert db_session.query(LogicChallenge).count() > 0, "Des défis logiques devraient être créés"
    assert db_session.query(Attempt).count() > 0, "Des tentatives devraient être créées"

def test_populate_test_data_error_handling(db_session):
    """Test la gestion des erreurs lors du remplissage des données"""
    # Simuler une erreur pendant la création des utilisateurs
    with patch('app.services.db_init_service.create_test_users', side_effect=Exception("Erreur simulée")), \
         patch('app.services.db_init_service.get_db', return_value=iter([db_session])):
        
        # Vérifier que l'exception est gérée et qu'un rollback est effectué
        with pytest.raises(Exception):
            db_init_service.populate_test_data()

def test_create_test_users_already_exist(db_session):
    """Test que la création des utilisateurs est ignorée s'ils existent déjà"""
    # Créer d'abord un utilisateur
    user = User(
        username="existing_user",
        email="existing@example.com",
        hashed_password="hashed_password",
        role=UserRole.PADAWAN
    )
    db_session.add(user)
    db_session.commit()
    
    # Simuler que des utilisateurs existent déjà
    with patch.object(db_session, 'query') as mock_query:
        mock_query.return_value.count.return_value = 1
        
        # Vérifier que add_all n'est pas appelé
        with patch.object(db_session, 'add_all') as mock_add_all:
            db_init_service.create_test_users(db_session)
            mock_add_all.assert_not_called()

def test_populate_test_data_exception_handling():
    """Test la gestion des exceptions lors du remplissage de données de test"""
    mock_db = MagicMock(spec=Session)
    mock_db_generator = MagicMock()
    mock_db_generator.__next__.return_value = mock_db
    
    # Simuler une exception lors de la création des utilisateurs de test
    with patch('app.services.db_init_service.get_db', return_value=mock_db_generator), \
         patch('app.services.db_init_service.create_test_users', side_effect=Exception("Erreur simulée")), \
         pytest.raises(Exception) as excinfo:
        
        # Appeler la fonction qui devrait lever une exception
        db_init_service.populate_test_data()
        
        # Vérifier que l'exception est bien propagée
        assert "Erreur simulée" in str(excinfo.value)
        
        # Vérifier que rollback est appelé
        mock_db.rollback.assert_called_once()
        
        # Vérifier que close est appelé (même en cas d'erreur)
        mock_db.close.assert_called_once()

def test_create_test_users_skip_if_exist(mock_db_session):
    """Test que la création des utilisateurs est ignorée s'ils existent déjà"""
    # Simuler que des utilisateurs existent déjà
    mock_db_session.query().count.return_value = 5
    
    # Appeler la fonction
    db_init_service.create_test_users(mock_db_session)
    
    # Vérifier que add_all n'est PAS appelé
    mock_db_session.add_all.assert_not_called()
    
    # Vérifier que flush n'est PAS appelé
    mock_db_session.flush.assert_not_called()

def test_create_test_exercises_skip_if_exist(mock_db_session):
    """Test que la création des exercices est ignorée s'ils existent déjà"""
    # Simuler que des exercices existent déjà
    mock_db_session.query().count.return_value = 3
    
    # Appeler la fonction
    db_init_service.create_test_exercises(mock_db_session)
    
    # Vérifier que les fonctions suivantes ne sont PAS appelées
    mock_db_session.add_all.assert_not_called()
    mock_db_session.flush.assert_not_called()
    mock_db_session.query().filter().first.assert_not_called()

def test_create_test_attempts_no_padawan(mock_db_session):
    """Test le comportement lorsqu'aucun utilisateur Padawan n'est trouvé"""
    # Simuler qu'aucune tentative n'existe
    mock_db_session.query().count.return_value = 0
    
    # Simuler qu'aucun utilisateur Padawan n'est trouvé
    mock_db_session.query().filter().first.return_value = None
    
    # Appeler la fonction
    db_init_service.create_test_attempts(mock_db_session)
    
    # Vérifier que add n'est pas appelé (car pas d'utilisateur Padawan)
    mock_db_session.add.assert_not_called()

def test_create_test_attempts_no_exercises(mock_db_session):
    """Test le comportement lorsqu'aucun exercice n'est trouvé"""
    # Simuler qu'aucune tentative n'existe
    mock_db_session.query().count.return_value = 0
    
    # Simuler qu'un utilisateur Padawan existe
    mock_padawan = MagicMock()
    mock_padawan.id = 2
    
    # Première requête (pour Padawan) retourne un utilisateur,
    # deuxième requête (pour exercices) retourne une liste vide
    mock_db_session.query().filter().first.return_value = mock_padawan
    mock_db_session.query().all.return_value = []
    
    # Appeler la fonction
    db_init_service.create_test_attempts(mock_db_session)
    
    # Vérifier que add n'est pas appelé (car pas d'exercices)
    mock_db_session.add.assert_not_called()

def test_initialize_database_success():
    """Test le cas de succès de l'initialisation de la base de données"""
    # Patcher les fonctions pour éviter les effets réels
    with patch('app.services.db_init_service.create_tables') as mock_create_tables, \
         patch('app.services.db_init_service.populate_test_data') as mock_populate_test_data:
        
        # Appeler la fonction
        db_init_service.initialize_database()
        
        # Vérifier que les fonctions sont appelées dans l'ordre
        mock_create_tables.assert_called_once()
        mock_populate_test_data.assert_called_once()

def test_initialize_database_exception():
    """Test le comportement en cas d'exception lors de l'initialisation"""
    # Patcher les fonctions pour simuler une exception
    with patch('app.services.db_init_service.create_tables', side_effect=Exception("Erreur de création des tables")), \
         pytest.raises(Exception) as excinfo:
        
        # Appeler la fonction qui devrait lever une exception
        db_init_service.initialize_database()
        
        # Vérifier que l'exception est propagée
        assert "Erreur de création des tables" in str(excinfo.value)

# Tests de comportement plus détaillés pour les fonctions existantes

def test_create_test_logic_challenges_skip_if_exist(mock_db_session):
    """Test que la création des défis logiques est ignorée s'ils existent déjà"""
    # Simuler que des défis logiques existent déjà
    mock_db_session.query().count.return_value = 4
    
    # Appeler la fonction
    db_init_service.create_test_logic_challenges(mock_db_session)
    
    # Vérifier que les fonctions suivantes ne sont PAS appelées
    mock_db_session.add_all.assert_not_called()
    mock_db_session.flush.assert_not_called()
    mock_db_session.query().filter().first.assert_not_called()
