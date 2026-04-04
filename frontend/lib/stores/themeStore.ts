import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "spatial" | "minimalist" | "ocean" | "dune" | "forest" | "aurora" | "dino" | "unicorn";

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
          "aurora",
          "dino",
          "unicorn",
        ];
        const t = valid.includes(theme) ? theme : "spatial";
        set({ theme: t });
      },
    }),
    {
      name: "theme-preferences",
      onRehydrateStorage: () => (state) => {
        if (!state) return;
        // Migration : neutral → dune (anciens utilisateurs), peach → aurora (refonte 2026-03-30)
        let theme = (state.theme as string) === "neutral" ? "dune" : state.theme;
        theme = (theme as string) === "peach" ? "aurora" : theme;
        const valid: Theme[] = [
          "spatial",
          "minimalist",
          "ocean",
          "dune",
          "forest",
          "aurora",
          "dino",
          "unicorn",
        ];
        const t = valid.includes(theme) ? theme : "spatial";
        if (t !== state.theme) {
          useThemeStore.setState({ theme: t });
        }
      },
    }
  )
);
