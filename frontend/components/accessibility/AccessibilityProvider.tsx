'use client';

import { useEffect } from 'react';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';

/**
 * Provider qui applique les classes CSS d'accessibilité au document
 * selon les préférences de l'utilisateur
 */
export function AccessibilityProvider({ children }: { children: React.ReactNode }) {
  const {
    highContrast,
    largeText,
    reducedMotion,
    dyslexiaMode,
    focusMode,
  } = useAccessibilityStore();

  useEffect(() => {
    // Appliquer les classes CSS selon les préférences
    const root = document.documentElement;
    
    root.classList.toggle('high-contrast', highContrast);
    root.classList.toggle('large-text', largeText);
    root.classList.toggle('reduced-motion', reducedMotion);
    root.classList.toggle('dyslexia-mode', dyslexiaMode);
    root.classList.toggle('focus-mode', focusMode);
  }, [highContrast, largeText, reducedMotion, dyslexiaMode, focusMode]);

  // Gestion des raccourcis clavier
  useEffect(() => {
    const {
      toggleHighContrast,
      toggleLargeText,
      toggleReducedMotion,
      toggleDyslexiaMode,
      toggleFocusMode,
    } = useAccessibilityStore.getState();

    const handleKeyDown = (event: KeyboardEvent) => {
      // Alt+C : Mode contraste élevé
      if (event.altKey && event.key === 'c') {
        event.preventDefault();
        toggleHighContrast();
      }
      
      // Alt+T : Texte plus grand
      if (event.altKey && event.key === 't') {
        event.preventDefault();
        toggleLargeText();
      }
      
      // Alt+M : Réduction animations
      if (event.altKey && event.key === 'm') {
        event.preventDefault();
        toggleReducedMotion();
      }
      
      // Alt+D : Mode dyslexie
      if (event.altKey && event.key === 'd') {
        event.preventDefault();
        toggleDyslexiaMode();
      }
      
      // Alt+F : Mode Focus
      if (event.altKey && event.key === 'f') {
        event.preventDefault();
        toggleFocusMode();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return <>{children}</>;
}

