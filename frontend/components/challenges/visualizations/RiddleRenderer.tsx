'use client';

import { useEffect, useState } from 'react';
import { Lightbulb, Key, HelpCircle, Grid3x3, Info } from 'lucide-react';
import { motion } from 'framer-motion';

interface RiddleRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les énigmes (riddles).
 * Affiche les indices, clés de résolution, grilles mathématiques ou éléments visuels.
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
  const context = visualData.context || visualData.scenario || visualData.scene || '';
  const riddle = visualData.riddle || visualData.question || '';
  const description = visualData.description || '';
  const size = visualData.size;

  // Énigme type "riddle" avec pots et plaque (ex: coffre du jardinier)
  const parseIfNeeded = (val: unknown): unknown => {
    if (typeof val === 'string') {
      try { return JSON.parse(val) as unknown; } catch { return val; }
    }
    return val;
  };
  const rawPots = parseIfNeeded(visualData.pots);
  const pots = Array.isArray(rawPots) ? rawPots : [];
  const rawPlaque = parseIfNeeded(visualData.plaque);
  const plaque = rawPlaque && typeof rawPlaque === 'object' && rawPlaque !== null ? rawPlaque as { text_lines?: unknown[] } : null;
  const plaqueLines = plaque?.text_lines && Array.isArray(plaque.text_lines) ? plaque.text_lines : [];
  const asciiArt = typeof visualData.ascii_art === 'string' ? visualData.ascii_art.trim() : '';

  // Détecter les grilles (mathématiques, patterns, etc.)
  const grid = visualData.grid || visualData.pattern || visualData.matrix || visualData.rows || null;
  const hasGrid = grid && Array.isArray(grid) && grid.length > 0;

  // Convertir la grille en 2D si nécessaire
  const grid2D = hasGrid ? (
    Array.isArray(grid[0]) 
      ? grid 
      : Array.from({ length: size || Math.ceil(Math.sqrt(grid.length)) }, (_, i) => 
          grid.slice(i * (size || Math.ceil(Math.sqrt(grid.length))), (i + 1) * (size || Math.ceil(Math.sqrt(grid.length))))
        )
  ) : [];

  // Vérifier si on a des données significatives à afficher
  const hasContent = context || riddle || description || clues.length > 0 || keyElements.length > 0 || hasGrid || pots.length > 0 || plaqueLines.length > 0 || !!asciiArt;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Description de l'énigme */}
      {description && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Info className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Description</h4>
          </div>
          <p className="text-muted-foreground leading-relaxed">{description}</p>
        </div>
      )}

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

      {/* Grille mathématique / Pattern */}
      {hasGrid && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Grid3x3 className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Grille</h4>
            {size && (
              <span className="text-xs text-muted-foreground ml-auto">
                Taille : {size}x{grid2D.length}
              </span>
            )}
          </div>
          
          <div className="flex justify-center">
            <div 
              className="grid gap-1 p-3 bg-muted/30 rounded-lg"
              style={{ gridTemplateColumns: `repeat(${grid2D[0]?.length || 3}, minmax(0, 1fr))` }}
            >
              {grid2D.flat().map((cell: any, index: number) => {
                const cellValue = typeof cell === 'object' 
                  ? cell.value || cell.label || '?' 
                  : String(cell);
                const isUnknown = cellValue === '?' || cellValue === '??' || cellValue.includes('?');
                
                return (
                  <motion.div
                    key={index}
                    className={`
                      w-14 h-14 rounded-lg border-2 font-bold text-lg
                      flex items-center justify-center
                      ${isUnknown 
                        ? 'bg-primary/20 text-primary border-primary border-dashed' 
                        : 'bg-card text-foreground border-primary/30'
                      }
                    `}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.03 }}
                  >
                    {isUnknown ? (
                      <span className="text-2xl animate-pulse">?</span>
                    ) : (
                      cellValue
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
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

      {/* Pots (énigme type coffre/jardinier) */}
      {pots.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Key className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Pots</h4>
          </div>
          <div className="space-y-2">
            {pots.map((pot: any, index: number) => {
              const label = pot.label ?? `Pot ${index + 1}`;
              const cluesList = Array.isArray(pot.visible_clues) ? pot.visible_clues : [];
              return (
                <div
                  key={index}
                  className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
                >
                  <p className="font-medium text-primary mb-1">Pot {label}</p>
                  {cluesList.length > 0 ? (
                    <ul className="list-disc list-inside space-y-1 text-foreground text-sm">
                      {cluesList.map((c: string, i: number) => (
                        <li key={i}>{typeof c === 'string' ? c : String(c)}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Plaque (équations, contraintes) */}
      {plaqueLines.length > 0 && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Info className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Plaque</h4>
          </div>
          <ul className="space-y-1.5 text-foreground font-mono text-sm">
            {plaqueLines.map((line: unknown, index: number) => (
              <li key={index} className="flex items-center gap-2">
                <span className="text-primary">—</span>
                {typeof line === 'string' ? line : String(line)}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Schéma ASCII (représentation visuelle) - masqué si pots + plaque déjà affichés pour éviter la redondance */}
      {asciiArt && pots.length === 0 && plaqueLines.length === 0 && (
        <div className="bg-muted/30 border border-border rounded-lg p-4 overflow-x-auto">
          <pre className="text-xs text-muted-foreground font-mono whitespace-pre leading-relaxed">
            {asciiArt}
          </pre>
        </div>
      )}

      {/* Hints (indices supplémentaires) */}
      {hints.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="h-5 w-5 text-amber-500" />
            <h4 className="font-semibold text-foreground">Astuces</h4>
          </div>
          <div className="space-y-2">
            {hints.map((hint: any, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 text-sm text-muted-foreground"
              >
                <span className="font-semibold text-amber-500">#{index + 1}</span> {typeof hint === 'string' ? hint : hint.text || JSON.stringify(hint)}
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
      {!hasContent && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-2">
            {Object.entries(visualData).map(([key, value]) => {
              // Skip les clés déjà traitées
              if (['grid', 'pattern', 'matrix', 'rows', 'clues', 'indices', 'hints', 
                   'key_elements', 'elements', 'context', 'scenario', 'scene', 
                   'riddle', 'question', 'description', 'size', 'pots', 'plaque', 
                   'type', 'ascii_art'].includes(key)) {
                return null;
              }
              
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

