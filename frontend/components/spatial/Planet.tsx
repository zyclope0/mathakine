"use client";

import { useEffect, useRef } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";
import { cn } from "@/lib/utils/cn";

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

  // Couleurs de la planète selon le thème
  const planetColors: Record<string, { bg: string; glow: string }> = {
    spatial: {
      bg: "radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.8), rgba(124, 58, 237, 0.6), rgba(79, 70, 229, 0.4))",
      glow: "rgba(139, 92, 246, 0.3)",
    },
    minimalist: {
      bg: "radial-gradient(circle at 30% 30%, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.5))",
      glow: "rgba(0, 0, 0, 0.2)",
    },
    ocean: {
      bg: "radial-gradient(circle at 30% 30%, rgba(14, 165, 233, 0.8), rgba(3, 105, 161, 0.6), rgba(2, 132, 199, 0.4))",
      glow: "rgba(14, 165, 233, 0.3)",
    },
    dune: {
      bg: "radial-gradient(circle at 30% 30%, rgba(251, 191, 36, 0.8), rgba(217, 119, 6, 0.6), rgba(180, 83, 9, 0.4))",
      glow: "rgba(251, 191, 36, 0.3)",
    },
    forest: {
      bg: "radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.8), rgba(16, 185, 129, 0.6), rgba(5, 150, 105, 0.4))",
      glow: "rgba(52, 211, 153, 0.3)",
    },
    peach: {
      bg: "radial-gradient(circle at 30% 30%, rgba(251, 146, 60, 0.8), rgba(249, 115, 22, 0.6), rgba(234, 88, 12, 0.4))",
      glow: "rgba(251, 146, 60, 0.3)",
    },
    dino: {
      bg: "radial-gradient(circle at 30% 30%, rgba(132, 204, 22, 0.8), rgba(101, 163, 13, 0.6), rgba(77, 124, 15, 0.4))",
      glow: "rgba(132, 204, 22, 0.3)",
    },
  };

  const colors = planetColors[theme] ||
    planetColors.spatial || {
      bg: "radial-gradient(circle at 30% 30%, rgba(139, 92, 246, 0.8), rgba(124, 58, 237, 0.6), rgba(79, 70, 229, 0.4))",
      glow: "rgba(139, 92, 246, 0.3)",
    };

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
            filter: `drop-shadow(0 0 30px ${colors.glow})`,
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
                color: "rgba(132, 204, 22, 0.9)",
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
          background: colors.bg,
          boxShadow: `
            inset -20px -20px 40px rgba(0, 0, 0, 0.5),
            inset 10px 10px 20px rgba(255, 255, 255, 0.1),
            0 0 60px ${colors.glow}
          `,
          transform: "rotate(var(--rotation, 0deg))",
        }}
      >
        {/* Cratères 3D */}
        <div
          className="absolute w-8 h-8 rounded-full top-4 left-6"
          style={{
            background:
              "radial-gradient(circle at 30% 30%, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6))",
            boxShadow: "inset 2px 2px 4px rgba(0, 0, 0, 0.8)",
          }}
        />
        <div
          className="absolute w-6 h-6 rounded-full bottom-8 right-8"
          style={{
            background:
              "radial-gradient(circle at 30% 30%, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.5))",
            boxShadow: "inset 2px 2px 4px rgba(0, 0, 0, 0.7)",
          }}
        />
        <div
          className="absolute w-10 h-10 rounded-full top-12 right-4"
          style={{
            background:
              "radial-gradient(circle at 30% 30%, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7))",
            boxShadow: "inset 2px 2px 4px rgba(0, 0, 0, 0.9)",
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
