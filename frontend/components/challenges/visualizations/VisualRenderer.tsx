"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Eye, FlipHorizontal, RotateCw, ZoomIn, ZoomOut, ScanSearch } from "lucide-react";
import { useState } from "react";
import { motion } from "framer-motion";

import {
  findVisualizationColorInText,
  resolveVisualizationColor,
} from "@/components/challenges/visualizations/_colorMap";

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

  const detectedColor = findVisualizationColorInText(text);

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
    heptagone: "heptagone",
    heptagon: "heptagone",
    octogone: "octogone",
    octagon: "octogone",
    nonagone: "nonagone",
    nonagon: "nonagone",
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

const POLYGON_SIDE_COUNTS: Readonly<Record<string, number>> = {
  triangle: 3,
  rectangle: 4,
  carré: 4,
  pentagone: 5,
  hexagone: 6,
  heptagone: 7,
  octogone: 8,
  nonagone: 9,
};

function getRegularPolygonPoints(sides: number): string {
  const center = 16;
  const radius = 11;
  return Array.from({ length: sides }, (_, index) => {
    const angle = -Math.PI / 2 + (index * 2 * Math.PI) / sides;
    const x = center + radius * Math.cos(angle);
    const y = center + radius * Math.sin(angle);
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
}

function ShapeGlyph({
  shapeText,
  color,
  className = "h-5 w-5",
}: {
  shapeText: string;
  color?: string | undefined;
  className?: string | undefined;
}) {
  const { shape } = parseShapeWithColor(shapeText);
  const fill = color ?? "currentColor";
  const stroke = color ? "rgba(15, 23, 42, 0.35)" : "currentColor";

  if (shape === "cercle") {
    return (
      <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
        <circle cx="16" cy="16" r="10" fill={fill} stroke={stroke} strokeWidth="1.5" />
      </svg>
    );
  }

  if (shape === "losange") {
    return (
      <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
        <polygon points="16,4 28,16 16,28 4,16" fill={fill} stroke={stroke} strokeWidth="1.5" />
      </svg>
    );
  }

  const sides = POLYGON_SIDE_COUNTS[shape];
  if (sides) {
    return (
      <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
        <polygon
          points={getRegularPolygonPoints(sides)}
          fill={fill}
          stroke={stroke}
          strokeWidth="1.5"
        />
      </svg>
    );
  }

  return (
    <span
      className={`${className} inline-flex items-center justify-center text-base font-semibold`}
    >
      {getShapeIcon(shapeText)}
    </span>
  );
}

type SymmetryCell = Record<string, unknown>;
type SymmetryPair = {
  left: SymmetryCell;
  right: SymmetryCell;
  rowIndex: number;
};

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

function shapeTextFromCell(item: SymmetryCell): string {
  return String(item.shape ?? item.label ?? item.value ?? "").trim();
}

function isQuestionCell(item: SymmetryCell): boolean {
  return Boolean(item.question) || shapeTextFromCell(item).includes("?");
}

function symmetryCellFromElement(
  side: "left" | "right",
  rawElement: unknown,
  rowIndex: number
): SymmetryCell {
  const shape = String(rawElement ?? "").trim();
  return {
    side,
    shape,
    position: rowIndex + 1,
    question: shape.includes("?"),
  };
}

function groupedElementsForSide(layout: SymmetryCell[], side: "left" | "right"): unknown[] {
  const group = layout.find(
    (item) =>
      String(item.side ?? "").toLowerCase() === side &&
      (Array.isArray(item.elements) || Array.isArray(item.shapes) || Array.isArray(item.items))
  );
  if (!group) return [];
  if (Array.isArray(group.elements)) return group.elements;
  if (Array.isArray(group.shapes)) return group.shapes;
  if (Array.isArray(group.items)) return group.items;
  return [];
}

/**
 * OpenAI produit parfois `layout: [{ side: "left", elements: [...] }, ...]`.
 * Le rendu attendu est une matrice de paires ligne par ligne, pas deux gros blocs.
 */
export function buildGroupedSymmetryLayoutPairs(layout: SymmetryCell[]): SymmetryPair[] {
  const leftElements = groupedElementsForSide(layout, "left");
  const rightElements = groupedElementsForSide(layout, "right");
  const rowCount = Math.max(leftElements.length, rightElements.length);
  if (rowCount === 0) return [];

  return Array.from({ length: rowCount }, (_, rowIndex) => ({
    left: symmetryCellFromElement("left", leftElements[rowIndex] ?? "", rowIndex),
    right: symmetryCellFromElement("right", rightElements[rowIndex] ?? "", rowIndex),
    rowIndex,
  }));
}

export function buildPositionedSymmetryLayoutPairs(layout: SymmetryCell[]): SymmetryPair[] {
  const hasPositions = layout.some((item) => typeof item.position === "number");
  if (!hasPositions) return [];

  const { left, right } = partitionSymmetryLayoutBySide(layout);
  const rowCount = Math.max(left.length, right.length);
  if (rowCount === 0) return [];

  return Array.from({ length: rowCount }, (_, rowIndex) => ({
    left: left[rowIndex] ?? symmetryCellFromElement("left", "", rowIndex),
    right: right[rowIndex] ?? symmetryCellFromElement("right", "", rowIndex),
    rowIndex,
  }));
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
            /* swallowed: malformed visual_data JSON, empty fallback used */
            return {};
          }
        })()
      : visualData;
  const layout = Array.isArray(p?.layout) ? (p.layout as SymmetryCell[]) : [];
  const isSym = p?.type === "symmetry" || !!p?.symmetry_line;
  if (!isSym || layout.length === 0) return 1;
  if (buildGroupedSymmetryLayoutPairs(layout).length > 0) return 1;
  if (buildPositionedSymmetryLayoutPairs(layout).length > 0) return 1;
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
  const shapeText = shapeTextFromCell(item);
  const parsed = parseShapeWithColor(shapeText);
  const color =
    (typeof item.color === "string" ? resolveVisualizationColor(item.color) : null) ?? parsed.color;
  const isQuestion = Boolean(item.question) || shapeText.includes("?");
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
        <ShapeGlyph shapeText={shapeText} color={color ?? undefined} className="h-7 w-7" />
      )}
    </motion.div>
  );
}

