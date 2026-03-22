"""
Service partagé pour le chatbot.

Factorise la logique commune entre chat_api (JSON) et chat_api_stream (SSE) :
image detection, DALL-E generation, prompt/config building, markdown cleanup.

Phase 3, item 3.2 — audit architecture 03/2026.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.core.ai_config import AIConfig
from app.core.app_model_policy import resolve_assistant_chat_model
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constantes partagées
# ---------------------------------------------------------------------------

EXPLICIT_IMAGE_KEYWORDS: Tuple[str, ...] = (
    "image",
    "dessine",
    "dessin",
    "schéma",
    "schema",
    "diagramme",
    "figure",
    "graphique",
    "visualise",
    "montre-moi",
    "affiche-moi",
    "illustration",
    "représente",
)

MATH_IMAGE_KEYWORDS: Tuple[str, ...] = (
    "géométrie",
    "triangle",
    "cercle",
    "carré",
    "rectangle",
    "forme",
    "angle",
    "fraction",
    "graphique",
    "courbe",
    "polygone",
    "losange",
    "trapèze",
    "ovale",
    "ligne",
    "point",
    "segment",
    "exercice",
    "problème",
)

MATH_GENERAL_KEYWORDS: Tuple[str, ...] = (
    "math",
    "mathématique",
    "calcul",
    "nombre",
    "équation",
    "exercice",
    "problème",
)

# Regex pré-compilées pour le nettoyage Markdown
_RE_PLACEHOLDER_IMG = re.compile(
    r"!\[([^\]]*)\]\([^)]*(?:placeholder|via\.placeholder|example\.com|example\.org)[^)]*\)",
    re.IGNORECASE,
)
_RE_GENERIC_IMG = re.compile(r"!\[([^\]]*)\]\([^)]*\)")

ASSISTANT_CHAT_METRICS_PREFIX = "assistant_chat"


# ---------------------------------------------------------------------------
# Fonctions publiques
# ---------------------------------------------------------------------------


def detect_image_request(message: str) -> Tuple[bool, bool]:
    """Détecte si le message demande une image et s'il est lié aux maths.

    Returns:
        (is_image_request, is_math_related)
    """
    lower = message.lower()
    is_image = any(kw in lower for kw in EXPLICIT_IMAGE_KEYWORDS)
    is_math = any(kw in lower for kw in MATH_IMAGE_KEYWORDS) or any(
        kw in lower for kw in MATH_GENERAL_KEYWORDS
    )
    return is_image, is_math


async def generate_image(client: Any, message: str) -> Optional[str]:
    """Génère une image éducative via DALL-E 3.

    Returns:
        URL de l'image ou None en cas d'erreur.
    """
    try:
        dalle_prompt = (
            f"Image éducative mathématique pour enfants de 5 à 20 ans : {message}. "
            "Style simple, clair, coloré, adapté aux enfants. "
            "Éléments visuels mathématiques uniquement. "
            "Pas de texte complexe, formes géométriques simples, couleurs vives et contrastées."
        )

        image_response = await client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return image_response.data[0].url
    except Exception as e:
        logger.error(f"Erreur génération image DALL-E: {e}")
        return None


def detect_complexity(message: str, conversation_history: list) -> str:
    """Détecte la complexité de la question pour smart routing.

    Returns:
        'simple' ou 'complex'.
    """
    message_lower = message.lower()

    complex_keywords = (
        "démontrer",
        "prouver",
        "théorème",
        "formule",
        "équation complexe",
        "raisonnement",
        "déduction",
        "logique avancée",
        "grille logique",
        "combinatoire",
        "probabilité",
        "séquence complexe",
        "pattern avancé",
        "résoudre étape par étape",
        "explique en détail",
        "comment fonctionne",
    )

    simple_keywords = (
        "combien fait",
        "c'est quoi",
        "qu'est-ce que",
        "définition",
        "exemple",
        "calcul simple",
        "addition",
        "soustraction",
        "multiplication",
        "division",
        "aide",
        "explique simplement",
    )

    if len(message.split()) <= 5:
        return "simple"

    if any(keyword in message_lower for keyword in complex_keywords):
        return "complex"

    if any(keyword in message_lower for keyword in simple_keywords):
        return "simple"

    return "simple"


def estimate_age(message: str) -> Optional[str]:
    """Estime la tranche d'âge de l'utilisateur à partir du message."""
    message_lower = message.lower()

    if any(
        word in message_lower
        for word in ("cm1", "cm2", "cp", "ce1", "ce2", "maternelle")
    ):
        return "5-8"
    elif any(word in message_lower for word in ("6ème", "5ème", "collège", "primaire")):
        return "9-12"
    elif any(word in message_lower for word in ("4ème", "3ème", "lycée", "seconde")):
        return "13-16"
    elif any(word in message_lower for word in ("terminale", "bac", "université")):
        return "17-20"

    return None


def build_system_prompt(estimated_age: Optional[str] = None) -> str:
    """Construit le prompt système optimisé avec few-shot learning."""
    age_context = ""
    if estimated_age:
        age_context = (
            f"\n\n📊 CONTEXTE UTILISATEUR : L'utilisateur a environ {estimated_age} ans. "
            "Adapte ton langage, tes exemples et ta complexité en conséquence."
        )

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
4.  **Formatage LaTeX Obligatoire**: Toutes les expressions mathématiques DOIVENT être en LaTeX.
    - Inline : $a + b = c$, $\\frac{{1}}{{2}}$, $x^2$, $\\sqrt{{x}}$, $\\times$, $\\div$
    - Bloc (étape importante) : $$\\frac{{a}}{{b}} = c$$
    - Le texte narratif reste en prose, seules les maths sont en LaTeX.
</regles_critiques>

{age_context}
"""


