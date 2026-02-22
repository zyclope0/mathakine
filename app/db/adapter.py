"""
Adaptateur de base de données pour Mathakine.
Fournit une interface unifiée entre les modèles SQLAlchemy et les requêtes SQL directes.
"""

from typing import Any, Dict, List, Optional, Type, Union

from app.core.logging_config import get_logger

logger = get_logger(__name__)
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.transaction import TransactionManager


class DatabaseAdapter:
    """
    Adaptateur pour les opérations de base de données.
    Permet d'utiliser une approche unifiée pour les opérations sur les modèles,
    que ce soit via SQLAlchemy ou via des requêtes SQL directes.
    """

    @staticmethod
    def get_by_id(db: Session, model_class: Type[Base], id: int) -> Optional[Base]:
        """
        Récupère un objet par son ID.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à récupérer
            id: ID de l'objet à récupérer

        Returns:
            L'objet correspondant à l'ID ou None s'il n'existe pas
        """
        try:
            return db.query(model_class).filter(model_class.id == id).first()
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération de {model_class.__name__} avec id={id}: {e}"
            )
            return None

    @staticmethod
    def get_by_field(
        db: Session, model_class: Type[Base], field_name: str, value: Any
    ) -> List[Base]:
        """
        Récupère des objets par la valeur d'un champ.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à récupérer
            field_name: Nom du champ à filtrer
            value: Valeur à rechercher

        Returns:
            Liste des objets correspondants
        """
        try:
            return (
                db.query(model_class)
                .filter(getattr(model_class, field_name) == value)
                .all()
            )
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération de {model_class.__name__} avec {field_name}={value}: {e}"
            )
            return []

    @staticmethod
    def list_active(
        db: Session, model_class: Type[Base], limit: int = None, offset: int = None
    ) -> List[Base]:
        """
        Liste les objets actifs (non archivés) d'un modèle.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à lister
            limit: Nombre maximum d'objets à retourner
            offset: Décalage pour la pagination

        Returns:
            Liste des objets actifs
        """
        try:
            query = db.query(model_class)

            # Filtrer par is_archived si le modèle a cet attribut
            if hasattr(model_class, "is_archived"):
                query = query.filter(getattr(model_class, "is_archived") == False)

            # Appliquer limit et offset si spécifiés
            if offset is not None:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)

            return query.all()
        except Exception as e:
            logger.error(
                f"Erreur lors de la liste des {model_class.__name__} actifs: {e}"
            )
            return []

    @staticmethod
    def create(
        db: Session, model_class: Type[Base], data: Dict[str, Any]
    ) -> Optional[Base]:
        """
        Crée un nouvel objet dans la base de données.

        Args:
            db: Session de base de données
            model_class: Classe du modèle à créer
            data: Dictionnaire contenant les données de l'objet

        Returns:
            L'objet créé ou None en cas d'erreur
        """
        with TransactionManager.transaction(db) as session:
            try:
                obj = model_class(**data)
                session.add(obj)
                session.flush()  # Pour obtenir l'ID généré
                return obj
            except Exception as e:
                logger.error(
                    f"Erreur lors de la création de {model_class.__name__}: {e}"
                )
                return None

    @staticmethod
    def update(db: Session, obj: Base, data: Dict[str, Any]) -> bool:
        """
        Met à jour un objet existant.

        Args:
            db: Session de base de données
            obj: Objet à mettre à jour
            data: Dictionnaire contenant les nouvelles valeurs

        Returns:
            True si la mise à jour a réussi, False sinon
        """
        with TransactionManager.transaction(db) as session:
            try:
                # S'assurer que l'objet est attaché à la session
                if obj not in session:
                    # Récupérer l'objet depuis la session si possible
                    obj_id = getattr(obj, "id", None)
                    if obj_id:
                        obj = (
                            session.query(obj.__class__)
                            .filter(obj.__class__.id == obj_id)
                            .first()
                        )
                        if not obj:
                            logger.error(
                                f"Objet {obj.__class__.__name__}(id={obj_id}) non trouvé dans la session"
                            )
                            return False
                    else:
                        # Si pas d'ID, merger l'objet
                        obj = session.merge(obj)

                # Mettre à jour les attributs
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
                session.flush()
                return True
            except Exception as e:
                logger.error(
                    f"Erreur lors de la mise à jour de {obj.__class__.__name__}(id={getattr(obj, 'id', 'N/A')}): {e}"
                )
                return False

    @staticmethod
    def archive(db: Session, obj: Base) -> bool:
        """
        Archive un objet (marque comme supprimé sans suppression physique).

        Args:
            db: Session de base de données
            obj: Objet à archiver

        Returns:
            True si l'archivage a réussi, False sinon
        """
        return TransactionManager.safe_archive(db, obj)

    @staticmethod
    def delete(db: Session, obj: Base) -> bool:
        """
        Supprime physiquement un objet de la base de données.
        Les suppressions en cascade sont gérées automatiquement.

        Args:
            db: Session de base de données
            obj: Objet à supprimer

        Returns:
            True si la suppression a réussi, False sinon
        """
        return TransactionManager.safe_delete(db, obj)

    @staticmethod
    def execute_query(
        db: Session, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Exécute une requête SQL personnalisée.

        SÉCURITÉ (audit 3.1) : params doit être un dict pour des paramètres nommés.
        Ne jamais concaténer de données utilisateur dans query. Utiliser exclusivement
        des paramètres nommés (ex: SELECT * FROM t WHERE id = :id avec params={"id": 1}).

        Args:
            db: Session de base de données
            query: Requête SQL avec paramètres nommés (:param_name)
            params: Dictionnaire de paramètres nommés (ou None)

        Returns:
            Liste de dictionnaires contenant les résultats
        """
        if params is not None and not isinstance(params, dict):
            raise TypeError(
                "execute_query exige params de type dict pour des paramètres nommés. "
                'Utiliser :param_name dans la requête et params={"param_name": value}.'
            )
        safe_params = params if params is not None else {}
        try:
            result = db.execute(text(query), safe_params)
            if result.returns_rows:
                column_names = result.keys()
                return [dict(zip(column_names, row)) for row in result.fetchall()]
            return []
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la requête SQL: {e}")
            db.rollback()
            return []
