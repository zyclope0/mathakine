'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Settings2,
  Contrast,
  Type,
  Move,
  BookOpen,
  Focus,
  Check,
} from 'lucide-react';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';
import { cn } from '@/lib/utils/cn';

/**
 * Toolbar d'accessibilité - Version compacte
 * 
 * Un seul bouton qui ouvre un menu avec toutes les options.
 * Best practice : évite l'encombrement et les conflits avec d'autres éléments UI.
 */
export function AccessibilityToolbar() {
  const [isOpen, setIsOpen] = useState(false);
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

  // Compte le nombre d'options actives
  const activeCount = [highContrast, largeText, reducedMotion, dyslexiaMode, focusMode].filter(Boolean).length;

  const options = [
    {
      id: 'highContrast',
      icon: Contrast,
      label: 'Contraste élevé',
      shortcut: 'Alt+C',
      active: highContrast,
      toggle: toggleHighContrast,
    },
    {
      id: 'largeText',
      icon: Type,
      label: 'Texte agrandi',
      shortcut: 'Alt+T',
      active: largeText,
      toggle: toggleLargeText,
    },
    {
      id: 'reducedMotion',
      icon: Move,
      label: 'Réduire animations',
      shortcut: 'Alt+M',
      active: reducedMotion,
      toggle: toggleReducedMotion,
    },
    {
      id: 'dyslexiaMode',
      icon: BookOpen,
      label: 'Mode dyslexie',
      shortcut: 'Alt+D',
      active: dyslexiaMode,
      toggle: toggleDyslexiaMode,
    },
    {
      id: 'focusMode',
      icon: Focus,
      label: 'Mode focus (TSA/TDAH)',
      shortcut: 'Alt+F',
      active: focusMode,
      toggle: toggleFocusMode,
    },
  ];

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className={cn(
            "fixed bottom-4 right-4 z-50 h-11 w-11 rounded-full shadow-lg",
            "bg-background/80 backdrop-blur-sm border-2",
            "transition-all duration-200 hover:scale-105",
            activeCount > 0 && "border-primary ring-2 ring-primary/20"
          )}
          aria-label={`Accessibilité${activeCount > 0 ? ` (${activeCount} option${activeCount > 1 ? 's' : ''} active${activeCount > 1 ? 's' : ''})` : ''}`}
        >
          <Settings2 className="h-5 w-5" />
          {activeCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
              {activeCount}
            </span>
          )}
        </Button>
      </PopoverTrigger>
      
      <PopoverContent 
        side="top" 
        align="end" 
        className="w-64 p-2"
        sideOffset={8}
      >
        <div className="space-y-1">
          <div className="px-2 py-1.5 text-sm font-semibold text-muted-foreground">
            Accessibilité
          </div>
          
          {options.map((option) => {
            const Icon = option.icon;
            return (
              <button
                key={option.id}
                onClick={() => option.toggle()}
                className={cn(
                  "flex w-full items-center gap-3 rounded-md px-2 py-2 text-sm",
                  "transition-colors hover:bg-accent",
                  option.active && "bg-primary/10 text-primary"
                )}
                aria-pressed={option.active}
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                <span className="flex-1 text-left">{option.label}</span>
                <span className="text-[10px] text-muted-foreground">{option.shortcut}</span>
                {option.active && (
                  <Check className="h-4 w-4 text-primary" aria-hidden="true" />
                )}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
