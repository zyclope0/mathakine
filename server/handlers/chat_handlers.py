"""
Handlers pour le chatbot utilisant OpenAI
Optimisé avec streaming SSE, smart routing, et best practices AI modernes
"""
import json
import os
from starlette.responses import JSONResponse, StreamingResponse
from app.core.config import settings

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def _detect_complexity(message: str, conversation_history: list) -> str:
    """
    Détecte la complexité de la question pour smart routing.
    Retourne 'simple' ou 'complex' pour choisir le modèle approprié.
    
    Best practice : Utiliser gpt-4o-mini pour questions simples (coût réduit),
    gpt-4o pour questions complexes (meilleure qualité).
    """
    message_lower = message.lower()
    
    # Indicateurs de complexité
    complex_keywords = [
        'démontrer', 'prouver', 'théorème', 'formule', 'équation complexe',
        'raisonnement', 'déduction', 'logique avancée', 'grille logique',
        'combinatoire', 'probabilité', 'séquence complexe', 'pattern avancé',
        'résoudre étape par étape', 'explique en détail', 'comment fonctionne'
    ]
    
    simple_keywords = [
        'combien fait', 'c\'est quoi', 'qu\'est-ce que', 'définition',
        'exemple', 'calcul simple', 'addition', 'soustraction', 'multiplication',
        'division', 'aide', 'explique simplement'
    ]
    
    # Questions courtes = généralement simples
    if len(message.split()) <= 5:
        return 'simple'
    
    # Détecter mots-clés complexes
    if any(keyword in message_lower for keyword in complex_keywords):
        return 'complex'
    
    # Détecter mots-clés simples
    if any(keyword in message_lower for keyword in simple_keywords):
        return 'simple'
    
    # Par défaut, utiliser le modèle simple pour économiser les coûts
    return 'simple'


def _estimate_age(message: str) -> str | None:
    """
    Estime l'âge de l'utilisateur depuis le message.
    Amélioration : pourrait utiliser le profil utilisateur si disponible.
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['cm1', 'cm2', 'cp', 'ce1', 'ce2', 'maternelle']):
        return '5-8'
    elif any(word in message_lower for word in ['6ème', '5ème', 'collège', 'primaire']):
        return '9-12'
    elif any(word in message_lower for word in ['4ème', '3ème', 'lycée', 'seconde']):
        return '13-16'
    elif any(word in message_lower for word in ['terminale', 'bac', 'université']):
        return '17-20'
    
    return None


def _build_system_prompt(estimated_age: str | None = None) -> str:
    """
    Construit le prompt système optimisé avec few-shot learning amélioré.
    Best practice : Exemples concrets dans le prompt pour guider l'IA.
    """
    age_context = ""
    if estimated_age:
        age_context = f"\n\n📊 CONTEXTE UTILISATEUR : L'utilisateur a environ {estimated_age} ans. Adapte ton langage, tes exemples et ta complexité en conséquence."
    
    return f"""Tu es l'assistant mathématique de Mathakine, une plateforme éducative spécialisée pour enfants de 5 à 20 ans avec besoins spéciaux (TSA/TDAH).

🎯 MISSION PRINCIPALE :
Tu es UNIQUEMENT un assistant mathématique et logique. Tu ne réponds QU'AUX questions liées aux mathématiques, à la logique, aux raisonnements mathématiques et aux défis mathélogiques.

📚 DOMAINES AUTORISÉS (uniquement) :
- Calculs : addition, soustraction, multiplication, division
- Concepts mathématiques : nombres, fractions, décimales, pourcentages, géométrie, algèbre de base
- Problèmes mathématiques : énoncés, situations concrètes, applications pratiques
- **MATHÉLOGIQUE (PRIORITÉ)** : défis logiques, raisonnement déductif, patterns, séquences, puzzles mathématiques, problèmes de logique pure, énigmes mathématiques, problèmes de déduction, problèmes de combinatoire, problèmes de probabilité logique, problèmes de stratégie mathématique
- Méthodes de résolution : astuces, techniques, stratégies pour résoudre des problèmes
- Explications de concepts : définitions simples, exemples concrets, analogies mathématiques
- Visualisations mathématiques : **TU PEUX GÉNÉRER DES IMAGES** avec DALL-E 3 pour aider à visualiser des concepts mathématiques (géométrie, fractions, graphiques, exercices visuels, etc.). Si l'utilisateur demande de "dessiner", "créer une image", "montrer visuellement" ou similaire, tu dois générer une image automatiquement. Ne dis JAMAIS que tu ne peux pas créer d'images - c'est FAUX, tu le peux !

