"""
Tests unitaires pour le module adapter.py.
Ce module teste l'adaptateur de base de données qui fournit une interface unifiée entre SQLAlchemy et SQL.
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.adapter import DatabaseAdapter
from app.models.exercise import Exercise
from app.models.user import User
from app.utils.db_helpers import get_enum_value


def test_get_by_id_success():
    """Teste la méthode get_by_id avec succès"""
    # Créer un mock pour la session et la requête
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.first.return_value = "mock_object"
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Appeler la méthode
    result = DatabaseAdapter.get_by_id(mock_session, mock_model, 1)
    
    # Vérifier les appels et le résultat
    mock_session.query.assert_called_once_with(mock_model)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result == "mock_object"


def test_get_by_id_exception():
    """Teste la méthode get_by_id avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Configurer le mock pour lever une exception lors de la requête
    mock_session.query.side_effect = SQLAlchemyError("Test exception")
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Appeler la méthode
    result = DatabaseAdapter.get_by_id(mock_session, mock_model, 1)
    
    # Vérifier que le résultat est None en cas d'exception
    assert result is None


def test_get_by_field_success():
    """Teste la méthode get_by_field avec succès"""
    # Créer un mock pour la session et la requête
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.all.return_value = ["mock_object1", "mock_object2"]
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Appeler la méthode
    result = DatabaseAdapter.get_by_field(mock_session, mock_model, "field_name", "value")
    
    # Vérifier les appels et le résultat
    mock_session.query.assert_called_once_with(mock_model)
    mock_query.filter.assert_called_once()
    mock_filter.all.assert_called_once()
    assert result == ["mock_object1", "mock_object2"]


def test_get_by_field_exception():
    """Teste la méthode get_by_field avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Configurer le mock pour lever une exception lors de la requête
    mock_session.query.side_effect = SQLAlchemyError("Test exception")
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Appeler la méthode
    result = DatabaseAdapter.get_by_field(mock_session, mock_model, "field_name", "value")
    
    # Vérifier que le résultat est une liste vide en cas d'exception
    assert result == []


def test_list_active_success():
    """Teste la méthode list_active avec succès"""
    # Créer un mock pour la session et la requête
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_offset = mock_filter.offset.return_value
    mock_limit = mock_offset.limit.return_value
    mock_limit.all.return_value = ["mock_object1", "mock_object2"]
    
    # Créer un mock pour la classe de modèle avec attribut is_archived
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Configurer le mock pour hasattr
    with patch('app.db.adapter.hasattr', return_value=True):
        # Appeler la méthode
        result = DatabaseAdapter.list_active(mock_session, mock_model, limit=10, offset=0)
        
        # Vérifier les appels et le résultat
        mock_session.query.assert_called_once_with(mock_model)
        mock_query.filter.assert_called_once()
        mock_filter.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)
        mock_limit.all.assert_called_once()
        assert result == ["mock_object1", "mock_object2"]


def test_list_active_without_archived_flag():
    """Teste la méthode list_active avec un modèle sans attribut is_archived"""
    # Créer un mock pour la session et la requête
    mock_session = MagicMock(spec=Session)
    mock_query = mock_session.query.return_value
    mock_query.all.return_value = ["mock_object1", "mock_object2"]
    
    # Créer un mock pour la classe de modèle sans attribut is_archived
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # S'assurer que hasattr retourne False pour is_archived
    with patch('app.db.adapter.hasattr', return_value=False):
        # Appeler la méthode
        result = DatabaseAdapter.list_active(mock_session, mock_model)
        
        # Vérifier les appels et le résultat
        mock_session.query.assert_called_once_with(mock_model)
        mock_query.filter.assert_not_called()
        mock_query.all.assert_called_once()
        assert result == ["mock_object1", "mock_object2"]


def test_list_active_exception():
    """Teste la méthode list_active avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Configurer le mock pour lever une exception lors de la requête
    mock_session.query.side_effect = SQLAlchemyError("Test exception")
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Appeler la méthode
    result = DatabaseAdapter.list_active(mock_session, mock_model)
    
    # Vérifier que le résultat est une liste vide en cas d'exception
    assert result == []


def test_create_success():
    """Teste la méthode create avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le gestionnaire de transaction
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_session
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    mock_instance = mock_model.return_value
    
    # Configurer le mock pour TransactionManager.transaction
    with patch('app.db.adapter.TransactionManager.transaction', return_value=mock_transaction):
        # Appeler la méthode
        data = {"field1": "value1", "field2": "value2"}
        result = DatabaseAdapter.create(mock_session, mock_model, data)
        
        # Vérifier les appels et le résultat
        mock_model.assert_called_once_with(**data)
        mock_session.add.assert_called_once_with(mock_instance)
        mock_session.flush.assert_called_once()
        assert result == mock_instance


def test_create_exception():
    """Teste la méthode create avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le gestionnaire de transaction
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_session
    
    # Créer un mock pour la classe de modèle
    mock_model = MagicMock()
    mock_model.__name__ = "MockModel"
    
    # Configurer le mock pour lever une exception lors de la création
    mock_model.side_effect = SQLAlchemyError("Test exception")
    
    # Configurer le mock pour TransactionManager.transaction
    with patch('app.db.adapter.TransactionManager.transaction', return_value=mock_transaction):
        # Appeler la méthode
        data = {"field1": "value1", "field2": "value2"}
        result = DatabaseAdapter.create(mock_session, mock_model, data)
        
        # Vérifier les appels et le résultat
        mock_model.assert_called_once_with(**data)
        assert result is None


