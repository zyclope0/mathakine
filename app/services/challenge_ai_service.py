"""
Service de génération de challenges par IA.
Extrait la logique de génération streaming depuis challenge_handlers.
"""
import json
import traceback
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, Optional

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.ai_config import AIConfig
from app.core.config import settings
from app.core.constants import calculate_difficulty_for_age_group
from app.core.logging_config import get_logger
from app.services import challenge_service
from app.services.challenge_validator import (
    auto_correct_challenge,
    validate_challenge_logic,
)
from app.services.challenge_service import normalize_age_group_for_frontend
from app.utils.db_utils import db_session
from app.utils.generation_metrics import generation_metrics
from app.utils.json_utils import extract_json_from_text
from app.utils.sse_utils import sse_error_message, sse_status_message
from app.utils.token_tracker import token_tracker

logger = get_logger(__name__)

# Paramètres de difficulté par groupe d'âge (affichage, complexité, etc.)
AGE_GROUP_PARAMS = {
    "6-8": {
        "complexity": "très simple",
        "numbers_max": 20,
        "steps": "1-2",
        "vocabulary": "élémentaire, mots simples",
        "display": "6-8 ans",
    },
    "9-11": {
        "complexity": "simple à moyen",
        "numbers_max": 100,
        "steps": "2-3",
        "vocabulary": "accessible aux enfants",
        "display": "9-11 ans",
    },
    "12-14": {
        "complexity": "moyen",
        "numbers_max": 500,
        "steps": "3-4",
        "vocabulary": "langage courant",
        "display": "12-14 ans",
    },
    "15-17": {
        "complexity": "moyen à complexe",
        "numbers_max": 1000,
        "steps": "4-5",
        "vocabulary": "langage précis",
        "display": "15-17 ans",
    },
    "adulte": {
        "complexity": "complexe",
        "numbers_max": 10000,
        "steps": "5+",
        "vocabulary": "langage technique possible",
        "display": "adultes",
    },
    "tous-ages": {
        "complexity": "simple à moyen",
        "numbers_max": 100,
        "steps": "2-3",
        "vocabulary": "accessible à tous",
        "display": "tous âges",
    },
}


