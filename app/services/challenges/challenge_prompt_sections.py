"""
Fragments de texte pour la composition du prompt système des défis IA (lot IA4).

Séparation volontaire : ce module ne contient que du contenu statique ;
l'assemblage par type vit dans ``challenge_prompt_composition``.
"""

from __future__ import annotations

# --- Toujours inclus (règles transverses pédagogiques / sécurité du contrat) ---

TEXT_ROLE_HEADER = """Tu es un assistant pédagogique spécialisé dans la création de défis mathélogiques (logique mathématique)."""

TEXT_TYPE_LOCK_TEMPLATE = (
    'RÈGLE ABSOLUE : Tu DOIS créer un défi de type "{challenge_type}" uniquement. '
    "Ne crée JAMAIS un défi d'un autre type."
)

TEXT_TYPES_COMPACT = """Types valides (référence) : sequence, pattern, visual, puzzle, graph, riddle, deduction, probability, coding, chess.
Tu ne génères que le type demandé dans ce message (pas d'autre type, pas de mélange)."""

TEXT_MATHLOG_CONTEXT = """CONTEXTE MATHÉLOGIQUE :
Inspire-toi des exercices de mathélogique qui combinent raisonnement logique, éléments visuels (grilles, formes), patterns, déduction et problèmes résolubles avec une méthode claire."""

TEXT_HINTS_RULES = """RÈGLE IMPORTANTE POUR LES INDICES :
Les indices (hints) doivent être des PISTES pédagogiques qui guident l'élève vers la solution, MAIS NE DOIVENT JAMAIS donner la réponse directement.
- ✅ BON : "Regarde la différence entre chaque élément"
- ✅ BON : "Quel pattern se répète ?"
- ✅ BON : "Pense à l'ordre logique des étapes"
- ❌ MAUVAIS : "La réponse est X"
- ❌ MAUVAIS : "Il faut faire Y puis Z"
Les indices doivent encourager la réflexion sans révéler la solution."""

TEXT_LATEX_RULES = """FORMATAGE MATHÉMATIQUE (OBLIGATOIRE) :
Toutes les expressions mathématiques DOIVENT être écrites en LaTeX dans les champs `description`, `question` et `solution_explanation`.
- Formule inline : $a + b = c$ (délimiteurs $ ... $)
- Formule bloc centrée : $$\\frac{{a}}{{b}} = c$$ (pour les étapes clés de l'explication)
- Opérateurs : $\\times$ (×), $\\div$ (÷), $\\frac{{a}}{{b}}$ (fraction), $a^2$ (exposant), $\\sqrt{{x}}$ (racine)
- CRITIQUE LaTeX : Après une fraction $\\frac{{a}}{{b}}$, TOUJOURS un espace avant le mot/nombre suivant.
- Le texte narratif (contexte, titre, thème) reste en prose normale, seules les maths sont en LaTeX.
- Ne pas utiliser LaTeX dans `title`, `correct_answer`, ni dans `visual_data`."""

TEXT_DIFFICULTY_RULES = """RÈGLES DE DIFFICULTÉ (difficulty_rating) :
- 6-8 ans : 1.0 à 2.0 (très facile)
- 9-11 ans : 2.0 à 3.0 (facile à moyen)
- 12-14 ans : 3.0 à 4.0 (moyen)
- 15-17 ans : 3.5 à 4.5 (moyen-difficile)
- adulte : 4.0 à 5.0 (difficile)

CALIBRATION STRICTE — Ne PAS surévaluer la difficulté :
- Si la règle est DANS LE TITRE → max 3.0.
- Si principe connu (Sudoku, Latin square de base) sans piège → max 3.5.
- UNE SEULE case vide ("?") dans la grille → max 2.5-3.0.
- PUZZLE avec 4 pièces et indices directs → max 3.0. Pour 4+ : minimum 6 pièces, indices indirects.
- Difficile (4+) = plusieurs "?" OU pattern non évident OU piège. La règle doit être DÉCOUVERTE.
- Pas de piège, règle explicite, 1 seul manquant → difficulté BASSE.
- Ne PAS sous-évaluer : plusieurs inconnues, 6+ pièces avec contraintes, message codé long, graphe dense ou probabilité multi-événements doivent rester au moins moyen-difficiles (3.5+), sauf si la règle est explicitement donnée."""

