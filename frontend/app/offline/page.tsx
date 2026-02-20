"use client";

import { Button } from "@/components/ui/button";
import { WifiOff, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";

export default function OfflinePage() {
  const router = useRouter();

  const handleRetry = () => {
    if (navigator.onLine) {
      router.refresh();
    } else {
      // Attendre que la connexion revienne
      window.addEventListener(
        "online",
        () => {
          router.refresh();
        },
        { once: true }
      );
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-4">
      <div className="text-center space-y-6 max-w-md">
        <div className="flex justify-center">
          <div className="rounded-full bg-muted p-6">
            <WifiOff className="h-16 w-16 text-muted-foreground" />
          </div>
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Hors ligne</h1>
          <p className="text-muted-foreground">
            Vous n&apos;êtes pas connecté à Internet. Vérifiez votre connexion et réessayez.
          </p>
        </div>

        <Button onClick={handleRetry} className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4" />
          Réessayer
        </Button>

        <p className="text-sm text-muted-foreground">
          Certaines fonctionnalités peuvent être disponibles hors ligne grâce au cache.
        </p>
      </div>
    </div>
  );
}
