import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Locale = "fr" | "en";

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
