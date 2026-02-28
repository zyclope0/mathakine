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
