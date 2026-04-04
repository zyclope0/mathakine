"use client";

import { STORAGE_KEYS } from "@/lib/storage";
import type { Theme } from "@/lib/stores/themeStore";

const THEME_SWITCHING_CLASS = "theme-switching";

function scheduleTransitionReset(root: HTMLElement) {
  const reset = () => root.classList.remove(THEME_SWITCHING_CLASS);
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(reset);
  });
}

export function readStoredDarkMode() {
  if (typeof window === "undefined") {
    return false;
  }

  const stored = window.localStorage.getItem(STORAGE_KEYS.darkMode);
  if (stored !== null) {
    return stored === "true";
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

interface ApplyThemeDomStateOptions {
  theme: Theme;
  isDark: boolean;
  disableTransitions?: boolean;
}

export function applyThemeDomState({
  theme,
  isDark,
  disableTransitions = false,
}: ApplyThemeDomStateOptions) {
  if (typeof document === "undefined") {
    return;
  }

  const root = document.documentElement;

  if (disableTransitions) {
    root.classList.add(THEME_SWITCHING_CLASS);
  }

  root.setAttribute("data-theme", theme);
  root.classList.toggle("dark", isDark);

  if (disableTransitions) {
    scheduleTransitionReset(root);
  }
}
