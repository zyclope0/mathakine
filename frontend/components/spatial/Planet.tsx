"use client";

import { useEffect, useRef } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";

/**
 * Composant Planet - Planète rotative avec cratères 3D et symboles orbitants
 *
 * Symboles mathématiques orbitants : ∑∫π∞√Δ
 * S'adapte aux 7 thèmes (Spatial, Minimaliste, Océan, Dune, Forêt, Lumière, Dinosaures)
 * Thème Dino : silhouette T-Rex à la place de la planète
 * Respecte prefers-reduced-motion et se désactive en mode Focus
 */
export function Planet() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { focusMode, reducedMotion } = useAccessibilityStore();
  const { theme } = useThemeStore();

  // Symboles mathématiques à faire orbiter
  const symbols = ["∑", "∫", "π", "∞", "√", "Δ"];

  useEffect(() => {
    if (focusMode || reducedMotion || typeof window === "undefined") {
      return;
    }

    const container = containerRef.current;
    if (!container) return;

    // Animation de rotation de la planète
    let rotation = 0;
    const rotationSpeed = 0.5; // degrés par frame

    const animate = () => {
      if (container) {
        rotation += rotationSpeed;
        container.style.setProperty("--rotation", `${rotation}deg`);
      }
      requestAnimationFrame(animate);
    };

    const animationId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [focusMode, reducedMotion]);

  const planetGradient =
    "radial-gradient(circle at 30% 30%, rgb(var(--spatial-planet-color-1-rgb) / 0.8), rgb(var(--spatial-planet-color-2-rgb) / 0.6), rgb(var(--spatial-planet-color-3-rgb) / 0.4))";

  // Ne pas rendre si mode Focus ou reduced motion
  if (focusMode || reducedMotion) {
    return null;
  }

  // Thème Dino : silhouette de dinosaure à la place de la planète
  if (theme === "dino") {
    return (
      <div
        ref={containerRef}
        className="fixed bottom-8 right-8 z-[-5] pointer-events-none"
        aria-hidden="true"
      >
        <div
          className="relative w-32 h-32 flex items-center justify-center"
          style={{
            filter: "drop-shadow(0 0 30px rgb(var(--spatial-planet-glow-rgb) / 0.3))",
            animation: "dino-bob 4s ease-in-out infinite",
          }}
        >
          {/* Emoji T-Rex — immédiatement reconnaissable */}
          <span className="text-7xl" role="img" aria-hidden="true">
            🦖
          </span>
        </div>
        {/* Symboles mathématiques orbitants */}
        {symbols.map((symbol, index) => {
          const angle = (360 / symbols.length) * index;
          return (
            <div
              key={index}
              className="absolute text-xl font-bold"
              style={{
                color: "rgb(var(--spatial-dino-symbol-rgb) / 0.9)",
                top: "50%",
                left: "50%",
                transform: `
                  translate(-50%, -50%)
                  rotate(${angle}deg)
                  translateY(-80px)
                  rotate(-${angle}deg)
                `,
                animation: `orbit-${index} 20s linear infinite`,
              }}
            >
              {symbol}
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="fixed bottom-8 right-8 z-[-5] pointer-events-none"
      aria-hidden="true"
    >
      {/* Planète avec cratères 3D */}
      <div
        className="relative w-32 h-32 rounded-full"
        style={{
          background: planetGradient,
          boxShadow: `
            inset -20px -20px 40px rgb(0 0 0 / 0.5),
            inset 10px 10px 20px rgb(255 255 255 / 0.1),
            0 0 60px rgb(var(--spatial-planet-glow-rgb) / 0.3)
          `,
          transform: "rotate(var(--rotation, 0deg))",
        }}
      >
        {/* Cratères 3D */}
        <div
          className="absolute w-8 h-8 rounded-full top-4 left-6"
          style={{
            background: "radial-gradient(circle at 30% 30%, rgb(0 0 0 / 0.4), rgb(0 0 0 / 0.6))",
            boxShadow: "inset 2px 2px 4px rgb(0 0 0 / 0.8)",
          }}
        />
        <div
          className="absolute w-6 h-6 rounded-full bottom-8 right-8"
          style={{
            background: "radial-gradient(circle at 30% 30%, rgb(0 0 0 / 0.3), rgb(0 0 0 / 0.5))",
            boxShadow: "inset 2px 2px 4px rgb(0 0 0 / 0.7)",
          }}
        />
        <div
          className="absolute w-10 h-10 rounded-full top-12 right-4"
          style={{
            background: "radial-gradient(circle at 30% 30%, rgb(0 0 0 / 0.5), rgb(0 0 0 / 0.7))",
            boxShadow: "inset 2px 2px 4px rgb(0 0 0 / 0.9)",
          }}
        />

        {/* Anneau pulsant autour de la planète */}
        <div
          className="absolute inset-0 rounded-full border-2 border-primary/30"
          style={{
            animation: "pulse-ring 3s ease-in-out infinite",
          }}
        />
      </div>

      {/* Symboles mathématiques orbitants */}
      {symbols.map((symbol, index) => {
        const angle = (360 / symbols.length) * index;
        const radius = 80; // Distance de l'orbite

        return (
          <div
            key={index}
            className="absolute text-2xl font-bold text-primary"
            style={{
              top: "50%",
              left: "50%",
              transform: `
                translate(-50%, -50%)
                rotate(${angle}deg)
                translateY(-${radius}px)
                rotate(-${angle}deg)
              `,
              animation: `orbit-${index} 20s linear infinite`,
            }}
          >
            {symbol}
          </div>
        );
      })}
    </div>
  );
}