def test_update_success():
    """Teste la méthode update avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le gestionnaire de transaction
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_session
    
    # Créer un mock pour l'objet à mettre à jour
    mock_obj = MagicMock()
    mock_obj.__class__.__name__ = "MockModel"
    mock_obj.id = 1
    
    # Configurer le mock pour hasattr et getattr/setattr
    with patch('app.db.adapter.hasattr', return_value=True), \
         patch('app.db.adapter.getattr', return_value=None), \
         patch('app.db.adapter.setattr') as mock_setattr, \
         patch('app.db.adapter.TransactionManager.transaction', return_value=mock_transaction):
        # Appeler la méthode
        data = {"field1": "new_value1", "field2": "new_value2"}
        result = DatabaseAdapter.update(mock_session, mock_obj, data)
        
        # Vérifier les appels et le résultat
        assert mock_setattr.call_count == 2  # Un appel pour chaque clé dans data
        mock_session.flush.assert_called_once()
        assert result is True


def test_update_exception():
    """Teste la méthode update avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le gestionnaire de transaction
    mock_transaction = MagicMock()
    mock_transaction.__enter__.return_value = mock_session
    
    # Créer un mock pour l'objet à mettre à jour
    mock_obj = MagicMock()
    mock_obj.__class__.__name__ = "MockModel"
    mock_obj.id = 1
    
    # Configurer le mock pour lever une exception lors du flush
    mock_session.flush.side_effect = SQLAlchemyError("Test exception")
    
    # S'assurer que l'objet est reconnu comme etant dans la session
    mock_session.__contains__ = MagicMock(return_value=True)
    
    # Configurer le mock pour hasattr
    with patch('app.db.adapter.hasattr', return_value=True):
        # Configurer le mock pour TransactionManager.transaction
        with patch('app.db.adapter.TransactionManager.transaction', return_value=mock_transaction):
            # Appeler la méthode
            data = {"field1": "new_value1", "field2": "new_value2"}
            result = DatabaseAdapter.update(mock_session, mock_obj, data)
            
            # Vérifier les appels et le résultat
            mock_session.flush.assert_called_once()
            assert result is False


def test_archive():
    """Teste la méthode archive"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour l'objet à archiver
    mock_obj = MagicMock()
    
    # Configurer le mock pour TransactionManager.safe_archive
    with patch('app.db.adapter.TransactionManager.safe_archive', return_value=True) as mock_safe_archive:
        # Appeler la méthode
        result = DatabaseAdapter.archive(mock_session, mock_obj)
        
        # Vérifier les appels et le résultat
        mock_safe_archive.assert_called_once_with(mock_session, mock_obj)
        assert result is True


def test_delete():
    """Teste la méthode delete"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour l'objet à supprimer
    mock_obj = MagicMock()
    
    # Configurer le mock pour TransactionManager.safe_delete
    with patch('app.db.adapter.TransactionManager.safe_delete', return_value=True) as mock_safe_delete:
        # Appeler la méthode
        result = DatabaseAdapter.delete(mock_session, mock_obj)
        
        # Vérifier les appels et le résultat
        mock_safe_delete.assert_called_once_with(mock_session, mock_obj)
        assert result is True


def test_execute_query_success():
    """Teste la méthode execute_query avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le résultat de l'exécution
    mock_result = MagicMock()
    mock_result.returns_rows = True
    mock_result.keys.return_value = ["col1", "col2"]
    mock_result.fetchall.return_value = [("value1", "value2"), ("value3", "value4")]
    
    # Configurer le mock pour l'exécution
    mock_session.execute.return_value = mock_result
    
    # Configurer le mock pour sqlalchemy.text
    with patch('app.db.adapter.text', return_value="SQL Text") as mock_text:
        # Appeler la méthode
        query = "SELECT * FROM table"
        params = (1, 2)
        result = DatabaseAdapter.execute_query(mock_session, query, params)
        
        # Vérifier les appels et le résultat
        mock_text.assert_called_once_with(query)
        mock_session.execute.assert_called_once_with("SQL Text", params)
        mock_result.keys.assert_called_once()
        mock_result.fetchall.assert_called_once()
        assert result == [{"col1": "value1", "col2": "value2"}, {"col1": "value3", "col2": "value4"}]


def test_execute_query_no_rows():
    """Teste la méthode execute_query sans lignes retournées"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Créer un mock pour le résultat de l'exécution
    mock_result = MagicMock()
    mock_result.returns_rows = False
    
    # Configurer le mock pour l'exécution
    mock_session.execute.return_value = mock_result
    
    # Configurer le mock pour sqlalchemy.text
    with patch('app.db.adapter.text', return_value="SQL Text") as mock_text:
        # Appeler la méthode
        query = "UPDATE table SET column = value"
        result = DatabaseAdapter.execute_query(mock_session, query)
        
        # Vérifier les appels et le résultat
        mock_text.assert_called_once_with(query)
        mock_session.execute.assert_called_once_with("SQL Text", {})
        mock_result.keys.assert_not_called()
        mock_result.fetchall.assert_not_called()
        assert result == []


def test_execute_query_exception():
    """Teste la méthode execute_query avec une exception"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)
    
    # Configurer le mock pour lever une exception lors de l'exécution
    mock_session.execute.side_effect = SQLAlchemyError("Test exception")
    
    # Configurer le mock pour sqlalchemy.text
    with patch('app.db.adapter.text', return_value="SQL Text") as mock_text:
        # Appeler la méthode
        query = "SELECT * FROM table"
        result = DatabaseAdapter.execute_query(mock_session, query)
        
        # Vérifier les appels et le résultat
        mock_text.assert_called_once_with(query)
        mock_session.execute.assert_called_once_with("SQL Text", {})
        mock_session.rollback.assert_called_once()
        assert result == [] 