TEXT_JSON_CONTRACT_TEMPLATE = """Retourne uniquement le défi au format JSON valide avec ces champs:
{{
  "title": "Titre du défi mathélogique (accrocheur, adapté à {age_display})",
  "description": "Description claire du problème avec contexte engageant",
  "question": "Question spécifique et précise à résoudre",
  "correct_answer": "Réponse correcte (VALIDÉE pour correspondre au pattern)",
  "solution_explanation": "Explication détaillée adaptée à {age_display} (COHÉRENTE avec correct_answer)",
  "hints": ["Indice 1 (piste pédagogique)", "Indice 2 (piste)", "Indice 3 (piste)"],
  "visual_data": {{...}},
  "difficulty_rating": X.X,
  "difficulty_axes": {{"reasoning_steps": 3, "rule_visibility": "hidden|partial|explicit", "constraint_count_hint": 5}},
  "choices": ["distracteur plausible A", "distracteur plausible B", "bonne réponse", "..."]
}}

CHOIX / QCM (politique par type — IA9) :
- ``deduction``, ``chess`` : **ne jamais** inclure ``choices``.
- ``visual``, ``puzzle`` : ``choices`` **uniquement** si ``difficulty_rating`` < 2.0 (défis très faciles) ; sinon omettre ``choices`` et utiliser l'interaction (symétrie, ordre des pièces).
- ``sequence`` : QCM possible pour les défis simples à moyens ; pour ``difficulty_rating >= 4.0`` omettre ``choices`` et laisser une réponse libre.
- ``pattern``, ``graph``, ``probability``, ``coding`` : QCM possible si vrai mini-QCM (sinon omettre ``choices``).
- ``probability`` : si ``choices`` est présent, aucune option ne doit être mathématiquement équivalente à une autre (ex. ``10/27`` et ``50/135`` interdits dans le même QCM).
- ``riddle`` : QCM possible seulement pour les énigmes simples à moyennes ; pour ``difficulty_rating >= 4.0`` omettre ``choices`` et garder une réponse libre.
- Si ``choices`` est présent : minimum 3 options **distinctes** ; ``correct_answer`` = l'une d'elles exactement ; distracteurs plausibles, longueurs comparables.

DIFFICULTÉ / AXES (optionnel mais recommandé) :
- ``difficulty_axes`` doit être **cohérent** avec ``difficulty_rating`` (ex. rule_visibility \"hidden\" si la règle n'est pas dans le titre ; reasoning_steps plus élevé si plusieurs étapes).

Assure-toi que le visual_data est complet et permet une visualisation interactive.
IMPORTANT : Vérifie TOUJOURS la cohérence logique avant de retourner le JSON."""

# --- Règle adulte / visual (conditionnelle) ---

TEXT_VISUAL_ADULT_RULE = """
RÈGLE COMPLEXITÉ ADULTE pour VISUAL (OBLIGATOIRE) :
Pour le groupe adulte, les défis visuels/spatiaux DOIVENT être plus complexes :
- Au moins 5-6 formes différentes (cercle, carré, triangle, losange, étoile, hexagone)
- 8 à 10 positions au lieu de 6 (plus de cellules à déduire)
- OU plusieurs "?" (2-3 cases vides à remplir) dans une grille 4x4
- OU combinaison symétrie + règle supplémentaire (ex: couleur suit un pattern)
- Les grilles de symétrie doivent avoir plus de 6 éléments de chaque côté
"""

# --- VISUAL_DATA par type (injecté seul pour le type courant) ---

TEXT_VISUAL_DATA_SEQUENCE = """VISUAL_DATA OBLIGATOIRE (type sequence) :
- Exemple de forme : {{"sequence": [2, 4, 6, 8], "pattern": "n+2"}}
- RÈGLE DIFFICULTÉ SEQUENCE : Pour difficulty_rating >= 4, NE PAS inclure "pattern" dans visual_data (le pattern suggère trop la solution).
- Pour difficulty_rating >= 4, construire une vraie séquence difficile :
  - au moins 7 éléments visibles OU plusieurs inconnues à compléter ;
  - pas de simple progression arithmétique ou géométrique directe ;
  - préférer une règle composite, alternée, quadratique discrète, ou une transformation en deux étapes.
- VARIATION OBLIGATOIRE pour défis difficiles (adulte, difficulty >= 4) :
  - ÉVITER le pattern surutilisé "écarts qui doublent" (+3, +6, +12, +24).
  - Préférer : géométrique (×3, ×4), carrés, n×2+1, différences en progression arithmétique, alternance +3/×2, Fibonacci-like, etc."""

