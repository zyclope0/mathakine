# Script pour ajouter la route /api/users/stats à la liste des routes
with open('enhanced_server.py', 'r', encoding='utf-8') as file:
    content = file.read()

# Chercher la liste des routes et ajouter notre nouvelle route
if 'Route("/exercise/{exercise_id:int}", exercise_detail_page),' in content:
    modified_content = content.replace(
        'Route("/exercise/{exercise_id:int}", exercise_detail_page),',
        'Route("/exercise/{exercise_id:int}", exercise_detail_page),\n    Route("/api/users/stats", get_user_stats),'
    )

    # Écrire le contenu modifié
    with open('enhanced_server.py', 'w', encoding='utf-8') as file:
        file.write(modified_content)

    print("Route /api/users/stats ajoutée avec succès!")
else:
    print("Pattern non trouvé. Vérifiez le fichier enhanced_server.py manuellement.")
