"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Eye, FlipHorizontal, RotateCw, ZoomIn, ZoomOut, ScanSearch } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

interface VisualRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
}

/**
 * Fonction helper pour parser une forme avec sa couleur
 */
function parseShapeWithColor(shapeText: string): {
  shape: string;
  color: string | null;
  isQuestion: boolean;
} {
  const text = shapeText.toLowerCase().trim();

  // Détecter si c'est une question
  const isQuestion = text.includes("?");

  // Map des couleurs français/anglais vers CSS (utilisé aussi pour layout.color)
  const colorMap: Record<string, string> = {
    rouge: "#ef4444",
    red: "#ef4444",
    bleu: "#3b82f6",
    blue: "#3b82f6",
    vert: "#22c55e",
    green: "#22c55e",
    jaune: "#eab308",
    yellow: "#eab308",
    orange: "#f97316",
    violet: "#a855f7",
    purple: "#a855f7",
    rose: "#ec4899",
    pink: "#ec4899",
    noir: "#1f2937",
    black: "#1f2937",
    blanc: "#f9fafb",
    white: "#f9fafb",
    gris: "#6b7280",
    gray: "#6b7280",
  };

  // Trouver la couleur dans le texte
  let detectedColor: string | null = null;
  for (const [colorName, colorValue] of Object.entries(colorMap)) {
    if (text.includes(colorName)) {
      detectedColor = colorValue;
      break;
    }
  }

  // Map des formes
  const shapeMap: Record<string, string> = {
    triangle: "triangle",
    rectangle: "rectangle",
    cercle: "cercle",
    circle: "cercle",
    carré: "carré",
    carre: "carré",
    square: "carré",
    losange: "losange",
    diamond: "losange",
    étoile: "étoile",
    etoile: "étoile",
    star: "étoile",
    hexagone: "hexagone",
    hexagon: "hexagone",
    pentagone: "pentagone",
    pentagon: "pentagone",
  };

  // Trouver la forme dans le texte
  let detectedShape = "unknown";
  for (const [shapeName, shapeValue] of Object.entries(shapeMap)) {
    if (text.includes(shapeName)) {
      detectedShape = shapeValue;
      break;
    }
  }

  return { shape: detectedShape, color: detectedColor, isQuestion };
}

/**
 * Résout un nom de couleur (ex: "bleu", "rouge") vers une valeur CSS
 */
function resolveColor(colorName: string | undefined | null): string | null {
  if (!colorName || typeof colorName !== "string" || colorName === "?") return null;
  const colorMap: Record<string, string> = {
    rouge: "#ef4444",
    red: "#ef4444",
    bleu: "#3b82f6",
    blue: "#3b82f6",
    vert: "#22c55e",
    green: "#22c55e",
    jaune: "#eab308",
    yellow: "#eab308",
    orange: "#f97316",
    violet: "#a855f7",
    purple: "#a855f7",
    rose: "#ec4899",
    pink: "#ec4899",
    noir: "#1f2937",
    black: "#1f2937",
    blanc: "#f9fafb",
    white: "#f9fafb",
    gris: "#6b7280",
    gray: "#6b7280",
  };
  const key = colorName.toLowerCase().trim();
  return colorMap[key] ?? null;
}

/**
 * Fonction helper pour obtenir l'icône d'une forme
 */
function getShapeIcon(shape: string): string {
  const shapeIconMap: Record<string, string> = {
    triangle: "▲",
    rectangle: "■",
    cercle: "●",
    circle: "●",
    carré: "■",
    square: "■",
    losange: "◆",
    diamond: "◆",
    étoile: "★",
    star: "★",
    hexagone: "⬡",
    pentagone: "⬠",
  };

  // Parser la forme pour extraire le nom de base
  const { shape: baseShape } = parseShapeWithColor(shape);
  return shapeIconMap[baseShape] || shape.charAt(0).toUpperCase();
}

type SymmetryCell = Record<string, unknown>;

/**
 * Ordre stable : ``position`` numérique si présent, sinon ordre d'origine dans le tableau.
 * (Contrat IA9 : layout[{ side, ... }] — nombre variable d'items par côté.)
 */
export function stableSortSymmetryLayoutCells(items: SymmetryCell[]): SymmetryCell[] {
  return items
    .map((item, origIdx) => ({ item, origIdx }))
    .sort((a, b) => {
      const pa =
        typeof a.item.position === "number" && !Number.isNaN(a.item.position)
          ? (a.item.position as number)
          : a.origIdx;
      const pb =
        typeof b.item.position === "number" && !Number.isNaN(b.item.position)
          ? (b.item.position as number)
          : b.origIdx;
      return pa - pb;
    })
    .map(({ item }) => item);
}

