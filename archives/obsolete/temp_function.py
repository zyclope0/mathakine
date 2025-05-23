import sqlite3
import json
from fastapi.responses import JSONResponse
import requests
import traceback

async def get_exercise_by_id(request):
    exercise_id = request.path_params.get('exercise_id')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exercises WHERE id = ?', (exercise_id,))
    exercise = cursor.fetchone()
    if not exercise:
        conn.close()
        return JSONResponse({'error': 'Exercice non trouvé'}, status_code=404)
    exercise_dict = dict(exercise)
    if exercise_dict.get('choices'):
        exercise_dict['choices'] = json.loads(exercise_dict['choices'])
    conn.close()
    return JSONResponse(exercise_dict)

"""
Fonction améliorée pour la génération d'exercices avec IA thématique Star Wars
"""

async def generate_ai_exercise(exercise_type, difficulty, age=9):
    """
    Génère un exercice mathématique avec thématique Star Wars en utilisant une API d'IA.
    """
    if not USE_AI_GENERATION:
        return None
    
    try:
        # Traduire les niveaux de difficulté du format API au format Star Wars
        difficulty_mapping = {
            "easy": "Initié",
            "medium": "Padawan", 
            "hard": "Chevalier",
            "very_hard": "Maître"
        }
        
        # Traduire les types d'exercices dans un format plus lisible
        type_mapping = {
            "addition": "addition",
            "subtraction": "soustraction",
            "multiplication": "multiplication", 
            "division": "division"
        }
        
        # Obtenir les versions traduites ou utiliser les valeurs par défaut
        star_wars_difficulty = difficulty_mapping.get(difficulty, "Padawan")
        math_type = type_mapping.get(exercise_type, exercise_type)
        
        prompt = f"""
        Crée un exercice de mathématiques de type {math_type} avec un niveau de difficulté {star_wars_difficulty} 
        pour un enfant de {age} ans, dans l'univers Star Wars.
        
        Niveaux de difficulté Star Wars:
        - Initié = facile (nombres simples de 1 à 10)
        - Padawan = moyen (nombres de 10 à 50)
        - Chevalier = difficile (nombres de 50 à 100)
        - Maître = très difficile (nombres plus grands)
        
        Format de réponse en JSON avec les champs suivants:
        {{
            "question": "L'énoncé de l'exercice avec un contexte Star Wars",
            "choices": [choix1, choix2, choix3, choix4],
            "correct_answer": "Le bon choix",
            "explanation": "Explication avec termes de l'univers Star Wars"
        }}
        
        Assure-toi que la question contient des références à Star Wars (comme les cristaux Kyber, 
        Jedi, Padawan, vaisseaux, droïdes, etc.) et que la difficulté est adaptée au niveau.
        """
        
        # Appel à l'API OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extraire le JSON de la réponse
            import re
            json_match = re.search(r'({.*})', content, re.DOTALL)
            if json_match:
                exercise_data = json.loads(json_match.group(1))
                return exercise_data
        
        print(f"Erreur lors de l'appel à l'API IA: {response.status_code} - {response.text}")
        return None
    
    except Exception as e:
        print(f"Exception lors de la génération d'exercice IA: {e}")
        traceback.print_exc()
        return None