TEXT_VISUAL_DATA_PATTERN = """VISUAL_DATA OBLIGATOIRE (type pattern) :
- Exemple : {{"grid": [["X", "O", "X"], ["O", "X", "O"], ["X", "O", "?"]], "size": 3}}
- Pour 9-11 ans : formes (cercle, triangle, carré) au lieu de X/O si pertinent. Patterns : damier, Latin square, glissement cyclique, alternance.
- Plusieurs "?" : correct_answer DOIT lister TOUS les symboles dans l'ordre (ligne par ligne). Format: "O, O, X, O".
- DESCRIPTION / QUESTION : rester sobres et orientées tâche. Donner l'objectif, la taille de la grille et le format de réponse, mais NE PAS dévoiler directement la mécanique exacte du motif si la difficulté visée est moyenne ou élevée.
- À éviter dans `description` / `question` si tu veux garder la règle à découvrir : "carré latin", "décalage cyclique", "symétrie horizontale", "chaque ligne est la précédente décalée", "on ajoute +1 à chaque pas", ou toute formulation qui donne la transformation complète.
- Réserve l'explication détaillée de la règle à `solution_explanation` et garde `hints` comme simples pistes graduelles."""

TEXT_VISUAL_DATA_PUZZLE = """VISUAL_DATA OBLIGATOIRE (type puzzle) :
- {{"pieces": [...], "hints": ["...", "..."], "description": "..."}}
- correct_answer : ordre des pièces de gauche à droite, séparées par des virgules.
- IMPORTANT : indices suffisants pour déduire l'ordre.
- INTERDIT si pièces numériques : correct_answer ne doit pas être simplement le tri croissant ou décroissant des nombres.
- Si difficulty_rating >= 4 : minimum 6-7 pièces, indices INDIRECTS, combinaison de contraintes (pas seulement 4 couleurs)."""

TEXT_VISUAL_DATA_GRAPH = """VISUAL_DATA OBLIGATOIRE (type graph) :
- {{"nodes": ["A", "B", ...], "edges": [["A", "B"], ...]}}
- Tous les noms dans edges DOIVENT exister dans nodes.
- Si la question demande un arbre couvrant minimal : chaque arête DOIT inclure un poids numérique (ex. ["A", "B", 4]) et visual_data doit inclure "objective": "minimum_spanning_tree".
- Pour un arbre couvrant minimal, correct_answer = somme minimale recalculée des arêtes choisies, pas une arête isolée ni une estimation.
- Si la question demande un chemin/route minimal(e) : chaque arête DOIT inclure un poids numérique et visual_data doit inclure "objective": "shortest_path", "source": "A", "target": "G".
- Pour un chemin minimal, correct_answer = coût total minimal recalculé (Dijkstra si poids positifs), pas la liste des nœuds seule.
- Optionnel : "positions" pour placement explicite (x,y)."""

TEXT_VISUAL_DATA_DEDUCTION = """VISUAL_DATA OBLIGATOIRE (type deduction) :
- {{"type": "logic_grid", "entities": {{"personnes": [...], "metiers": [...], "villes": [...]}}, "clues": [...], "description": "..."}}
- La première catégorie dans entities = celle que l'utilisateur associe aux autres.
- correct_answer : "Alice:Médecin:Paris,Bob:Avocat:Lyon,..." (virgules entre associations, ":" entre champs).
- Les clues doivent mener à une solution unique.
- Recommandé pour fiabiliser la validation : ajoute aussi `constraints`, liste machine-readable alignée avec les clues.
- Types de contraintes acceptés : entity_value, entity_not_value, same_row, entity_before_entity, entity_after_entity, entity_immediately_before_entity, value_before_value, entity_not_adjacent_value.
- Format contrainte : {{"type": "entity_value", "left": {{"category": "Personnes", "value": "Alice"}}, "right": {{"category": "Jours", "value": "Mardi"}}}}.
- N'inclus `constraints` que si chaque contrainte correspond explicitement à un indice textuel."""

