import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AccessibilityState {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  dyslexiaMode: boolean;
  focusMode: boolean;
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  toggleReducedMotion: () => void;
  toggleDyslexiaMode: () => void;
  toggleFocusMode: () => void;
  resetAll: () => void;
}

const DEFAULT_STATE = {
  highContrast: false,
  largeText: false,
  reducedMotion: false,
  dyslexiaMode: false,
  focusMode: false,
};

export const useAccessibilityStore = create<AccessibilityState>()(
  persist(
    (set) => ({
      ...DEFAULT_STATE,
      toggleHighContrast: () => set((state) => ({ highContrast: !state.highContrast })),
      toggleLargeText: () => set((state) => ({ largeText: !state.largeText })),
      toggleReducedMotion: () => set((state) => ({ reducedMotion: !state.reducedMotion })),
      toggleDyslexiaMode: () => set((state) => ({ dyslexiaMode: !state.dyslexiaMode })),
      toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),
      resetAll: () => set(DEFAULT_STATE),
    }),
    { name: "accessibility-preferences" }
  )
);
