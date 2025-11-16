'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Grid3x3, MousePointerClick } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

interface PatternRendererProps {
  visualData: any;
  className?: string | undefined;
  onAnswerChange?: ((answer: string) => void) | undefined;
}

/**
 * Renderer pour les défis de type PATTERN.
 * Affiche une grille interactive pour identifier les motifs.
 */
export function PatternRenderer({ visualData, className, onAnswerChange }: PatternRendererProps) {
  // Parser les données de pattern
  const grid = visualData?.grid || visualData?.pattern || visualData?.matrix || [];
  const gridSize = visualData?.size || Math.sqrt(grid.length) || 3;
  const [selectedCells, setSelectedCells] = useState<Set<number>>(new Set());
  const [patternAnswer, setPatternAnswer] = useState<string>('');

  const toggleCell = (index: number) => {
    const newSelected = new Set(selectedCells);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedCells(newSelected);
  };

  // Si grid est un tableau 1D, le convertir en 2D
  const grid2D = Array.isArray(grid[0]) 
    ? grid 
    : Array.from({ length: gridSize }, (_, i) => 
        grid.slice(i * gridSize, (i + 1) * gridSize)
      );

  if (!grid || grid.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ''}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun pattern disponible
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`bg-card border-primary/20 ${className || ''}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Grid3x3 className="h-5 w-5 text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Grille de pattern</h4>
            <span className="text-xs text-muted-foreground ml-auto">
              Cliquez sur les cellules pour les sélectionner
            </span>
          </div>
          
          <div className="flex justify-center">
            <div 
              className="grid gap-1 p-2 bg-muted/30 rounded-lg"
              style={{ gridTemplateColumns: `repeat(${grid2D[0]?.length || gridSize}, minmax(0, 1fr))` }}
            >
              {grid2D.flat().map((cell: any, index: number) => {
                const isSelected = selectedCells.has(index);
                const cellValue = typeof cell === 'object' ? cell.value || cell.label || '?' : String(cell);
                
                return (
                  <motion.button
                    key={index}
                    className={`
                      w-12 h-12 rounded border-2 font-semibold text-sm
                      transition-all flex items-center justify-center
                      ${isSelected 
                        ? 'bg-primary text-primary-foreground border-primary shadow-lg' 
                        : 'bg-card text-foreground border-primary/30 hover:border-primary/50 hover:bg-primary/10'
                      }
                    `}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => toggleCell(index)}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.02 }}
                  >
                    {cellValue}
                  </motion.button>
                );
              })}
            </div>
          </div>

          {selectedCells.size > 0 && (
            <div className="text-xs text-center text-muted-foreground">
              {selectedCells.size} cellule{selectedCells.size > 1 ? 's' : ''} sélectionnée{selectedCells.size > 1 ? 's' : ''}
            </div>
          )}

          {/* Zone de réponse pour identifier le pattern */}
          {onAnswerChange && (
            <div className="space-y-2 pt-2 border-t border-primary/20">
              <label className="text-sm font-medium text-foreground">
                Quel est le pattern identifié ?
              </label>
              <input
                type="text"
                value={patternAnswer}
                onChange={(e) => {
                  const value = e.target.value;
                  setPatternAnswer(value);
                  if (onAnswerChange) {
                    onAnswerChange(value);
                  }
                }}
                placeholder="Décrivez le pattern..."
                className="w-full px-3 py-2 rounded-lg border-2 border-primary/30 bg-card text-foreground focus:border-primary focus:outline-none"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

