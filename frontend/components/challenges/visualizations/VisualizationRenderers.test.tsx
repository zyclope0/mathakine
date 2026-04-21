import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { ChessRenderer } from "@/components/challenges/visualizations/ChessRenderer";
import { ChallengeVisualRenderer } from "@/components/challenges/visualizations/ChallengeVisualRenderer";
import { CodingRenderer } from "@/components/challenges/visualizations/CodingRenderer";
import { GraphRenderer } from "@/components/challenges/visualizations/GraphRenderer";
import { ProbabilityRenderer } from "@/components/challenges/visualizations/ProbabilityRenderer";
import { RiddleRenderer } from "@/components/challenges/visualizations/RiddleRenderer";
import fr from "@/messages/fr.json";

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
    expect(screen.getByText(/1 arête/i)).toBeInTheDocument();
    expect(screen.getByText(/pondéré/i)).toBeInTheDocument();
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

  it("rend le LaTeX dans les indices d'énigme sans afficher les commandes brutes", async () => {
    const { container } = render(
      <RiddleRenderer
        visualData={{
          clues: ["Le produit de mes chiffres vaut $2^3 \\times 3$."],
          key_elements: ["produit de chiffres"],
        }}
      />
    );

    expect(await screen.findByText(/Le produit de mes chiffres vaut/i)).toBeInTheDocument();
    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.querySelector(".katex-error")).toBeNull();
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

  it("affiche les urnes structurées d'un défi de probabilité", async () => {
    render(
      <NextIntlClientProvider locale="fr" messages={fr}>
        <ProbabilityRenderer
          visualData={{
            urns: {
              A: { red: 5, blue: 5 },
              B: { red: 8, blue: 2 },
              C: { red: 1, blue: 9 },
            },
            total_per_urn: 10,
            urn_selection: "equiprobable",
            draws_without_replacement: 2,
            question: "Probabilité d'obtenir deux couleurs différentes.",
          }}
        />
      </NextIntlClientProvider>
    );

    expect(await screen.findByText("Urnes")).toBeInTheDocument();
    expect(screen.getByText("Urne A")).toBeInTheDocument();
    expect(screen.getByText("Urne B")).toBeInTheDocument();
    expect(screen.getByText("Urne C")).toBeInTheDocument();
    expect(screen.getAllByText("Rouge")).toHaveLength(3);
    expect(screen.getAllByText("Bleu")).toHaveLength(3);
    expect(screen.getByText("2 tirage(s) sans remise")).toBeInTheDocument();
    expect(screen.queryByText("[object Object]")).not.toBeInTheDocument();
  });

  it("localise les couleurs d'une composition et masque une question auxiliaire anglaise", async () => {
    render(
      <NextIntlClientProvider locale="fr" messages={fr}>
        <ProbabilityRenderer
          visualData={{
            red_marbles: 15,
            blue_marbles: 10,
            green_marbles: 5,
            total_marbles: 30,
            draws_without_replacement: 2,
            question:
              "Probability that two marbles drawn without replacement are of different colors",
          }}
        />
      </NextIntlClientProvider>
    );

    expect(await screen.findByText("Composition (30 billes)")).toBeInTheDocument();
    expect(screen.getByText("Rouge")).toBeInTheDocument();
    expect(screen.getByText("Bleu")).toBeInTheDocument();
    expect(screen.getByText("Vert")).toBeInTheDocument();
    expect(screen.queryByText(/Probability that two marbles/i)).not.toBeInTheDocument();
  });

  it("rend les urnes pondérées sans compter total ni probabilité de sélection comme des billes", async () => {
    render(
      <NextIntlClientProvider locale="fr" messages={fr}>
        <ProbabilityRenderer
          visualData={{
            box_A: { red: 40, blue: 60, total: 100, selection_probability: 0.7 },
            box_B: { red: 30, blue: 20, total: 50, selection_probability: 0.3 },
            draws: "2 marbles without replacement",
            event: "two marbles of different colors",
          }}
        />
      </NextIntlClientProvider>
    );

    expect(await screen.findByText("Urne A")).toBeInTheDocument();
    expect(screen.getByText("Urne B")).toBeInTheDocument();
    expect(screen.getByText("P(sélection) 70%")).toBeInTheDocument();
    expect(screen.getByText("P(sélection) 30%")).toBeInTheDocument();
    expect(screen.getByText("2 tirage(s) sans remise")).toBeInTheDocument();
    expect(screen.getAllByText("Rouge")).toHaveLength(2);
    expect(screen.getAllByText("Bleu")).toHaveLength(2);
    expect(screen.queryByText("Selection_probability")).not.toBeInTheDocument();
    expect(screen.queryByText("Composition (301 éléments)")).not.toBeInTheDocument();
  });
});
