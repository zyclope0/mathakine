import { describe, expect, it } from "vitest";
import { parseSpacedRepetitionUserSummary, safeValidateUserStats } from "./dashboard";

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
  it("retourne null pour data null ou undefined", () => {
    expect(safeValidateUserStats(null)).toBe(null);
    expect(safeValidateUserStats(undefined)).toBe(null);
  });

  it("retourne null pour data non-objet", () => {
    expect(safeValidateUserStats("string")).toBe(null);
    expect(safeValidateUserStats(42)).toBe(null);
    expect(safeValidateUserStats(true)).toBe(null);
  });

  it("retourne des valeurs par défaut pour champs obligatoires manquants", () => {
    const result = safeValidateUserStats({});
    expect(result).not.toBe(null);
    expect(result!.total_exercises).toBe(0);
    expect(result!.correct_answers).toBe(0);
  });

  it("préserve total_exercises et correct_answers quand fournis", () => {
    const result = safeValidateUserStats({
      total_exercises: 10,
      correct_answers: 8,
    });
    expect(result!.total_exercises).toBe(10);
    expect(result!.correct_answers).toBe(8);
  });

  it("ignore les reliquats legacy (level, xp, experience_points) — gamification via /me", () => {
    const result = safeValidateUserStats({
      total_exercises: 1,
      correct_answers: 1,
      level: { current: 3, title: "X", current_xp: 1, next_level_xp: 100 },
      xp: 99,
      experience_points: 1234,
    });
    expect(result).not.toBe(null);
    expect("level" in (result as object)).toBe(false);
    expect("xp" in (result as object)).toBe(false);
    expect("experience_points" in (result as object)).toBe(false);
  });

  it("valide progress_over_time si labels et datasets sont des tableaux", () => {
    const data = {
      total_exercises: 0,
      correct_answers: 0,
      progress_over_time: {
        labels: ["Sem1", "Sem2"],
        datasets: [{ label: "Exercices", data: [5, 8] }],
      },
    };
    const result = safeValidateUserStats(data);
    expect(result!.progress_over_time).toEqual(data.progress_over_time);
  });

  it("ignore progress_over_time si structure invalide", () => {
    const result = safeValidateUserStats({
      total_exercises: 0,
      correct_answers: 0,
      progress_over_time: { labels: "not-array" },
    });
    expect(result!.progress_over_time).toBeUndefined();
  });

  it("valide exercises_by_day si labels et datasets sont des tableaux", () => {
    const data = {
      total_exercises: 0,
      correct_answers: 0,
      exercises_by_day: {
        labels: ["Lun", "Mar"],
        datasets: [{ label: "Complétés", data: [2, 3] }],
      },
    };
    const result = safeValidateUserStats(data);
    expect(result!.exercises_by_day).toEqual(data.exercises_by_day);
  });

  it("préserve exercises_by_type et exercises_by_difficulty comme Record", () => {
    const result = safeValidateUserStats({
      total_exercises: 0,
      correct_answers: 0,
      exercises_by_type: { fractions: 5, geometry: 3 },
      exercises_by_difficulty: { easy: 10, medium: 4 },
    });
    expect(result!.exercises_by_type).toEqual({ fractions: 5, geometry: 3 });
    expect(result!.exercises_by_difficulty).toEqual({ easy: 10, medium: 4 });
  });

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
