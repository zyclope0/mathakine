"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Circle, Grid3x3, Square, Triangle } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

const SHAPE_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  cercle: Circle,
  circle: Circle,
  triangle: Triangle,
  carré: Square,
  square: Square,
};

function ShapeIcon({ type }: { type: string }) {
  const Icon = SHAPE_ICONS[type?.toLowerCase?.()];
  if (!Icon) return <span>{type}</span>;
  return <Icon className="h-7 w-7 stroke-2 text-current" />;
}

interface PatternRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
  onAnswerChange?: ((answer: string) => void) | undefined;
}

/**
 * Renderer pour les défis de type PATTERN.
 * Affiche une grille interactive pour identifier les motifs.
 */
export function PatternRenderer({ visualData, className, onAnswerChange }: PatternRendererProps) {
  // Parser les données de pattern
  const grid = Array.isArray(visualData?.grid)
    ? visualData.grid
    : Array.isArray(visualData?.pattern)
      ? visualData.pattern
      : Array.isArray(visualData?.matrix)
        ? visualData.matrix
        : [];
  const gridSize: number =
    typeof visualData?.size === "number" ? visualData.size : Math.sqrt(grid.length) || 3;
  const [selectedCells, setSelectedCells] = useState<Set<number>>(new Set());
  const [patternAnswer, setPatternAnswer] = useState<string>("");

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
  const grid2D: unknown[][] = Array.isArray(grid[0])
    ? (grid as unknown[][])
    : Array.from({ length: gridSize }, (_, i) =>
        (grid as unknown[]).slice(i * gridSize, (i + 1) * gridSize)
      );

  const questionCount = grid2D
    .flat()
    .filter((c: unknown) => c === "?" || (typeof c === "string" && c.includes("?"))).length;

  const flatGrid = grid2D.flat();
  const usesShapes = flatGrid.some((c: unknown) => {
    const v =
      typeof c === "object" && c !== null
        ? ((c as Record<string, unknown>).value ?? (c as Record<string, unknown>).label)
        : String(c ?? "");
    return ["cercle", "circle", "triangle", "carré", "square"].includes(String(v).toLowerCase());
  });
  const placeholder = usesShapes
    ? "Ex : cercle, triangle ou carré"
    : questionCount > 1
      ? "Ex : O O X O ou O, O, X, O (espaces ou virgules)"
      : "Ex : X ou O (le symbole manquant)";

  if (!grid || grid.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ""}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun pattern disponible
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
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
              style={{
                gridTemplateColumns: `repeat(${grid2D[0] != null && Array.isArray(grid2D[0]) ? grid2D[0].length : gridSize}, minmax(0, 1fr))`,
              }}
            >
              {grid2D.flat().map((cell: unknown, index: number) => {
                const isSelected = selectedCells.has(index);
                const cellValue =
                  typeof cell === "object" && cell !== null
                    ? String(
                        (cell as Record<string, unknown>).value ??
                          (cell as Record<string, unknown>).label ??
                          "?"
                      )
                    : String(cell);

                return (
                  <motion.button
                    key={index}
                    className={`
                      w-12 h-12 rounded border-2 font-semibold text-sm
                      transition-all flex items-center justify-center
                      ${
                        cellValue === "?"
                          ? "bg-primary/20 text-primary border-primary border-dashed animate-pulse"
                          : isSelected
                            ? "bg-primary text-primary-foreground border-primary shadow-lg"
                            : "bg-card text-foreground border-primary/30 hover:border-primary/50 hover:bg-primary/10"
                      }
                    `}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => toggleCell(index)}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.02 }}
                  >
                    {cellValue === "?" ? (
                      <span className="text-lg font-bold">?</span>
                    ) : SHAPE_ICONS[cellValue?.toLowerCase?.()] ? (
                      <ShapeIcon type={cellValue} />
                    ) : (
                      cellValue
                    )}
                  </motion.button>
                );
              })}
            </div>
          </div>

          {selectedCells.size > 0 && (
            <div className="text-xs text-center text-muted-foreground">
              {selectedCells.size} cellule{selectedCells.size > 1 ? "s" : ""} sélectionnée
              {selectedCells.size > 1 ? "s" : ""}
            </div>
          )}

          {/* Zone de réponse pour identifier le pattern */}
          {onAnswerChange && (
            <div className="space-y-2 pt-2 border-t border-primary/20">
              <label className="text-sm font-medium text-foreground">
                {questionCount > 1
                  ? `Quels ${usesShapes ? "formes" : "symboles"} remplacent les ${questionCount} « ? » ? (ordre ligne par ligne)`
                  : usesShapes
                    ? "Quelle forme remplace le « ? » ?"
                    : "Quel symbole remplace le « ? » ?"}
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
                placeholder={placeholder}
                className="w-full px-3 py-2 rounded-lg border-2 border-primary/30 bg-card text-foreground focus:border-primary focus:outline-none"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
