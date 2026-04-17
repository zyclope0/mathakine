"use client";

import { useEffect } from "react";
import { useLocaleStore } from "@/lib/stores/localeStore";

/**
 * Composant pour initialiser la locale au chargement
 * Détecte la langue du navigateur et applique la locale appropriée
 */
export function LocaleInitializer() {
  const { setLocale } = useLocaleStore();

  // Première visite : détection navigateur (persist Zustand absent).
  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("locale-preferences")) {
      const browserLang = navigator.language?.split("-")[0] || "fr";
      const supportedLocales: ("fr" | "en")[] = ["fr", "en"];
      const detectedLocale: "fr" | "en" = supportedLocales.includes(browserLang as "fr" | "en")
        ? (browserLang as "fr" | "en")
        : "fr";

      setLocale(detectedLocale);
    }
  }, [setLocale]);

  return null;
}
