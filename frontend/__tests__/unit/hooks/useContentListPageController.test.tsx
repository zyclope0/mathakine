import { renderHook, act } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { CONTENT_LIST_ORDER } from "@/lib/constants/contentListOrder";
import { useContentListPageController } from "@/hooks/useContentListPageController";
import { STORAGE_KEYS } from "@/lib/storage";
import * as storage from "@/lib/storage";

describe("useContentListPageController", () => {
  beforeEach(() => {
    vi.spyOn(window, "scrollTo").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("initializes with default filter and view state", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    expect(result.current.typeFilter).toBe("all");
    expect(result.current.ageFilter).toBe("all");
    expect(result.current.searchQuery).toBe("");
    expect(result.current.filtersPanelOpen).toBe(false);
    expect(result.current.hideCompleted).toBe(false);
    expect(result.current.selectedItemId).toBeNull();
    expect(result.current.isModalOpen).toBe(false);
    expect(result.current.currentPage).toBe(1);
    expect(result.current.viewMode).toBe("grid");
  });

  it("has hasActiveFilters false and advancedActiveCount 0 by default", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefChallengeOrder })
    );

    expect(result.current.hasActiveFilters).toBe(false);
    expect(result.current.advancedActiveCount).toBe(0);
  });

  it("handleFilterChange resets current page to 1", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.setCurrentPage(4);
    });
    expect(result.current.currentPage).toBe(4);

    act(() => {
      result.current.handleFilterChange();
    });
    expect(result.current.currentPage).toBe(1);
  });

  it("clearFilters resets type, age, search, order, hideCompleted, and page", () => {
    const setLocalSpy = vi.spyOn(storage, "setLocalString").mockImplementation(() => {});
    const removeSpy = vi.spyOn(storage, "removeLocalKey").mockImplementation(() => {});

    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.setTypeFilter("algebra");
      result.current.setAgeFilter("8-10");
      result.current.setSearchQuery("foo");
      result.current.setHideCompleted(true);
      result.current.setCurrentPage(3);
      result.current.handleOrderChange(CONTENT_LIST_ORDER.RECENT);
    });

    act(() => {
      result.current.clearFilters();
    });

    expect(result.current.typeFilter).toBe("all");
    expect(result.current.ageFilter).toBe("all");
    expect(result.current.searchQuery).toBe("");
    expect(result.current.hideCompleted).toBe(false);
    expect(result.current.currentPage).toBe(1);
    expect(result.current.orderFilter).toBe(CONTENT_LIST_ORDER.RANDOM);
    expect(removeSpy).toHaveBeenCalledWith(STORAGE_KEYS.prefExerciseOrder);

    setLocalSpy.mockRestore();
    removeSpy.mockRestore();
  });

  it("openItem opens modal and sets selectedItemId", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.openItem(42);
    });

    expect(result.current.selectedItemId).toBe(42);
    expect(result.current.isModalOpen).toBe(true);
  });

  it("closeModal closes modal and clears selectedItemId", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.openItem(7);
    });
    act(() => {
      result.current.closeModal();
    });

    expect(result.current.isModalOpen).toBe(false);
    expect(result.current.selectedItemId).toBeNull();
  });

  it("handleModalOpenChange(false) clears selection like closeModal", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.openItem(99);
    });
    act(() => {
      result.current.handleModalOpenChange(false);
    });

    expect(result.current.isModalOpen).toBe(false);
    expect(result.current.selectedItemId).toBeNull();
  });

  it("persists order via storage key when handleOrderChange runs", () => {
    const setLocalSpy = vi.spyOn(storage, "setLocalString").mockImplementation(() => {});

    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefChallengeOrder })
    );

    act(() => {
      result.current.handleOrderChange(CONTENT_LIST_ORDER.RECENT);
    });

    expect(setLocalSpy).toHaveBeenCalledWith(
      STORAGE_KEYS.prefChallengeOrder,
      CONTENT_LIST_ORDER.RECENT
    );

    setLocalSpy.mockRestore();
  });

  it("clearTypeFilter resets type to all and resets page", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.setTypeFilter("geometry");
      result.current.setCurrentPage(2);
    });

    act(() => {
      result.current.clearTypeFilter();
    });

    expect(result.current.typeFilter).toBe("all");
    expect(result.current.currentPage).toBe(1);
  });

  it("clearAgeFilter resets age to all and resets page", () => {
    const { result } = renderHook(() =>
      useContentListPageController({ orderPreferenceStorageKey: STORAGE_KEYS.prefExerciseOrder })
    );

    act(() => {
      result.current.setAgeFilter("12-14");
      result.current.setCurrentPage(5);
    });

    act(() => {
      result.current.clearAgeFilter();
    });

    expect(result.current.ageFilter).toBe("all");
    expect(result.current.currentPage).toBe(1);
  });
});
