#!/usr/bin/env python3
"""
Debug des types normalisés dans generate_ai_exercise
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server.exercise_generator import normalize_exercise_type
from app.core.constants import ExerciseTypes

def test_normalization():
    """Test de normalisation des types"""
    print("🔍 DEBUG NORMALISATION DES TYPES")
    print("=" * 50)
    
    test_types = ["mixte", "texte", "addition", "soustraction"]
    
    for test_type in test_types:
        normalized = normalize_exercise_type(test_type)
        print(f"Input: '{test_type}' -> Normalized: '{normalized}' (type: {type(normalized)})")
        
        # Comparaisons avec les constantes
        print(f"  ExerciseTypes.MIXTE = '{ExerciseTypes.MIXTE}' (type: {type(ExerciseTypes.MIXTE)})")
        print(f"  ExerciseTypes.TEXTE = '{ExerciseTypes.TEXTE}' (type: {type(ExerciseTypes.TEXTE)})")
        print(f"  normalized == ExerciseTypes.MIXTE: {normalized == ExerciseTypes.MIXTE}")
        print(f"  normalized == ExerciseTypes.TEXTE: {normalized == ExerciseTypes.TEXTE}")
        print()

if __name__ == "__main__":
    test_normalization() 