TEXT_VISUAL_DATA_VISUAL = """VISUAL_DATA OBLIGATOIRE (type visual) :
- Symétrie/rotation : {{"type": "symmetry", "symmetry_line": "vertical", "layout": [...], "shapes": [...], "arrangement": "horizontal", "description": "..."}} — pour un carré (■) utiliser "carré" pas "rectangle".
- Formes colorées : {{"shapes": ["cercle rouge", "triangle vert", "carré ?"], "arrangement": "ligne"}} ou ascii si besoin.

IMPORTANT pour VISUAL :
- Si associations forme-couleur : montrer AU MOINS UN EXEMPLE VISIBLE de chaque association avant la question.
- L'utilisateur doit DÉDUIRE depuis l'exposition, pas deviner.
- Symétrie : utiliser la structure "symmetry" avec layout et symmetry_line.
- TERMINOLOGIE : "carré" pour 4 côtés égaux ; "rectangle" = oblong.
- Ne génère JAMAIS de JSON malformé (clés/valeurs invalides)."""

TEXT_VISUAL_DATA_CODING = """VISUAL_DATA OBLIGATOIRE (type coding = cryptographie / décodage) :
- César : {{"type": "caesar", "encoded_message": "...", "shift": N, ...}}
- Substitution : clé complète (26 lettres) OU partial_key seulement si règle DÉDUCTIBLE + "rule_type": "caesar"|"atbash"|"keyword".
- Pour substitution avec partial_key : utiliser un OBJET JSON (ex. {{"keyword_length": 6, "theme_clue": "astronome", "mapping_known": {{"G": "A", "A": "B"}}}}), pas une chaîne masquée comme "GALIEO????".
- Binaire, symboles, algorithme simple, labyrinthe : voir formats standards du projet.
- ⛔ INTERDIT pour coding : "sequence" de nombres, "pattern" grille décoratif, shapes/couleurs seuls, numbers/target/movement_options sans message à décoder.
- correct_answer = mot ou phrase décodée (texte clair) ou directions pour maze.
- Rappel : CODING = décoder un message secret (lettres/symboles), pas naviguer dans une liste de nombres."""

TEXT_VISUAL_DATA_RIDDLE = """VISUAL_DATA OBLIGATOIRE (type riddle) :
- {{"clues": [...], "context": "...", "riddle": "...", "description": "...", "key_elements": [...]}}
- Pour difficulty_rating >= 4.0 : titre neutre, pas de QCM, au moins 5 indices ou contraintes, et pas de formulation qui donne directement la mécanique ("suite décroissante", "chiffre des centaines", "nombre de lettres", "produit des chiffres") si ces éléments suffisent presque seuls à trouver la réponse.
- Une énigme difficile doit demander une combinaison de contraintes indirectes, pas seulement reconnaître la bonne réponse parmi 4 choix."""

TEXT_VISUAL_DATA_PROBABILITY = """VISUAL_DATA OBLIGATOIRE (type probability) :
- Exemple simple : {{"rouge_bonbons": 10, "bleu_bonbons": 5, "total_bonbons": 15, "question": "...", "description": "..."}} (adapter le contexte : billes, cartes, dés).
- Urnes : {{"urns": {{"A": {{"red": 5, "blue": 5}}, "B": {{"red": 8, "blue": 2}}}}, "total_per_urn": 10, "urn_selection": "equiprobable", "draws_without_replacement": 2, "question": "..."}}
- Urnes pondérées : utilise le même format `urns`, avec `selection_probability` dans chaque urne (ex. {{"urns": {{"A": {{"red": 40, "blue": 60, "selection_probability": 0.7}}, "B": {{"red": 30, "blue": 20, "selection_probability": 0.3}}}}, "draws_without_replacement": 2, "event": "couleurs différentes"}}). Évite `box_A` / `box_B` si possible.
- Tous les textes narratifs dans `visual_data.question` et `visual_data.description` doivent rester en FRANÇAIS. Les clés techniques peuvent rester simples (`red`, `blue`, `green`), mais pas de phrase anglaise visible.
- Pour ``difficulty_rating >= 4.0`` : un tirage direct dans un seul sac/une urne, même avec 3 couleurs et sans remise, ne suffit pas. Ajouter au moins une vraie couche de complexité : 3+ tirages, observation partielle, question inverse/conditionnelle (Bayes, probabilité a posteriori), urne choisie aléatoirement, ou plusieurs événements combinés.
- Si tu fournis ``choices`` : les fractions doivent être distinctes mathématiquement ; ne mets jamais à la fois une fraction simplifiée et sa forme non simplifiée. Pour un défi 4+, les distracteurs doivent correspondre à des erreurs de raisonnement plausibles, pas à des fractions arbitraires."""

