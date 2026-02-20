/**
 * Utilitaires pour les défis VISUAL : extraction des formes depuis visual_data.
 * Permet d'afficher des boutons de choix (toutes les formes) au lieu du champ texte.
 */

const SHAPE_NAMES = [
  "triangle", "cercle", "circle", "carré", "carre", "square", "rectangle",
  "losange", "diamond", "étoile", "etoile", "star", "hexagone", "hexagon",
  "pentagone", "pentagon",
];
const COLOR_NAMES = [
  "rouge", "red", "bleu", "blue", "vert", "green", "jaune", "yellow",
  "orange", "violet", "purple", "rose", "pink", "gris", "gray", "noir",
  "black", "blanc", "white", "marron", "brown",
];

function toDisplayForm(shape: string): string {
  const m: Record<string, string> = {
    circle: "cercle", square: "carré", carre: "carré", rectangle: "rectangle",
    diamond: "losange", star: "étoile", etoile: "étoile", hexagon: "hexagone",
    pentagon: "pentagone", red: "rouge", blue: "bleu", green: "vert",
    yellow: "jaune", purple: "violet", pink: "rose", gray: "gris", black: "noir",
    white: "blanc", brown: "marron",
  };
  return m[shape.toLowerCase()] ?? shape;
}

/**
 * Extrait toutes les combinaisons "forme couleur" uniques depuis visual_data.
 * Ne pas orienter : on renvoie TOUTES les formes présentes (sauf "?").
 */
export function extractShapeChoicesFromVisualData(visualData: unknown): string[] {
  const seen = new Set<string>();
  const add = (raw: string) => {
    const s = String(raw).trim();
    if (!s || s === "?" || s.includes("?")) return;
    const lower = s.toLowerCase();
    let shape = "";
    let color = "";
    for (const sn of SHAPE_NAMES) {
      if (lower.includes(sn)) {
        shape = toDisplayForm(sn);
        break;
      }
    }
    for (const cn of COLOR_NAMES) {
      if (lower.includes(cn)) {
        color = toDisplayForm(cn);
        break;
      }
    }
    if (shape && color) {
      seen.add(`${shape} ${color}`);
    } else if (s && s.length < 30 && !s.includes("position")) {
      seen.add(s);
    }
  };

  if (!visualData || typeof visualData !== "object") return [];

  const v = visualData as Record<string, unknown>;

  // shapes: ["cercle rouge", "carré bleu", "?", ...]
  const shapes = v.shapes ?? v.items ?? v.elements;
  if (Array.isArray(shapes)) {
    for (const item of shapes) {
      if (typeof item === "string") add(item);
      else if (item && typeof item === "object" && "label" in item) add((item as { label: string }).label);
      else if (item && typeof item === "object" && "value" in item) add((item as { value: string }).value);
    }
  }

  // layout: [{shape, color, side}, ...]
  const layout = v.layout;
  if (Array.isArray(layout)) {
    for (const item of layout) {
      if (item && typeof item === "object") {
        const o = item as Record<string, unknown>;
        const shape = String(o.shape ?? "").trim();
        const color = String(o.color ?? "").trim();
        if (shape && color && shape !== "?" && color !== "?") {
          seen.add(`${toDisplayForm(shape)} ${toDisplayForm(color)}`);
        }
      }
    }
  }

  return Array.from(seen).sort();
}

/**
 * Parse correct_answer pour extraire les positions (multi-cellules).
 * Ex: "Position 6: carré bleu, Position 9: triangle vert" -> [6, 9]
 * Ex: "carré bleu" -> [] (single)
 */
export function parsePositionsFromCorrectAnswer(correctAnswer: string | null | undefined): number[] {
  if (!correctAnswer || typeof correctAnswer !== "string") return [];
  const lower = correctAnswer.toLowerCase();
  if (!lower.includes("position")) return [];
  const positions: number[] = [];
  const re = /position\s*(\d+)/gi;
  let m;
  while ((m = re.exec(lower)) !== null) {
    const s = m[1];
    if (s) {
      const n = parseInt(s, 10);
      if (!Number.isNaN(n) && !positions.includes(n)) positions.push(n);
    }
  }
  return positions.sort((a, b) => a - b);
}

/**
 * Parse visual_data.layout pour extraire les positions des cellules à remplir (question: true).
 * Fallback quand correct_answer et question n'ont pas le format "Position N:".
 * Pour symétrie : left positions 1-5, right positions 6-10.
 */
export function parsePositionsFromLayout(visualData: unknown): number[] {
  if (!visualData || typeof visualData !== "object") return [];
  const v = visualData as Record<string, unknown>;

  // Symmetry layout : left/right avec question: true
  const layout = v.layout;
  if (Array.isArray(layout) && layout.some((i: unknown) => (i as Record<string, unknown>)?.question)) {
    const positions: number[] = [];
    const itemPos = (i: unknown) => (i as Record<string, unknown>)?.position as number | undefined;
    const leftItems = layout
      .filter((i: unknown) => i && typeof i === "object" && (i as Record<string, unknown>).side === "left")
      .sort((a, b) => (itemPos(a) ?? 0) - (itemPos(b) ?? 0));
    const rightItems = layout
      .filter((i: unknown) => i && typeof i === "object" && (i as Record<string, unknown>).side === "right")
      .sort((a, b) => (itemPos(a) ?? 0) - (itemPos(b) ?? 0));

    leftItems.forEach((item: unknown, idx: number) => {
      if ((item as Record<string, unknown>)?.question) positions.push(idx + 1);
    });
    rightItems.forEach((item: unknown, idx: number) => {
      if ((item as Record<string, unknown>)?.question) positions.push(leftItems.length + idx + 1);
    });
    return positions.sort((a, b) => a - b);
  }

  // Fallback: shapes array avec "?" - positions 1-based
  const shapes = v.shapes ?? v.items ?? v.elements;
  if (Array.isArray(shapes)) {
    const positions: number[] = [];
    shapes.forEach((s: unknown, idx: number) => {
      const obj = s as Record<string, unknown>;
      const val = typeof s === "string" ? s : obj?.label ?? obj?.value ?? "";
      if (String(val).includes("?") || val === "?") positions.push(idx + 1);
    });
    return positions;
  }

  return [];
}

/**
 * Parse la question pour extraire les positions quand correct_answer n'a pas le format "Position N:".
 * Ex: "placer en positions 6 et 9" -> [6, 9]
 * Ex: "position 5" -> [5]
 */
export function parsePositionsFromQuestion(question: string | null | undefined): number[] {
  if (!question || typeof question !== "string") return [];
  const positions: number[] = [];
  const re = /positions?\s*(\d+)(?:\s*(?:et|and|,)\s*(\d+))?/gi;
  let m;
  while ((m = re.exec(question)) !== null) {
    for (let i = 1; i < m.length; i++) {
      const s = m[i];
      if (s) {
        const n = parseInt(s, 10);
        if (!Number.isNaN(n) && !positions.includes(n)) positions.push(n);
      }
    }
  }
  return positions.sort((a, b) => a - b);
}
