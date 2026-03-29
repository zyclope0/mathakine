import { describe, it, expect } from "vitest";
import {
  challengeToAIGeneratedItem,
  exerciseToAIGeneratedItem,
} from "@/lib/ai/generation/toAIGeneratedItem";

describe("toAIGeneratedItem", () => {
  it("maps exercise with persisted id and subtitle", () => {
    expect(
      exerciseToAIGeneratedItem({
        id: 7,
        title: "T",
        question: "Q?",
      })
    ).toEqual({ id: 7, title: "T", subtitle: "Q?" });
  });

  it("omits id when exercise id is not persistable", () => {
    expect(
      exerciseToAIGeneratedItem({
        id: 0,
        title: "T",
        question: null,
      })
    ).toEqual({ title: "T" });
  });

  it("maps challenge with persisted id", () => {
    expect(challengeToAIGeneratedItem({ id: 3, title: "C" })).toEqual({ id: 3, title: "C" });
  });

  it("returns null for null resource", () => {
    expect(exerciseToAIGeneratedItem(null)).toBeNull();
    expect(challengeToAIGeneratedItem(null)).toBeNull();
  });
});
