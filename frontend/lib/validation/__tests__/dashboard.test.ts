import { describe, expect, it } from "vitest";
import {
  parseSpacedRepetitionUserSummary,
  safeValidateUserStats,
} from "@/lib/validation/dashboard";

describe("parseSpacedRepetitionUserSummary", () => {
  it("retourne des défauts si données absentes ou invalides", () => {
    expect(parseSpacedRepetitionUserSummary(undefined)).toEqual({
      f04_initialized: false,
      active_cards_count: 0,
      due_today_count: 0,
      overdue_count: 0,
      next_review_date: null,
    });
    expect(parseSpacedRepetitionUserSummary("x")).toEqual(
      parseSpacedRepetitionUserSummary(undefined)
    );
  });

  it("parse un bloc API valide", () => {
    expect(
      parseSpacedRepetitionUserSummary({
        f04_initialized: true,
        active_cards_count: 3,
        due_today_count: 1,
        overdue_count: 2,
        next_review_date: "2026-07-01",
      })
    ).toEqual({
      f04_initialized: true,
      active_cards_count: 3,
      due_today_count: 1,
      overdue_count: 2,
      next_review_date: "2026-07-01",
    });
  });

  it("rejette next_review_date mal formé", () => {
    const r = parseSpacedRepetitionUserSummary({
      f04_initialized: true,
      active_cards_count: 1,
      due_today_count: 0,
      overdue_count: 0,
      next_review_date: "not-a-date",
    });
    expect(r.next_review_date).toBeNull();
  });

  it("normalise les compteurs négatifs ou non finis", () => {
    const r = parseSpacedRepetitionUserSummary({
      f04_initialized: true,
      active_cards_count: -1,
      due_today_count: NaN,
      overdue_count: 2.7,
      next_review_date: null,
    });
    expect(r.active_cards_count).toBe(0);
    expect(r.due_today_count).toBe(0);
    expect(r.overdue_count).toBe(2);
  });
});

describe("safeValidateUserStats", () => {
  it("injecte spaced_repetition même si absent du JSON", () => {
    const out = safeValidateUserStats({
      total_exercises: 1,
      correct_answers: 1,
    });
    expect(out).not.toBeNull();
    expect(out!.spaced_repetition).toEqual(parseSpacedRepetitionUserSummary(null));
  });

  it("fusionne spaced_repetition fourni par l'API", () => {
    const out = safeValidateUserStats({
      total_exercises: 0,
      correct_answers: 0,
      spaced_repetition: {
        f04_initialized: true,
        active_cards_count: 5,
        due_today_count: 2,
        overdue_count: 0,
        next_review_date: "2026-12-31",
      },
    });
    expect(out!.spaced_repetition.due_today_count).toBe(2);
    expect(out!.spaced_repetition.next_review_date).toBe("2026-12-31");
  });
});
