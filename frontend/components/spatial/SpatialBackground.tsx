"use client";

import { Starfield } from "./Starfield";
import { Planet } from "./Planet";
import { Particles } from "./Particles";
import { DinoFloating } from "./DinoFloating";

/**
 * Composant SpatialBackground - Conteneur pour toutes les animations spatiales
 *
 * Combine Starfield, Planet et Particles
 * Thème Dino : silhouette dino + petit dino flottant
 * S'adapte automatiquement au thème et aux préférences d'accessibilité
 */
export function SpatialBackground() {
  return (
    <>
      <Starfield />
      <Planet />
      <Particles />
      <DinoFloating />
    </>
  );
}