TEXT_VISUAL_DATA_CHESS = """VISUAL_DATA OBLIGATOIRE (type chess) :
- INTERDIT : position de départ complète pour mat en X coups.
- Mat en X coups : position TACTIQUE (peu de pièces, roi noir menacé).
- Notation : K/k Roi, Q/q Dame, R/r Tour, B/b Fou, N/n Cavalier, P/p Pion. MAJ = blanc, min = noir. "" = vide.
- board[0] = rangée 8, board[7] = rangée 1 ; board[row][0] = colonne a.
- "turn" : white/black ; "objective" : mat_en_1, mat_en_2, mat_en_3, meilleur_coup.
- correct_answer : notation algébrique ; duals séparés par " | ".
- highlight_positions : uniquement des cases avec une pièce."""

TEXT_VISUAL_DATA_FALLBACK = """VISUAL_DATA OBLIGATOIRE :
Construis un objet visual_data strictement adapté au type demandé, complet pour le frontend, sans mélanger les conventions d'un autre type."""

# --- Validations ciblées par type (évite d'envoyer les 10 blocs à chaque appel) ---

TEXT_VAL_INTRO = "VALIDATION LOGIQUE (obligatoire avant de retourner le JSON) :"

TEXT_VAL_PATTERN = """1. PATTERN (grille) :
   - Déduis correct_answer depuis la grille (Latin square, damier, symétrie, alternance).
   - solution_explanation COHÉRENTE avec correct_answer (pas de contradiction).
   - Si ``difficulty_rating >= 3.5`` ou ``rule_visibility`` vaut ``hidden`` / ``partial`` : ne révèle pas la règle exacte dans `description` ni dans `question`.
   - Pour ces cas moyens / difficiles, le titre et l'énoncé peuvent annoncer une grille, un motif, une progression ou un ordre à retrouver, mais pas nommer explicitement la mécanique ("carré latin", "décalage cyclique", "chaque ligne est décalée d'une case", etc.).
   - Exemple : grille X-O-X / O-X-O / X-O-"?" → "?" = X si colonne droite X-O-X."""

TEXT_VAL_SEQUENCE = """2. SEQUENCE :
   - Calcule différences entre termes consécutifs ; déduis le suivant.
   - Recalcule mentalement : correct_answer et solution_explanation alignés.
   - difficulty >= 4 : varier les familles de règles ; éviter systématiquement "écarts qui doublent".
   - difficulty >= 4 : pas de QCM, pas de ``pattern`` explicite, pas de suite courte avec un seul ``?``.
   - difficulty >= 4 : éviter les suites purement arithmétiques ou géométriques à lecture directe.
   - TITRE : ne pas révéler la règle (×3, +1, etc.) si tu veux viser une difficulté élevée."""

TEXT_VAL_PUZZLE = """3. PUZZLE :
   - Indices indispensables pour déduire l'ordre ; correct_answer contient toutes les pièces.
   - Si les pièces sont numériques, vérifie que l'ordre correct n'est PAS le simple ordre croissant/décroissant.
   - difficulty >= 4 : 6+ pièces, indices indirects, contraintes combinées."""

TEXT_VAL_VISUAL = """4. VISUAL (formes/couleurs, symétrie) :
   - Symétrie : ``type`` = \"symmetry\", ``symmetry_line`` = vertical|horizontal, ``layout`` avec ``side`` left/right.
   - Si la réponse est une couleur, montrer cette couleur sur une autre forme dans les éléments visibles.
   - correct_answer cohérent avec le miroir / la case manquante."""

TEXT_VAL_DEDUCTION = """5. DEDUCTION :
   - visual_data.type = "logic_grid" ; entities : au moins 2 catégories (listes) ; clues : au moins 2 indices.
   - correct_answer : une association par entité de la **première** catégorie, format "A:x:y,B:x:y,..." (\":\" entre champs).
   - Chaque valeur doit appartenir à la liste de sa catégorie.
   - Avant de retourner le JSON, vérifie qu'il n'existe qu'une seule solution compatible avec tous les indices ; si plusieurs solutions restent possibles, ajoute un indice discriminant.
   - Si `constraints` est fourni, il doit refléter les clues et conduire à la même unique solution que correct_answer."""

