"use client";

import { useEffect, useRef } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";
import { cn } from "@/lib/utils/cn";

/**
 * Composant Starfield - Système d'étoiles multi-couches
 *
 * 3 couches d'étoiles avec vitesses différentes pour effet de profondeur
 * Respecte prefers-reduced-motion et se désactive en mode Focus
 */
export function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { focusMode, reducedMotion } = useAccessibilityStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    // Ne pas afficher en mode Focus ou si reduced motion
    if (focusMode || reducedMotion || typeof window === "undefined") {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Ajuster la taille du canvas
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Couleur des étoiles selon le thème
    const starColors: Record<string, string> = {
      spatial: "rgba(255, 255, 255, ", // Blanc pour thème spatial
      minimalist: "rgba(0, 0, 0, ", // Noir pour thème minimaliste
      ocean: "rgba(255, 255, 255, ", // Blanc pour thème océan
      neutral: "rgba(107, 114, 128, ", // Gris pour thème neutre
    };

    const starColorBase = starColors[theme] || starColors.spatial;

    // Configuration des 3 couches d'étoiles avec vitesses réduites
    const layers = [
      { count: 100, speed: 0.08, size: 1, opacity: 0.8 }, // Couche lointaine (très lente)
      { count: 150, speed: 0.15, size: 1.5, opacity: 0.6 }, // Couche moyenne
      { count: 200, speed: 0.25, size: 2, opacity: 0.4 }, // Couche proche (lente)
    ];

    // Générer les étoiles pour chaque couche avec mouvement diagonal varié
    const stars = layers.map((layer) =>
      Array.from({ length: layer.count }, () => {
        // Angle de mouvement varié pour éviter l'effet "neige verticale"
        // Les étoiles se déplacent principalement vers le bas mais avec un léger angle horizontal
        const angle = (Math.random() - 0.5) * 0.3; // Angle entre -0.15 et 0.15 rad (environ -8° à 8°)
        return {
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          speedX: Math.sin(angle) * layer.speed, // Composante horizontale
          speedY: Math.cos(angle) * layer.speed, // Composante verticale (principale)
          size: layer.size,
          opacity: layer.opacity,
        };
      })
    );

    let animationId: number;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      stars.forEach((layerStars, layerIndex) => {
        layerStars.forEach((star) => {
          // Déplacer l'étoile avec mouvement diagonal
          star.x += star.speedX;
          star.y += star.speedY;

          // Réinitialiser si l'étoile sort de l'écran (par le bas ou les côtés)
          if (star.y > canvas.height) {
            star.y = 0;
            star.x = Math.random() * canvas.width;
          } else if (star.x < 0) {
            star.x = canvas.width;
          } else if (star.x > canvas.width) {
            star.x = 0;
          }

          // Dessiner l'étoile
          ctx.beginPath();
          ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2);
          ctx.fillStyle = `${starColorBase}${star.opacity})`;
          ctx.fill();
        });
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, [focusMode, reducedMotion, theme]);

  // Ne pas rendre si mode Focus ou reduced motion
  if (focusMode || reducedMotion) {
    return null;
  }

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[-10]"
      aria-hidden="true"
    />
  );
}
