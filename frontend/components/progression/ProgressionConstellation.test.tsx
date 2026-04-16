import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import {
  ProgressionConstellation,
  type ProgressionConstellationNode,
} from "@/components/progression/ProgressionConstellation";

const fourNodes: ProgressionConstellationNode[] = [
  { id: "a", state: "completed", label: "Débutant" },
  { id: "b", state: "completed", label: "Intermédiaire" },
  { id: "c", state: "current", label: "Actuel" },
  { id: "d", state: "upcoming", label: "Expert" },
];

describe("ProgressionConstellation", () => {
  it("expose role=img avec aria-label et liste sr-only décrite", () => {
    render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Progression sur 4 paliers" />);

    const img = screen.getByRole("img", { name: "Progression sur 4 paliers" });
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute("aria-describedby");

    const id = img.getAttribute("aria-describedby");
    expect(id).toBeTruthy();
    const list = document.getElementById(id!);
    expect(list?.tagName).toBe("UL");
    expect(list).toHaveClass("sr-only");
    expect(screen.getByText("Débutant: completed")).toBeInTheDocument();
    expect(screen.getByText("Actuel: current step")).toBeInTheDocument();
  });

  it("affiche les labels visibles (aria-hidden sur la grille)", () => {
    render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Résumé progression" />);
    expect(screen.getByText("Expert")).toBeInTheDocument();
  });

  it("aligne les labels sur une grille à colonnes explicites (4 paliers)", () => {
    const { container } = render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Test" />);
    const labelRow = container.querySelector(".grid-cols-4");
    expect(labelRow).toBeTruthy();
  });

  it("retourne null si nodes vide", () => {
    const { container } = render(<ProgressionConstellation nodes={[]} ariaLabel="Vide" />);
    expect(container.firstChild).toBeNull();
  });
});
