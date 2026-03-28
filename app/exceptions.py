"""
Exceptions métier pour différencier erreurs fonctionnelles vs techniques.

Mapping vers codes HTTP dans les handlers.
"""


class ExerciseSubmitError(Exception):
    """Erreur lors de la soumission d'une réponse (submit_answer)."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class ExerciseNotFoundError(ExerciseSubmitError):
    """Exercice non trouvé (404)."""

    def __init__(self, message: str = "Exercice non trouvé"):
        super().__init__(404, message)


class ChallengeNotFoundError(ExerciseSubmitError):
    """Défi logique non trouvé (404)."""

    def __init__(self, message: str = "Défi logique non trouvé"):
        super().__init__(404, message)


class ChallengeAttemptRecordError(Exception):
    """Impossible d'enregistrer la tentative de défi (erreur métier)."""

    def __init__(self, message: str = "Impossible d'enregistrer la tentative"):
        self.message = message
        super().__init__(message)


class UserNotFoundError(Exception):
    """Utilisateur non trouvé."""

    def __init__(self, message: str = "Utilisateur non trouvé"):
        self.message = message
        super().__init__(message)


class DatabaseOperationError(Exception):
    """Échec d'une opération base de données (suppression ou archivage)."""

    def __init__(self, message: str = "Échec de l'opération base de données"):
        self.message = message
        super().__init__(message)


class InterleavedNotEnoughVariety(Exception):
    """Pas assez de types éligibles pour une session entrelacée (F32)."""

    def __init__(self, message: str = "Pas assez de types pratiques récemment"):
        self.message = message
        super().__init__(message)


class SpacedRepetitionInputError(ValueError):
    """Données invalides pour le moteur SM-2 (qualité hors plage, etc.)."""

    def __init__(self, message: str = "Entrée spaced repetition invalide"):
        self.message = message
        super().__init__(message)
