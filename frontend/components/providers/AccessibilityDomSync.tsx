"use client";

import { useEffect } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";

/**
 * Mirror accessibility store flags to documentElement classes (FFI-L20C).
 */
export function AccessibilityDomSync() {
  const { highContrast, largeText, reducedMotion, dyslexiaMode, focusMode } =
    useAccessibilityStore();

  useEffect(() => {
    if (typeof document !== "undefined") {
      const root = document.documentElement;
      root.classList.toggle("high-contrast", highContrast);
      root.classList.toggle("large-text", largeText);
      root.classList.toggle("reduced-motion", reducedMotion);
      root.classList.toggle("dyslexia-mode", dyslexiaMode);
      root.classList.toggle("focus-mode", focusMode);
    }
  }, [highContrast, largeText, reducedMotion, dyslexiaMode, focusMode]);

  return null;
}
