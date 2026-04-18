import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChessRenderer } from "@/components/challenges/visualizations/ChessRenderer";
import { ChallengeVisualRenderer } from "@/components/challenges/visualizations/ChallengeVisualRenderer";
import { CodingRenderer } from "@/components/challenges/visualizations/CodingRenderer";
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

  it("affiche les indices utiles d'une substitution sans [object Object]", async () => {
    render(
      <CodingRenderer
        visualData={{
          type: "substitution",
          rule_type: "keyword",
          encoded_message: "SFA ROGNA KTRS BJMW",
          partial_key: {
            keyword_length: 4,
            theme_clue: "desert planet",
            mapping_known: {
              D: "A",
              U: "B",
              N: "C",
              E: "D",
            },
          },
        }}
      />
    );

    expect(await screen.findByText("Table de correspondance")).toBeInTheDocument();
    expect(screen.getByText(/Longueur du mot-clé/i)).toBeInTheDocument();
    expect(screen.getByText(/Indice thématique/i)).toBeInTheDocument();
    expect(screen.getByText("desert planet")).toBeInTheDocument();
    expect(screen.queryByText("[object Object]")).not.toBeInTheDocument();
  });

  it("n'affiche pas de champ inline sequence quand la modalité active est QCM", async () => {
    render(
      <ChallengeVisualRenderer
        challenge={{
          id: 1,
          title: "Suite",
          description: "Trouve le terme suivant.",
          age_group: "15-17",
          challenge_type: "sequence",
          visual_data: { sequence: [3, 8, 19, 40, 75, "?"] },
          response_mode: "single_choice",
        }}
        responseMode="single_choice"
        showMcq={true}
        onAnswerChange={() => {}}
      />
    );

    expect(await screen.findByText("Séquence à analyser")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/entrez le prochain nombre/i)).not.toBeInTheDocument();
  });

  it("affiche le champ inline sequence quand la modalité active est la grille", async () => {
    render(
      <ChallengeVisualRenderer
        challenge={{
          id: 2,
          title: "Suite",
          description: "Trouve le terme suivant.",
          age_group: "15-17",
          challenge_type: "sequence",
          visual_data: { sequence: [3, 8, 19, 40, 75, "?"] },
          response_mode: "interactive_grid",
        }}
        responseMode="interactive_grid"
        showMcq={false}
        onAnswerChange={() => {}}
      />
    );

    expect(await screen.findByPlaceholderText(/entrez le prochain nombre/i)).toBeInTheDocument();
  });

  it("n'affiche pas de champ inline pattern; la saisie reste dans la command bar", async () => {
    render(
      <ChallengeVisualRenderer
        challenge={{
          id: 3,
          title: "Motif",
          description: "Trouve les valeurs manquantes.",
          age_group: "15-17",
          challenge_type: "pattern",
          visual_data: {
            grid: [
              ["3", "5", "8", "12", "17"],
              ["4", "7", "11", "16", "?"],
            ],
          },
          response_mode: "interactive_grid",
        }}
        responseMode="interactive_grid"
        showMcq={false}
        onAnswerChange={() => {}}
      />
    );

    expect(await screen.findByText("Grille de pattern")).toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/22, 21, 28, 20, 16/i)).not.toBeInTheDocument();
  });
});
