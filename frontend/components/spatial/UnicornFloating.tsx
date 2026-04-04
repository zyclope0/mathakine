"use client";

import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";

/**
 * Petite licorne volante — visible uniquement avec le thème Licorne 🦄
 * Inspiration directe du DinoFloating du thème Dino.
 * Flotte en haut à gauche avec un tangage gracieux.
 */
export function UnicornFloating() {
  const { theme } = useThemeStore();
  const { focusMode, reducedMotion } = useAccessibilityStore();

  if (theme !== "unicorn" || focusMode || reducedMotion) {
    return null;
  }

  return (
    <div
      className="fixed top-20 left-8 z-[-5] pointer-events-none opacity-50"
      data-spatial-layer="unicorn-floating"
      aria-hidden="true"
      style={{
        animation: "unicorn-float 6s ease-in-out infinite",
        animationDelay: "0.5s",
      }}
    >
      <span className="text-4xl" role="img" aria-hidden="true">
        🦄
      </span>
    </div>
  );
}