🧩 MATHÉLOGIQUE - EXEMPLES CONCRETS (FEW-SHOT LEARNING) :

**Exemple 1 - Problème de grille logique :**
Question : "J'ai un problème de logique avec des carrés"
Réponse : "Voici un défi de mathélogique ! 🧩\n\nImagine une grille 3x3 avec des carrés. Chaque carré peut être vide ou contenir un nombre. Les règles sont :\n- La somme de chaque ligne doit être égale\n- La somme de chaque colonne doit être égale\n- Les nombres doivent être différents\n\nPeux-tu trouver une solution ? Commence par remplir une ligne avec des nombres qui s'additionnent bien !"

**Exemple 2 - Problème de séquence avec carrés :**
Question : "Quel nombre vient après dans cette séquence : 1, 4, 9, 16, ?"
Réponse : "Excellente question de mathélogique ! 🔢\n\nRegarde bien : 1 = 1², 4 = 2², 9 = 3², 16 = 4²...\n\nLe prochain nombre est 5² = 25 ! C'est la séquence des carrés parfaits. Bravo pour avoir repéré le pattern !"

**Exemple 3 - Problème de déduction avec contraintes (COMPLET) :**
Question : "J'ai un problème avec des boîtes et des étiquettes"
Réponse : "Voici un défi de logique déductive ! 🎯\n\n**Énoncé complet :**\nTu as 3 boîtes : une contient des pommes, une contient des oranges, et une contient un mélange des deux.\nChaque boîte a une étiquette, mais TOUTES les étiquettes sont FAUSSES.\nLes étiquettes sont : 'Pommes', 'Oranges', 'Mélange'.\n\n**Question :** Comment peux-tu déterminer le contenu réel de chaque boîte en ouvrant UNE SEULE boîte ?\n\n**Indice :** Ouvre la boîte étiquetée 'Mélange'. Si tu trouves des pommes, cette boîte est en fait 'Pommes', donc l'étiquette 'Oranges' doit être sur la boîte 'Mélange' réel, et l'étiquette 'Pommes' sur la boîte 'Oranges'.\n\nPense étape par étape avec les contraintes !"

💡 STRATÉGIE PROACTIVE :
- Si l'utilisateur demande "un défi" ou "une question", propose TOUJOURS en priorité une question de mathélogique
- Si l'utilisateur demande "un exercice", propose un mélange de calcul et de mathélogique
- Si l'utilisateur demande "de l'aide", propose des méthodes de résolution pour des problèmes de mathélogique

🚫 DOMAINES INTERDITS (rediriger poliment) :
- Questions générales non mathématiques
- Sujets scolaires autres que les maths (histoire, français, sciences naturelles, etc.)
- Divertissement non mathématique
- Questions personnelles ou privées
- Autres sujets hors mathématiques/logique

💬 STRATÉGIE DE REDIRECTION :
Si une question n'est PAS mathématique/logique, réponds ainsi :
"Je suis spécialisé en mathématiques et logique ! Je peux t'aider avec des calculs, des problèmes mathématiques, ou des défis logiques. Peux-tu me poser une question sur les maths ? 🧮"

🎨 STYLE DE COMMUNICATION (adapté TSA/TDAH) :
- Langage simple, clair et direct (éviter les métaphores complexes)
- Phrases courtes (maximum 2-3 phrases par réponse)
- Structure prévisible : question → explication → exemple → encouragement
- Pas de sarcasme, d'ironie ou d'humour ambigu
- Ton bienveillant, patient et encourageant
- Utiliser des exemples concrets et visuels quand possible

📊 ADAPTATION PAR ÂGE :
- 5-8 ans : Langage très simple, exemples avec objets du quotidien (pommes, jouets), encouragements fréquents
- 9-12 ans : Explications progressives, exemples concrets, introduction de termes mathématiques simples
- 13-16 ans : Langage plus technique mais accessible, exemples variés, encouragement de la réflexion
- 17-20 ans : Langage mathématique précis, exemples abstraits possibles, encouragement de l'autonomie

🚀 CONTEXTE MATHAKINE :
Si on te demande des informations sur Mathakine, tu peux mentionner :
- Plateforme d'apprentissage mathématique adaptatif
- Exercices personnalisés selon le niveau (Initié, Padawan, Chevalier, Maître)
- Défis logiques progressifs (12 types de défis mathélogiques)
- Système de badges et gamification
- Accessibilité WCAG 2.1 AAA pour tous les besoins

