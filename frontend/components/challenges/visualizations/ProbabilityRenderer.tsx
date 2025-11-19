'use client';

import { useEffect, useState } from 'react';
import { Dices, Percent, TrendingUp } from 'lucide-react';

interface ProbabilityRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les défis de probabilités.
 * Affiche des événements, probabilités, et diagrammes de chances.
 */
export function ProbabilityRenderer({ visualData, className = '' }: ProbabilityRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Extraire les données structurées
  const events = visualData.events || [];
  const probabilities = visualData.probabilities || visualData.probs || [];
  const outcomes = visualData.outcomes || [];
  const totalOutcomes = visualData.total_outcomes || visualData.total || 0;
  const favorableOutcomes = visualData.favorable_outcomes || visualData.favorable || 0;
  const question = visualData.question || '';
  const context = visualData.context || '';

  // Calculer la probabilité si on a les données
  const calculatedProbability = totalOutcomes > 0 
    ? ((favorableOutcomes / totalOutcomes) * 100).toFixed(2) 
    : null;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Contexte */}
      {context && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <p className="text-sm text-muted-foreground leading-relaxed">{context}</p>
        </div>
      )}

      {/* Question */}
      {question && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-3">
          <p className="text-foreground font-medium">{question}</p>
        </div>
      )}

      {/* Événements */}
      {events.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Dices className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Événements possibles</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {events.map((event: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                {typeof event === 'string' ? (
                  <p className="text-foreground font-medium">{event}</p>
                ) : (
                  <div>
                    {event.name && (
                      <p className="font-medium text-foreground">{event.name}</p>
                    )}
                    {event.probability !== undefined && (
                      <p className="text-xs text-muted-foreground mt-1">
                        <Percent className="h-3 w-3 inline mr-1" />
                        {event.probability}%
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Résultats possibles */}
      {outcomes.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Résultats possibles</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {outcomes.map((outcome: any, index: number) => (
              <div
                key={index}
                className="bg-primary/10 border border-primary/30 rounded-md px-3 py-2 text-sm font-medium text-foreground"
              >
                {typeof outcome === 'object' ? outcome.name || outcome.value : outcome}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Probabilités */}
      {probabilities.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Percent className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Probabilités</h4>
          </div>
          <div className="space-y-2">
            {probabilities.map((prob: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3"
              >
                {typeof prob === 'string' || typeof prob === 'number' ? (
                  <div className="flex items-center gap-2">
                    <Percent className="h-4 w-4 text-primary" />
                    <span className="text-foreground font-medium">{prob}%</span>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {prob.event && (
                      <p className="text-sm font-medium text-foreground">{prob.event}</p>
                    )}
                    <div className="flex items-center gap-3">
                      {prob.value !== undefined && (
                        <span className="text-lg font-semibold text-primary">{prob.value}%</span>
                      )}
                      {prob.fraction && (
                        <code className="text-xs bg-muted px-2 py-1 rounded text-muted-foreground">
                          {prob.fraction}
                        </code>
                      )}
                    </div>
                    {prob.description && (
                      <p className="text-xs text-muted-foreground">{prob.description}</p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Calcul de probabilité */}
      {(totalOutcomes > 0 || favorableOutcomes > 0) && (
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Calcul</h4>
          </div>
          <div className="space-y-2 text-sm">
            {favorableOutcomes > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Cas favorables :</span>
                <code className="bg-background px-2 py-1 rounded font-semibold text-foreground">
                  {favorableOutcomes}
                </code>
              </div>
            )}
            {totalOutcomes > 0 && (
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Cas possibles :</span>
                <code className="bg-background px-2 py-1 rounded font-semibold text-foreground">
                  {totalOutcomes}
                </code>
              </div>
            )}
            {calculatedProbability && (
              <div className="flex items-center gap-2 pt-2 border-t border-border">
                <span className="text-muted-foreground">Probabilité :</span>
                <code className="bg-primary/20 border border-primary/30 px-3 py-1 rounded font-bold text-primary text-lg">
                  {calculatedProbability}%
                </code>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Fallback : afficher toutes les données structurées */}
      {!context && !question && events.length === 0 && probabilities.length === 0 && outcomes.length === 0 && totalOutcomes === 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-2">
            {Object.entries(visualData).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <span className="text-sm font-semibold text-primary capitalize">
                  {key.replace(/_/g, ' ')} :
                </span>
                <span className="text-sm text-foreground">
                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

