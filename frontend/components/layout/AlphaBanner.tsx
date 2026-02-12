"use client";

import { useState, useEffect } from "react";
import { X, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "mathakine-alpha-banner-dismissed";

export function AlphaBanner() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Vérifier si l'utilisateur a déjà fermé la bannière
    const dismissed = localStorage.getItem(STORAGE_KEY);
    if (!dismissed) {
      setIsVisible(true);
    }
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
    localStorage.setItem(STORAGE_KEY, "true");
  };

  if (!isVisible) return null;

  return (
    <div
      role="alert"
      aria-live="polite"
      className="bg-amber-500/90 dark:bg-amber-600/90 text-amber-950 dark:text-amber-50 px-4 py-2 relative z-50"
    >
      <div className="container mx-auto flex items-center justify-center gap-2 text-sm">
        <AlertTriangle className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
        <span className="font-medium">Version Alpha</span>
        <span className="hidden sm:inline">
          — Des erreurs ou dysfonctionnements peuvent exister sur certains exercices et défis.
        </span>
        <span className="sm:hidden">— Erreurs possibles.</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDismiss}
          className="ml-2 h-6 w-6 p-0 hover:bg-amber-600/20 dark:hover:bg-amber-400/20"
          aria-label="Fermer l'avertissement"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
