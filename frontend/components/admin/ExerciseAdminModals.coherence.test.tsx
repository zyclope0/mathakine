import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ExerciseEditModal } from "./ExerciseEditModal";
import { ExerciseCreateModal } from "./ExerciseCreateModal";

const mockApiGet = vi.fn();
const mockApiPut = vi.fn();
const mockApiPost = vi.fn();

vi.mock("@/lib/api/client", () => ({
  api: {
    get: (...args: unknown[]) => mockApiGet(...args),
    put: (...args: unknown[]) => mockApiPut(...args),
    post: (...args: unknown[]) => mockApiPost(...args),
  },
}));

describe("ExerciseEditModal — admin coherence", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockApiGet.mockResolvedValue({
      id: 1,
      title: "T",
      exercise_type: "ADDITION",
      difficulty: "PADAWAN",
      age_group: "6_8",
      question: "Q",
      correct_answer: "A",
      choices: null,
      explanation: "",
      hint: "",
      is_archived: false,
    });
  });

  it("uses Select for âge (no legacy free-text placeholder)", async () => {
    render(<ExerciseEditModal exerciseId={1} open onOpenChange={() => {}} onSaved={() => {}} />);
    await waitFor(() => {
      expect(screen.queryByText("Chargement...")).not.toBeInTheDocument();
    });
    expect(screen.queryByPlaceholderText("ex: 8-10")).not.toBeInTheDocument();
    expect(screen.getAllByRole("combobox").length).toBeGreaterThanOrEqual(3);
  });
});

describe("ExerciseCreateModal — admin coherence", () => {
  it("shows canonical age label from shared default", () => {
    render(<ExerciseCreateModal open onOpenChange={() => {}} onCreated={() => {}} />);
    expect(screen.getByText("9-11 ans")).toBeInTheDocument();
    expect(screen.getAllByRole("combobox").length).toBeGreaterThanOrEqual(3);
  });
});