def build_chat_config(
    message: str,
    conversation_history: List[Dict[str, str]],
    *,
    user_tier: Optional[str] = None,
) -> Dict[str, Any]:
    """Construit la configuration complète pour l'appel OpenAI.

    Le modèle texte suit :mod:`app.core.app_model_policy` (défaut produit ``gpt-5-mini``).
    ``complexity`` (simple/complex) n'affecte que température / ``max_tokens``.

    Args:
        user_tier: Stub futur seam abonnement (ex. ``\"premium\"`` -> ``gpt-5.4``).

    Returns:
        Dict avec keys: model, messages, temperature, max_tokens, complexity.
    """
    complexity = detect_complexity(message, conversation_history)
    model = resolve_assistant_chat_model(user_tier=user_tier)
    estimated_age = estimate_age(message)
    system_prompt = build_system_prompt(estimated_age)

    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    for msg in conversation_history[-5:]:
        messages.append(
            {"role": msg.get("role", "user"), "content": msg.get("content", "")}
        )
    messages.append({"role": "user", "content": message})

    temperature = 0.4 if complexity == "simple" else 0.6
    max_tokens = 500 if complexity == "complex" else 400

    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "complexity": complexity,
    }


def assistant_chat_metrics_key(complexity: Optional[str]) -> str:
    """Clé stable pour l'observabilité runtime du chatbot."""
    cplx = (complexity or "simple").strip().lower()
    if cplx not in ("simple", "complex"):
        cplx = "simple"
    return f"{ASSISTANT_CHAT_METRICS_PREFIX}:{cplx}"


def estimate_chat_prompt_tokens(messages: List[Dict[str, str]]) -> int:
    """Estimation best-effort des tokens prompt pour le chat."""
    chars = sum(len(str(m.get("content", ""))) for m in messages)
    return max(0, chars // 4)


def extract_chat_usage_estimate(
    response_or_usage: Any,
    *,
    messages: List[Dict[str, str]],
    completion_text: str,
) -> Tuple[int, int]:
    """
    Retourne ``(prompt_tokens, completion_tokens)``.

    Utilise ``usage`` si disponible, sinon estimation simple longueur/4.
    """
    usage = getattr(response_or_usage, "usage", response_or_usage)
    prompt_estimate = estimate_chat_prompt_tokens(messages)
    completion_estimate = max(0, len(completion_text) // 4)

    prompt_tokens = getattr(usage, "prompt_tokens", None)
    completion_tokens = getattr(usage, "completion_tokens", None)

    return (
        int(prompt_tokens) if prompt_tokens is not None else prompt_estimate,
        (
            int(completion_tokens)
            if completion_tokens is not None
            else completion_estimate
        ),
    )


def generation_duration_seconds(started_at: datetime) -> float:
    """Durée wall-clock simple partagée par les handlers chat."""
    return max(0.0, (datetime.now() - started_at).total_seconds())


def build_openai_chat_completion_kwargs(
    cfg: Dict[str, Any],
    *,
    stream: bool = False,
) -> Dict[str, Any]:
    """
    Paramètres ``chat.completions.create`` alignés sur la famille du modèle.

    GPT-5 / o3 / o1 n'acceptent pas ``max_tokens`` (utiliser ``max_completion_tokens``).
    Les pénalités / ``top_p`` classiques ne sont envoyées que pour les modèles type GPT-4o.
    """
    model = cfg["model"]
    messages = cfg["messages"]
    max_out = int(cfg["max_tokens"])
    temperature = cfg["temperature"]

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if stream:
        kwargs["stream"] = True

    if AIConfig.is_o1_model(model):
        kwargs["max_completion_tokens"] = max_out
    elif AIConfig.is_o3_model(model):
        kwargs["max_completion_tokens"] = max_out
        kwargs["reasoning_effort"] = "low"
    elif AIConfig.is_gpt5_model(model):
        kwargs["max_completion_tokens"] = max_out
        kwargs["reasoning_effort"] = "low"
        kwargs["verbosity"] = "medium"
    else:
        kwargs["max_tokens"] = max_out
        kwargs["temperature"] = temperature
        kwargs["top_p"] = 0.9
        kwargs["frequency_penalty"] = 0.3
        kwargs["presence_penalty"] = 0.1

    return kwargs


def cleanup_markdown_images(text: str) -> str:
    """Supprime les placeholders d'images Markdown invalides.

    Conserve les images avec de vraies URLs http.
    """
    text = _RE_PLACEHOLDER_IMG.sub(r"\1", text)
    text = _RE_GENERIC_IMG.sub(
        lambda m: m.group(1) if "http" not in m.group(0).lower() else m.group(0),
        text,
    )
    return text
