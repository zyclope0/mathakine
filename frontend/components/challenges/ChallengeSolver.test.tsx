/**
 * Characterization tests for ChallengeSolver.tsx.
 *
 * Scope:
 * - loading / error / not-found states
 * - first-visit hint visibility
 * - QCM validation gating
 * - legacy JSON-string choices compatibility
 * - visual multi-position submit gating
 * - baseline answer area visibility before submit
 * - command bar: QCM mode renders choices
 * - command bar: visual multi-position renders position labels
 *
 * FFI-L10 lot 3 — tests de non-régression après split Command Bar + hook controller.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";
import type { Challenge } from "@/types/api";
import type { ApiClientError } from "@/lib/api/client";
import { STORAGE_KEYS } from "@/lib/storage/keys";

vi.mock("@/hooks/useChallenge");
vi.mock("@/hooks/useChallenges");
vi.mock("@/lib/stores/themeStore", () => ({
  useThemeStore: () => ({ theme: "spatial" }),
}));
vi.mock("@/components/challenges/visualizations/ChallengeVisualRenderer", () => ({
  ChallengeVisualRenderer: () => <div data-testid="visual-renderer" />,
}));

import { useChallenge } from "@/hooks/useChallenge";
import { useChallenges } from "@/hooks/useChallenges";
import { ChallengeSolver } from "./ChallengeSolver";

type UseChallengesReturn = ReturnType<typeof useChallenges>;
type SubmitAnswerFn = UseChallengesReturn["submitAnswer"];
type GetHintFn = UseChallengesReturn["getHint"];
type SetHintsFn = UseChallengesReturn["setHints"];

function baseChallenge(partial: Partial<Challenge> = {}): Challenge {
  return {
    id: 42,
    title: "Defi de test",
    description: "Une description",
    challenge_type: "logic",
    age_group: "9-11",
    response_mode: "open_text",
    choices: null,
    hints: null,
    visual_data: null,
    correct_answer: null,
    ...partial,
  } as Challenge;
}

function defaultUseChallengesMock(): UseChallengesReturn {
  const submitAnswer: SubmitAnswerFn = vi.fn(async () => {
    throw new Error("submitAnswer mock not configured");
  });
  const getHint: GetHintFn = vi.fn(async () => []);
  const setHints: SetHintsFn = vi.fn();

  return {
    submitAnswer,
    isSubmitting: false,
    submitResult: undefined,
    getHint,
    isGettingHint: false,
    setHints,
    challenges: [],
    total: 0,
    hasMore: false,
    isLoading: false,
    isFetching: false,
    error: null,
    hints: [],
  };
}

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function renderSolver(challengeId = 42) {
  return render(
    <Wrapper>
      <ChallengeSolver challengeId={challengeId} />
    </Wrapper>
  );
}

beforeEach(() => {
  vi.clearAllMocks();

  const store: Record<string, string> = {};
  vi.mocked(localStorage.getItem).mockImplementation((k) => store[k] ?? null);
  vi.mocked(localStorage.setItem).mockImplementation((k, v) => {
    store[k] = v;
  });
  vi.mocked(localStorage.removeItem).mockImplementation((k) => {
    delete store[k];
  });
  vi.mocked(localStorage.clear).mockImplementation(() => {
    Object.keys(store).forEach((k) => delete store[k]);
  });

  vi.mocked(useChallenges).mockReturnValue(defaultUseChallengesMock());
  vi.mocked(useChallenge).mockReturnValue({
    challenge: baseChallenge(),
    isLoading: false,
    error: null,
  });
});

describe("ChallengeSolver - loading state", () => {
  it("does not render the challenge title while loading", () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: undefined,
      isLoading: true,
      error: null,
    });

    renderSolver();

    expect(screen.queryByRole("heading", { level: 1 })).not.toBeInTheDocument();
  });
});

describe("ChallengeSolver - error state", () => {
  it("renders the error alert and back link", () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: undefined,
      isLoading: false,
      error: { status: 500, message: "Erreur serveur" } as ApiClientError,
    });

    renderSolver();

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /retour/i })).toBeInTheDocument();
  });

  it("renders not-found style error for 404", () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: undefined,
      isLoading: false,
      error: { status: 404, message: "Not found" } as ApiClientError,
    });

    renderSolver();

    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});

describe("ChallengeSolver - not found state", () => {
  it("renders the not-found block when challenge is missing without error", () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: undefined,
      isLoading: false,
      error: null,
    });

    renderSolver();

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /retour/i })).toBeInTheDocument();
  });
});

describe("ChallengeSolver - first visit hint", () => {
  it("shows the hint before submit on first visit", async () => {
    renderSolver();

    await screen.findByRole("region", { name: /comment/i });
  });

  it("does not show the hint when already seen in localStorage", async () => {
    localStorage.setItem(STORAGE_KEYS.challengeSolverHintSeen, "1");

    renderSolver();

    await waitFor(() => {
      expect(screen.queryByRole("region", { name: /comment/i })).not.toBeInTheDocument();
    });
  });
});

describe("ChallengeSolver - QCM mode", () => {
  it("keeps validate disabled until one choice is selected", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "single_choice",
        choices: ["Reponse A", "Reponse B", "Reponse C"],
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    await screen.findByRole("radio", { name: /option 1/i });

    expect(screen.getByRole("button", { name: /valider/i })).toBeDisabled();
  });

  it("enables validate after selecting one choice", async () => {
    const user = userEvent.setup();
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "single_choice",
        choices: ["Reponse A", "Reponse B"],
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    const choiceButton = await screen.findByRole("radio", { name: /reponse a/i });
    await user.click(choiceButton);

    expect(screen.getByRole("button", { name: /valider/i })).not.toBeDisabled();
  });

  it("renders QCM correctly when choices comes as a legacy JSON string", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "single_choice",
        choices: '["Reponse A", "Reponse B"]' as unknown as string[],
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    expect(await screen.findByRole("radio", { name: /reponse a/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /reponse b/i })).toBeInTheDocument();
  });
});

describe("ChallengeSolver - visual multi-position mode", () => {
  it("keeps validate disabled while required positions are incomplete", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        correct_answer: "Position 1: cercle rouge, Position 2: carre bleu",
        visual_data: {
          shapes: ["cercle rouge", "carre bleu", "triangle vert"],
        },
        choices: null,
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    await screen.findByText(/position 1/i);

    expect(screen.getByRole("button", { name: /valider/i })).toBeDisabled();
  });
});

describe("ChallengeSolver - initial answer area", () => {
  it("renders the text input before submit", async () => {
    renderSolver();

    expect(await screen.findByRole("textbox")).toBeInTheDocument();
  });

  it("renders the validate button before submit", async () => {
    renderSolver();

    await screen.findByRole("textbox");
    expect(screen.getByRole("button", { name: /valider/i })).toBeInTheDocument();
  });
});

/**
 * Tests sur la Command Bar extraite en lot 3.
 * Vérifient que les branches QCM et visual multi-position sont intactes.
 */