def build_challenge_system_prompt(challenge_type: str, age_group: str) -> str:
    """Construit le prompt système pour la génération de défis."""
    params = AGE_GROUP_PARAMS.get(age_group, AGE_GROUP_PARAMS["9-11"])
    age_display = params["display"]
    age_target_phrase = (
        "pour des adultes"
        if age_group == "adulte"
        else "pour un public de tous âges"
        if age_group == "tous-ages"
        else f"pour des enfants/élèves de {age_display}"
    )

    visual_adult_rule = ""
    if age_group == "adulte" and challenge_type == "visual":
        visual_adult_rule = """
RÈGLE COMPLEXITÉ ADULTE pour VISUAL (OBLIGATOIRE) :
Pour le groupe adulte, les défis visuels/spatiaux DOIVENT être plus complexes :
- Au moins 5-6 formes différentes (cercle, carré, triangle, losange, étoile, hexagone)
- 8 à 10 positions au lieu de 6 (plus de cellules à déduire)
- OU plusieurs "?" (2-3 cases vides à remplir) dans une grille 4x4
- OU combinaison symétrie + règle supplémentaire (ex: couleur suit un pattern)
- Les grilles de symétrie doivent avoir plus de 6 éléments de chaque côté
"""

    return f"""Tu es un assistant pédagogique spécialisé dans la création de défis mathélogiques (logique mathématique).

RÈGLE ABSOLUE : Tu DOIS créer un défi de type "{challenge_type}" uniquement. Ne crée JAMAIS un défi d'un autre type.

GROUPE D'ÂGE CIBLE : {params['display']}
- Complexité : {params["complexity"]}
- Nombres : max {params["numbers_max"]}
- Étapes de raisonnement : {params["steps"]}
- Vocabulaire : {params["vocabulary"]}

Types de défis possibles :
- "sequence" : Défis de séquences logiques (nombres, formes, motifs qui se suivent)
- "pattern" : Défis de motifs à identifier dans une grille ou un arrangement
- "visual" : Défis visuels et spatiaux (formes, couleurs, rotation, symétrie, positionnement)
- "puzzle" : Défis de puzzle (réorganisation, ordre logique, étapes)
- "graph" : Défis avec graphes et relations (chemins, connexions, réseaux)
- "riddle" : Énigmes logiques avec raisonnement
- "deduction" : Défis de déduction logique (inférence, conclusion)
- "probability" : Défis de probabilités simples
- "coding" : Défis de CRYPTOGRAPHIE et DÉCODAGE (code César, substitution alphabétique, binaire, symboles secrets)
- "chess" : Défis d'échecs (mat en X coups, meilleur coup)

CONTEXTE MATHÉLOGIQUE :
Inspire-toi des exercices de mathélogique qui combinent :
- Raisonnement logique
- Éléments visuels (grilles, formes, couleurs)
- Patterns et séquences
- Déduction et inférence
- Problèmes résolubles avec une méthode claire

RÈGLE IMPORTANTE POUR LES INDICES :
Les indices (hints) doivent être des PISTES pédagogiques qui guident l'élève vers la solution, MAIS NE DOIVENT JAMAIS donner la réponse directement.
- ✅ BON : "Regarde la différence entre chaque élément"
- ✅ BON : "Quel pattern se répète ?"
- ✅ BON : "Pense à l'ordre logique des étapes"
- ❌ MAUVAIS : "La réponse est X"
- ❌ MAUVAIS : "Il faut faire Y puis Z"

Les indices doivent encourager la réflexion sans révéler la solution.

VISUAL_DATA OBLIGATOIRE :
Tu DOIS créer un objet visual_data adapté au type de défi :
- SEQUENCE : {{"sequence": [2, 4, 6, 8], "pattern": "n+2"}}
  RÈGLE DIFFICULTÉ SEQUENCE : Pour difficulty_rating >= 4 (défis difficiles), NE PAS inclure "pattern" dans visual_data.
  Le pattern suggéré donne la solution et rend le défi trop facile. L'utilisateur doit découvrir la règle seul.
  VARIATION OBLIGATOIRE pour défis difficiles (adulte, difficulty >= 4) :
  - ÉVITER le pattern surutilisé "écarts qui doublent" (ex: +3, +6, +12, +24 → trop prévisible).
  - Préférer des règles plus variées mais toujours logiques :
    * Géométrique : 2, 6, 18, 54 (×3) ou 3, 12, 48 (×4)
    * Carrés : 1, 4, 9, 16, 25 ou 2, 5, 10, 17, 26 (n²+1)
    * n×2+1 : 1, 3, 7, 15, 31 (chaque terme = précédent×2+1)
    * Différences en progression arithmétique : 2, 4, 7, 11, 16 (diffs +2,+3,+4,+5 → prochaine +6)
    * Alternance : +3 puis ×2, puis +3, ×2... (ex: 5, 8, 16, 19, 38, 41...)
    * Fibonacci-like : 1, 2, 3, 5, 8, 13 (somme des deux précédents)
- PATTERN : {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]], "size": 3}}
  Pour 9-11 ans : tu peux utiliser des formes (cercle, triangle, carré) au lieu de X/O pour plus d'attrait. Patterns valides : damier, Latin square, glissement cyclique, alternance.
  Plusieurs "?" : correct_answer DOIT lister TOUS les symboles dans l'ordre (ligne par ligne). Format: "O, O, X, O"
- PUZZLE : {{"pieces": ["Rouge", "Bleu", "Vert", "Jaune"], "hints": ["L'indice 1 qui aide à trouver l'ordre", "L'indice 2 qui aide à trouver l'ordre", "L'indice 3 qui aide à trouver l'ordre"], "description": "Description du contexte du puzzle"}}
  correct_answer : ordre des pièces de gauche à droite, séparées par des virgules. Ex: "Algèbre, Géométrie, Analyse, Probabilités, Logique, Topologie"
  IMPORTANT PUZZLE : Tu DOIS toujours fournir des indices (hints) suffisants pour que l'utilisateur puisse déduire l'ordre correct ! Sans indices, le puzzle est impossible à résoudre.
  RÈGLE DIFFICULTÉ PUZZLE : Si tu attribues difficulty_rating >= 4 (défis difficiles) :
  - INTERDIT : 4 pièces uniquement (Rouge, Bleu, Vert, Jaune) → trop facile, max 3.0
  - OBLIGATOIRE : minimum 6-7 pièces (personnages, événements, objets à ranger)
  - Indices INDIRECTS : "X n'est pas à côté de Y", "A est entre B et C", "Le 3ème n'est pas Z", "Ni X ni Y aux extrémités"
  - ÉVITER les indices trop directs type "La Verte est immédiatement à gauche de la Rouge"
  - Combiner contraintes : ordre + position relative + exclusions + paires/impaires
- GRAPH : {{"nodes": ["A", "B", "C", "D"], "edges": [["A", "B"], ["B", "C"], ["C", "D"], ["D", "A"]]}}
  IMPORTANT : Tous les noms de nœuds dans edges DOIVENT exister dans nodes.
  Optionnel : {{"positions": {{"A": [50, 50], "B": [150, 50], "C": [150, 150], "D": [50, 150]}}}} pour un placement explicite (x,y) et améliorer la lisibilité des graphes complexes.
- DEDUCTION (grille logique) : {{"type": "logic_grid", "entities": {{"personnes": ["Alice", "Bob", "Charlie"], "metiers": ["Médecin", "Avocat", "Ingénieur"], "villes": ["Paris", "Lyon", "Marseille"]}}, "clues": ["Alice n'est pas médecin", "L'avocat vit à Lyon", "Charlie ne vit pas à Paris"], "description": "Grille de déduction logique à trois dimensions"}}
  IMPORTANT DEDUCTION :
  - Le visual_data DOIT contenir "type": "logic_grid" et "entities" avec les catégories
  - La première catégorie dans "entities" est celle sur laquelle l'utilisateur fait ses associations (personnes, élèves, etc.)
  - correct_answer DOIT être au format : "Alice:Médecin:Paris,Bob:Avocat:Lyon,Charlie:Ingénieur:Marseille"
  - Les associations sont séparées par des virgules, les éléments de chaque association par des ":"
  - Les clues doivent permettre de déduire la solution unique
- VISUAL (inclut spatial) :
  * Pour symétrie/rotation : {{"type": "symmetry", "symmetry_line": "vertical", "layout": [{{"position": 0, "shape": "carré", "color": "bleu", "side": "left"}}, {{"position": 1, "shape": "triangle", "color": "vert", "side": "left"}}, {{"position": 2, "shape": "?", "color": "?", "side": "right", "question": true}}, {{"position": 3, "shape": "triangle", "color": "vert", "side": "right"}}], "shapes": ["carré bleu", "triangle vert", "?", "triangle vert"], "arrangement": "horizontal", "description": "Ligne de symétrie verticale au centre"}} — Pour une forme 4 côtés égaux (■), utilise "carré" pas "rectangle".
  * Pour formes colorées : {{"shapes": ["cercle rouge", "triangle vert", "carré bleu", "cercle rouge", "triangle vert", "carré ?"], "arrangement": "ligne"}}
  * Pour autres : {{"shapes": ["cercle", "carré", "triangle"], "arrangement": "ligne"}} ou {{"ascii": "ASCII art"}}
- CODING (cryptographie et décodage) :
  * Pour code César : {{"type": "caesar", "encoded_message": "KHOOR", "shift": 3, "alphabet": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "hint": "Chaque lettre est décalée de 3 positions", "description": "Décode ce message secret en utilisant le code César"}}
  * Pour substitution avec TABLE DE CORRESPONDANCE : deux options VALIDES uniquement :
  A) Clé COMPLÈTE (key, 26 lettres) : pour substitution arbitraire sans règle déductible.
  B) Clé PARTIELLE (partial_key) : UNIQUEMENT si la règle est DÉDUCTIBLE. Ajouter "rule_type": "caesar"|"atbash"|"keyword" dans visual_data.
  Règles déductibles (3-5 exemples dans partial_key, format lettre codée→lettre claire) :
  - César : {{"rule_type": "caesar", "partial_key": {{"D": "A", "E": "B", "F": "C"}}, ...}} → décalage constant +3
  - Atbash : {{"rule_type": "atbash", "partial_key": {{"Z": "A", "Y": "B"}}, ...}} → alphabet inversé
  - Clé-mot : {{"rule_type": "keyword", "partial_key": {{"M": "A", "A": "B", "T": "C", "H": "D"}}, ...}} → 4-6 exemples pour retrouver le mot
  ⛔ INTERDIT : substitution arbitraire avec partial_key (B→C, N→R, J→G = décalages incohérents, impossible à déduire).
  * Pour binaire : {{"type": "binary", "encoded_message": "01001000 01001001", "hint": "Chaque groupe de 8 bits représente une lettre ASCII", "description": "Convertis ce code binaire en lettres"}}
  * Pour symboles : {{"type": "symbols", "encoded_message": "★●★ ▲■", "key": {{"★": "A", "●": "B", "▲": "C", "■": "D"}}, "description": "Utilise la clé pour décoder les symboles"}}
  * Pour algorithme simple : {{"type": "algorithm", "steps": ["Prends le nombre de départ", "Multiplie par 2", "Ajoute 5", "Divise par le nombre de départ", "Résultat ?"], "input": 3, "description": "Suis les étapes avec le nombre donné"}}
  ⚠️⚠️⚠️ RÈGLES CRITIQUES POUR CODING - LIRE ATTENTIVEMENT ⚠️⚠️⚠️

  ❌ CE QUI EST STRICTEMENT INTERDIT POUR LE TYPE "coding" :
  - "sequence" avec des nombres (2, 4, 8, 16...) → C'est le type SEQUENCE, pas CODING !
  - "pattern" avec motifs → C'est le type PATTERN, pas CODING !
  - "shapes", "formes", "couleurs" → C'est le type VISUAL, pas CODING !
  - Multiplications simples (n*2, n+3) → C'est SEQUENCE ou PATTERN !
  - Tout défi qui n'implique pas de DÉCODER UN MESSAGE SECRET

  ✅ CE QU'EST VRAIMENT LE TYPE "coding" (CRYPTOGRAPHIE) :
  - DÉCODER un MESSAGE SECRET composé de LETTRES ou SYMBOLES
  - Le visual_data DOIT contenir "type" parmi : "caesar", "substitution", "binary", "symbols", "maze"
  - correct_answer = le MOT ou la PHRASE décodé(e) (ex: "CHAT", "BONJOUR", "OUI")

  ✅ EXEMPLES VALIDES DE DÉFIS "coding" :
  - Code César : "FKDW" avec décalage 3 → réponse "CHAT"
  - Substitution : "YFW" avec A→Y, H→F, E→W → réponse "AHE"
  - Binaire : "01000011 01000001 01010100" → réponse "CAT"
  - Symboles : "★●★" avec ★=O, ●=U, →=I → réponse "OUO"
  - Labyrinthe : grille avec robot à programmer → réponse "BAS, DROITE, DROITE"

  ❌ EXEMPLES INVALIDES (NE PAS FAIRE POUR "coding") :
  - Séquence 5, 10, 20, 40, ? → UTILISER LE TYPE "sequence" !
  - Grille avec formes et couleurs → UTILISER LE TYPE "visual" !
  - Pattern dans une grille → UTILISER LE TYPE "pattern" !
  - "Labyrinthe de nombres" avec numbers: [1,2,3,4,5...] et target: X → CE N'EST PAS DE LA CRYPTO !
  - Tout défi avec "numbers", "target", "movement_options" → INVALIDE !
  - Robot qui navigue dans une liste de NOMBRES → UTILISER SEQUENCE ou PUZZLE !

  ⛔⛔⛔ ERREURS FATALES À ÉVITER ABSOLUMENT ⛔⛔⛔
  SI TU GÉNÈRES UN DÉFI "coding" AVEC :
  - "numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9] → ERREUR FATALE
  - "target": un_nombre → ERREUR FATALE
  - "movement_options": [1, 2] → ERREUR FATALE
  - N'importe quelle liste de nombres sans MESSAGE À DÉCODER → ERREUR FATALE

  CODING = DÉCODER UN MESSAGE SECRET EN LETTRES/SYMBOLES, PAS naviguer dans des nombres !

- RIDDLE (énigmes) : {{"clues": ["Indice 1", "Indice 2", "Indice 3"], "context": "Contexte de l'énigme", "riddle": "Question ou énigme à résoudre", "description": "Description du problème", "key_elements": ["élément1", "élément2"]}}
- PROBABILITY (probabilités) : {{"rouge_bonbons": 10, "bleu_bonbons": 5, "vert_bonbons": 3, "total_bonbons": 18, "question": "Quelle est la probabilité de tirer un bonbon rouge ?", "description": "Dans un sac de bonbons..."}} (ou billes, cartes, dés selon le contexte)
- CHESS (échecs) :
  * INTERDIT : Ne JAMAIS utiliser la position de départ complète pour un mat en X coups (c'est impossible).
  * Pour mat en X coups : utiliser une position TACTIQUE (peu de pièces au centre, roi noir menacé).
  * Exemple réaliste mat en 2 : board avec roi noir en e8, dame blanche proche, peu de pions.
  * Notation : K/k=Roi, Q/q=Dame, R/r=Tour, B/b=Fou, N/n=Cavalier, P/p=Pion. MAJUSCULE = blanc, minuscule = noir. "" = case vide.
  * board[0] = rangée 8 (haut), board[7] = rangée 1 (bas). board[row][0] = colonne a, board[row][7] = colonne h.
  * "turn" : "white" ou "black". "objective" : "mat_en_1", "mat_en_2", "mat_en_3", "meilleur_coup".
  * correct_answer : notation algébrique "Dd7+, Rf8, Df7#" ou "Qh7+, Kf8, Qf7#"
  * highlight_positions : UNIQUEMENT des cases contenant une pièce (pas de cases vides). Notation ["d5", "h8"] ou indices [[3,3], [0,7]]

IMPORTANT pour VISUAL :
- Si le défi utilise des associations forme-couleur, tu DOIS montrer AU MOINS UN EXEMPLE VISIBLE de chaque association AVANT la question.
  Exemple MAUVAIS : ["cercle rouge", "triangle vert", "carré ?"] → L'utilisateur ne sait pas quelle couleur va avec "carré"
  Exemple BON : ["cercle rouge", "carré bleu", "triangle vert", "cercle rouge", "carré ?"] → L'utilisateur voit que carré = bleu
- L'utilisateur doit pouvoir DÉDUIRE la réponse à partir des éléments visibles, pas deviner au hasard.
- Si le défi concerne la symétrie, tu DOIS utiliser la structure "symmetry" avec "layout" et "symmetry_line".
- TERMINOLOGIE : Utilise "carré" (pas "rectangle") pour une forme à 4 côtés égaux (■). "Rectangle" = oblong. Visuellement un ■ est un carré.
- Ne génère JAMAIS de JSON malformé avec des clés comme "arrangement": "[" ou des valeurs invalides.
{visual_adult_rule}

VALIDATION LOGIQUE OBLIGATOIRE :
Avant de retourner le JSON, tu DOIS vérifier la cohérence logique :

1. Pour PATTERN avec grille (OBLIGATOIRE) :
   - CALCULE correct_answer à partir de la grille : Latin square, damier (lignes 0=2), symétrie, alternance
   - correct_answer DOIT être le symbole manquant (X, O, A, B...) déduit logiquement
   - solution_explanation DOIT expliquer CE symbole et être COHÉRENT avec correct_answer
   - Incohérence (ex. correct_answer=O alors que l'explication dit X) = ERREUR GRAVE
   - Exemple : Si grid = [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]
     → Le pattern X-O-X suggère que ? = X
     → correct_answer DOIT être "X", pas "O"

2. Pour SEQUENCE :
   - Calcule les DIFFÉRENCES entre termes consécutifs
   - Si les différences sont constantes (ex: +2, +2, +2) → prochain = dernier + cette différence
   - Si les différences AUGMENTENT de 1 (ex: +2, +3, +4, +5) → prochaine diff = dernière + 1, prochain = dernier + cette diff
   - Exemple [2, 4, 6, 8] : diffs 2,2,2 → prochain = 8+2 = 10 → correct_answer = "10"
   - Exemple [2, 4, 7, 11, 16] : diffs 2,3,4,5 → prochaine diff 6 → prochain = 16+6 = 22 → correct_answer = "22" (PAS 18 !)
   - AVANT de finaliser : recalcule mentalement. correct_answer ET solution_explanation DOIVENT être identiques.
   - Pour difficulty >= 4 : VARIER les types de patterns (géométrique, carrés, n×2+1, Fibonacci...). ÉVITER systématiquement "écarts qui doublent".
   - TITRE : Ne JAMAIS mettre la règle dans le titre (×3, +1, "double", "alternance", etc.). Si le titre révèle le pattern → difficulty max 3.0. Ex: "Le cycle caché" ✅ ; "Le cycle ×3 puis +1" ❌ (trop facile).

3. Pour PUZZLE :
   - Tu DOIS fournir des indices (hints) qui permettent de DÉDUIRE l'ordre
   - Chaque indice doit donner une information utile (ex: "Le rouge vient avant le bleu", "Le vert est en 3ème position")
   - Vérifie que correct_answer contient tous les éléments de pieces
   - Vérifie que l'ordre donné par correct_answer est DÉDUCTIBLE à partir des indices
   - L'explication doit montrer comment utiliser les indices pour trouver l'ordre
   - Pour difficulty >= 4 : minimum 6 pièces, indices indirects, combinaison de contraintes. Jamais 4 couleurs basiques.

4. Pour VISUAL avec formes et couleurs :
   - Si la réponse est une couleur (ex: "bleu", "rouge"), tu DOIS montrer cette couleur AVEC une autre forme dans les éléments visibles
   - Exemple : Si correct_answer = "bleu" et c'est pour un carré manquant, il DOIT y avoir un autre "carré bleu" visible dans shapes
   - L'utilisateur ne peut PAS deviner une couleur qu'il n'a jamais vue associée à une forme
   - La description doit expliquer la règle à trouver (ex: "Chaque forme a sa propre couleur")
   - Pour SYMÉTRIE (type "symmetry") : correct_answer = "forme couleur" (ex: "cercle rouge"). La position "?" DOIT avoir son miroir dans le layout ; correct_answer = l'élément qui occupe la position miroir (même shape + color).

5. Pour DEDUCTION (grille logique) :
   - Tu DOIS fournir des clues (indices) qui permettent de déduire UNE SEULE solution
   - Chaque entité de la première catégorie doit être associée à exactement une valeur de chaque autre catégorie
   - correct_answer DOIT utiliser le format "Entité1:Val1:Val2,Entité2:Val1:Val2,..."
   - Exemple : Si entities = {{"eleves": ["Emma", "Lucas"], "matieres": ["Maths", "Français"], "scores": [80, 90]}}
     Et la solution est Emma→Maths→90, Lucas→Français→80
     → correct_answer = "Emma:Maths:90,Lucas:Français:80"
   - L'ordre des associations (Emma avant Lucas) n'a pas d'importance
   - Vérifie que les indices permettent de trouver cette solution unique

6. Pour CODING (cryptographie) - VALIDATION STRICTE :
   - Tu DOIS fournir un "type" parmi : "caesar", "substitution", "binary", "symbols", "algorithm", "maze"
   - ERREUR FATALE si visual_data contient : "shapes", "arrangement", "cercle", "carré", "triangle", "couleur"
   - ERREUR FATALE si visual_data contient : "numbers", "target", "movement_options" (ce n'est pas de la crypto !)
   - Ces éléments appartiennent au type "visual", "pattern" ou "sequence", PAS à "coding" !
   - Pour "caesar" : fournis "encoded_message", correct_answer = mot décodé.
     * Avec shift explicite : shift (1-25). Exemple : encoded_message="FKDW", shift=3, correct_answer="CHAT"
     * Avec partial_key (défi à déduction) : NE PAS fournir shift ; ajoute "rule_type": "caesar" et partial_key (ex: {{"F": "A", "G": "B", "H": "C"}}) ; vérifie que le décalage déduit donne correct_answer après décodage.
   - Pour "substitution" : fournis "encoded_message" et soit "key" complète, soit "partial_key" si la règle est déductible (César, Atbash, clé-mot).
   - Pour "binary" : fournis "encoded_message" (groupes de 8 bits : "01001111 01010101 01001001"), correct_answer = "OUI"
   - Pour "symbols" : fournis "encoded_message" avec symboles (★●▲), "key" (table symbole→lettre)
   - Pour "algorithm" : fournis "steps" (instructions), "input" (nombre), correct_answer = résultat
   - Pour "maze" : fournis "maze" (grille de murs #), "start", "end", correct_answer = directions (BAS, DROITE...)
   - correct_answer est TOUJOURS du texte en clair (lettres/mots décodés, directions, ou un nombre pour algorithm)

7. Pour CHESS (échecs) :
   - Tu DOIS fournir "board" : tableau 2D de 8x8. Notation : K/k, Q/q, R/r, B/b, N/n, P/p. "" = vide.
   - board[0] = rangée 8 (haut), board[7] = rangée 1 (bas). "turn" : "white" ou "black".
   - "objective" : "mat_en_1", "mat_en_2", "mat_en_3", "meilleur_coup".
   - correct_answer : notation algébrique. Si plusieurs solutions valides (duals), sépare-les par " | " (ex: "Dg8+ Txg8 Cf7# | Bg8+ Txg8 Cf7#").
   - CRITIQUE : Vérifie que la position n'admet qu'UNE SEULE solution. Si tu découvres des duals, liste TOUTES les variantes dans correct_answer.
   - ERREUR : Ne JAMAIS utiliser la position de départ pour mat en X coups (impossible tactiquement).
   - La position doit être TACTIQUE : roi noir menacé, peu de pièces au centre, mat réalisable en X coups.
   - highlight_positions : UNIQUEMENT les cases avec une pièce (dame, roi, Tours clés...). Jamais de cases vides. Notation ["d5", "h8"].

8. Pour RIDDLE (énigmes) :
   - Les clues (dans visual_data) DOIVENT permettre de DÉDUIRE correct_answer de façon unique.
   - solution_explanation DOIT montrer le raisonnement étape par étape, cohérent avec correct_answer.
   - key_elements doit lister les notions clés (somme, double, symétrie, etc.) pour orienter le solveur.
   - Éviter les énigmes impossibles : chaque indice doit apporter une information exploitable.

9. Pour PROBABILITY (probabilités) :
   - correct_answer DOIT être cohérent avec visual_data : favorable / total.
   - Format : fraction "6/10" ou "3/5" (préférer favorable/total pour 6-8 ans). Le système accepte aussi "0.6", "60%".
   - Vérifie : somme des couleurs (rouge_bonbons + bleu_bonbons + ...) = total_bonbons.
   - La question dans visual_data doit correspondre à l'événement demandé (ex: "rouge" → rouge_bonbons).
   - solution_explanation DOIT montrer le calcul : favorable/total, cohérent avec correct_answer.

10. Pour GRAPH (graphes) :
   - Vérifie : tous les nœuds des edges DOIVENT exister dans nodes.
   - correct_answer : selon le type de question.
     * Liste de nœuds (points d'articulation, sommets, etc.) : format "A, B, C" (ordre alphabétique recommandé ; le système accepte tout ordre).
     * Chemin : format "A-B-C-D" ou "A, B, C, D" (ordre significatif).
     * Distance/nombre : un seul nombre.
   - solution_explanation DOIT expliquer la méthode (DFS, BFS, algorithme) et la cohérence avec le graphe.

11. Vérification finale :
   - La solution_explanation DOIT expliquer pourquoi correct_answer est correct
   - L'explication DOIT être cohérente avec le visual_data
   - L'explication NE DOIT PAS être contradictoire avec correct_answer

EXEMPLES VALIDES DE PATTERNS :

Exemple 1 - Pattern correct :
visual_data: {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "?", "X"]]}}
correct_answer: "O" ✅
solution_explanation: "En observant la colonne du milieu, on voit X-O-X. Le pattern se répète, donc ? = O."

Exemple 2 - Pattern correct :
visual_data: {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]]}}
correct_answer: "X" ✅
solution_explanation: "En observant la colonne de droite et la ligne du bas, le pattern X-O-X se répète. Donc ? = X."

Retourne uniquement le défi au format JSON valide avec ces champs:
{{
  "title": "Titre du défi mathélogique (accrocheur, adapté à {age_display})",
  "description": "Description claire du problème avec contexte engageant",
  "question": "Question spécifique et précise à résoudre",
  "correct_answer": "Réponse correcte (VALIDÉE pour correspondre au pattern)",
  "solution_explanation": "Explication détaillée adaptée à {age_display} (COHÉRENTE avec correct_answer)",
  "hints": ["Indice 1 (piste pédagogique)", "Indice 2 (piste)", "Indice 3 (piste)"],
  "visual_data": {{...}},
  "difficulty_rating": X.X // Note de 1.0 à 5.0 adaptée au groupe d'âge
}}

RÈGLES DE DIFFICULTÉ (difficulty_rating) :
- 6-8 ans : 1.0 à 2.0 (très facile)
- 9-11 ans : 2.0 à 3.0 (facile à moyen)
- 12-14 ans : 3.0 à 4.0 (moyen)
- 15-17 ans : 3.5 à 4.5 (moyen-difficile)
- adulte : 4.0 à 5.0 (difficile)

CALIBRATION STRICTE — Ne PAS surévaluer la difficulté :
- Si la règle est DANS LE TITRE (ex. "double cycle", "symétrie") → max 3.0. L'utilisateur sait déjà quoi chercher.
- Si c'est un principe connu (Sudoku, Latin square de base) sans piège → max 3.5.
- UNE SEULE case vide ("?") dans la grille → max 2.5-3.0 : on déduit par élimination sans chercher le pattern. Pas besoin de comprendre la logique globale.
- PUZZLE avec 4 pièces (ex. 4 couleurs) et indices directs ("X à gauche de Y") → max 3.0. Pour 4+ : minimum 6 pièces, indices indirects.
- Difficile (4+) = plusieurs "?" à remplir OU pattern non évident à découvrir OU piège. La règle doit être DÉCOUVERTE.
- Pas de piège, règle explicite, 1 seul manquant → difficulté BASSE.

Assure-toi que le visual_data est complet et permet une visualisation interactive.
IMPORTANT : Vérifie TOUJOURS la cohérence logique avant de retourner le JSON."""


