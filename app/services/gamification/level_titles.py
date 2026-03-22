"""
Titres d'affichage des niveaux gamification (compte).

Les numéros de niveau suivent la formule persistée (total_points // POINTS_PER_LEVEL + 1).
Au-delà des entrées connues, l'API retombe sur un libellé générique « Niveau N ».
"""

from typing import Dict

LEVEL_TITLES: Dict[int, str] = {
    1: "Jeune Padawan",
    2: "Padawan",
    3: "Chevalier Jedi",
    4: "Maître Jedi",
    5: "Grand Maître",
    6: "Maître du Conseil",
    7: "Légende Jedi",
    8: "Gardien de la Force",
    9: "Seigneur Jedi",
    10: "Archiviste Jedi",
    11: "Grand Archiviste",
}