describe("ChallengeSolver - command bar QCM mode", () => {
  it("renders all choice buttons in QCM mode", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "single_choice",
        choices: ["Option A", "Option B", "Option C"],
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    expect(await screen.findByRole("radio", { name: /option a/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /option b/i })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: /option c/i })).toBeInTheDocument();
  });

  it("enables validate after selecting a choice in QCM mode", async () => {
    const user = userEvent.setup();
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "single_choice",
        choices: ["Option A", "Option B"],
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    const choiceBtn = await screen.findByRole("radio", { name: /option a/i });
    await user.click(choiceBtn);

    expect(screen.getByRole("button", { name: /valider/i })).not.toBeDisabled();
  });
});

describe("ChallengeSolver - command bar visual multi-position mode", () => {
  it("renders position labels for multi-position challenges", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        correct_answer: "Position 1: cercle rouge, Position 2: carre bleu",
        visual_data: {
          shapes: ["cercle rouge", "carre bleu", "triangle vert"],
        },
        choices: null,
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    await screen.findByText(/position 1/i);
    expect(screen.getByText(/position 2/i)).toBeInTheDocument();
  });

  it("keeps validate disabled until all positions are filled", async () => {
    vi.mocked(useChallenge).mockReturnValue({
      challenge: baseChallenge({
        response_mode: "interactive_visual",
        challenge_type: "visual",
        correct_answer: "Position 1: cercle rouge, Position 2: carre bleu",
        visual_data: {
          shapes: ["cercle rouge", "carre bleu", "triangle vert"],
        },
        choices: null,
      }),
      isLoading: false,
      error: null,
    });

    renderSolver();

    await screen.findByText(/position 1/i);
    expect(screen.getByRole("button", { name: /valider/i })).toBeDisabled();
  });
});
