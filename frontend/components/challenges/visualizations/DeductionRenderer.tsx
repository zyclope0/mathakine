'use client';

import { useEffect, useState } from 'react';
import { Users, ArrowRight, Calendar } from 'lucide-react';

interface DeductionRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les défis de déduction logique.
 * Affiche les entités, leurs attributs et les relations entre elles.
 */
export function DeductionRenderer({ visualData, className = '' }: DeductionRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Extraire les données structurées
  const friends = visualData.friends || [];
  const ages = visualData.ages || [];
  const relationships = visualData.relationships || [];
  const entities = visualData.entities || [];
  const attributes = visualData.attributes || {};
  const rules = visualData.rules || relationships || [];

  // Cas 1 : Données de type "friends + ages + relationships"
  if (friends.length > 0 && ages.length > 0) {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Liste des personnes */}
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Personnes et âges</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {friends.map((friend: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                <div className="font-medium text-foreground">{friend}</div>
                {ages[index] && (
                  <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                    <Calendar className="h-3 w-3" />
                    <span>{ages[index]} ans</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Relations logiques */}
        {relationships.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ArrowRight className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">Relations</h4>
            </div>
            <div className="space-y-2">
              {relationships.map((rel: any, index: number) => (
                <div
                  key={index}
                  className="bg-background/50 border border-border rounded-md p-3 flex items-center gap-2 hover:border-primary/50 transition-colors"
                >
                  <span className="font-medium text-primary">{rel.name || rel.subject}</span>
                  <span className="text-muted-foreground text-sm">{rel.relation || 'est'}</span>
                  <span className="font-medium text-foreground">{rel.target || rel.object}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Cas 2 : Données génériques avec entités et attributs
  if (entities.length > 0) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Entités</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {entities.map((entity: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                <div className="font-medium text-foreground">{entity}</div>
                {attributes[entity] && (
                  <div className="text-sm text-muted-foreground mt-1">
                    {typeof attributes[entity] === 'object'
                      ? Object.entries(attributes[entity]).map(([key, value]) => (
                          <div key={key}>
                            {key}: {String(value)}
                          </div>
                        ))
                      : attributes[entity]}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Règles logiques */}
        {rules.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ArrowRight className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">Règles</h4>
            </div>
            <div className="space-y-2">
              {rules.map((rule: any, index: number) => (
                <div
                  key={index}
                  className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
                >
                  {typeof rule === 'string' ? (
                    <span className="text-foreground">{rule}</span>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-primary">{rule.name || rule.subject}</span>
                      <span className="text-muted-foreground text-sm">{rule.relation || 'est'}</span>
                      <span className="font-medium text-foreground">{rule.target || rule.object}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fallback : afficher les données brutes de manière structurée
  return (
    <div className={`bg-card/50 border border-border rounded-lg p-4 ${className}`}>
      <div className="text-sm text-muted-foreground">
        <pre className="whitespace-pre-wrap break-words font-mono text-xs">
          {JSON.stringify(visualData, null, 2)}
        </pre>
      </div>
    </div>
  );
}

