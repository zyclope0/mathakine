import { describe, expect, it } from "vitest";
import { buildExercisePageFilters } from "./buildExercisePageFilters";
import { CONTENT_LIST_ORDER } from "../constants/contentListOrder";

describe("buildExercisePageFilters", () => {
  it("maps pagination and order", () => {
    const f = buildExercisePageFilters({
      itemsPerPage: 15,
      currentPage: 2,
      exerciseTypeFilter: "all",
      ageGroupFilter: "all",
      searchQuery: "",
      orderFilter: CONTENT_LIST_ORDER.RECENT,
      hideCompleted: true,
    });
    expect(f).toEqual({
      limit: 15,
      skip: 15,
      order: CONTENT_LIST_ORDER.RECENT,
      hide_completed: true,
    });
  });

  it("includes type, age, and trimmed search when set", () => {
    const f = buildExercisePageFilters({
      itemsPerPage: 15,
      currentPage: 1,
      exerciseTypeFilter: "addition",
      ageGroupFilter: "6-8",
      searchQuery: "  foo  ",
      orderFilter: CONTENT_LIST_ORDER.RANDOM,
      hideCompleted: false,
    });
    expect(f.exercise_type).toBe("addition");
    expect(f.age_group).toBe("6-8");
    expect(f.search).toBe("foo");
    expect(f.hide_completed).toBe(false);
  });
});
