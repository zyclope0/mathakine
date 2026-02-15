"use client";

import { useEffect, useRef } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";

/**
 * Composant Particles - Système de particules subtiles en arrière-plan
 *
 * Particules adaptées au thème actuel
 * Respecte prefers-reduced-motion et se désactive en mode Focus
 */
export function Particles() {
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

    // Couleurs selon le thème
    const themeColors: Record<string, string> = {
      spatial: "rgba(139, 92, 246, 0.3)",
      minimalist: "rgba(0, 0, 0, 0.2)",
      ocean: "rgba(14, 165, 233, 0.3)",
      dune: "rgba(251, 191, 36, 0.25)",
      forest: "rgba(52, 211, 153, 0.25)",
      peach: "rgba(251, 146, 60, 0.25)",
      dino: "rgba(132, 204, 22, 0.25)",
    };

    const particleColor = themeColors[theme] || themeColors.spatial || "rgba(139, 92, 246, 0.3)";

    // Créer les particules
    const particleCount = 50;
    const particles = Array.from({ length: particleCount }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5, // Vitesse horizontale
      vy: (Math.random() - 0.5) * 0.5, // Vitesse verticale
      size: Math.random() * 2 + 1,
      opacity: Math.random() * 0.5 + 0.2,
    }));

    let animationId: number;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((particle) => {
        // Mettre à jour la position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Réinitialiser si la particule sort de l'écran
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

        // Garder dans les limites
        particle.x = Math.max(0, Math.min(canvas.width, particle.x));
        particle.y = Math.max(0, Math.min(canvas.height, particle.y));

        // Dessiner la particule
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particleColor.replace("0.3", particle.opacity.toString());
        ctx.fill();
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
      className="fixed inset-0 pointer-events-none z-[-8]"
      aria-hidden="true"
    />
  );
}
