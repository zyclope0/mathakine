import { describe, it, expect, vi, beforeEach } from "vitest";
import { dispatchExerciseAiSseEvent } from "./dispatchExerciseAiSseEvent";
import { toast } from "sonner";

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  },
}));

const t = (key: string) => key;

describe("dispatchExerciseAiSseEvent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("succès avec id numérique : met à jour l'exercice et invalide les listes", () => {
    const setExercise = vi.fn();
    const invalidate = vi.fn();
    dispatchExerciseAiSseEvent(
      {
        type: "exercise",
        exercise: {
          id: 99,
          title: "Mon exercice",
          question: "Q?",
          correct_answer: "1",
          exercise_type: "addition",
        },
      },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedExercise: setExercise,
        onInvalidateLists: invalidate,
      }
    );
    expect(setExercise).toHaveBeenCalledWith(
      expect.objectContaining({ id: 99, title: "Mon exercice" })
    );
    expect(invalidate).toHaveBeenCalled();
    expect(toast.success).toHaveBeenCalled();
  });

  it("succès avec id string : normalise l'id", () => {
    const setExercise = vi.fn();
    dispatchExerciseAiSseEvent(
      {
        type: "exercise",
        exercise: {
          id: "100",
          title: "T",
          question: "Q",
          correct_answer: "2",
          exercise_type: "addition",
        },
      },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedExercise: setExercise,
        onInvalidateLists: vi.fn(),
      }
    );
    expect(setExercise).toHaveBeenCalledWith(expect.objectContaining({ id: 100 }));
  });

  it("exercise sans id persisté : warning, pas d'état généré navigable", () => {
    const setExercise = vi.fn();
    dispatchExerciseAiSseEvent(
      {
        type: "exercise",
        exercise: {
          title: "T",
          question: "Q",
          correct_answer: "1",
          exercise_type: "addition",
        },
        warning: "Non sauvegardé",
      },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedExercise: setExercise,
        onInvalidateLists: vi.fn(),
      }
    );
    expect(setExercise).toHaveBeenCalledWith(null);
    expect(toast.warning).toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
  });

  it("warning seul : pas de succès", () => {
    const setExercise = vi.fn();
    dispatchExerciseAiSseEvent(
      { type: "warning", message: "Surveillance" },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedExercise: setExercise,
        onInvalidateLists: vi.fn(),
      }
    );
    expect(toast.warning).toHaveBeenCalled();
    expect(setExercise).not.toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
  });
});
