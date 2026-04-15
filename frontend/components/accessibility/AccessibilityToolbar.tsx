"use client";

import { useEffect, useState, useRef } from "react";
import { createPortal } from "react-dom";
import {
  Settings2,
  Contrast,
  Type,
  Move,
  BookOpen,
  Focus,
  X,
  Check,
  RotateCcw,
} from "lucide-react";
import { useHydrated } from "@/lib/hooks/useHydrated";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { cn } from "@/lib/utils";

/**
 * Toolbar d'accessibilité - Version robuste avec Portal dans body
 *
 * Best practices implementées :
 * - Position bottom-left (convention UserWay/accessiBe)
 * - Taille 44x44px minimum (WCAG 2.2 AAA)
 * - Contraste élevé et focus visible
 * - Menu personnalisé (pas de Portal imbriqué)
 */

interface AccessibilityOption {
  id: string;
  label: string;
  shortcut: string;
  icon: React.ReactNode;
  isActive: boolean;
  toggle: () => void;
}

export function AccessibilityToolbar() {
  const isHydrated = useHydrated();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

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
    resetAll,
  } = useAccessibilityStore();

  // Options d'accessibilité
  const options: AccessibilityOption[] = [
    {
      id: "contrast",
      label: "Contraste élevé",
      shortcut: "Alt+C",
      icon: <Contrast className="h-4 w-4" />,
      isActive: highContrast,
      toggle: toggleHighContrast,
    },
    {
      id: "text",
      label: "Texte agrandi",
      shortcut: "Alt+T",
      icon: <Type className="h-4 w-4" />,
      isActive: largeText,
      toggle: toggleLargeText,
    },
    {
      id: "motion",
      label: "Réduire animations",
      shortcut: "Alt+M",
      icon: <Move className="h-4 w-4" />,
      isActive: reducedMotion,
      toggle: toggleReducedMotion,
    },
    {
      id: "dyslexia",
      label: "Mode dyslexie",
      shortcut: "Alt+D",
      icon: <BookOpen className="h-4 w-4" />,
      isActive: dyslexiaMode,
      toggle: toggleDyslexiaMode,
    },
    {
      id: "focus",
      label: "Mode focus",
      shortcut: "Alt+F",
      icon: <Focus className="h-4 w-4" />,
      isActive: focusMode,
      toggle: toggleFocusMode,
    },
  ];

  const activeCount = options.filter((o) => o.isActive).length;

  // Fermer le menu quand on clique en dehors
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [isOpen]);

  if (!isHydrated) {
    return null;
  }

  const toolbarContent = (
    <div className="fixed bottom-6 left-6 z-[99999] pointer-events-auto">
      <div className="relative">
        {/* Bouton principal - Visible toujours */}
        <button
          ref={buttonRef}
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-haspopup="true"
          aria-label={`Options d'accessibilité${activeCount > 0 ? ` (${activeCount} actif${activeCount > 1 ? "s" : ""})` : ""}`}
          className={cn(
            "relative flex items-center justify-center h-12 w-12 rounded-full",
            "bg-primary text-primary-foreground",
            "border-2 border-white/80",
            "shadow-lg shadow-primary/30",
            "transition-[transform,box-shadow] duration-200",
            "hover:scale-110 hover:shadow-xl hover:shadow-primary/40",
            "focus:outline-none focus:ring-4 focus:ring-primary/50 focus:ring-offset-2 focus:ring-offset-background",
            isOpen && "ring-2 ring-primary/50"
          )}
        >
          <Settings2 className="h-6 w-6" aria-hidden="true" />

          {activeCount > 0 && (
            <span
              className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-white text-[10px] font-bold text-primary ring-2 ring-primary"
              aria-hidden="true"
            >
              {activeCount}
            </span>
          )}
        </button>

        {isOpen && (
          <div
            ref={menuRef}
            role="dialog"
            aria-label="Options d'accessibilité"
            className={cn(
              "absolute bottom-14 left-0",
              "w-64 rounded-lg",
              "bg-popover border border-border shadow-2xl",
              "animate-in fade-in slide-in-from-bottom-2 duration-200"
            )}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-border">
              <span className="font-semibold text-sm text-popover-foreground">Accessibilité</span>
              <button
                type="button"
                onClick={() => setIsOpen(false)}
                className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-md p-2 hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                aria-label="Fermer le menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="py-2" role="group" aria-label="Options disponibles">
              {options.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  role="switch"
                  aria-label={option.label}
                  aria-checked={option.isActive}
                  onClick={() => {
                    option.toggle();
                  }}
                  className={cn(
                    "w-full flex items-center gap-3 px-4 py-2.5 text-left",
                    "hover:bg-muted focus:outline-none focus:bg-muted",
                    "transition-colors",
                    option.isActive && "bg-primary/10"
                  )}
                >
                  <span
                    className={cn(
                      "flex-shrink-0",
                      option.isActive ? "text-primary" : "text-muted-foreground"
                    )}
                  >
                    {option.icon}
                  </span>
                  <span
                    className={cn(
                      "flex-1 text-sm text-foreground",
                      option.isActive && "font-medium"
                    )}
                  >
                    {option.label}
                  </span>
                  <span className="text-xs text-muted-foreground hidden sm:inline">
                    {option.shortcut}
                  </span>
                  {option.isActive && (
                    <Check className="h-4 w-4 text-primary flex-shrink-0" aria-hidden="true" />
                  )}
                </button>
              ))}
            </div>

            <div className="px-4 py-2 border-t border-border bg-muted/50 rounded-b-lg flex items-center justify-between gap-2">
              <p className="text-xs text-muted-foreground">
                Utilisez Alt + lettre pour activer rapidement
              </p>
              {activeCount > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    resetAll();
                    setIsOpen(false);
                  }}
                  className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors shrink-0"
                  aria-label="Réinitialiser toutes les options d'accessibilité"
                >
                  <RotateCcw className="h-3 w-3" aria-hidden="true" />
                  Réinitialiser
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return createPortal(toolbarContent, document.body);
}
