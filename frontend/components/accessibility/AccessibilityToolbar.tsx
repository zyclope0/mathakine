'use client';

import { Button } from '@/components/ui/button';
import {
  Contrast,
  Type,
  Move,
  BookOpen,
  Focus,
} from 'lucide-react';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';

export function AccessibilityToolbar() {
  const {
    highContrast,
    largeText,
    reducedMotion,
    dyslexiaMode,
    focusMode,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    toggleDyslexiaMode,
    toggleFocusMode,
  } = useAccessibilityStore();

  return (
    <div className="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2">
      <Button
        onClick={toggleHighContrast}
        variant={highContrast ? 'default' : 'outline'}
        size="icon"
        aria-label="Mode contraste élevé (Alt+C)"
        title="Mode contraste élevé"
        className="h-12 w-12"
      >
        <Contrast className="h-5 w-5" aria-hidden="true" />
      </Button>
      
      <Button
        onClick={toggleLargeText}
        variant={largeText ? 'default' : 'outline'}
        size="icon"
        aria-label="Texte plus grand (Alt+T)"
        title="Texte plus grand"
        className="h-12 w-12"
      >
        <Type className="h-5 w-5" aria-hidden="true" />
      </Button>
      
      <Button
        onClick={toggleReducedMotion}
        variant={reducedMotion ? 'default' : 'outline'}
        size="icon"
        aria-label="Réduire les animations (Alt+M)"
        title="Réduire les animations"
        className="h-12 w-12"
      >
        <Move className="h-5 w-5" aria-hidden="true" />
      </Button>
      
      <Button
        onClick={toggleDyslexiaMode}
        variant={dyslexiaMode ? 'default' : 'outline'}
        size="icon"
        aria-label="Mode dyslexie (Alt+D)"
        title="Mode dyslexie"
        className="h-12 w-12"
      >
        <BookOpen className="h-5 w-5" aria-hidden="true" />
      </Button>
      
      <Button
        onClick={toggleFocusMode}
        variant={focusMode ? 'default' : 'outline'}
        size="icon"
        aria-label="Mode Focus TSA/TDAH"
        title="Mode Focus - Réduire les distractions"
        className="h-12 w-12 bg-primary/20 hover:bg-primary/30"
      >
        <Focus className="h-5 w-5" aria-hidden="true" />
      </Button>
    </div>
  );
}

