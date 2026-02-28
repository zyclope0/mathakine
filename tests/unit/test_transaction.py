"""
Tests unitaires pour le module transaction.py.
Ce module teste les fonctionnalités de gestion des transactions.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.transaction import TransactionManager
from app.models.exercise import Exercise
from app.models.user import User
from app.utils.db_helpers import get_enum_value


# Tests pour le gestionnaire de contexte transaction
def test_transaction_context_manager_commit():
    """Teste le gestionnaire de contexte transaction avec commit automatique"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Simuler un savepoint
    mock_savepoint = MagicMock()
    mock_savepoint.is_active = False
    mock_session.begin_nested.return_value = mock_savepoint

    # Utiliser le gestionnaire de contexte
    with TransactionManager.transaction(mock_session) as session:
        # Vérifier que la session retournée est la même que celle passée
        assert session == mock_session

        # Simuler des opérations
        user = User(
            username="test", email="test@example.com", hashed_password="test_hash"
        )
        session.add(user)

    # Vérifier que les méthodes ont été appelées
    mock_session.begin_nested.assert_called_once()
    mock_savepoint.commit.assert_called_once()
    mock_session.commit.assert_called_once()


def test_transaction_context_manager_with_exception():
    """Teste le gestionnaire de contexte transaction quand une exception est levée"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Simuler un savepoint
    mock_savepoint = MagicMock()
    mock_savepoint.is_active = True
    mock_session.begin_nested.return_value = mock_savepoint

    # Utiliser le gestionnaire de contexte avec une exception
    try:
        with TransactionManager.transaction(mock_session) as session:
            # Simuler une opération qui génère une exception
            raise ValueError("Test exception")
    except ValueError:
        pass  # On s'attend à ce que l'exception soit propagée

    # Vérifier que les méthodes de rollback ont été appelées
    mock_savepoint.rollback.assert_called_once()
    mock_session.rollback.assert_called_once()
    # Vérifier que commit n'a pas été appelé
    mock_session.commit.assert_not_called()


def test_transaction_without_auto_commit():
    """Teste le gestionnaire de contexte transaction sans commit automatique"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Simuler un savepoint
    mock_savepoint = MagicMock()
    mock_session.begin_nested.return_value = mock_savepoint

    # Utiliser le gestionnaire de contexte sans auto_commit
    with TransactionManager.transaction(mock_session, auto_commit=False) as session:
        # Simuler des opérations
        user = User(
            username="test", email="test@example.com", hashed_password="test_hash"
        )
        session.add(user)

    # Vérifier que les méthodes ont été appelées correctement
    mock_session.begin_nested.assert_called_once()
    # Vérifier que commit n'a pas été appelé sur le savepoint ni sur la session
    mock_savepoint.commit.assert_not_called()
    mock_session.commit.assert_not_called()


# Tests pour les méthodes individuelles
def test_commit_success():
    """Teste la méthode commit avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Appeler la méthode
    result = TransactionManager.commit(mock_session)

    # Vérifier que commit a été appelé et que le résultat est True
    mock_session.commit.assert_called_once()
    assert result is True


def test_commit_failure():
    """Teste la méthode commit avec échec"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Configurer le mock pour lever une exception lors du commit
    mock_session.commit.side_effect = SQLAlchemyError("Test exception")

    # Appeler la méthode
    result = TransactionManager.commit(mock_session)

    # Vérifier que rollback a été appelé et que le résultat est False
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    assert result is False


def test_rollback_success():
    """Teste la méthode rollback avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Appeler la méthode
    result = TransactionManager.rollback(mock_session)

    # Vérifier que rollback a été appelé et que le résultat est True
    mock_session.rollback.assert_called_once()
    assert result is True


def test_rollback_failure():
    """Teste la méthode rollback avec échec"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Configurer le mock pour lever une exception lors du rollback
    mock_session.rollback.side_effect = SQLAlchemyError("Test exception")

    # Appeler la méthode
    result = TransactionManager.rollback(mock_session)

    # Vérifier que le résultat est False
    mock_session.rollback.assert_called_once()
    assert result is False


