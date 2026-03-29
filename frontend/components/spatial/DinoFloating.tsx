"use client";

import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";

/**
 * Petit dinosaure flottant — visible uniquement avec le thème Dino
 * Touche décorative discrète pour le thème enfant
 */
export function DinoFloating() {
  const { theme } = useThemeStore();
  const { focusMode, reducedMotion } = useAccessibilityStore();

  if (theme !== "dino" || focusMode || reducedMotion) {
    return null;
  }

  return (
    <div
      className="fixed top-20 left-8 z-[-5] pointer-events-none opacity-40"
      data-spatial-layer="dino-floating"
      aria-hidden="true"
      style={{
        animation: "dino-bob 5s ease-in-out infinite",
        animationDelay: "1s",
      }}
    >
      <span className="text-4xl" role="img" aria-hidden="true">
        🦕
      </span>
    </div>
  );
}
