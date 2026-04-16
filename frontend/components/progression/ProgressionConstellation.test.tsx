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
  it("expose role=region avec aria-label et liste sr-only décrite", () => {
    render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Progression sur 4 paliers" />);

    const region = screen.getByRole("region", { name: "Progression sur 4 paliers" });
    expect(region).toBeInTheDocument();
    expect(region).toHaveAttribute("aria-describedby");

    const id = region.getAttribute("aria-describedby");
    expect(id).toBeTruthy();
    const list = document.getElementById(id!);
    expect(list?.tagName).toBe("UL");
    expect(list).toHaveClass("sr-only");
    expect(screen.getByText("Débutant: completed")).toBeInTheDocument();
    expect(screen.getByText("Actuel: current step")).toBeInTheDocument();
  });

  it("affiche les labels visibles (aria-hidden sur le conteneur des libellés)", () => {
    render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Résumé progression" />);
    expect(screen.getByText("Expert")).toBeInTheDocument();
  });

  it("zone défilante horizontale sans scrollbar visible (no-scrollbar)", () => {
    const { container } = render(<ProgressionConstellation nodes={fourNodes} ariaLabel="Test" />);
    const scrollRegion = container.querySelector(".no-scrollbar.overflow-x-auto");
    expect(scrollRegion).toBeTruthy();
  });

  it("retourne null si nodes vide", () => {
    const { container } = render(<ProgressionConstellation nodes={[]} ariaLabel="Vide" />);
    expect(container.firstChild).toBeNull();
  });
});
