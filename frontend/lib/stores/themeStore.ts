import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "spatial" | "minimalist" | "ocean" | "neutral";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "spatial",
      setTheme: (theme) => {
        set({ theme });
        // Appliquer le thème au document
        if (typeof document !== "undefined") {
          document.documentElement.setAttribute("data-theme", theme);
        }
      },
    }),
    {
      name: "theme-preferences",
      onRehydrateStorage: () => (state) => {
        // Appliquer le thème au chargement
        if (state && typeof document !== "undefined") {
          document.documentElement.setAttribute("data-theme", state.theme);
        }
      },
    }
  )
);
