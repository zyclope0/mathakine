import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChessRenderer } from "@/components/challenges/visualizations/ChessRenderer";
import { GraphRenderer } from "@/components/challenges/visualizations/GraphRenderer";

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({
    shouldReduceMotion: false,
  }),
}));

describe("Visualization renderers", () => {
  beforeEach(() => {
    window.requestAnimationFrame = vi.fn((callback: FrameRequestCallback) => {
      callback(0);
      return 1;
    });
    window.cancelAnimationFrame = vi.fn();
  });

  it("affiche le plateau d'échecs avec des données valides", async () => {
    render(
      <ChessRenderer
        visualData={{
          board: Array.from({ length: 8 }, () => Array.from({ length: 8 }, () => ".")),
          knight_position: [3, 3],
          reachable_positions: [
            [1, 2],
            [1, 4],
          ],
          piece: "knight",
          question: "Trouve les cases atteignables.",
        }}
      />
    );

    expect(await screen.findByText("Échiquier")).toBeInTheDocument();
    expect(screen.getByText("Trouve les cases atteignables.")).toBeInTheDocument();
  });

  it("affiche le graphe même sans ResizeObserver", async () => {
    render(
      <GraphRenderer
        visualData={{
          nodes: [{ label: "A" }, { label: "B" }],
          edges: [["A", "B", 2]],
        }}
      />
    );

    expect(await screen.findByText("Graphe")).toBeInTheDocument();
    expect(screen.getByText(/2 nœuds/i)).toBeInTheDocument();
  });
});
