import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  buildGroupedSymmetryLayoutPairs,
  partitionSymmetryLayoutBySide,
  stableSortSymmetryLayoutCells,
  VisualRenderer,
} from "@/components/challenges/visualizations/VisualRenderer";

describe("VisualRenderer symmetry layout (IA9b)", () => {
  it("partitionne N cellules par côté (plus de plafond 5/5)", () => {
    const left = Array.from({ length: 7 }, (_, i) => ({
      side: "left",
      position: i,
      shape: "cercle",
    }));
    const right = Array.from({ length: 7 }, (_, i) => ({
      side: "right",
      position: i,
      shape: i === 6 ? "?" : "triangle",
      question: i === 6,
    }));
    const layout = [...left, ...right];
    const { left: L, right: R } = partitionSymmetryLayoutBySide(layout);
    expect(L.length).toBe(7);
    expect(R.length).toBe(7);
  });

  it("stableSortSymmetryLayoutCells respecte position puis ordre d'origine", () => {
    const items = [
      { side: "left", position: 2, shape: "b" },
      { side: "left", position: 0, shape: "a" },
      { side: "left", shape: "c" },
    ];
    const sorted = stableSortSymmetryLayoutCells(items);
    expect(sorted.map((x) => x.shape)).toEqual(["a", "b", "c"]);
  });

  it("convertit un layout groupé side/elements en 7 paires visuelles", () => {
    const pairs = buildGroupedSymmetryLayoutPairs([
      {
        side: "left",
        elements: [
          "triangle rouge",
          "carré vert",
          "pentagone bleu",
          "?",
          "nonagone violet",
          "octogone orange",
          "heptagone gris",
        ],
      },
      {
        side: "right",
        elements: [
          "nonagone rouge",
          "octogone vert",
          "?",
          "hexagone jaune",
          "triangle violet",
          "?",
          "pentagone gris",
        ],
      },
    ]);

    expect(pairs).toHaveLength(7);
    expect(pairs.filter((pair) => pair.left.question || pair.right.question)).toHaveLength(3);
    expect(pairs[2]?.right.shape).toBe("?");
    expect(pairs[3]?.left.shape).toBe("?");
  });

  it("convertit un layout groupé side/shapes en paires visuelles", () => {
    const pairs = buildGroupedSymmetryLayoutPairs([
      {
        side: "left",
        shapes: ["triangle bleu", "carré rouge", "cercle vert", "hexagone jaune"],
      },
      {
        side: "right",
        shapes: ["hexagone jaune", "cercle vert", "?", "triangle bleu"],
        question: true,
      },
    ]);

    expect(pairs).toHaveLength(4);
    expect(pairs[0]?.left.shape).toBe("triangle bleu");
    expect(pairs[0]?.right.shape).toBe("hexagone jaune");
    expect(pairs[2]?.right.question).toBe(true);
  });

  it("rend les colonnes groupées ligne par ligne au lieu de deux grands blocs", () => {
    const { container } = render(
      <VisualRenderer
        visualData={{
          type: "symmetry",
          symmetry_line: "vertical",
          layout: [
            {
              side: "left",
              elements: [
                "triangle rouge",
                "carré vert",
                "pentagone bleu",
                "?",
                "nonagone violet",
                "octogone orange",
                "heptagone gris",
              ],
            },
            {
              side: "right",
              elements: [
                "nonagone rouge",
                "octogone vert",
                "?",
                "hexagone jaune",
                "triangle violet",
                "?",
                "pentagone gris",
              ],
            },
          ],
        }}
      />
    );

    expect(screen.getByText("triangle rouge")).toBeInTheDocument();
    expect(screen.getByText("nonagone rouge")).toBeInTheDocument();
    expect(screen.getByText("heptagone gris")).toBeInTheDocument();
    expect(screen.getAllByLabelText("Forme manquante")).toHaveLength(3);
    expect(container.querySelectorAll('polygon[fill="#ef4444"]').length).toBeGreaterThan(0);
    expect(container.querySelectorAll('polygon[fill="#3b82f6"]').length).toBeGreaterThan(0);
  });

  it("rend les colonnes groupées avec clé shapes sans blocs vides", () => {
    render(
      <VisualRenderer
        visualData={{
          type: "symmetry",
          symmetry_line: "vertical",
          layout: [
            {
              side: "left",
              shapes: ["triangle bleu", "carré rouge", "cercle vert", "hexagone jaune"],
            },
            {
              side: "right",
              shapes: ["hexagone jaune", "cercle vert", "?", "triangle bleu"],
              question: true,
            },
          ],
        }}
      />
    );

    expect(screen.getAllByText("triangle bleu")).toHaveLength(2);
    expect(screen.getByText("carré rouge")).toBeInTheDocument();
    expect(screen.getAllByText("hexagone jaune")).toHaveLength(2);
    expect(screen.getAllByLabelText("Forme manquante")).toHaveLength(1);
  });
});
