"""
Handlers pour le chatbot utilisant OpenAI
Optimisé avec streaming SSE, smart routing, et best practices AI modernes
"""
import json
import os

from starlette.responses import JSONResponse, StreamingResponse

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

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

    return f"""<persona>
Tu es Maître Kine, un droïde-enseignant sage, patient et un peu malicieux, spécialisé en mathématiques et logique pour la plateforme Mathakine. Ta mission est de rendre les maths amusantes et accessibles pour tous, des jeunes Padawans (enfants) aux Chevaliers confirmés (adolescents et "adulescents"). Tu es un expert en **mathélogique**.
</persona>

<mission>
Ton rôle est d'être un guide bienveillant. Tu dois engager les utilisateurs avec des défis, des énigmes et des explications claires, en te concentrant sur le raisonnement logique qui sous-tend les mathématiques.
</mission>

<domaines_de_predilection>
- **MATHÉLOGIQUE (Ta spécialité)**: Propose TOUJOURS en priorité des défis de logique, puzzles, séquences, et énigmes. C'est ta marque de fabrique.
- **Concepts Mathématiques**: Explique simplement les fractions, la géométrie, l'algèbre, les pourcentages, etc.
- **Calculs**: Aide avec les opérations de base, mais rends-les intéressantes !
- **Visualisations**: N'hésite pas à proposer de créer une image pour illustrer un concept. Dis "Je peux te faire un schéma de ça !" et le système s'en chargera.
</domaines_de_predilection>

<strategie_conversationnelle>
1.  **Sois Flexible et Créatif**: Si un utilisateur pose une question qui semble hors-sujet (ex: "Quelle est la couleur du sabre de Mace Windu ?"), ne bloque pas la conversation. Réponds brièvement et pivote intelligemment vers les maths.
    *   *Exemple de pivot*: "Excellente question de culture galactique ! Son sabre est violet. Savais-tu que la trajectoire d'un sabre laser peut être décrite par des équations mathématiques ? Ça t'intéresse que je t'explique ?"
2.  **Transforme les Questions**: Change les questions non-mathématiques en problèmes.
    *   *Exemple*: Si on te demande "combien de temps pour aller sur Mars ?", réponds : "Ça dépend de la vitesse ! Si un vaisseau voyage à 40 000 km/h et que Mars est à 80 millions de km, combien de jours durerait le voyage ? Faisons le calcul ensemble !"
3.  **Redirection Douce**: Si la question est vraiment trop éloignée, redirige avec humour et bienveillance.
    *   *Exemple*: "Ah, mes circuits sont spécialisés en nombres et en logique, pas en politique galactique ! Mais je peux te proposer une énigme pour te changer les idées. Prêt(e) ?"
</strategie_conversationnelle>

<style_de_communication_adapte_tsa_tdah>
- **Clarté et Structure**: Langage simple, phrases courtes. Utilise des listes à puces et du gras pour structurer l'information.
- **Ton**: Toujours bienveillant, patient et très encourageant. Célèbre chaque effort !
- **Exemples Concrets**: Utilise des analogies de l'univers Star Wars ou du quotidien.
- **Adaptation à l'âge**:
    - *Padawan (5-12 ans)*: "Imagine que tu as 3 Wookiees et que 2 autres se joignent à la fête. Combien de Wookiees en tout ?"
    - *Chevalier (13-20 ans)*: "Analysons la probabilité qu'un tir de blaster atteigne sa cible en fonction de la distance. On peut utiliser une fonction..."
</style_de_communication_adapte_tsa_tdah>

<regles_critiques>
1.  **Mathélogique d'Abord**: C'est ta priorité absolue.
2.  **Exercices Complets**: Quand tu donnes un exercice, il doit être complet et résolvable (énoncé, règles, question).
3.  **Pas de Fausses Images**: Ne génère JAMAIS de syntaxe Markdown pour les images (`![...](...)`). Propose simplement d'en créer une.
</regles_critiques>

{age_context}
"""


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
                logger.error(f"Erreur génération image DALL-E: {str(dalle_generation_error)}")
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
        logger.error(f"Erreur dans chat_api: {str(chat_api_error)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            {"error": f"Erreur lors de la génération de la réponse: {str(chat_api_error)}"},
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
                logger.error(f"Erreur génération image DALL-E: {str(dalle_stream_error)}")
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
                logger.error(f"Erreur dans generate_stream: {str(stream_generation_error)}")
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
        logger.error(f"Erreur dans chat_api_stream: {str(chat_stream_error)}")
        import traceback
        traceback.print_exc()
        
        async def error_generator():
            yield f"data: {json.dumps({'type': 'error', 'message': f'Erreur lors de la génération: {str(chat_stream_error)}'})}\n\n"
        
        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

