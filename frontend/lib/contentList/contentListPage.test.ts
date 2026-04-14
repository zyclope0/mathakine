import { describe, expect, it } from "vitest";
import {
  CONTENT_LIST_ORDER,
  isValidStoredContentListOrder,
} from "../constants/contentListOrder";
import {
  contentListAdvancedFilterActiveCount,
  contentListTotalPages,
  hasActiveContentListFilters,
} from "./pageHelpers";

describe("isValidStoredContentListOrder", () => {
  it("accepts API order strings", () => {
    expect(isValidStoredContentListOrder(CONTENT_LIST_ORDER.RANDOM)).toBe(true);
    expect(isValidStoredContentListOrder(CONTENT_LIST_ORDER.RECENT)).toBe(true);
  });

  it("rejects unknown or null", () => {
    expect(isValidStoredContentListOrder("bogus")).toBe(false);
    expect(isValidStoredContentListOrder(null)).toBe(false);
  });
});

describe("contentListTotalPages", () => {
  it("returns at least one page", () => {
    expect(contentListTotalPages(0, 15)).toBe(1);
    expect(contentListTotalPages(1, 15)).toBe(1);
    expect(contentListTotalPages(15, 15)).toBe(1);
    expect(contentListTotalPages(16, 15)).toBe(2);
  });
});

describe("hasActiveContentListFilters", () => {
  const base = {
    typeFilter: "all",
    ageFilter: "all",
    searchQuery: "",
    orderFilter: CONTENT_LIST_ORDER.RANDOM,
    hideCompleted: false,
  };

  it("is false when all defaults", () => {
    expect(hasActiveContentListFilters(base)).toBe(false);
  });

  it("detects non-default order", () => {
    expect(hasActiveContentListFilters({ ...base, orderFilter: CONTENT_LIST_ORDER.RECENT })).toBe(
      true
    );
  });

  it("detects hide completed", () => {
    expect(hasActiveContentListFilters({ ...base, hideCompleted: true })).toBe(true);
  });
});

describe("contentListAdvancedFilterActiveCount", () => {
  it("counts type and age when set", () => {
    expect(contentListAdvancedFilterActiveCount("all", "all")).toBe(0);
    expect(contentListAdvancedFilterActiveCount("x", "all")).toBe(1);
    expect(contentListAdvancedFilterActiveCount("all", "y")).toBe(1);
    expect(contentListAdvancedFilterActiveCount("x", "y")).toBe(2);
  });
});
