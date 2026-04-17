import { create } from "zustand";
import { persist } from "zustand/middleware";

import {
  getLocaleFromDocumentCookie,
  type LocaleCode,
  setLocaleCookieClient,
} from "@/lib/localeCookie";

export type Locale = LocaleCode;

/**
 * Reads the effective locale for API / non-React callers: cookie first, then
 * persisted Zustand payload in localStorage.
 */
export function getPersistedLocale(): Locale {
  if (typeof window === "undefined") {
    return "fr";
  }
  const fromCookie = getLocaleFromDocumentCookie();
  if (fromCookie) {
    return fromCookie;
  }
  try {
    const stored = localStorage.getItem("locale-preferences");
    if (!stored) {
      return "fr";
    }
    const parsed: unknown = JSON.parse(stored);
    if (
      parsed !== null &&
      typeof parsed === "object" &&
      "state" in parsed &&
      parsed.state !== null &&
      typeof parsed.state === "object" &&
      "locale" in parsed.state &&
      (parsed.state.locale === "fr" || parsed.state.locale === "en")
    ) {
      return parsed.state.locale as Locale;
    }
  } catch {
    // localStorage unavailable or malformed JSON — silent fallback
  }
  return "fr";
}

function syncLocaleToBrowser(locale: Locale): void {
  if (typeof document !== "undefined") {
    document.documentElement.lang = locale;
  }
  setLocaleCookieClient(locale);
}

interface LocaleState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      locale: "fr",
      setLocale: (locale) => set({ locale }),
    }),
    {
      name: "locale-preferences",
      onRehydrateStorage: () => (state) => {
        if (typeof window === "undefined" || !state) {
          return;
        }
        const cookieLocale = getLocaleFromDocumentCookie();
        if (cookieLocale && cookieLocale !== state.locale) {
          useLocaleStore.setState({ locale: cookieLocale });
        } else if (!cookieLocale) {
          syncLocaleToBrowser(state.locale);
        }
      },
    }
  )
);

useLocaleStore.subscribe((state, prev) => {
  if (prev !== undefined && state.locale !== prev.locale) {
    syncLocaleToBrowser(state.locale);
  }
});
