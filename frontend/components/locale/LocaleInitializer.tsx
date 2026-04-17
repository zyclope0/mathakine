"use client";

import { useEffect } from "react";
import { getLocaleFromDocumentCookie } from "@/lib/localeCookie";
import { useLocaleStore } from "@/lib/stores/localeStore";

/**
 * Initializes locale on first visit.
 * Browser language detection is only used when neither the persisted store nor
 * the canonical locale cookie exists yet.
 */
export function LocaleInitializer() {
  const { setLocale } = useLocaleStore();

  useEffect(() => {
    if (
      typeof window !== "undefined" &&
      !localStorage.getItem("locale-preferences") &&
      !getLocaleFromDocumentCookie()
    ) {
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