/** Export test : partition gauche / droite selon contrat canonique. */
export function partitionSymmetryLayoutBySide(layout: SymmetryCell[]): {
  left: SymmetryCell[];
  right: SymmetryCell[];
} {
  const left = stableSortSymmetryLayoutCells(
    layout.filter((item) => String(item.side ?? "").toLowerCase() === "left")
  );
  const right = stableSortSymmetryLayoutCells(
    layout.filter((item) => String(item.side ?? "").toLowerCase() === "right")
  );
  return { left, right };
}

/** Scale selon le nombre de cellules (évite débordement 6+ par côté). */
function getDefaultScale(visualData: Record<string, unknown> | null): number {
  if (!visualData) return 1;
  const p =
    typeof visualData === "string"
      ? (() => {
          try {
            return JSON.parse(visualData) as Record<string, unknown>;
          } catch {
            return {};
          }
        })()
      : visualData;
  const layout = Array.isArray(p?.layout) ? (p.layout as SymmetryCell[]) : [];
  const isSym = p?.type === "symmetry" || !!p?.symmetry_line;
  if (!isSym || layout.length === 0) return 1;
  const { left, right } = partitionSymmetryLayoutBySide(layout);
  const n = Math.max(left.length, right.length);
  if (n >= 8) return 0.5;
  if (n >= 6) return 0.55;
  if (n >= 4) return 0.65;
  return 1;
}

function SymmetryMirrorCell({
  item,
  side,
  idx,
}: {
  item: SymmetryCell;
  side: "left" | "right";
  idx: number;
}) {
  const color = resolveColor(typeof item.color === "string" ? item.color : undefined);
  const isQuestion = Boolean(item.question) || String(item.shape ?? "").includes("?");
  const fromLeft = side === "left";
  return (
    <motion.div
      className={`aspect-square min-w-0 border-2 rounded-lg flex items-center justify-center font-semibold text-base sm:text-lg ${
        isQuestion
          ? "border-dashed border-primary/70 bg-primary/5 animate-pulse"
          : fromLeft
            ? "border-primary bg-primary/10"
            : "border-primary bg-primary/10"
      }`}
      initial={{ opacity: 0, x: fromLeft ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: idx * 0.08 }}
    >
      {isQuestion ? (
        <span className="text-xl sm:text-2xl font-bold text-primary">?</span>
      ) : (
        <span style={color ? { color } : undefined}>{getShapeIcon(String(item.shape ?? ""))}</span>
      )}
    </motion.div>
  );
}

/**
 * Renderer pour les défis de type VISUAL/SPATIAL.
 * Affiche des formes, rotations et manipulations spatiales.
 */
