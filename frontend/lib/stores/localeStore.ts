import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Locale = "fr" | "en";

/**
 * Reads the persisted locale from localStorage without importing the Zustand store
 * (safe to call outside React components and during SSR-safe code paths).
 * Returns "fr" as fallback if nothing is stored or the format is unexpected.
 */
export function getPersistedLocale(): Locale {
  if (typeof window === "undefined") return "fr";
  try {
    const stored = localStorage.getItem("locale-preferences");
    if (!stored) return "fr";
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

interface LocaleState {
  locale: Locale;
  setLocale: (locale: Locale) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      locale: "fr",
      setLocale: (locale) => {
        set({ locale });
        // Mettre à jour l'attribut lang sur le document
        if (typeof document !== "undefined") {
          document.documentElement.lang = locale;
        }
      },
    }),
    { name: "locale-preferences" }
  )
);
