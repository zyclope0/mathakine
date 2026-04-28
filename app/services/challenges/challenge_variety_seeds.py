# app/services/challenges/challenge_variety_seeds.py
"""
Bibliothèque de seeds de variété pour la génération IA des défis (lot Qualité).

Chaque seed injecte deux suggestions dans le prompt utilisateur :
- narrative_context : domaine situationnel concret (vide pour les types purement formels)
- resolution_mechanism : famille de mécanisme cognitif propre au type

Le seed est une suggestion faible — type, âge et contrat visual_data restent absolus.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class VarietySeed:
    narrative_context: str  # domaine situationnel (vide si type purement formel)
    resolution_mechanism: str  # famille de mécanisme cognitif
    cognitive_skill: str = (
        ""  # not yet active — réservé : déduction, inhibition, séquençage…
    )
    min_level: str = (
        ""  # not yet active — réservé : beginner, intermediate, advanced, adult
    )


# Types dont le contexte narratif n'apporte rien (mécanique auto-référentielle ou purement spatiale).
_TYPES_IGNORE_NARRATIVE: frozenset[str] = frozenset({"chess", "visual", "pattern"})

# Mécanismes riddle séparés par niveau cible (P1-01).
_RIDDLE_MECHANISMS_ALL_AGES: list[str] = [
    "contraintes numériques croisées (âge, date, valeur)",
    "raisonnement par l'absurde (éliminer l'impossible)",
]
_RIDDLE_MECHANISMS_ADVANCED: list[str] = [  # groupes 12-14, 15-17, adulte uniquement
    "auto-référence (la réponse est cachée dans l'énoncé)",
    "double sens à démêler",
    "métaphore à interpréter puis résoudre",
]
_RIDDLE_ADVANCED_AGE_GROUPS: frozenset[str] = frozenset({"12-14", "15-17", "adulte"})

NARRATIVE_CONTEXTS: list[str] = [
    "une bibliothèque où les livres sont classés par code secret",
    "un atelier de menuiserie avec des planches de longueurs différentes",
    "une cuisine de restaurant avec des recettes et des contraintes d'ingrédients",
    "un réseau de pistes cyclables entre quartiers",
    "un entrepôt logistique avec des colis à acheminer",
    "une serre botanique avec des espèces et des conditions de culture",
    "un studio de musique avec des partitions et des rythmes",
    "un chantier de construction avec des matériaux et des plans",
    "une compétition sportive avec des résultats à analyser",
    "un atelier de cartographie avec des distances et des routes",
    "une salle des codes avec des messages à déchiffrer",
    "un club d'astronomie avec des trajectoires et des distances",
    "un marché alimentaire avec des prix, poids et quantités",
    "un atelier de robots avec des programmes à corriger",
    "un studio d'animation avec des séquences d'images",
    "une école d'architecture avec des plans et contraintes spatiales",
    "un réseau ferroviaire avec des horaires et correspondances",
    "un laboratoire avec des expériences à interpréter",
]

RESOLUTION_MECHANISMS_BY_TYPE: dict[str, list[str]] = {
    "coding": [
        "décalage de lettres (César, décalage non fourni)",
        "substitution alphabétique par mot-clé à déduire",
        "inversion partielle ou totale du message",
        "lecture en grille (transposition de colonnes)",
        "coordonnées dans un tableau comme index de lettres",
        "table de symboles personnalisés à reconstituer",
        "indices croisés entre deux messages partiels",
        "erreur à détecter dans un code presque correct",
        "code à compléter (début fourni, fin à retrouver)",
    ],
    "sequence": [
        "progression arithmétique à différences variables",
        "suite géométrique (×r, r non entier possible)",
        "suite récursive type Fibonacci ou variante",
        "alternance de deux sous-suites entrelacées",
        "suite quadratique (différences secondes constantes)",
        "suite de carrés ou cubes perturbée",
        "règle composite alternée (×2 puis +3)",
        "terme manquant au milieu de la suite (pas à la fin)",
        "plusieurs inconnues à retrouver simultanément",
    ],
    "pattern": [
        "Latin square (chaque symbole une fois par ligne et colonne)",
        "rotation cyclique (chaque ligne = précédente décalée)",
        "symétrie axiale à compléter",
        "règle composite (position ET couleur combinées)",
        "erreur à identifier dans une grille presque correcte",
        "progression de formes avec contrainte croisée",
    ],
    "deduction": [
        "bijection simple (2 catégories, déduction directe)",
        "bijection triple (3 catégories, élimination progressive)",
        "contraintes d'ordre temporel (avant/après uniquement)",
        "contraintes d'adjacence ou de voisinage",
        "indices négatifs seulement (aucun positif direct)",
        "mix positif/négatif avec un piège de symétrie",
    ],
    "probability": [
        "tirage sans remise en 1 étape",
        "double tirage indépendant (avec remise)",
        "probabilité conditionnelle (Bayes simplifié)",
        "urne choisie aléatoirement, tirage dedans",
        "événement complémentaire (P(pas A))",
        "problème inverse : trouver la composition, pas la proba",
    ],
    "graph": [
        "chemin le plus court avec poids (Dijkstra)",
        "arbre couvrant minimal (Kruskal/Prim)",
        "coloration minimale (nombre de couleurs)",
        "circuit : passer par chaque arête exactement une fois",
        "composantes connexes (graphe fragmenté)",
        "chemin hamiltonien (passer par chaque nœud une fois)",
    ],
    "chess": [
        "mat en 1 coup (tactique simple)",
        "mat en 2 coups avec ligne forcée",
        "fourchette (attaque simultanée deux pièces)",
        "clouage (pièce clouée contre le roi)",
        "promotion de pion avec conversion immédiate",
        "meilleur coup défensif (éviter le mat)",
    ],
    "visual": [
        "symétrie axiale (compléter le miroir)",
        "rotation (deviner l'orientation manquante)",
        "matrice de règles (lignes × colonnes → case ?)",
        "case manquante dans une séquence spatiale",
        "repérage d'une erreur dans une grille symétrique",
        "reconstruction d'un pattern partiellement caché",
    ],
    "puzzle": [
        "ordre chronologique par indices indirects",
        "tri par priorité avec contraintes combinées",
        "ordre logique cause → effet (chaîne de dépendances)",
        "reconstruction par exclusions uniquement",
    ],
    "riddle": _RIDDLE_MECHANISMS_ALL_AGES + _RIDDLE_MECHANISMS_ADVANCED,
}


def pick_variety_seed(challenge_type: str, age_group: str = "") -> VarietySeed:
    """Tire un seed aléatoire pour le type et le groupe d'âge donnés.

    Retourne un seed entièrement vide si le type n'a pas de mécanismes définis —
    build_challenge_user_prompt() n'injectera alors aucun bloc ORIENTATION.

    Pour le type ``riddle``, les mécanismes linguistiques avancés (auto-référence,
    double sens, métaphore) sont réservés aux groupes 12-14, 15-17 et adulte.
    Les types purement formels (chess, visual, pattern) reçoivent un seed sans
    contexte narratif — seul le mécanisme de résolution est injecté.
    """
    ct = challenge_type.strip().lower()
    mechanisms = RESOLUTION_MECHANISMS_BY_TYPE.get(ct, [])

    if ct == "riddle" and age_group and age_group not in _RIDDLE_ADVANCED_AGE_GROUPS:
        mechanisms = _RIDDLE_MECHANISMS_ALL_AGES

    if not mechanisms or not NARRATIVE_CONTEXTS:
        return VarietySeed(narrative_context="", resolution_mechanism="")

    narrative = (
        "" if ct in _TYPES_IGNORE_NARRATIVE else random.choice(NARRATIVE_CONTEXTS)
    )
    return VarietySeed(
        narrative_context=narrative,
        resolution_mechanism=random.choice(mechanisms),
    )
