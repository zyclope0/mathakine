"use client";

import { useEffect, useState, useRef } from "react";
import { createPortal } from "react-dom";
import { Settings2, Contrast, Type, Move, BookOpen, Focus, X, Check } from "lucide-react";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { cn } from "@/lib/utils/cn";

/**
 * Toolbar d'accessibilité - Version robuste avec Portal dédié
 *
 * Best practices implementées :
 * - Position bottom-left (convention UserWay/accessiBe)
 * - Conteneur Portal dédié pour éviter les conflits
 * - Taille 44x44px minimum (WCAG 2.2 AAA)
 * - Contraste élevé et focus visible
 * - Menu personnalisé (pas de Portal imbriqué)
 */

// ID unique pour le conteneur Portal
const PORTAL_CONTAINER_ID = "accessibility-toolbar-portal";

interface AccessibilityOption {
  id: string;
  label: string;
  shortcut: string;
  icon: React.ReactNode;
  isActive: boolean;
  toggle: () => void;
}

export function AccessibilityToolbar() {
  const [mounted, setMounted] = useState(false);
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

  // Créer/obtenir le conteneur Portal au montage
  useEffect(() => {
    let container = document.getElementById(PORTAL_CONTAINER_ID);

    if (!container) {
      container = document.createElement("div");
      container.id = PORTAL_CONTAINER_ID;
      // Styles inline pour garantir le positionnement
      container.style.cssText = `
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 99999;
        pointer-events: auto;
      `;
      document.body.appendChild(container);
    }

    setMounted(true);

    return () => {
      // Ne pas supprimer le conteneur au démontage (évite les flickering)
    };
  }, []);

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

  // Ne pas rendre côté serveur
  if (!mounted) {
    return null;
  }

  const container = document.getElementById(PORTAL_CONTAINER_ID);
  if (!container) {
    return null;
  }

  const toolbarContent = (
    <div className="relative">
      {/* Bouton principal - Visible toujours */}
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen ? "true" : "false"}
        aria-haspopup="true"
        aria-label={`Options d'accessibilité${activeCount > 0 ? ` (${activeCount} actif${activeCount > 1 ? "s" : ""})` : ""}`}
        className={cn(
          // Taille WCAG AAA (44x44 minimum)
          "relative flex items-center justify-center h-12 w-12 rounded-full",
          // Couleurs avec bon contraste
          "bg-violet-600 text-white",
          "border-2 border-white/80",
          // Ombre et effet glow
          "shadow-lg shadow-violet-600/30",
          // Transition et hover
          "transition-all duration-200",
          "hover:scale-110 hover:shadow-xl hover:shadow-violet-600/40",
          // Focus visible (WCAG)
          "focus:outline-none focus:ring-4 focus:ring-violet-400 focus:ring-offset-2 focus:ring-offset-background",
          // État actif (sans pulse pour ne pas distraire)
          isOpen && "ring-2 ring-violet-400"
        )}
      >
        <Settings2 className="h-6 w-6" aria-hidden="true" />

        {/* Badge compteur — discret, cohérent avec le violet */}
        {activeCount > 0 && (
          <span
            className="absolute -top-0.5 -right-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-white text-[10px] font-bold text-violet-600 ring-2 ring-violet-600"
            aria-hidden="true"
          >
            {activeCount}
          </span>
        )}
      </button>

      {/* Menu des options */}
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
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-border">
            <span className="font-semibold text-sm text-popover-foreground">Accessibilité</span>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
              aria-label="Fermer le menu"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Options */}
          <div className="py-2" role="group" aria-label="Options disponibles">
            {options.map((option) => (
              <button
                key={option.id}
                type="button"
                role="switch"
                aria-label={option.label}
                aria-checked={option.isActive ? "true" : "false"}
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
                  className={cn("flex-1 text-sm text-foreground", option.isActive && "font-medium")}
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

          {/* Footer avec info */}
          <div className="px-4 py-2 border-t border-border bg-muted/50 rounded-b-lg">
            <p className="text-xs text-muted-foreground">
              Utilisez Alt + lettre pour activer rapidement
            </p>
          </div>
        </div>
      )}
    </div>
  );

  return createPortal(toolbarContent, container);
}