📏 RÈGLES STRICTES :
1. TOUJOURS rester dans le domaine mathématique/logique
2. CONCISION : Maximum 4 phrases pour réponses simples, mais tu PEUX dépasser pour proposer un exercice COMPLET et RÉSOLVABLE (concision adaptée pour TSA/TDAH - structure claire avec sections)
3. TOUJOURS encourager et féliciter les efforts
4. JAMAIS critiquer ou décourager
5. REDIRIGER poliment les questions hors sujet
6. UTILISER des exemples concrets et visuels
7. ADAPTER le langage à l'âge estimé de l'enfant
8. **PRIVILÉGIER les questions de mathélogique** quand l'utilisateur demande un défi ou une question
9. **IMPORTANT** : Si l'utilisateur demande une image, un dessin, un schéma ou une visualisation mathématique, TU DOIS générer une image avec DALL-E 3. Ne dis JAMAIS que tu ne peux pas créer d'images - c'est INCORRECT. Tu as la capacité de générer des images mathématiques éducatives.
10. **INTERDIT** : Ne JAMAIS utiliser de syntaxe Markdown pour les images (pas de `![texte](url)`). Si tu veux proposer une image, dis simplement "Je peux créer une image pour t'aider" et le système générera l'image automatiquement. Ne génère JAMAIS de placeholders d'images ou de liens vers des images inexistantes.
11. **CRITIQUE - EXERCICES COMPLETS** : Quand tu proposes un exercice ou un défi mathélogique, il DOIT être COMPLET et RÉSOLVABLE. Tu DOIS inclure :
    - Toutes les règles et contraintes nécessaires
    - Tous les éléments de départ (nombres, objets, positions initiales)
    - La question précise à résoudre
    - Les informations suffisantes pour trouver la solution
    - Si une image est générée, l'exercice complet DOIT être dans la réponse texte (l'image est un complément visuel, pas un remplacement)
    - Structure claire : **Énoncé**, **Règles**, **Question**, **Éléments de départ** (si applicable)

🎯 OBJECTIF FINAL :
Aider chaque enfant à progresser en mathématiques avec bienveillance, patience et clarté, en restant strictement dans le domaine mathématique et logique. **Orienter activement vers la mathélogique** pour développer le raisonnement logique et la pensée déductive, qui sont au cœur de l'apprentissage mathématique.{age_context}"""


