"use client";

import { Button } from "@/components/ui/button";
import { useHydrated } from "@/lib/hooks/useHydrated";
import { Sun, Moon } from "lucide-react";
import { useEffect, useState } from "react";
import { useThemeStore } from "@/lib/stores/themeStore";
import { STORAGE_KEYS } from "@/lib/storage";
import { applyThemeDomState, readStoredDarkMode } from "@/lib/theme/themeDom";

/**
 * Toggle pour basculer entre mode clair et sombre
 * Ajoute/enlève la classe `.dark` sur document.documentElement
 * pour activer les variantes dark: spécifiques à chaque thème
 */
export function DarkModeToggle() {
  const isHydrated = useHydrated();
  const [isDark, setIsDark] = useState(() => {
    if (typeof window === "undefined") {
      return false;
    }

    return readStoredDarkMode();
  });
  const { theme } = useThemeStore();

  useEffect(() => {
    if (!isHydrated) {
      return;
    }

    applyThemeDomState({ theme, isDark, disableTransitions: false });
  }, [isDark, isHydrated, theme]);

  const toggleDarkMode = () => {
    const newIsDark = !isDark;
    setIsDark(newIsDark);
    window.localStorage.setItem(STORAGE_KEYS.darkMode, String(newIsDark));
    applyThemeDomState({ theme, isDark: newIsDark, disableTransitions: true });
  };

  // Éviter le flash de contenu non stylé (hydration mismatch)
  if (!isHydrated) {
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-9 w-9 p-0"
        aria-label="Changer le thème clair/sombre"
        disabled
      >
        <Moon className="h-4 w-4" aria-hidden="true" />
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleDarkMode}
      aria-label={isDark ? "Passer en mode clair" : "Passer en mode sombre"}
      title={isDark ? "Mode sombre actif" : "Mode clair actif"}
      className="h-9 w-9 p-0"
    >
      {isDark ? (
        <Sun className="h-4 w-4" aria-hidden="true" />
      ) : (
        <Moon className="h-4 w-4" aria-hidden="true" />
      )}
    </Button>
  );
}
