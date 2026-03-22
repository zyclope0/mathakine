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

const noop = () => {};

const labels: ContentListFilterToolbarLabels = {
  filterButton: "Filtres",
  filterButtonAriaExpand: "Afficher filtres détaillés",
  filterButtonAriaCollapse: "Masquer filtres détaillés",
  advancedRegionLabel: "Filtres par type et par âge",
  reset: "Réinitialiser",
  typeHeading: "Type d'exercice",
  allTypes: "Tous les types",
  ageGroup: "Tranche d'âge",
  allAgesPlaceholder: "Tous les âges",
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

function ToolbarHarness() {
  const [panelOpen, setPanelOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [ageFilter, setAgeFilter] = useState("all");
  const [order, setOrder] = useState<ContentListOrder>(CONTENT_LIST_ORDER.RANDOM);
  const [hideCompleted, setHideCompleted] = useState(false);

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
      advancedActiveCount={0}
    />
  );
}

describe("ContentListProgressiveFilterToolbar", () => {
  it("bouton Filtres pilote aria-expanded et aria-controls vers le panneau", async () => {
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
});