def test_safe_delete_success():
    """Teste la méthode safe_delete avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Créer un mock pour l'objet à supprimer
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.__tablename__ = "exercises"

    # L'objet doit être considéré comme attaché à la session (sinon safe_delete requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Appeler la méthode
    result = TransactionManager.safe_delete(mock_session, mock_obj)

    # Vérifier que delete a été appelé et que le résultat est True
    mock_session.delete.assert_called_once_with(mock_obj)
    mock_session.commit.assert_called_once()
    assert result is True


def test_safe_delete_with_commit_error():
    """Teste la méthode safe_delete avec erreur lors du commit"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Configurer le mock pour lever une exception lors du commit
    mock_session.commit.side_effect = [SQLAlchemyError("Test exception"), None]

    # Créer un mock pour l'objet à supprimer
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.__tablename__ = "exercises"

    # L'objet doit être considéré comme attaché à la session (sinon safe_delete requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Patcher la méthode execute pour simuler une suppression directe
    with patch.object(mock_session, "execute") as mock_execute:
        # Appeler la méthode
        result = TransactionManager.safe_delete(mock_session, mock_obj)

        # Vérifier que delete a été appelé, puis un rollback, puis execute pour la suppression alternative
        mock_session.delete.assert_called_once_with(mock_obj)
        # Vérifier que rollback a été appelé au moins une fois (peut être appelé plusieurs fois selon l'implémentation)
        assert mock_session.rollback.call_count >= 1
        mock_execute.assert_called_once()
        # La méthode doit retourner True car la suppression alternative a réussi
        assert result is True


def test_safe_delete_with_alternative_error():
    """Teste la méthode safe_delete avec échec de la méthode alternative"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Configurer le mock pour lever une exception lors du commit
    mock_session.commit.side_effect = SQLAlchemyError("Test exception")

    # Créer un mock pour l'objet à supprimer
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.__tablename__ = "exercises"

    # Patcher la méthode execute pour simuler une erreur lors de la suppression directe
    with patch.object(
        mock_session, "execute", side_effect=SQLAlchemyError("Another exception")
    ):
        # Appeler la méthode
        result = TransactionManager.safe_delete(mock_session, mock_obj)

        # La méthode doit retourner False car les deux tentatives de suppression ont échoué
        assert result is False
        # Vérifier que rollback a été appelé deux fois
        assert mock_session.rollback.call_count == 2


def test_safe_delete_without_auto_commit():
    """Teste la méthode safe_delete sans commit automatique"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Créer un mock pour l'objet à supprimer
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"

    # L'objet doit être considéré comme attaché à la session (sinon safe_delete requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Appeler la méthode sans auto_commit
    result = TransactionManager.safe_delete(mock_session, mock_obj, auto_commit=False)

    # Vérifier que delete a été appelé mais pas commit
    mock_session.delete.assert_called_once_with(mock_obj)
    mock_session.commit.assert_not_called()
    assert result is True


def test_safe_archive_success():
    """Teste la méthode safe_archive avec succès"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Créer un mock pour l'objet à archiver
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.is_archived = False

    # L'objet doit être considéré comme attaché à la session (sinon safe_archive requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Appeler la méthode
    result = TransactionManager.safe_archive(mock_session, mock_obj)

    # Vérifier que is_archived a été mis à True et commit a été appelé
    assert mock_obj.is_archived is True
    mock_session.commit.assert_called_once()
    assert result is True


def test_safe_archive_with_error():
    """Teste la méthode safe_archive avec une erreur"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Configurer le mock pour lever une exception lors du commit
    mock_session.commit.side_effect = SQLAlchemyError("Test exception")

    # Créer un mock pour l'objet à archiver
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.is_archived = False

    # L'objet doit être considéré comme attaché à la session (sinon safe_archive requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Appeler la méthode
    result = TransactionManager.safe_archive(mock_session, mock_obj)

    # Vérifier que is_archived a été mis à True, mais le commit a échoué
    assert mock_obj.is_archived is True
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_called_once()
    assert result is False


def test_safe_archive_without_is_archived():
    """Teste la méthode safe_archive avec un objet sans attribut is_archived"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Créer un mock pour l'objet sans attribut is_archived
    mock_obj = MagicMock()
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "SomeClass"

    # Supprimer l'attribut is_archived s'il existe
    if hasattr(mock_obj, "is_archived"):
        delattr(mock_obj, "is_archived")

    # Appeler la méthode
    result = TransactionManager.safe_archive(mock_session, mock_obj)

    # Vérifier que le résultat est False et commit n'a pas été appelé
    mock_session.commit.assert_not_called()
    assert result is False


def test_safe_archive_without_auto_commit():
    """Teste la méthode safe_archive sans commit automatique"""
    # Créer un mock pour la session
    mock_session = MagicMock(spec=Session)

    # Créer un mock pour l'objet à archiver
    mock_obj = MagicMock(spec=Exercise)
    mock_obj.id = 1
    mock_obj.__class__.__name__ = "Exercise"
    mock_obj.is_archived = False

    # L'objet doit être considéré comme attaché à la session (sinon safe_archive requête la DB)
    mock_session.__contains__ = MagicMock(return_value=True)

    # Appeler la méthode sans auto_commit
    result = TransactionManager.safe_archive(mock_session, mock_obj, auto_commit=False)

    # Vérifier que is_archived a été mis à True mais commit n'a pas été appelé
    assert mock_obj.is_archived is True
    mock_session.commit.assert_not_called()
    assert result is True
