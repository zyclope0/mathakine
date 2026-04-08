"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/lib/stores/themeStore";
import { getLocalString, STORAGE_KEYS } from "@/lib/storage";
import { applyThemeDomState, readStoredDarkMode } from "@/lib/theme/themeDom";

/**
 * Initial theme preference from system + apply theme tokens to document (FFI-L20C).
 */
export function ThemeBootstrap() {
  const { theme, setTheme } = useThemeStore();

  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = getLocalString(STORAGE_KEYS.themePreferences);
    if (!stored) {
      const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
      setTheme(prefersLight ? "minimalist" : "spatial");
    }
  }, [setTheme]);

  useEffect(() => {
    applyThemeDomState({
      theme,
      isDark: readStoredDarkMode(),
      disableTransitions: true,
    });
  }, [theme]);

  return null;
}
