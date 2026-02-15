"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useEffect } from "react";
import { Toaster } from "@/components/ui/sonner";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { NextIntlProvider } from "./NextIntlProvider";
import { AuthSyncProvider } from "./AuthSyncProvider";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const THEME_STORAGE_KEY = "theme-preferences";

export function Providers({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useThemeStore();
  const { highContrast, largeText, reducedMotion, dyslexiaMode, focusMode } =
    useAccessibilityStore();

  // Premier chargement : appliquer prefers-color-scheme si l'utilisateur n'a jamais choisi de thème
  useEffect(() => {
    if (typeof window === "undefined") return;
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (!stored) {
      const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
      setTheme(prefersLight ? "minimalist" : "spatial");
    }
  }, [setTheme]);

  // Appliquer le thème au chargement
  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", theme);

      // Réappliquer le dark mode si activé (pour synchroniser avec les variantes dark: du thème)
      const stored = localStorage.getItem("dark-mode");
      const isDarkMode = stored === "true";
      if (isDarkMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    }
  }, [theme]);

  // Appliquer les préférences d'accessibilité
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

  // Gestion des raccourcis clavier d'accessibilité
  useEffect(() => {
    const {
      toggleHighContrast,
      toggleLargeText,
      toggleReducedMotion,
      toggleDyslexiaMode,
      toggleFocusMode,
    } = useAccessibilityStore.getState();

    const handleKeyDown = (event: KeyboardEvent) => {
      // Alt+C : Mode contraste élevé
      if (event.altKey && event.key.toLowerCase() === "c") {
        event.preventDefault();
        toggleHighContrast();
      }

      // Alt+T : Texte plus grand
      if (event.altKey && event.key.toLowerCase() === "t") {
        event.preventDefault();
        toggleLargeText();
      }

      // Alt+M : Réduction animations
      if (event.altKey && event.key.toLowerCase() === "m") {
        event.preventDefault();
        toggleReducedMotion();
      }

      // Alt+D : Mode dyslexie
      if (event.altKey && event.key.toLowerCase() === "d") {
        event.preventDefault();
        toggleDyslexiaMode();
      }

      // Alt+F : Mode Focus
      if (event.altKey && event.key.toLowerCase() === "f") {
        event.preventDefault();
        toggleFocusMode();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <NextIntlProvider>
      <QueryClientProvider client={queryClient}>
        <AuthSyncProvider>{children}</AuthSyncProvider>
        <Toaster />
        {/* ReactQueryDevtools uniquement en développement */}
        {process.env.NODE_ENV === "development" && (
          <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
        )}
      </QueryClientProvider>
    </NextIntlProvider>
  );
}
