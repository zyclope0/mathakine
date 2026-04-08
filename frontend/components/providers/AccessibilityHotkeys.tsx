"use client";

import { useEffect } from "react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";

/**
 * Global Alt+* shortcuts for accessibility toggles (FFI-L20C).
 */
export function AccessibilityHotkeys() {
  useEffect(() => {
    const {
      toggleHighContrast,
      toggleLargeText,
      toggleReducedMotion,
      toggleDyslexiaMode,
      toggleFocusMode,
    } = useAccessibilityStore.getState();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.altKey && event.key.toLowerCase() === "c") {
        event.preventDefault();
        toggleHighContrast();
      }

      if (event.altKey && event.key.toLowerCase() === "t") {
        event.preventDefault();
        toggleLargeText();
      }

      if (event.altKey && event.key.toLowerCase() === "m") {
        event.preventDefault();
        toggleReducedMotion();
      }

      if (event.altKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        toggleDyslexiaMode();
      }

      if (event.altKey && event.key.toLowerCase() === "f") {
        event.preventDefault();
        toggleFocusMode();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return null;
}