TEXT_VAL_CODING = """6. CODING :
   - "type" parmi caesar, substitution, binary, symbols, algorithm, maze.
   - Pas de shapes/couleurs seuls ni numbers/target/movement_options hors maze/crypto valide.
   - correct_answer = texte décodé ou résultat attendu selon le sous-type."""

TEXT_VAL_CHESS = """7. CHESS :
   - board 8x8 cohérent ; pas de mat en X depuis la position initiale complète.
   - Vérifier unicité ou lister les duals dans correct_answer.
   - highlight_positions : cases occupées uniquement."""

TEXT_VAL_RIDDLE = """8. RIDDLE :
   - clues → réponse unique ; solution_explanation étape par étape ; key_elements utiles.
   - difficulty >= 4 : pas de QCM, pas de règle révélée dans le titre, et pas d'indices numériques tous directs (position des chiffres + ordre + produit/somme/divisibilité) qui rendent la réponse quasi immédiate."""

TEXT_VAL_PROBABILITY = """9. PROBABILITY :
   - correct_answer cohérent avec favorable/total ; fractions ou % acceptés selon consignes.
   - Somme des sous-populations = total.
   - visual_data.question et visual_data.description doivent rester dans la même langue que l'énoncé (français ici), sans phrase anglaise visible.
   - Si choices est présent : correct_answer doit être une option exacte et aucune autre option ne doit être équivalente mathématiquement.
   - difficulty >= 4 : éviter les problèmes directs de tirage en 1-2 étapes ; utiliser conditionnel/inverse/Bayes, 3+ tirages, urne aléatoire ou omettre le QCM."""

TEXT_VAL_GRAPH = """10. GRAPH :
   - edges référencent uniquement des nodes existants ; explication alignée avec la question (chemin, distance, liste, etc.).
   - Arbre couvrant minimal : recalcule Kruskal/Prim, vérifie que correct_answer est bien la somme minimale.
   - Chemin minimal : recalcule Dijkstra/plus court chemin, vérifie que correct_answer est bien le coût minimal."""

TEXT_VAL_FINAL = """11. FINAL :
   - solution_explanation explique pourquoi correct_answer est correct, sans contradiction avec visual_data."""

TEXT_PATTERN_EXAMPLES = """EXEMPLES VALIDES DE PATTERNS (rappel) :
- Grille [["X","O","X"],["O","X","O"],["X","?","X"]] → correct_answer "O" si colonne milieu X-O-X.
- Grille [["X","O","X"],["O","X","O"],["X","O","?"]] → correct_answer "X" si colonne droite / ligne bas X-O-X."""

# Maps utilisées par challenge_prompt_composition
VISUAL_DATA_SECTION_BY_TYPE: dict[str, str] = {
    "sequence": TEXT_VISUAL_DATA_SEQUENCE,
    "pattern": TEXT_VISUAL_DATA_PATTERN,
    "puzzle": TEXT_VISUAL_DATA_PUZZLE,
    "graph": TEXT_VISUAL_DATA_GRAPH,
    "deduction": TEXT_VISUAL_DATA_DEDUCTION,
    "visual": TEXT_VISUAL_DATA_VISUAL,
    "coding": TEXT_VISUAL_DATA_CODING,
    "riddle": TEXT_VISUAL_DATA_RIDDLE,
    "probability": TEXT_VISUAL_DATA_PROBABILITY,
    "chess": TEXT_VISUAL_DATA_CHESS,
}

VALIDATION_SECTION_BY_TYPE: dict[str, str] = {
    "pattern": TEXT_VAL_PATTERN,
    "sequence": TEXT_VAL_SEQUENCE,
    "puzzle": TEXT_VAL_PUZZLE,
    "visual": TEXT_VAL_VISUAL,
    "deduction": TEXT_VAL_DEDUCTION,
    "coding": TEXT_VAL_CODING,
    "chess": TEXT_VAL_CHESS,
    "riddle": TEXT_VAL_RIDDLE,
    "probability": TEXT_VAL_PROBABILITY,
    "graph": TEXT_VAL_GRAPH,
}
