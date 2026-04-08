import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { BadgesProgressTabsSection } from "@/components/badges/BadgesProgressTabsSection";
import type { Badge } from "@/types/api";
import type { BadgeProgressItem } from "@/lib/badges/types";
import type { SortBy } from "@/lib/badges/badgesPage";

vi.mock("@/components/badges/BadgeGrid", () => ({
  BadgeGrid: () => <div data-testid="badge-grid-mock" />,
}));

const baseLabels = {
  tabsAriaLabel: "Tabs badges",
  formatTabInProgress: (count: number) => `En cours (${count})`,
  formatTabToUnlock: (count: number) => `À débloquer (${count})`,
  noInProgress: "Aucun en cours",
  noToUnlock: "Rien à débloquer",
  showLess: "Voir moins",
  formatShowMore: (n: number) => `Voir ${n} de plus`,
  formatSuccessRate: (args: { correct: number; total: number; rate: number }) =>
    `${args.correct}/${args.total} ${args.rate}%`,
  tuApproches: "Tu y es presque",
  formatPlusQueCorrect: (c: number) => `Encore ${c} bonnes réponses`,
  formatPlusQue: (c: number) => `Encore ${c}`,
};

function buildProps(overrides: Partial<Parameters<typeof BadgesProgressTabsSection>[0]> = {}) {
  return {
    inProgressWithTarget: [] as BadgeProgressItem[],
    filteredLocked: [] as Badge[],
    availableBadges: [] as Badge[],
    sortBy: "category" as SortBy,
    rarityMap: {},
    progressMap: {},
    activeTab: "inProgress",
    defaultTab: "inProgress",
    onTabChange: vi.fn(),
    toUnlockExpanded: false,
    onToUnlockToggle: vi.fn(),
    ...baseLabels,
    ...overrides,
  };
}

describe("BadgesProgressTabsSection", () => {
  it("renders nothing when both lists are empty", () => {
    const { container } = render(<BadgesProgressTabsSection {...buildProps()} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders tablist and empty in-progress panel", () => {
    const locked = [
      { id: 9, name: "L", code: "l9", difficulty: "bronze", category: "special", points_reward: 5 },
    ] as Badge[];
    render(
      <BadgesProgressTabsSection
        {...buildProps({
          filteredLocked: locked,
          availableBadges: locked,
        })}
      />
    );
    expect(screen.getByRole("tablist", { name: /Tabs badges/i })).toBeInTheDocument();
    expect(screen.getByText("Aucun en cours")).toBeInTheDocument();
  });

  it("renders in-progress cards using shared motivation helper output", () => {
    const item: BadgeProgressItem = {
      id: 1,
      code: "c1",
      name: "Progress name",
      target: 10,
      current: 8,
      progress: 0.8,
    };
    const full = {
      id: 1,
      name: "Progress name",
      code: "c1",
      difficulty: "silver",
      category: "mastery",
      points_reward: 10,
    } as Badge;
    render(
      <BadgesProgressTabsSection
        {...buildProps({
          inProgressWithTarget: [item],
          availableBadges: [full],
          filteredLocked: [full],
        })}
      />
    );
    expect(screen.getByText("Encore 2")).toBeInTheDocument();
  });

  it("mounts BadgeGrid for to-unlock tab content", () => {
    const locked = [
      { id: 2, name: "X", code: "x", difficulty: "gold", category: "special", points_reward: 20 },
    ] as Badge[];
    render(
      <BadgesProgressTabsSection
        {...buildProps({
          filteredLocked: locked,
          availableBadges: locked,
          activeTab: "toUnlock",
        })}
      />
    );
    expect(screen.getByTestId("badge-grid-mock")).toBeInTheDocument();
  });
});
