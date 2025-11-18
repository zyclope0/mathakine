'use client';

import { useEffect, useState } from 'react';
import { Lightbulb, Key, HelpCircle } from 'lucide-react';

interface RiddleRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les énigmes (riddles).
 * Affiche les indices, clés de résolution ou éléments visuels de manière intuitive.
 */
export function RiddleRenderer({ visualData, className = '' }: RiddleRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Extraire les données structurées
  const clues = visualData.clues || visualData.indices || [];
  const hints = visualData.hints || [];
  const keyElements = visualData.key_elements || visualData.elements || [];
  const context = visualData.context || visualData.scenario || '';
  const riddle = visualData.riddle || visualData.question || '';

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Contexte ou scénario */}
      {context && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <HelpCircle className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Contexte</h4>
          </div>
          <p className="text-muted-foreground leading-relaxed">{context}</p>
        </div>
      )}

      {/* Énigme principale (si différente de la question) */}
      {riddle && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
          <p className="text-foreground font-medium italic">{riddle}</p>
        </div>
      )}

      {/* Indices visuels */}
      {clues.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="h-5 w-5 text-yellow-500" />
            <h4 className="font-semibold text-foreground">Indices</h4>
          </div>
          <div className="space-y-2">
            {clues.map((clue: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                {typeof clue === 'string' ? (
                  <p className="text-foreground">{clue}</p>
                ) : (
                  <div>
                    {clue.title && (
                      <p className="font-medium text-primary mb-1">{clue.title}</p>
                    )}
                    {clue.description && (
                      <p className="text-muted-foreground text-sm">{clue.description}</p>
                    )}
                    {clue.value && (
                      <p className="text-foreground mt-1">{clue.value}</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Éléments clés */}
      {keyElements.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Key className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Éléments importants</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {keyElements.map((element: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                {typeof element === 'string' ? (
                  <p className="text-foreground font-medium">{element}</p>
                ) : (
                  <div>
                    {element.name && (
                      <p className="font-medium text-foreground">{element.name}</p>
                    )}
                    {element.value !== undefined && (
                      <p className="text-muted-foreground text-sm mt-1">{element.value}</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback : afficher toutes les données structurées */}
      {!context && !riddle && clues.length === 0 && keyElements.length === 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-2">
            {Object.entries(visualData).map(([key, value]) => {
              if (Array.isArray(value) && value.length > 0) {
                return (
                  <div key={key} className="space-y-1">
                    <p className="text-sm font-semibold text-primary capitalize">
                      {key.replace(/_/g, ' ')}:
                    </p>
                    <div className="pl-3 space-y-1">
                      {value.map((item: any, i: number) => (
                        <p key={i} className="text-sm text-foreground">
                          • {typeof item === 'object' ? JSON.stringify(item) : String(item)}
                        </p>
                      ))}
                    </div>
                  </div>
                );
              }
              if (value && typeof value === 'object') {
                return (
                  <div key={key} className="space-y-1">
                    <p className="text-sm font-semibold text-primary capitalize">
                      {key.replace(/_/g, ' ')}:
                    </p>
                    <pre className="text-xs text-muted-foreground font-mono pl-3">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  </div>
                );
              }
              return (
                <div key={key} className="flex gap-2">
                  <span className="text-sm font-semibold text-primary capitalize">
                    {key.replace(/_/g, ' ')}:
                  </span>
                  <span className="text-sm text-foreground">{String(value)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

