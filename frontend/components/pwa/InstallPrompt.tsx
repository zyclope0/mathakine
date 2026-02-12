"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Download, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Vérifier si l'app est déjà installée
    if (window.matchMedia("(display-mode: standalone)").matches) {
      setIsInstalled(true);
      return;
    }

    // Écouter l'événement beforeinstallprompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      // Afficher le prompt après un délai (par exemple, après 30 secondes d'utilisation)
      setTimeout(() => {
        setShowPrompt(true);
      }, 30000); // 30 secondes
    };

    // Écouter l'événement appinstalled
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
    window.addEventListener("appinstalled", handleAppInstalled);

    return () => {
      window.removeEventListener("beforeinstallprompt", handleBeforeInstallPrompt);
      window.removeEventListener("appinstalled", handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    // Afficher le prompt d'installation
    await deferredPrompt.prompt();

    // Attendre le choix de l'utilisateur
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === "accepted") {
      setShowPrompt(false);
      setDeferredPrompt(null);
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    // Ne pas réafficher pendant cette session
    sessionStorage.setItem("pwa-install-dismissed", "true");
  };

  // Ne pas afficher si déjà installé ou si dismissé dans cette session
  if (
    isInstalled ||
    !showPrompt ||
    !deferredPrompt ||
    sessionStorage.getItem("pwa-install-dismissed")
  ) {
    return null;
  }

  return (
    <AnimatePresence>
      {showPrompt && (
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:w-96"
        >
          <div className="bg-card border border-border rounded-lg shadow-lg p-4 flex items-center gap-4">
            <div className="flex-1">
              <h3 className="font-semibold text-sm mb-1">Installer Mathakine</h3>
              <p className="text-xs text-muted-foreground">
                Installez l'application pour un accès rapide et une meilleure expérience.
              </p>
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleInstallClick} className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Installer
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleDismiss}
                className="h-8 w-8 p-0"
                aria-label="Fermer"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
