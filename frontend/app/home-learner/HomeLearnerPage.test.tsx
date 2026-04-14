/**
 * Smoke tests for app/home-learner/page.tsx composition (ARCH-HOME-LEARNER-01).
 * Asserts stable section ids and anchor hrefs; no product behavior change intended.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import React from "react";
import HomeLearnerPage from "./page";
import { EMPTY_SPACED_REPETITION } from "@/components/learner/homeLearnerConstants";

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string, params?: Record<string, unknown>) => {
    if (params) return `${key}(${JSON.stringify(params)})`;
    return key;
  },
  NextIntlClientProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

const mockUseAuth = vi.fn();
const mockUseProgressStats = vi.fn();
const mockUseUserStats = vi.fn();
const mockUseRecommendations = vi.fn();

vi.mock("@/hooks/useAuth", () => ({ useAuth: () => mockUseAuth() }));
vi.mock("@/hooks/useProgressStats", () => ({ useProgressStats: () => mockUseProgressStats() }));
vi.mock("@/hooks/useUserStats", () => ({ useUserStats: () => mockUseUserStats() }));
vi.mock("@/hooks/useRecommendations", () => ({
  useRecommendations: () => mockUseRecommendations(),
}));

vi.mock("@/components/dashboard/StudentChallengesBoard", () => ({
  StudentChallengesBoard: () => <div data-testid="student-challenges-board" />,
}));

vi.mock("@/components/dashboard/SpacedRepetitionSummaryWidget", () => ({
  SpacedRepetitionSummaryWidget: () => <div data-testid="spaced-repetition-widget" />,
}));

vi.mock("@/components/dashboard/StreakWidget", () => ({
  StreakWidget: () => <div data-testid="streak-widget" />,
}));

vi.mock("@/components/dashboard/LevelIndicator", () => ({
  LevelIndicator: () => <div data-testid="level-indicator" />,
}));

vi.mock("@/components/dashboard/LevelEstablishedWidget", () => ({
  LevelEstablishedWidget: () => <div data-testid="level-established-widget" />,
}));

function makeDefaultAuth(overrides: Record<string, unknown> = {}) {
  return {
    user: {
      full_name: "Test Learner",
      username: "testlearner",
      gamification_level: {
        current: 2,
        current_xp: 10,
        next_level_xp: 100,
      },
    },
    ...overrides,
  };
}

function makeDefaultUserStats(overrides: Record<string, unknown> = {}) {
  return {
    stats: {
      total_exercises: 0,
      correct_answers: 0,
      spaced_repetition: { ...EMPTY_SPACED_REPETITION },
    },
    isLoading: false,
    error: null,
    refetch: vi.fn(),
    ...overrides,
  };
}

describe("HomeLearnerPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseAuth.mockReturnValue(makeDefaultAuth());
    mockUseProgressStats.mockReturnValue({
      data: { current_streak: 0, highest_streak: 0 },
      isLoading: false,
    });
    mockUseUserStats.mockReturnValue(makeDefaultUserStats());
    mockUseRecommendations.mockReturnValue({
      recommendations: [],
      isLoading: false,
      recordOpen: vi.fn(),
    });
  });

  it("renders core section ids for in-page navigation", () => {
    const { container } = render(<HomeLearnerPage />);

    expect(container.querySelector("#section-actions")).toBeTruthy();
    expect(container.querySelector("#section-reviews")).toBeTruthy();
    expect(container.querySelector("#section-challenges")).toBeTruthy();
    expect(container.querySelector("#section-progress")).toBeTruthy();
  });

  it("renders page-map anchor hrefs matching section ids (default order: actions before reviews)", () => {
    render(<HomeLearnerPage />);

    const nav = screen.getByRole("navigation", { name: "pageMap.label" });
    const links = within(nav).getAllByRole("link");
    const hrefs = links.map((a) => a.getAttribute("href"));

    expect(hrefs).toContain("#section-actions");
    expect(hrefs).toContain("#section-reviews");
    expect(hrefs).toContain("#section-challenges");
    expect(hrefs).toContain("#section-progress");

    const actionsIdx = hrefs.indexOf("#section-actions");
    const reviewsIdx = hrefs.indexOf("#section-reviews");
    expect(actionsIdx).toBeLessThan(reviewsIdx);
  });

  it("places reviews before actions in DOM when urgent reviews are present", () => {
    mockUseUserStats.mockReturnValue(
      makeDefaultUserStats({
        stats: {
          total_exercises: 0,
          correct_answers: 0,
          spaced_repetition: {
            ...EMPTY_SPACED_REPETITION,
            due_today_count: 1,
          },
        },
      })
    );

    const { container } = render(<HomeLearnerPage />);

    const reviews = container.querySelector("#section-reviews");
    const actions = container.querySelector("#section-actions");
    expect(reviews).toBeTruthy();
    expect(actions).toBeTruthy();
    const pos = reviews!.compareDocumentPosition(actions!);
    expect(pos & Node.DOCUMENT_POSITION_FOLLOWING).toBe(Node.DOCUMENT_POSITION_FOLLOWING);
  });

  it("lists reviews anchor before actions in the page map when urgent reviews are present", () => {
    mockUseUserStats.mockReturnValue(
      makeDefaultUserStats({
        stats: {
          total_exercises: 0,
          correct_answers: 0,
          spaced_repetition: {
            ...EMPTY_SPACED_REPETITION,
            overdue_count: 1,
          },
        },
      })
    );

    render(<HomeLearnerPage />);

    const nav = screen.getByRole("navigation", { name: "pageMap.label" });
    const links = within(nav).getAllByRole("link");
    const hrefs = links.map((a) => a.getAttribute("href"));

    expect(hrefs.indexOf("#section-reviews")).toBeLessThan(hrefs.indexOf("#section-actions"));
  });
});
