"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileJson, Type } from "lucide-react";
import { useState } from "react";

interface DefaultRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
}

/** Rendu coloré d'une valeur JSON pour la vue structurée */
function renderValue(value: unknown): React.ReactNode {
  if (value === null) return <span className="text-muted-foreground italic">null</span>;
  if (typeof value === "boolean")
    return <span className="text-info font-mono">{String(value)}</span>;
  if (typeof value === "number") return <span className="text-success font-mono">{value}</span>;
  if (typeof value === "string") return <span className="text-warning">&quot;{value}&quot;</span>;
  if (Array.isArray(value))
    return (
      <span className="text-muted-foreground">
        [
        {value.map((v, i) => (
          <span key={i}>
            {i > 0 && ", "}
            {renderValue(v)}
          </span>
        ))}
        ]
      </span>
    );
  return <span className="text-muted-foreground font-mono">{JSON.stringify(value)}</span>;
}

/**
 * Renderer par défaut pour les types de challenges non supportés.
 * Affiche les visual_data dans une Card avec formatage typographique.
 */
export function DefaultRenderer({ visualData, className }: DefaultRendererProps) {
  const [showRaw, setShowRaw] = useState(false);

  if (!visualData) return null;

  const isString = typeof visualData === "string";
  const dataType = isString ? "text" : "json";

  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
      <CardHeader className="pb-2 flex-row items-center justify-between space-y-0">
        <CardTitle className="text-sm font-semibold flex items-center gap-2">
          {isString ? (
            <Type className="h-4 w-4 text-primary" />
          ) : (
            <FileJson className="h-4 w-4 text-primary" />
          )}
          Données visuelles
          <Badge variant="outline" className="text-[10px] px-1.5 py-0 font-mono">
            {dataType}
          </Badge>
        </CardTitle>
        {!isString && (
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors underline-offset-2 hover:underline"
          >
            {showRaw ? "Vue structurée" : "Vue JSON"}
          </button>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        {isString ? (
          <div className="text-foreground whitespace-pre-wrap break-words leading-relaxed">
            {visualData as unknown as string}
          </div>
        ) : showRaw ? (
          <pre className="text-xs font-mono whitespace-pre-wrap break-words overflow-x-auto bg-muted/40 border border-border/50 p-3 rounded-md leading-relaxed">
            {JSON.stringify(visualData, null, 2)}
          </pre>
        ) : (
          <div className="space-y-1.5">
            {Object.entries(visualData).map(([key, value]) => (
              <div key={key} className="flex gap-2 border-l-2 border-primary/30 pl-3 py-0.5">
                <span className="text-xs font-semibold text-primary shrink-0">{key}:</span>
                <span className="text-sm">{renderValue(value)}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
