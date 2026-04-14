import { describe, it, expect } from "vitest";
import { parseNextReviewApiResponse } from "./spacedRepetitionNextReview";

const validSummary = {
  f04_initialized: true,
  active_cards_count: 2,
  due_today_count: 1,
  overdue_count: 0,
  next_review_date: "2026-03-30",
};

const validExercise = {
  id: 10,
  title: "Ex",
  question: "1+1?",
  exercise_type: "ADDITION",
  difficulty: "INITIE",
  age_group: "6-8",
  difficulty_tier: null,
  choices: ["1", "2"],
  image_url: null,
  audio_url: null,
};

describe("parseNextReviewApiResponse", () => {
  it("accepte une réponse sans carte due", () => {
    const out = parseNextReviewApiResponse({
      has_due_review: false,
      summary: validSummary,
      next_review: null,
    });
    expect(out).not.toBeNull();
    expect(out?.has_due_review).toBe(false);
    expect(out?.next_review).toBeNull();
    expect(out?.summary.active_cards_count).toBe(2);
  });

  it("accepte une carte due valide", () => {
    const out = parseNextReviewApiResponse({
      has_due_review: true,
      summary: validSummary,
      next_review: {
        review_item_id: 42,
        exercise_id: 10,
        due_status: "overdue",
        next_review_date: "2026-03-28",
        exercise: validExercise,
      },
    });
    expect(out?.has_due_review).toBe(true);
    expect(out?.next_review?.exercise_id).toBe(10);
    expect(out?.next_review?.due_status).toBe("overdue");
  });

  it("rejette un exercice contenant un spoiler", () => {
    const out = parseNextReviewApiResponse({
      has_due_review: true,
      summary: validSummary,
      next_review: {
        review_item_id: 1,
        exercise_id: 10,
        due_status: "due_today",
        next_review_date: "2026-03-27",
        exercise: { ...validExercise, correct_answer: "2" },
      },
    });
    expect(out).toBeNull();
  });

  it("rejette un exercice contenant une explication ou un indice", () => {
    const withExplanation = parseNextReviewApiResponse({
      has_due_review: true,
      summary: validSummary,
      next_review: {
        review_item_id: 1,
        exercise_id: 10,
        due_status: "due_today",
        next_review_date: "2026-03-27",
        exercise: { ...validExercise, explanation: "La bonne methode" },
      },
    });
    const withHint = parseNextReviewApiResponse({
      has_due_review: true,
      summary: validSummary,
      next_review: {
        review_item_id: 1,
        exercise_id: 10,
        due_status: "due_today",
        next_review_date: "2026-03-27",
        exercise: { ...validExercise, hint: "Pense aux doubles" },
      },
    });
    expect(withExplanation).toBeNull();
    expect(withHint).toBeNull();
  });

  it("rejette has_due_review true sans next_review", () => {
    const out = parseNextReviewApiResponse({
      has_due_review: true,
      summary: validSummary,
      next_review: null,
    });
    expect(out).toBeNull();
  });
});
