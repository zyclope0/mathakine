#!/usr/bin/env python3
"""
Script de test pour vérifier le système de badges après validation d'exercice
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "ObiWan"
PASSWORD = "password123"

def test_badges_after_exercise():
    """Test complet du système de badges"""
    
    print("🧪 Test du système de badges après validation d'exercice")
    print("=" * 60)
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    # 1. Connexion via formulaire web
    print("1. Connexion via formulaire web...")
    login_response = session.post(f"{BASE_URL}/login", data={
        "username": USERNAME,
        "password": PASSWORD
    }, allow_redirects=False)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Erreur de connexion: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}")
        return
    
    print("✅ Connexion réussie")
    
    # 2. Vérifier les badges avant
    print("\n2. État des badges avant exercice...")
    badges_before = session.get(f"{BASE_URL}/api/badges/user")
    if badges_before.status_code == 200:
        data = badges_before.json()
        badges_data = data.get('data', {})
        earned_badges = badges_data.get('earned_badges', [])
        user_stats = badges_data.get('user_stats', {})
        print(f"   Badges obtenus: {len(earned_badges)}")
        print(f"   Points: {user_stats.get('total_points', 0)}")
    else:
        print(f"   ❌ Erreur récupération badges: {badges_before.status_code}")
    
    # 3. Générer et soumettre un exercice
    print("\n3. Génération d'un exercice...")
    exercise_response = session.post(f"{BASE_URL}/api/exercises/generate", json={
        "exercise_type": "addition",
        "difficulty": "initie",
        "save": True
    })
    
    if exercise_response.status_code != 200:
        print(f"❌ Erreur génération exercice: {exercise_response.status_code}")
        print(f"Response: {exercise_response.text[:200]}")
        return
    
    exercise_data = exercise_response.json()
    exercise_info = exercise_data.get('data', {})
    exercise_id = exercise_info.get('id')
    correct_answer = exercise_info.get('correct_answer')
    
    print(f"✅ Exercice généré (ID: {exercise_id})")
    print(f"   Question: {exercise_info.get('question')}")
    print(f"   Réponse correcte: {correct_answer}")
    
    # 4. Soumettre la réponse correcte
    print("\n4. Soumission de la réponse...")
    
    submit_response = session.post(f"{BASE_URL}/api/submit-answer", json={
        "exercise_id": exercise_id,
        "user_answer": str(correct_answer),
        "time_spent": 3.5  # Temps rapide pour potentiellement déclencher le badge vitesse
    })
    
    if submit_response.status_code != 200:
        print(f"❌ Erreur soumission: {submit_response.status_code}")
        print(f"Response: {submit_response.text[:200]}")
        return
    
    submit_data = submit_response.json()
    print(f"✅ Réponse soumise")
    print(f"   Correcte: {submit_data.get('is_correct', False)}")
    
    # Vérifier si des badges ont été obtenus
    new_badges = submit_data.get('new_badges', [])
    if new_badges:
        print(f"🎖️ Nouveaux badges obtenus: {len(new_badges)}")
        for badge in new_badges:
            print(f"   - {badge.get('name')} (+{badge.get('points_reward')} pts)")
    else:
        print("   Aucun nouveau badge")
    
    # 5. Vérifier les badges après
    print("\n5. État des badges après exercice...")
    badges_after = session.get(f"{BASE_URL}/api/badges/user")
    if badges_after.status_code == 200:
        data = badges_after.json()
        badges_data = data.get('data', {})
        earned_badges = badges_data.get('earned_badges', [])
        user_stats = badges_data.get('user_stats', {})
        
        print(f"   Badges obtenus: {len(earned_badges)}")
        print(f"   Points: {user_stats.get('total_points', 0)}")
        print(f"   Niveau: {user_stats.get('current_level', 1)}")
        print(f"   Rang Jedi: {user_stats.get('jedi_rank', 'youngling')}")
        
        if earned_badges:
            print("\n   Badges détaillés:")
            for badge in earned_badges:
                print(f"   - {badge.get('name')} ({badge.get('star_wars_title')})")
                print(f"     {badge.get('description')}")
                earned_at = badge.get('earned_at', 'N/A')
                if earned_at != 'N/A':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(earned_at.replace('Z', '+00:00'))
                        earned_at = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        pass
                print(f"     Obtenu le: {earned_at}")
    else:
        print(f"   ❌ Erreur récupération badges après: {badges_after.status_code}")
    
    # 6. Test de vérification manuelle des badges
    print("\n6. Test de vérification manuelle...")
    check_response = session.post(f"{BASE_URL}/api/badges/check")
    if check_response.status_code == 200:
        check_data = check_response.json()
        badges_earned = check_data.get('badges_earned', 0)
        print(f"✅ Vérification terminée: {badges_earned} nouveaux badges")
        
        if badges_earned > 0:
            print("🎉 Des badges supplémentaires ont été trouvés !")
    else:
        print(f"❌ Erreur vérification: {check_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Test terminé !")
    
    # 7. Afficher les badges disponibles
    print("\n7. Badges disponibles...")
    available_response = session.get(f"{BASE_URL}/api/badges/available")
    if available_response.status_code == 200:
        available_data = available_response.json()
        available_badges = available_data.get('data', [])
        print(f"   Total badges disponibles: {len(available_badges)}")
        
        for badge in available_badges[:3]:  # Afficher les 3 premiers
            print(f"   - {badge.get('name')} ({badge.get('difficulty')})")
            print(f"     {badge.get('description')}")
            print(f"     Récompense: {badge.get('points_reward')} points")

if __name__ == "__main__":
    try:
        test_badges_after_exercise()
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        import traceback
        traceback.print_exc() 