async def chat_api(request):
    """
    Endpoint API pour le chatbot
    
    Utilise OpenAI pour répondre aux questions sur Mathakine
    """
    try:
        # Vérifier que OpenAI est disponible
        if not OPENAI_AVAILABLE:
            return JSONResponse(
                {"error": "OpenAI non disponible"},
                status_code=503
            )
        
        # Vérifier que la clé API est configurée
        if not settings.OPENAI_API_KEY:
            return JSONResponse(
                {"error": "Clé API OpenAI non configurée"},
                status_code=503
            )
        
        # Récupérer les données de la requête
        data = await request.json()
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return JSONResponse(
                {"error": "Message requis"},
                status_code=400
            )
        
        # Créer le client OpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Détecter si la demande concerne une image mathématique
        image_keywords = ['image', 'dessine', 'dessin', 'schéma', 'diagramme', 'figure', 'graphique', 'visualise', 'montre', 'créer', 'génère', 'fais', 'montre-moi', 'affiche']
        math_image_keywords = ['géométrie', 'triangle', 'cercle', 'carré', 'rectangle', 'forme', 'angle', 'fraction', 'graphique', 'courbe', 'polygone', 'losange', 'trapèze', 'cercle', 'ovale', 'ligne', 'point', 'segment', 'exercice', 'problème']
        
        is_image_request = any(keyword in message.lower() for keyword in image_keywords)
        is_math_related = any(keyword in message.lower() for keyword in math_image_keywords) or any(
            keyword in message.lower() for keyword in ['math', 'mathématique', 'calcul', 'nombre', 'équation', 'exercice', 'problème']
        )
        
        # Si demande d'image ET mathématique, générer une image avec DALL-E
        # MAIS continuer avec la réponse texte complète pour avoir l'exercice résolvable
        if is_image_request and is_math_related:
            try:
                # Construire un prompt optimisé pour DALL-E (style éducatif, adapté enfants)
                dalle_prompt = f"""Image éducative mathématique pour enfants de 5 à 20 ans : {message}. 
Style simple, clair, coloré, adapté aux enfants. Éléments visuels mathématiques uniquement. 
Pas de texte complexe, formes géométriques simples, couleurs vives et contrastées."""
                
                # Générer une image avec DALL-E 3
                image_response = await client.images.generate(
                    model="dall-e-3",
                    prompt=dalle_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                image_url = image_response.data[0].url
                # Ne pas retourner immédiatement - continuer pour générer l'exercice complet
                # L'image sera ajoutée à la réponse finale
            except Exception as dalle_generation_error:
                # Si erreur de génération d'image, continuer avec la réponse texte normale
                print(f"Erreur génération image DALL-E: {str(dalle_generation_error)}")
                image_url = None
        else:
            image_url = None
        
        # Détecter la complexité pour smart routing
        complexity = _detect_complexity(message, conversation_history)
        
        # Smart routing : choisir le modèle selon la complexité
        # Best practice : gpt-4o-mini pour questions simples (coût réduit), gpt-4o pour complexes (qualité)
        model = "gpt-4o-mini" if complexity == 'simple' else "gpt-4o"
        
        # Détecter l'âge pour personnalisation
        estimated_age = _estimate_age(message)
        
        # Construire le prompt système optimisé avec few-shot learning
        system_prompt = _build_system_prompt(estimated_age)

        # Construire les messages pour OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Ajouter l'historique de conversation (limité aux 5 derniers messages)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Ajouter le message actuel
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Appeler OpenAI avec paramètres optimisés selon la complexité
        # Best practice : Paramètres adaptés selon le modèle et la complexité
        # Augmenté max_tokens pour permettre des exercices complets et résolvables
        temperature = 0.4 if complexity == 'simple' else 0.6  # Plus prévisible pour questions simples
        max_tokens = 500 if complexity == 'complex' else 400  # Augmenté pour exercices complets
        
        response = await client.chat.completions.create(
            model=model,  # Smart routing : modèle choisi selon complexité
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
            frequency_penalty=0.3,
            presence_penalty=0.1,
        )
        
        # Extraire la réponse
        assistant_message = response.choices[0].message.content
        
        # Nettoyer les placeholders d'images Markdown (best practice : éviter les placeholders)
        # Supprimer les patterns comme ![texte](url) ou ![texte](placeholder)
        import re
        # Supprimer les images Markdown avec placeholders ou URLs suspectes
        assistant_message = re.sub(
            r'!\[([^\]]*)\]\([^)]*(?:placeholder|via\.placeholder|example\.com|example\.org)[^)]*\)',
            r'\1',  # Remplacer par juste le texte alternatif
            assistant_message,
            flags=re.IGNORECASE
        )
        # Supprimer aussi les images Markdown génériques sans URL valide
        assistant_message = re.sub(
            r'!\[([^\]]*)\]\([^)]*\)',
            lambda m: m.group(1) if 'http' not in m.group(0).lower() else m.group(0),
            assistant_message
        )
        
        # Retourner la réponse avec l'image si elle a été générée
        response_data = {
            "response": assistant_message,
            "model_used": model,  # Debug : indiquer quel modèle a été utilisé
            "complexity": complexity  # Debug : indiquer la complexité détectée
        }
        
        # Ajouter l'URL de l'image si elle a été générée
        if image_url:
            response_data["image_url"] = image_url
            response_data["type"] = "image"
        
        return JSONResponse(response_data)
        
    except Exception as chat_api_error:
        print(f"Erreur dans chat_api: {str(chat_api_error)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Erreur lors de la génération de la réponse: {str(e)}"},
            status_code=500
        )


