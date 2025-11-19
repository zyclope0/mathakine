'use client';

import { useEffect, useState } from 'react';
import { Code, Terminal, FileCode, CheckCircle2, XCircle } from 'lucide-react';

interface CodingRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les défis de codage/programmation.
 * Affiche du code, des exemples d'entrée/sortie, et des contraintes.
 */
export function CodingRenderer({ visualData, className = '' }: CodingRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Extraire les données structurées
  const code = visualData.code || visualData.snippet || '';
  const language = visualData.language || visualData.lang || 'python';
  const examples = visualData.examples || visualData.test_cases || [];
  const input = visualData.input || '';
  const output = visualData.output || '';
  const expectedOutput = visualData.expected_output || visualData.expected || '';
  const constraints = visualData.constraints || [];
  const hints = visualData.hints || [];
  const question = visualData.question || '';

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Question */}
      {question && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-3">
          <p className="text-foreground font-medium">{question}</p>
        </div>
      )}

      {/* Code snippet */}
      {code && (
        <div className="bg-card/50 border border-border rounded-lg overflow-hidden">
          <div className="flex items-center gap-2 bg-muted px-4 py-2 border-b border-border">
            <FileCode className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">Code</span>
            {language && (
              <span className="ml-auto text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                {language}
              </span>
            )}
          </div>
          <pre className="p-4 overflow-x-auto text-sm">
            <code className="text-foreground font-mono">{code}</code>
          </pre>
        </div>
      )}

      {/* Exemples d'entrée/sortie */}
      {examples.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Terminal className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Exemples</h4>
          </div>
          <div className="space-y-3">
            {examples.map((example: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md overflow-hidden"
              >
                <div className="bg-muted/50 px-3 py-1 border-b border-border">
                  <span className="text-xs font-semibold text-muted-foreground">
                    Exemple {index + 1}
                  </span>
                </div>
                <div className="p-3 space-y-2">
                  {example.input !== undefined && (
                    <div>
                      <span className="text-xs font-semibold text-muted-foreground">Entrée :</span>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                        {typeof example.input === 'object' 
                          ? JSON.stringify(example.input, null, 2) 
                          : String(example.input)}
                      </pre>
                    </div>
                  )}
                  {example.output !== undefined && (
                    <div>
                      <span className="text-xs font-semibold text-muted-foreground">Sortie :</span>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                        {typeof example.output === 'object' 
                          ? JSON.stringify(example.output, null, 2) 
                          : String(example.output)}
                      </pre>
                    </div>
                  )}
                  {example.explanation && (
                    <div className="text-xs text-muted-foreground italic pt-1 border-t border-border">
                      {example.explanation}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Entrée/Sortie simple */}
      {(input || output || expectedOutput) && examples.length === 0 && (
        <div className="grid gap-3 md:grid-cols-2">
          {input && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Terminal className="h-4 w-4 text-primary" />
                <h5 className="text-sm font-semibold text-foreground">Entrée</h5>
              </div>
              <pre className="p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                {typeof input === 'object' ? JSON.stringify(input, null, 2) : String(input)}
              </pre>
            </div>
          )}
          {(output || expectedOutput) && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <h5 className="text-sm font-semibold text-foreground">Sortie attendue</h5>
              </div>
              <pre className="p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                {typeof (output || expectedOutput) === 'object' 
                  ? JSON.stringify(output || expectedOutput, null, 2) 
                  : String(output || expectedOutput)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Contraintes */}
      {constraints.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <XCircle className="h-5 w-5 text-orange-500" />
            <h4 className="font-semibold text-foreground">Contraintes</h4>
          </div>
          <ul className="space-y-1.5 text-sm">
            {constraints.map((constraint: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-orange-500 mt-0.5">•</span>
                <span className="text-muted-foreground">{constraint}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Indices */}
      {hints.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Code className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Indices</h4>
          </div>
          <div className="space-y-2">
            {hints.map((hint: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 text-sm text-muted-foreground"
              >
                <span className="font-semibold text-primary">Indice {index + 1} :</span> {hint}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback : afficher toutes les données structurées */}
      {!code && !question && examples.length === 0 && !input && !output && constraints.length === 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Code className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Données du défi</h4>
          </div>
          <div className="space-y-2">
            {Object.entries(visualData).map(([key, value]) => {
              if (Array.isArray(value) && value.length > 0) {
                return (
                  <div key={key} className="space-y-1">
                    <p className="text-sm font-semibold text-primary capitalize">
                      {key.replace(/_/g, ' ')} :
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
              return (
                <div key={key} className="flex gap-2">
                  <span className="text-sm font-semibold text-primary capitalize">
                    {key.replace(/_/g, ' ')} :
                  </span>
                  <span className="text-sm text-foreground">
                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

