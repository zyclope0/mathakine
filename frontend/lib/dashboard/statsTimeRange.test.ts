import { describe, expect, it } from "vitest";
import { statsTimeRangeToMessageKey } from "./statsTimeRange";

describe("statsTimeRangeToMessageKey", () => {
  it("maps each TimeRange to dashboard.timeRange keys", () => {
    expect(statsTimeRangeToMessageKey("7")).toBe("7days");
    expect(statsTimeRangeToMessageKey("30")).toBe("30days");
    expect(statsTimeRangeToMessageKey("90")).toBe("90days");
    expect(statsTimeRangeToMessageKey("all")).toBe("all");
  });
});
