import { useState } from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  ContentListProgressiveFilterToolbar,
  type ContentListFilterToolbarLabels,
} from "@/components/shared/ContentListProgressiveFilterToolbar";
import { AGE_GROUPS, EXERCISE_TYPE_STYLES } from "@/lib/constants/exercises";
import { CONTENT_LIST_ORDER, type ContentListOrder } from "@/lib/constants/contentListOrder";
import { contentListAdvancedFilterActiveCount } from "@/lib/contentList/pageHelpers";

const noop = () => {};

const labels: ContentListFilterToolbarLabels = {
  filterButton: "Plus de filtres",
  filterButtonAriaExpand: "Afficher filtres avancés",
  filterButtonAriaCollapse: "Masquer filtres avancés",
  advancedRegionLabel: "Filtres avancés",
  reset: "Réinitialiser",
  typeHeading: "Type d'exercice",
  allTypes: "Tous les types",
  ageGroup: "Tranche d'âge",
  allAgesPlaceholder: "Tous les âges",
  orderLabel: "Tri",
  orderAria: "Tri",
  orderRandom: "Aléatoire",
  orderRecent: "Plus récents",
  hideCompleted: "Masquer les réussis",
  searchPlaceholder: "Rechercher",
  searchAriaLabel: "Rechercher",
  activeFiltersSummary: "Critères actifs",
  removeTypeChip: "Retirer le type",
  removeAgeChip: "Retirer l'âge",
};