function SymmetryPairCell({
  item,
  side,
  rowIndex,
}: {
  item: SymmetryCell;
  side: "left" | "right";
  rowIndex: number;
}) {
  const shapeText = shapeTextFromCell(item);
  const parsed = parseShapeWithColor(shapeText);
  const color =
    (typeof item.color === "string" ? resolveVisualizationColor(item.color) : null) ?? parsed.color;
  const isQuestion = isQuestionCell(item);
  const fromLeft = side === "left";

  return (
    <motion.div
      className={`min-h-12 rounded-xl border-2 px-3 py-2 flex items-center gap-2 ${
        isQuestion ? "border-dashed border-primary/70 bg-primary/5" : "border-primary/30 bg-card"
      }`}
      initial={{ opacity: 0, x: fromLeft ? -12 : 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: rowIndex * 0.04 }}
      aria-label={isQuestion ? "Forme manquante" : shapeText}
      title={shapeText || (isQuestion ? "Forme manquante" : undefined)}
    >
      {isQuestion ? (
        <span className="text-xl font-bold text-primary">?</span>
      ) : (
        <>
          <ShapeGlyph shapeText={shapeText} color={color ?? undefined} className="h-5 w-5" />
          <span className="min-w-0 truncate text-xs sm:text-sm text-foreground">{shapeText}</span>
        </>
      )}
    </motion.div>
  );
}

function SymmetryPairRows({ pairs }: { pairs: SymmetryPair[] }) {
  return (
    <div className="w-full max-w-3xl mx-auto space-y-1.5">
      {pairs.map((pair) => (
        <div
          key={`sym-pair-${pair.rowIndex}`}
          className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] items-center gap-2 sm:gap-3"
        >
          <SymmetryPairCell item={pair.left} side="left" rowIndex={pair.rowIndex} />
          <div className="h-12 w-0.5 rounded-full bg-primary/50" aria-hidden />
          <SymmetryPairCell item={pair.right} side="right" rowIndex={pair.rowIndex} />
        </div>
      ))}
    </div>
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
    <Card flat className={`bg-card border-primary/20 ${className || ""}`}>
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
                  const groupedPairs = buildGroupedSymmetryLayoutPairs(cells);
                  const positionedPairs = buildPositionedSymmetryLayoutPairs(cells);
                  const pairRows = groupedPairs.length > 0 ? groupedPairs : positionedPairs;
                  const { left: leftCells, right: rightCells } =
                    partitionSymmetryLayoutBySide(cells);
                  const axis = String(symmetryLine ?? "vertical").toLowerCase();
                  const isVertical = axis === "vertical" || axis === "v";

                  if (isVertical) {
                    if (pairRows.length > 0) {
                      return <SymmetryPairRows pairs={pairRows} />;
                    }

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
                          <ShapeGlyph
                            shapeText={cellValue}
                            color={parseShapeWithColor(cellValue).color ?? undefined}
                            className="h-7 w-7"
                          />
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
                        <ShapeGlyph
                          shapeText={String(shape)}
                          color={parseShapeWithColor(String(shape)).color ?? undefined}
                          className="h-4 w-4"
                        />
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
                          <ShapeGlyph
                            shapeText={shapeText}
                            color={color ?? undefined}
                            className="h-10 w-10"
                          />
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
