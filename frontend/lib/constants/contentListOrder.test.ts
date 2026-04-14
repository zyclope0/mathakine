import { describe, expect, it } from "vitest";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "./contentListOrder";

/** Contrat API `order` (exercices / défis paginés). */
describe("CONTENT_LIST_ORDER", () => {
  it("expose random et recent alignés backend", () => {
    expect(CONTENT_LIST_ORDER.RANDOM).toBe("random");
    expect(CONTENT_LIST_ORDER.RECENT).toBe("recent");
    const _check: ContentListOrder[] = [CONTENT_LIST_ORDER.RANDOM, CONTENT_LIST_ORDER.RECENT];
    expect(_check).toHaveLength(2);
  });
});