def build_challenge_user_prompt(challenge_type: str, age_group: str, prompt: str) -> str:
    """Construit le prompt utilisateur pour la génération de défis."""
    params = AGE_GROUP_PARAMS.get(age_group, AGE_GROUP_PARAMS["9-11"])
    age_display = params["display"]
    age_target_phrase = (
        "pour des adultes"
        if age_group == "adulte"
        else "pour un public de tous âges"
        if age_group == "tous-ages"
        else f"pour des enfants/élèves de {age_display}"
    )

    user_prompt = f"""Crée un défi mathélogique de type "{challenge_type}" {age_target_phrase}.

CONTRAINTES OBLIGATOIRES :
- Type de défi : {challenge_type} (pas un autre type !)
- Groupe d'âge : {age_display} (adapter la complexité et le vocabulaire)
- Le visual_data DOIT correspondre au type {challenge_type}
- La difficulté doit être adaptée à {age_display}"""

    if prompt:
        user_prompt += f"""

DEMANDE PERSONNALISÉE DE L'UTILISATEUR (à respecter en priorité) :
{prompt}

Note : Respecte la demande ci-dessus tout en gardant le type "{challenge_type}" et le groupe d'âge {age_group}."""

    return user_prompt


def normalize_generated_challenge(
    challenge_data: Dict[str, Any],
    challenge_type: str,
    age_group: str,
) -> Dict[str, Any]:
    """
    Normalise les données générées avec ajustements de difficulté.
    """
    if age_group not in AGE_GROUP_PARAMS:
        logger.warning(f"Groupe d'âge '{age_group}' non trouvé dans le mapping, utilisation de '9-11' par défaut")

    final_age_group = age_group
    ai_difficulty = challenge_data.get("difficulty_rating")
    expected_difficulty = calculate_difficulty_for_age_group(final_age_group)

    if ai_difficulty and isinstance(ai_difficulty, (int, float)) and 1.0 <= ai_difficulty <= 5.0:
        if abs(ai_difficulty - expected_difficulty) > 1.5:
            logger.info(
                f"Difficulté IA ({ai_difficulty}) ajustée pour groupe d'âge {final_age_group} -> {expected_difficulty}"
            )
            final_difficulty = expected_difficulty
        else:
            final_difficulty = float(ai_difficulty)
    else:
        final_difficulty = expected_difficulty

    # Plancher adulte
    if final_age_group == "adulte" and final_difficulty < 4.0:
        logger.info(f"Difficulté adulte ({final_difficulty}) relevée au minimum 4.0")
        final_difficulty = 4.0

    # PATTERN : 1 seule case vide → plafond 3.0
    if challenge_type.lower() == "pattern":
        vd = challenge_data.get("visual_data", {})
        grid = vd.get("grid", []) if isinstance(vd, dict) else []
        question_count = sum(
            1
            for row in (grid if isinstance(grid, list) else [])
            for c in (row if isinstance(row, (list, tuple)) else [])
            if c == "?" or (isinstance(c, str) and "?" in str(c))
        )
        if question_count <= 1 and final_difficulty > 3.0:
            logger.info(
                f"PATTERN: 1 seule case vide → difficulté plafonnée à 3.0 (était {final_difficulty})"
            )
            final_difficulty = min(final_difficulty, 3.0)

    return {
        "challenge_type": challenge_type,
        "age_group": final_age_group,
        "title": challenge_data.get("title", f"Défi {challenge_type}"),
        "description": challenge_data.get("description", ""),
        "question": challenge_data.get("question", ""),
        "correct_answer": str(challenge_data.get("correct_answer", "")),
        "solution_explanation": challenge_data.get("solution_explanation", ""),
        "hints": challenge_data.get("hints", []),
        "visual_data": challenge_data.get("visual_data", {}),
        "difficulty_rating": final_difficulty,
        "estimated_time_minutes": 10,
        "tags": "ai,generated,mathélogique",
    }


