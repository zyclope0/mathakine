"""
Tests pour vérifier la gestion des valeurs d'énumération PostgreSQL.
"""
import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.models.logic_challenge import LogicChallengeType, AgeGroup
from app.utils.db_helpers import get_enum_value, adapt_enum_for_db
from app.core.security import get_password_hash
from app.core.config import settings


class PostgreSQLEnumTest(unittest.TestCase):
    """Test de la gestion des valeurs d'énumération PostgreSQL."""
    
    @classmethod
    def setUpClass(cls):
        """Configurer la base de données pour les tests."""
        # Utiliser la base de données PostgreSQL définie dans .env
        cls.engine = create_engine(settings.DATABASE_URL, echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
        
        # Créer les tables nécessaires
        from app.db.base import Base
        Base.metadata.create_all(cls.engine)
        
        # Créer une session
        cls.session = cls.Session()
    
    @classmethod
    def tearDownClass(cls):
        """Nettoyer après les tests."""
        cls.session.close()
        
    def test_user_role_adaptation(self):
        """Tester l'adaptation des rôles utilisateur."""
        # Récupérer les valeurs adaptées pour chaque rôle
        padawan_role = get_enum_value(UserRole, UserRole.PADAWAN)
        maitre_role = get_enum_value(UserRole, UserRole.MAITRE)
        gardien_role = get_enum_value(UserRole, UserRole.GARDIEN)
        archiviste_role = get_enum_value(UserRole, UserRole.ARCHIVISTE)
        
        # Afficher les valeurs adaptées
        print(f"UserRole.PADAWAN adapté en: '{padawan_role}'")
        print(f"UserRole.MAITRE adapté en: '{maitre_role}'")
        print(f"UserRole.GARDIEN adapté en: '{gardien_role}'")
        print(f"UserRole.ARCHIVISTE adapté en: '{archiviste_role}'")
        
        # Vérifier que les valeurs correspondent aux valeurs PostgreSQL attendues
        self.assertEqual(padawan_role, "PADAWAN")
        self.assertEqual(maitre_role, "MAITRE")
        self.assertEqual(gardien_role, "GARDIEN")
        self.assertEqual(archiviste_role, "ARCHIVISTE")
    
    def test_logic_challenge_type_adaptation(self):
        """Tester l'adaptation des types de défis logiques."""
        # Récupérer les valeurs adaptées
        sequence_type = get_enum_value(LogicChallengeType, LogicChallengeType.SEQUENCE)
        pattern_type = get_enum_value(LogicChallengeType, LogicChallengeType.PATTERN)
        puzzle_type = get_enum_value(LogicChallengeType, LogicChallengeType.PUZZLE)
        
        # Afficher les valeurs adaptées
        print(f"LogicChallengeType.SEQUENCE adapté en: '{sequence_type}'")
        print(f"LogicChallengeType.PATTERN adapté en: '{pattern_type}'")
        print(f"LogicChallengeType.PUZZLE adapté en: '{puzzle_type}'")
        
        # Vérifier que les valeurs correspondent aux valeurs attendues pour PostgreSQL
        self.assertEqual(sequence_type, "SEQUENCE")
        self.assertEqual(pattern_type, "PATTERN")
        self.assertEqual(puzzle_type, "PUZZLE")
    
    def test_age_group_adaptation(self):
        """Tester l'adaptation des groupes d'âge."""
        # Récupérer les valeurs adaptées
        age_9_12 = get_enum_value(AgeGroup, AgeGroup.AGE_9_12)
        age_13_plus = get_enum_value(AgeGroup, AgeGroup.AGE_13_PLUS)
        
        # Afficher les valeurs adaptées
        print(f"AgeGroup.AGE_9_12 adapté en: '{age_9_12}'")
        print(f"AgeGroup.AGE_13_PLUS adapté en: '{age_13_plus}'")
        
        # Vérifier que les valeurs correspondent aux valeurs attendues pour PostgreSQL
        self.assertEqual(age_9_12, "GROUP_10_12")
        self.assertEqual(age_13_plus, "GROUP_13_15")  # Correction : maintenant mappé vers GROUP_13_15
    
    def test_direct_adaptation(self):
        """Tester l'adaptation directe des valeurs."""
        # Adapter directement des valeurs avec le nom de l'enum en premier paramètre
        maitre_adapted = adapt_enum_for_db("UserRole", "maitre")
        padawan_adapted = adapt_enum_for_db("UserRole", "padawan")
        sequence_adapted = adapt_enum_for_db("LogicChallengeType", "sequence")
        age_adapted = adapt_enum_for_db("AgeGroup", "age_9_12")
        
        # Afficher les résultats
        print(f"'maitre' adapté en: '{maitre_adapted}'")
        print(f"'padawan' adapté en: '{padawan_adapted}'")
        print(f"'sequence' adapté en: '{sequence_adapted}'")
        print(f"'age_9_12' adapté en: '{age_adapted}'")
        
        # Vérifier que les valeurs correspondent aux valeurs PostgreSQL attendues
        self.assertEqual(maitre_adapted, "MAITRE")
        self.assertEqual(padawan_adapted, "PADAWAN")
        self.assertEqual(sequence_adapted, "SEQUENCE")
        self.assertEqual(age_adapted, "GROUP_10_12")


if __name__ == "__main__":
    unittest.main() 