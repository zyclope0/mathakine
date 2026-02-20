"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Eye } from "lucide-react";
import { useState } from "react";

interface DefaultRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
}

/**
 * Renderer par défaut pour les types de challenges non supportés.
 * Affiche les visual_data de manière propre et interactive.
 */
export function DefaultRenderer({ visualData, className }: DefaultRendererProps) {
  const [showRaw, setShowRaw] = useState(false);

  if (!visualData) return null;

  // Si c'est une string simple, l'afficher directement
  if (typeof visualData === "string") {
    return (
      <Card className={`bg-card border-primary/20 ${className || ""}`}>
        <CardContent className="p-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Données visuelles
              </h4>
              <button
                onClick={() => setShowRaw(!showRaw)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                {showRaw ? "Vue formatée" : "Vue brute"}
              </button>
            </div>
            {showRaw ? (
              <pre className="text-xs text-muted-foreground font-mono whitespace-pre-wrap break-words">
                {visualData}
              </pre>
            ) : (
              <div className="text-foreground whitespace-pre-wrap break-words">{visualData}</div>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Si c'est un objet JSON, l'afficher de manière structurée
  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
      <CardContent className="p-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
              <Eye className="h-4 w-4" />
              Données visuelles
            </h4>
            <button
              onClick={() => setShowRaw(!showRaw)}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              {showRaw ? "Vue structurée" : "Vue JSON"}
            </button>
          </div>
          {showRaw ? (
            <pre className="text-xs text-muted-foreground font-mono whitespace-pre-wrap break-words overflow-x-auto bg-muted/30 p-3 rounded">
              {JSON.stringify(visualData, null, 2)}
            </pre>
          ) : (
            <div className="space-y-2">
              {Object.entries(visualData).map(([key, value]) => (
                <div key={key} className="border-l-2 border-primary/30 pl-3">
                  <span className="text-xs font-semibold text-primary">{key}:</span>{" "}
                  <span className="text-sm text-foreground">
                    {typeof value === "object" ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