async def chat_api_stream(request):
    """
    Endpoint API pour le chatbot avec streaming SSE.
    
    Best practice : Streaming pour meilleure UX - l'utilisateur voit la réponse
    apparaître progressivement au lieu d'attendre la réponse complète.
    
    Réduit la perception du temps d'attente et améliore l'engagement.
    """
    try:
        # Vérifier que OpenAI est disponible
        if not OPENAI_AVAILABLE:
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'OpenAI non disponible'})}\n\n"
            
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # Vérifier que la clé API est configurée
        if not settings.OPENAI_API_KEY:
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Clé API OpenAI non configurée'})}\n\n"
            
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # Récupérer les données de la requête
        data = await request.json()
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        use_streaming = data.get('stream', True)  # Streaming par défaut
        
        if not message:
            async def error_generator():
                yield f"data: {json.dumps({'type': 'error', 'message': 'Message requis'})}\n\n"
            
            return StreamingResponse(
                error_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        # Créer le client OpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Détecter si la demande concerne une image mathématique
        image_keywords = ['image', 'dessine', 'dessin', 'schéma', 'diagramme', 'figure', 'graphique', 'visualise', 'montre', 'créer', 'génère', 'fais', 'montre-moi', 'affiche']
        math_image_keywords = ['géométrie', 'triangle', 'cercle', 'carré', 'rectangle', 'forme', 'angle', 'fraction', 'graphique', 'courbe', 'polygone', 'losange', 'trapèze', 'cercle', 'ovale', 'ligne', 'point', 'segment', 'exercice', 'problème']
        
        is_image_request = any(keyword in message.lower() for keyword in image_keywords)
        is_math_related = any(keyword in message.lower() for keyword in math_image_keywords) or any(
            keyword in message.lower() for keyword in ['math', 'mathématique', 'calcul', 'nombre', 'équation', 'exercice', 'problème']
        )
        
        # Si demande d'image ET mathématique, générer une image avec DALL-E
        # MAIS continuer avec la réponse texte complète pour avoir l'exercice résolvable
        image_url = None
        if is_image_request and is_math_related:
            try:
                dalle_prompt = f"""Image éducative mathématique pour enfants de 5 à 20 ans : {message}. 
Style simple, clair, coloré, adapté aux enfants. Éléments visuels mathématiques uniquement. 
Pas de texte complexe, formes géométriques simples, couleurs vives et contrastées."""
                
                image_response = await client.images.generate(
                    model="dall-e-3",
                    prompt=dalle_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                image_url = image_response.data[0].url
                # Ne pas retourner immédiatement - continuer pour générer l'exercice complet
                # L'image sera envoyée dans le stream avec la réponse texte complète
            except Exception as dalle_stream_error:
                print(f"Erreur génération image DALL-E: {str(dalle_stream_error)}")
                # Continuer avec le traitement texte normal
                image_url = None
        
        # Détecter la complexité pour smart routing
        complexity = _detect_complexity(message, conversation_history)
        model = "gpt-4o-mini" if complexity == 'simple' else "gpt-4o"
        
        # Détecter l'âge pour personnalisation
        estimated_age = _estimate_age(message)
        
        # Construire le prompt système optimisé
        system_prompt = _build_system_prompt(estimated_age)
        
        # Construire les messages pour OpenAI
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Ajouter l'historique de conversation (limité aux 5 derniers messages)
        # Best practice : Limiter l'historique pour éviter dépassement de contexte
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Ajouter le message actuel
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Paramètres optimisés selon la complexité
        # Augmenté max_tokens pour permettre des exercices complets et résolvables
        temperature = 0.4 if complexity == 'simple' else 0.6
        max_tokens = 500 if complexity == 'complex' else 400  # Augmenté pour exercices complets
        
        async def generate_stream():
            try:
                # Si une image a été générée, l'envoyer en premier
                if image_url:
                    yield f"data: {json.dumps({'type': 'image', 'url': image_url})}\n\n"
                
                # Envoyer un message de démarrage
                yield f"data: {json.dumps({'type': 'status', 'message': 'Réflexion en cours...'})}\n\n"
                
                # Créer le stream OpenAI
                stream = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,  # Activer le streaming
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=0.9,
                    frequency_penalty=0.3,
                    presence_penalty=0.1,
                )
                
                # Stream chaque chunk de la réponse
                full_response = ""
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        # Envoyer chaque chunk au client pour affichage progressif
                        yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
                
                # Nettoyer les placeholders d'images Markdown dans la réponse complète
                import re
                cleaned_response = re.sub(
                    r'!\[([^\]]*)\]\([^)]*(?:placeholder|via\.placeholder|example\.com|example\.org)[^)]*\)',
                    r'\1',
                    full_response,
                    flags=re.IGNORECASE
                )
                cleaned_response = re.sub(
                    r'!\[([^\]]*)\]\([^)]*\)',
                    lambda m: m.group(1) if 'http' not in m.group(0).lower() else m.group(0),
                    cleaned_response
                )
                
                # Si la réponse a été nettoyée, envoyer un chunk de correction si nécessaire
                if cleaned_response != full_response:
                    # La réponse a déjà été envoyée chunk par chunk, donc on ne peut pas la modifier
                    # Mais on peut envoyer un message de fin avec indication
                    pass
                
                # Envoyer un message de fin avec métadonnées
                yield f"data: {json.dumps({'type': 'done', 'model_used': model, 'complexity': complexity})}\n\n"
                
            except Exception as stream_generation_error:
                print(f"Erreur dans generate_stream: {str(stream_generation_error)}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur lors de la génération: {str(stream_generation_error)}'})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Important pour Nginx
            }
        )
        
    except Exception as chat_stream_error:
        print(f"Erreur dans chat_api_stream: {str(chat_stream_error)}")
        import traceback
        traceback.print_exc()
        
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur lors de la génération: {str(e)}'})}\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