function ToolbarHarness({
  initialAdvancedCount = 0,
  initialOrder = CONTENT_LIST_ORDER.RANDOM,
  initialHideCompleted = false,
}: {
  initialAdvancedCount?: number;
  initialOrder?: ContentListOrder;
  initialHideCompleted?: boolean;
}) {
  const [panelOpen, setPanelOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [ageFilter, setAgeFilter] = useState("all");
  const [order, setOrder] = useState<ContentListOrder>(initialOrder);
  const [hideCompleted, setHideCompleted] = useState(initialHideCompleted);

  return (
    <ContentListProgressiveFilterToolbar
      labels={labels}
      searchQuery={searchQuery}
      onSearchChange={setSearchQuery}
      onSearchPageReset={noop}
      panelOpen={panelOpen}
      onPanelOpenChange={setPanelOpen}
      typeFilterValue={typeFilter}
      onTypeFilterChange={setTypeFilter}
      typeStyles={EXERCISE_TYPE_STYLES}
      ageFilterValue={ageFilter}
      onAgeFilterChange={setAgeFilter}
      ageGroupValues={Object.values(AGE_GROUPS)}
      orderValue={order}
      onOrderChange={setOrder}
      hideCompleted={hideCompleted}
      onHideCompletedChange={setHideCompleted}
      hideCompletedFieldId="hide-test"
      getTypeDisplay={(k) => k}
      getAgeDisplay={(k) => k}
      onResetAll={noop}
      onFilterAdjust={noop}
      onClearTypeFilter={noop}
      onClearAgeFilter={noop}
      hasResettableState={false}
      advancedActiveCount={initialAdvancedCount}
    />
  );
}

describe("ContentListProgressiveFilterToolbar", () => {
  it("bouton 'Plus de filtres' pilote aria-expanded et aria-controls vers le panneau", async () => {
    const user = userEvent.setup();
    render(<ToolbarHarness />);

    const toggle = screen.getByRole("button", { expanded: false });
    const controls = toggle.getAttribute("aria-controls");
    expect(controls).toBeTruthy();

    await user.click(toggle);

    expect(screen.getByRole("button", { expanded: true })).toBeInTheDocument();
    const region = screen.getByRole("region", { name: labels.advancedRegionLabel });
    expect(region).toHaveAttribute("id", controls);
  });

  it("affiche le tri et masquer-réussis dans le panneau avancé (pas sur la ligne principale)", async () => {
    const user = userEvent.setup();
    render(<ToolbarHarness />);

    // Avant ouverture : le select Tri ne doit pas être visible
    expect(screen.queryByLabelText("Tri")).not.toBeVisible();

    // Ouvrir le panneau
    await user.click(screen.getByRole("button", { name: /Plus de filtres/ }));

    // Après ouverture : le select Tri et le switch masquer-réussis sont présents
    expect(screen.getByLabelText("Tri")).toBeVisible();
    expect(screen.getByLabelText("Masquer les réussis")).toBeVisible();
  });

  it("affiche le badge quand advancedActiveCount > 0", () => {
    render(<ToolbarHarness initialAdvancedCount={2} />);
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("n'affiche pas de badge quand advancedActiveCount = 0", () => {
    render(<ToolbarHarness initialAdvancedCount={0} />);
    expect(screen.queryByText("0")).not.toBeInTheDocument();
  });

  it("n'affiche pas le <p> de résumé état quand ordre=aléatoire et hideCompleted=false", () => {
    const { container } = render(<ToolbarHarness />);
    expect(container.querySelector("p[aria-live]")).not.toBeInTheDocument();
  });

  it("affiche le résumé état 'Plus récents' dans le <p> quand panneau fermé et ordre=recent", () => {
    const { container } = render(<ToolbarHarness initialOrder={CONTENT_LIST_ORDER.RECENT} />);
    const summary = container.querySelector("p[aria-live]");
    expect(summary).toBeInTheDocument();
    expect(summary).toHaveTextContent("Plus récents");
  });

  it("affiche le résumé état dans le <p> quand hideCompleted=true", () => {
    const { container } = render(<ToolbarHarness initialHideCompleted />);
    const summary = container.querySelector("p[aria-live]");
    expect(summary).toBeInTheDocument();
    expect(summary).toHaveTextContent("Masquer les réussis");
  });

  it("n'affiche pas le <p> de résumé état quand le panneau est ouvert", async () => {
    const user = userEvent.setup();
    const { container } = render(<ToolbarHarness initialOrder={CONTENT_LIST_ORDER.RECENT} />);
    await user.click(screen.getByRole("button", { name: /Plus de filtres/ }));
    expect(container.querySelector("p[aria-live]")).not.toBeInTheDocument();
  });
});

describe("contentListAdvancedFilterActiveCount", () => {
  it("retourne 0 quand tout est à l'état par défaut", () => {
    expect(
      contentListAdvancedFilterActiveCount("all", "all", CONTENT_LIST_ORDER.RANDOM, false)
    ).toBe(0);
  });

  it("compte le filtre type actif", () => {
    expect(
      contentListAdvancedFilterActiveCount("addition", "all", CONTENT_LIST_ORDER.RANDOM, false)
    ).toBe(1);
  });

  it("compte le filtre âge actif", () => {
    expect(
      contentListAdvancedFilterActiveCount("all", "6-8", CONTENT_LIST_ORDER.RANDOM, false)
    ).toBe(1);
  });

  it("compte le tri non-aléatoire comme filtre actif", () => {
    expect(
      contentListAdvancedFilterActiveCount("all", "all", CONTENT_LIST_ORDER.RECENT, false)
    ).toBe(1);
  });

  it("compte hideCompleted=true comme filtre actif", () => {
    expect(
      contentListAdvancedFilterActiveCount("all", "all", CONTENT_LIST_ORDER.RANDOM, true)
    ).toBe(1);
  });

  it("cumule tous les filtres actifs simultanément", () => {
    expect(
      contentListAdvancedFilterActiveCount("addition", "6-8", CONTENT_LIST_ORDER.RECENT, true)
    ).toBe(4);
  });

  it("retourne 0 quand orderFilter est undefined (compatibilité ancienne signature)", () => {
    expect(contentListAdvancedFilterActiveCount("all", "all")).toBe(0);
  });
});
