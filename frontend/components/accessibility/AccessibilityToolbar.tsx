'use client';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
  DropdownMenuTrigger,
  DropdownMenuShortcut,
} from '@/components/ui/dropdown-menu';
import {
  Settings2,
  Contrast,
  Type,
  Move,
  BookOpen,
  Focus,
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

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="default"
          size="icon"
          className={cn(
            "fixed bottom-6 right-6 z-[9999] h-14 w-14 rounded-full",
            "bg-violet-600 text-white border-4 border-white/50",
            "shadow-[0_0_20px_rgba(139,92,246,0.5)]",
            "transition-all duration-200 hover:scale-110 hover:shadow-[0_0_30px_rgba(139,92,246,0.7)]",
            activeCount > 0 && "ring-4 ring-violet-400/50 animate-pulse"
          )}
          aria-label={`Accessibilité${activeCount > 0 ? ` (${activeCount} actif${activeCount > 1 ? 's' : ''})` : ''}`}
        >
          <Settings2 className="h-7 w-7" />
          {activeCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-xs font-bold text-white border-2 border-white">
              {activeCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent 
        side="top" 
        align="end" 
        className="w-56"
        sideOffset={8}
      >
        <DropdownMenuLabel>Options d'accessibilité</DropdownMenuLabel>
        <DropdownMenuSeparator />
        
        <DropdownMenuCheckboxItem
          checked={highContrast}
          onCheckedChange={toggleHighContrast}
        >
          <Contrast className="mr-2 h-4 w-4" />
          Contraste élevé
          <DropdownMenuShortcut>Alt+C</DropdownMenuShortcut>
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={largeText}
          onCheckedChange={toggleLargeText}
        >
          <Type className="mr-2 h-4 w-4" />
          Texte agrandi
          <DropdownMenuShortcut>Alt+T</DropdownMenuShortcut>
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={reducedMotion}
          onCheckedChange={toggleReducedMotion}
        >
          <Move className="mr-2 h-4 w-4" />
          Réduire animations
          <DropdownMenuShortcut>Alt+M</DropdownMenuShortcut>
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={dyslexiaMode}
          onCheckedChange={toggleDyslexiaMode}
        >
          <BookOpen className="mr-2 h-4 w-4" />
          Mode dyslexie
          <DropdownMenuShortcut>Alt+D</DropdownMenuShortcut>
        </DropdownMenuCheckboxItem>
        
        <DropdownMenuCheckboxItem
          checked={focusMode}
          onCheckedChange={toggleFocusMode}
        >
          <Focus className="mr-2 h-4 w-4" />
          Mode focus
          <DropdownMenuShortcut>Alt+F</DropdownMenuShortcut>
        </DropdownMenuCheckboxItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