export function VisualRenderer({ visualData, className }: VisualRendererProps) {
  const [rotation, setRotation] = useState(0);
  const [scale, setScale] = useState(() => getDefaultScale(visualData));
  const [flipped, setFlipped] = useState(false);

  // Parser les données visuelles avec gestion robuste
  const parseVisualData = (data: unknown) => {
    if (!data)
      return {
        shapes: [],
        asciiArt: null,
        layout: [],
        symmetryType: null,
        symmetryLine: null,
        description: null,
        grid: null,
        gridSize: 3,
        rawData: null,
      };

    // Si c'est une string, essayer de la parser comme JSON
    let parsed = data;
    if (typeof data === "string") {
      try {
        parsed = JSON.parse(data);
      } catch {
        // C'est peut-être de l'ASCII art directement
        return {
          shapes: [],
          asciiArt: data,
          layout: [],
          symmetryType: null,
          symmetryLine: null,
          description: null,
          grid: null,
          gridSize: 3,
          rawData: null,
        };
      }
    }

    const p = parsed as Record<string, unknown> | null;
    // Détecter si c'est une grille
    const grid = p?.grid ?? p?.matrix ?? p?.pattern;
    const gridArr = Array.isArray(grid) ? grid : null;
    const gridSizeNum =
      typeof p?.size === "number"
        ? p.size
        : gridArr && gridArr.length > 0 && Array.isArray(gridArr[0])
          ? (gridArr[0] as unknown[]).length
          : gridArr
            ? Math.ceil(Math.sqrt(gridArr.length)) || 3
            : 3;

    return {
      shapes: Array.isArray(p?.shapes)
        ? p.shapes
        : Array.isArray(p?.items)
          ? p.items
          : Array.isArray(p?.elements)
            ? p.elements
            : Array.isArray(p?.figures)
              ? p.figures
              : [],
      asciiArt: p?.ascii ?? p?.art ?? p?.content ?? p?.diagram ?? p?.visual ?? null,
      layout: Array.isArray(p?.layout) ? p.layout : [],
      symmetryType: (p?.type ?? (p?.symmetry_line ? "symmetry" : null)) as string | null,
      symmetryLine: p?.symmetry_line ?? p?.symmetryLine ?? p?.axis ?? null,
      description: (p?.description ?? p?.text ?? p?.explanation) as string | null,
      grid: grid ?? null,
      gridSize: typeof gridSizeNum === "number" ? gridSizeNum : 3,
      // Garder les données brutes seulement si aucun format reconnu
      rawData: !p?.shapes && !p?.ascii && !p?.layout && !p?.items && !grid ? parsed : null,
    };
  };

  const {
    shapes,
    asciiArt,
    layout,
    symmetryType,
    symmetryLine,
    description,
    grid,
    gridSize,
    rawData,
  } = parseVisualData(visualData);

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.1, 0.4));
  };

  const handleFitView = () => {
    setScale(getDefaultScale(visualData));
  };

  const handleFlip = () => {
    setFlipped((prev) => !prev);
  };

  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-primary" />
              <h4 className="text-sm font-semibold text-foreground">Visualisation spatiale</h4>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleRotate}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Rotation"
                aria-label="Rotation"
              >
                <RotateCw className="h-4 w-4" />
              </button>
              <button
                onClick={handleZoomIn}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Zoom avant"
                aria-label="Zoom avant"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Zoom arrière"
                aria-label="Zoom arrière"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <button
                onClick={handleFitView}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Vue d'ensemble"
                aria-label="Vue d'ensemble"
              >
                <ScanSearch className="h-4 w-4" />
              </button>
              <button
                onClick={handleFlip}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Retourner"
                aria-label="Retourner"
              >
                <FlipHorizontal className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div className="flex justify-center items-center min-h-[200px] bg-muted/30 rounded-lg p-4 w-full overflow-hidden">
            {symmetryType === "symmetry" && layout.length > 0 ? (
              <motion.div
                className="w-full max-w-full"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? "scaleX(-1)" : ""}`,
                  transformOrigin: "center",
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                {(() => {
                  const cells = layout as SymmetryCell[];
                  const { left: leftCells, right: rightCells } =
                    partitionSymmetryLayoutBySide(cells);
                  const axis = String(symmetryLine ?? "vertical").toLowerCase();
                  const isVertical = axis === "vertical" || axis === "v";

                  if (isVertical) {
                    const totalCols = leftCells.length + 1 + rightCells.length;
                    return (
                      <div
                        className="grid gap-1 sm:gap-2 w-full"
                        style={{
                          gridTemplateColumns: `repeat(${totalCols}, minmax(0, 1fr))`,
                        }}
                      >
                        {leftCells.map((item, idx) => (
                          <SymmetryMirrorCell
                            key={`sym-left-${idx}`}
                            item={item}
                            side="left"
                            idx={idx}
                          />
                        ))}
                        <div className="col-span-1 flex items-center justify-center min-h-[3rem]">
                          <div className="w-0.5 sm:w-1 h-full min-h-[2.5rem] bg-primary/50" />
                        </div>
                        {rightCells.map((item, idx) => (
                          <SymmetryMirrorCell
                            key={`sym-right-${idx}`}
                            item={item}
                            side="right"
                            idx={idx}
                          />
                        ))}
                      </div>
                    );
                  }

                  /* symmetry_line horizontal : miroir haut/bas ; côté API = left → ligne du haut, right → bas */
                  return (
                    <div className="flex flex-col gap-2 sm:gap-3 w-full items-stretch">
                      <div className="flex flex-wrap justify-center gap-1 sm:gap-2 content-start">
                        {leftCells.map((item, idx) => (
                          <SymmetryMirrorCell
                            key={`sym-top-${idx}`}
                            item={item}
                            side="left"
                            idx={idx}
                          />
                        ))}
                      </div>
                      <div className="flex justify-center py-1 px-2" aria-hidden>
                        <div className="h-0.5 sm:h-1 w-full max-w-lg rounded-full bg-primary/50" />
                      </div>
                      <div className="flex flex-wrap justify-center gap-1 sm:gap-2 content-start">
                        {rightCells.map((item, idx) => (
                          <SymmetryMirrorCell
                            key={`sym-bottom-${idx}`}
                            item={item}
                            side="right"
                            idx={idx}
                          />
                        ))}
                      </div>
                    </div>
                  );
                })()}
                {Boolean(visualData?.description) && (
                  <p className="text-xs text-muted-foreground text-center mt-4">
                    {String(visualData?.description ?? "")}
                  </p>
                )}
              </motion.div>
            ) : grid && Array.isArray(grid) && grid.length > 0 ? (
              // Rendu de grille avec formes
              <motion.div
                className="w-full flex flex-col items-center"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? "scaleX(-1)" : ""}`,
                  transformOrigin: "center",
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                <div
                  className="grid gap-2 p-4 bg-muted/20 rounded-lg"
                  style={{ gridTemplateColumns: `repeat(${gridSize}, minmax(0, 1fr))` }}
                >
                  {grid.flat().map((cell: unknown, index: number) => {
                    const cellValue =
                      typeof cell === "object" && cell !== null
                        ? String(
                            (cell as Record<string, unknown>).value ??
                              (cell as Record<string, unknown>).label ??
                              "?"
                          )
                        : String(cell);
                    const isQuestion = cellValue === "?" || cellValue.includes("?");

                    return (
                      <motion.div
                        key={index}
                        className={`
                          w-16 h-16 border-2 rounded-lg flex items-center justify-center font-semibold text-lg
                          ${
                            isQuestion
                              ? "border-dashed border-primary bg-primary/10 animate-pulse"
                              : "border-primary/40 bg-card"
                          }
                        `}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                        title={cellValue}
                      >
                        {isQuestion ? (
                          <span className="text-2xl font-bold text-primary">?</span>
                        ) : (
                          <span className="text-xl">{getShapeIcon(cellValue)}</span>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
                {/* Légende des formes */}
                <div className="flex gap-3 mt-4 text-xs text-muted-foreground">
                  {Array.from(new Set(grid.flat().filter((c: unknown) => c !== "?")))
                    .slice(0, 5)
                    .map((shape: unknown, idx: number) => (
                      <div key={idx} className="flex items-center gap-1">
                        <span className="text-base">{getShapeIcon(String(shape))}</span>
                        <span>= {String(shape)}</span>
                      </div>
                    ))}
                </div>
              </motion.div>
            ) : asciiArt ? (
              <motion.pre
                className="text-foreground font-mono text-sm whitespace-pre"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? "scaleX(-1)" : ""}`,
                  transformOrigin: "center",
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                {String(asciiArt ?? "")}
              </motion.pre>
            ) : shapes.length > 0 ? (
              <motion.div
                className="flex flex-wrap gap-4 justify-center"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? "scaleX(-1)" : ""}`,
                  transformOrigin: "center",
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                {shapes.map((shapeData: string | Record<string, unknown>, index: number) => {
                  const shapeText =
                    typeof shapeData === "string"
                      ? shapeData
                      : String(
                          (shapeData as Record<string, unknown>).label ??
                            (shapeData as Record<string, unknown>).value ??
                            index + 1
                        );
                  const { color, isQuestion } = parseShapeWithColor(shapeText);
                  const icon = getShapeIcon(shapeText);

                  return (
                    <motion.div
                      key={index}
                      className={`w-20 h-20 border-2 rounded-lg flex flex-col items-center justify-center font-semibold ${
                        isQuestion
                          ? "border-dashed border-primary animate-pulse bg-primary/10"
                          : "border-primary/40 bg-card"
                      }`}
                      initial={{ opacity: 0, scale: 0 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1 }}
                      title={shapeText}
                    >
                      {isQuestion ? (
                        <span className="text-3xl font-bold text-primary">?</span>
                      ) : (
                        <>
                          <span className="text-4xl" style={{ color: color || "currentColor" }}>
                            {icon}
                          </span>
                          {color && (
                            <span className="text-[10px] text-muted-foreground mt-1 capitalize">
                              {shapeText.split(" ").pop()}
                            </span>
                          )}
                        </>
                      )}
                    </motion.div>
                  );
                })}
              </motion.div>
            ) : rawData ? (
              // Afficher les données brutes de manière structurée
              <div className="w-full max-w-md">
                {typeof rawData === "object" ? (
                  <div className="space-y-2 text-left">
                    {Object.entries(rawData).map(([key, value]) => (
                      <div key={key} className="border-l-2 border-primary/30 pl-3 py-1">
                        <span className="text-xs font-semibold text-primary">{key}:</span>
                        <span className="text-sm text-foreground ml-2">
                          {typeof value === "object" ? JSON.stringify(value) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-foreground whitespace-pre-wrap">{String(rawData)}</p>
                )}
              </div>
            ) : description ? (
              // Afficher la description si disponible
              <div className="text-foreground text-center max-w-md">
                <p className="whitespace-pre-wrap">{description}</p>
              </div>
            ) : (
              <div className="text-muted-foreground text-center">
                <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Aucune donnée visuelle disponible</p>
                {process.env.NODE_ENV === "development" && visualData && (
                  <pre className="text-xs mt-2 text-left bg-muted/30 p-2 rounded max-w-md overflow-auto">
                    {JSON.stringify(visualData, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>

          <div className="text-xs text-center text-muted-foreground">
            Utilisez les contrôles pour manipuler la visualisation
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
