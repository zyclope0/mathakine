import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "spatial" | "minimalist" | "ocean" | "dune" | "forest" | "peach" | "dino";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "spatial",
      setTheme: (theme) => {
        const valid: Theme[] = [
          "spatial",
          "minimalist",
          "ocean",
          "dune",
          "forest",
          "peach",
          "dino",
        ];
        const t = valid.includes(theme) ? theme : "spatial";
        set({ theme: t });
        if (typeof document !== "undefined") {
          document.documentElement.setAttribute("data-theme", t);
        }
      },
    }),
    {
      name: "theme-preferences",
      onRehydrateStorage: () => (state) => {
        if (!state || typeof document === "undefined") return;
        // Migration: neutral → dune (anciens utilisateurs avec thème Neutral)
        const theme = (state.theme as string) === "neutral" ? "dune" : state.theme;
        const valid: Theme[] = [
          "spatial",
          "minimalist",
          "ocean",
          "dune",
          "forest",
          "peach",
          "dino",
        ];
        const t = valid.includes(theme) ? theme : "spatial";
        document.documentElement.setAttribute("data-theme", t);
        if (t !== state.theme) {
          useThemeStore.getState().setTheme(t);
        }
      },
    }
  )
);
