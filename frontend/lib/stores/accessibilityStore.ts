import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AccessibilityState {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  dyslexiaMode: boolean;
  focusMode: boolean; // Mode unique Phase 1
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  toggleReducedMotion: () => void;
  toggleDyslexiaMode: () => void;
  toggleFocusMode: () => void;
}

export const useAccessibilityStore = create<AccessibilityState>()(
  persist(
    (set) => ({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      dyslexiaMode: false,
      focusMode: false,
      toggleHighContrast: () => set((state) => ({ highContrast: !state.highContrast })),
      toggleLargeText: () => set((state) => ({ largeText: !state.largeText })),
      toggleReducedMotion: () => set((state) => ({ reducedMotion: !state.reducedMotion })),
      toggleDyslexiaMode: () => set((state) => ({ dyslexiaMode: !state.dyslexiaMode })),
      toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),
    }),
    { name: 'accessibility-preferences' }
  )
);