async def generate_challenge_stream(
    challenge_type: str,
    age_group: str,
    prompt: str,
    user_id: Optional[int],
    locale: str = "fr",
) -> AsyncGenerator[str, None]:
    """
    Générateur async qui produit des événements SSE (f"data: {json.dumps(...)}\n\n").
    """
    start_time = datetime.now()
    generation_success = False
    validation_passed = True
    auto_corrected = False

    try:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            yield sse_error_message("Bibliothèque OpenAI non installée")
            return

        if not settings.OPENAI_API_KEY:
            yield sse_error_message("OpenAI API key non configurée")
            return

        ai_params = AIConfig.get_openai_params(challenge_type)
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=ai_params["timeout"],
        )

        system_prompt = build_challenge_system_prompt(challenge_type, age_group)
        user_prompt = build_challenge_user_prompt(challenge_type, age_group, prompt)

        if AIConfig.is_o1_model(ai_params["model"]):
            system_prompt += "\n\nCRITIQUE : Retourne UNIQUEMENT un objet JSON valide, sans texte ou markdown avant/après. Aucune explication hors du JSON."

        yield sse_status_message("Génération en cours...")

        @retry(
            stop=stop_after_attempt(AIConfig.MAX_RETRIES),
            wait=wait_exponential(
                multiplier=AIConfig.RETRY_BACKOFF_MULTIPLIER,
                min=AIConfig.RETRY_MIN_WAIT,
                max=AIConfig.RETRY_MAX_WAIT,
            ),
            retry=retry_if_exception_type((RateLimitError, APIError, APITimeoutError)),
            reraise=True,
        )
        async def create_stream_with_retry():
            use_o1 = AIConfig.is_o1_model(ai_params["model"])
            use_o3 = AIConfig.is_o3_model(ai_params["model"])
            api_kwargs = {
                "model": ai_params["model"],
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
            }
            if not use_o1:
                api_kwargs["response_format"] = {"type": "json_object"}

            if use_o1:
                api_kwargs["max_completion_tokens"] = ai_params["max_tokens"]
            elif use_o3:
                api_kwargs["max_completion_tokens"] = ai_params["max_tokens"]
                api_kwargs["reasoning_effort"] = ai_params.get("reasoning_effort", "medium")
            elif AIConfig.is_gpt5_model(ai_params["model"]):
                api_kwargs["max_completion_tokens"] = ai_params["max_tokens"]
                api_kwargs["reasoning_effort"] = ai_params.get("reasoning_effort", "medium")
                api_kwargs["verbosity"] = ai_params.get("verbosity", "low")
                if ai_params.get("reasoning_effort") == "none" and "temperature" in ai_params:
                    api_kwargs["temperature"] = ai_params["temperature"]
            else:
                api_kwargs["max_tokens"] = ai_params["max_tokens"]
                api_kwargs["temperature"] = ai_params.get("temperature", 0.5)

            logger.info(
                f"Appel API: model={ai_params['model']}, o1={use_o1}, o3={use_o3}, reasoning={ai_params.get('reasoning_effort', 'N/A')}"
            )
            return await client.chat.completions.create(**api_kwargs)

        try:
            stream = await create_stream_with_retry()
        except (RateLimitError, APIError, APITimeoutError) as api_error:
            logger.error(f"Erreur API OpenAI après {AIConfig.MAX_RETRIES} tentatives: {api_error}")
            yield sse_error_message(f"Erreur lors de la génération après plusieurs tentatives: {str(api_error)}")
            return
        except Exception as unexpected_error:
            logger.error(f"Erreur inattendue lors de la génération: {unexpected_error}")
            yield sse_error_message("Erreur inattendue lors de la génération")
            return

        full_response = ""
        prompt_tokens_estimate = 0
        completion_tokens_estimate = 0
        prompt_length = len(system_prompt) + len(user_prompt)
        prompt_tokens_estimate = prompt_length // 4

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                completion_tokens_estimate = len(full_response) // 4
            if hasattr(chunk, "usage") and chunk.usage:
                prompt_tokens_estimate = chunk.usage.prompt_tokens or prompt_tokens_estimate
                completion_tokens_estimate = chunk.usage.completion_tokens or completion_tokens_estimate

        # Fallback si réponse vide (o3)
        if not full_response.strip() and AIConfig.is_o3_model(ai_params["model"]):
            logger.warning("Réponse vide de o3, fallback vers modèle sans raisonnement...")
            fallback_model = AIConfig.ADVANCED_MODEL
            try:
                fallback_client = AsyncOpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=ai_params.get("timeout", 120),
                )
                fallback_resp = await fallback_client.chat.completions.create(
                    model=fallback_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=ai_params["max_tokens"],
                    temperature=0.4,
                )
                if fallback_resp.choices and fallback_resp.choices[0].message.content:
                    full_response = fallback_resp.choices[0].message.content
                    logger.info(f"Fallback {fallback_model}: {len(full_response)} caractères reçus")
            except Exception as fb_err:
                logger.error(f"Fallback échoué: {fb_err}")

        logger.info(f"Réponse reçue: {len(full_response)} caractères, ~{len(full_response)//4} tokens estimés")

        try:
            challenge_data = extract_json_from_text(full_response)
        except json.JSONDecodeError as json_error:
            logger.error(f"Erreur de parsing JSON: {json_error}")
            logger.debug(f"Réponse reçue: {full_response[:500]}")
            duration = (datetime.now() - start_time).total_seconds()
            generation_metrics.record_generation(
                challenge_type=challenge_type,
                success=False,
                validation_passed=False,
                duration_seconds=duration,
                error_type="json_decode_error",
            )
            yield sse_error_message("Erreur lors du parsing de la réponse JSON")
            return

        if not challenge_data.get("title") or not challenge_data.get("description"):
            logger.error(f"Données de challenge incomplètes: {challenge_data}")
            yield sse_error_message("Les données générées sont incomplètes (titre ou description manquant)")
            return

        challenge_data["challenge_type"] = challenge_type
        if challenge_type.lower() == "pattern":
            challenge_data = auto_correct_challenge(challenge_data)
        is_valid, validation_errors = validate_challenge_logic(challenge_data)

        if not is_valid:
            logger.warning(f"Challenge généré avec erreurs de validation: {validation_errors}")
            logger.info("Tentative de correction automatique...")
            corrected_challenge = auto_correct_challenge(challenge_data)
            is_valid_after_correction, remaining_errors = validate_challenge_logic(corrected_challenge)
            if is_valid_after_correction:
                logger.info("Correction automatique réussie")
                challenge_data = corrected_challenge
                auto_corrected = True
                validation_passed = True
            else:
                logger.error(f"Correction automatique impossible. Erreurs restantes: {remaining_errors}")
                validation_passed = False
                errors_str = ", ".join(remaining_errors[:2])
                yield f"data: {json.dumps({'type': 'warning', 'message': f'Avertissement: {errors_str}'})}\n\n"
        else:
            logger.debug("Challenge validé avec succès")
            validation_passed = True

        normalized_challenge = normalize_generated_challenge(challenge_data, challenge_type, age_group)

        if not normalized_challenge.get("title") or not normalized_challenge.get("description"):
            logger.error(f"Challenge normalisé invalide: {normalized_challenge}")
            yield sse_error_message("Erreur lors de la normalisation des données")
            return

        try:
            async with db_session() as db:
                created_challenge = challenge_service.create_challenge(
                    db=db,
                    title=normalized_challenge["title"],
                    description=normalized_challenge["description"],
                    challenge_type=normalized_challenge["challenge_type"],
                    age_group=normalized_challenge["age_group"],
                    question=normalized_challenge.get("question"),
                    correct_answer=normalized_challenge["correct_answer"],
                    solution_explanation=normalized_challenge["solution_explanation"],
                    hints=normalized_challenge.get("hints", []),
                    visual_data=normalized_challenge.get("visual_data", {}),
                    difficulty_rating=normalized_challenge.get("difficulty_rating", 3.0),
                    estimated_time_minutes=normalized_challenge.get("estimated_time_minutes", 10),
                    tags=normalized_challenge.get("tags", "ai,generated"),
                    creator_id=user_id,
                    generation_parameters={
                        "source": "ai",
                        "challenge_type": normalized_challenge["challenge_type"],
                        "age_group": normalized_challenge["age_group"],
                        "model": ai_params.get("model", "unknown"),
                    },
                )

                if created_challenge and hasattr(created_challenge, "title") and created_challenge.title:
                    usage_stats = token_tracker.track_usage(
                        challenge_type=challenge_type,
                        prompt_tokens=prompt_tokens_estimate,
                        completion_tokens=completion_tokens_estimate,
                        model=ai_params["model"],
                    )
                    logger.debug(f"Token usage tracked: {usage_stats}")

                    generation_success = True
                    duration = (datetime.now() - start_time).total_seconds()
                    generation_metrics.record_generation(
                        challenge_type=challenge_type,
                        success=True,
                        validation_passed=validation_passed,
                        auto_corrected=auto_corrected,
                        duration_seconds=duration,
                    )

                    challenge_dict = {
                        "id": created_challenge.id,
                        "title": created_challenge.title,
                        "description": created_challenge.description,
                        "challenge_type": (
                            str(created_challenge.challenge_type)
                            if hasattr(created_challenge.challenge_type, "value")
                            else created_challenge.challenge_type
                        ),
                        "age_group": normalize_age_group_for_frontend(created_challenge.age_group),
                        "question": created_challenge.question,
                        "correct_answer": created_challenge.correct_answer,
                        "solution_explanation": created_challenge.solution_explanation,
                        "hints": created_challenge.hints or [],
                        "visual_data": created_challenge.visual_data or {},
                        "difficulty_rating": created_challenge.difficulty_rating,
                        "estimated_time_minutes": created_challenge.estimated_time_minutes,
                        "tags": created_challenge.tags,
                        "is_active": created_challenge.is_active,
                        "created_at": (
                            created_challenge.created_at.isoformat()
                            if created_challenge.created_at
                            else None
                        ),
                    }
                    yield f"data: {json.dumps({'type': 'challenge', 'challenge': challenge_dict})}\n\n"
                else:
                    logger.error(f"Challenge créé mais invalide: {created_challenge}")
                    yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
        except Exception as db_error:
            logger.error(f"Erreur lors de la sauvegarde du challenge: {db_error}")
            logger.debug(traceback.format_exc())
            if normalized_challenge.get("title"):
                yield f"data: {json.dumps({'type': 'challenge', 'challenge': normalized_challenge, 'warning': 'Non sauvegardé en base'})}\n\n"
            else:
                yield sse_error_message("Erreur lors de la sauvegarde et challenge invalide")

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as gen_error:
        logger.error(f"Erreur lors de la génération: {gen_error}")
        logger.debug(traceback.format_exc())
        duration = (datetime.now() - start_time).total_seconds()
        generation_metrics.record_generation(
            challenge_type=challenge_type,
            success=False,
            validation_passed=False,
            duration_seconds=duration,
            error_type=type(gen_error).__name__,
        )
        yield sse_error_message(str(gen_error))
