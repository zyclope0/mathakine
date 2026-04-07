import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { Puzzle } from "lucide-react";
import { ContentListResultsSection } from "@/components/shared/ContentListResultsSection";
import fr from "@/messages/fr.json";

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

const baseProps = {
  isLoading: false,
  error: null,
  errorTitle: "Erreur titre",
  errorDescription: "Erreur desc",
  loadingLabel: "Chargement liste",
  listHeaderTitle: "3 éléments",
  itemCount: 2,
  emptyTitle: "Vide",
  emptyDescription: "Indice",
  viewMode: "grid" as const,
  onViewModeChange: vi.fn(),
  ariaLabelGrid: "Grille",
  ariaLabelList: "Liste",
  renderGrid: () => <div data-testid="grid-body">grid</div>,
  renderList: () => <div data-testid="list-body">list</div>,
  totalPages: 1,
  currentPage: 1,
  onPageChange: vi.fn(),
  itemsPerPage: 15,
  totalItems: 2,
};

describe("ContentListResultsSection", () => {
  it("shows loading skeleton with expected accessible status", () => {
    render(
      <Wrapper>
        <ContentListResultsSection {...baseProps} isLoading itemCount={0} listHeaderTitle="" />
      </Wrapper>
    );
    expect(screen.getByRole("status", { name: "Chargement liste" })).toBeInTheDocument();
  });

  it("shows error EmptyState", () => {
    render(
      <Wrapper>
        <ContentListResultsSection
          {...baseProps}
          error={new Error("fail")}
          itemCount={0}
          listHeaderTitle=""
        />
      </Wrapper>
    );
    expect(screen.getByText("Erreur titre")).toBeInTheDocument();
    expect(screen.getByText("Erreur desc")).toBeInTheDocument();
  });

  it("shows empty EmptyState when not loading and no items", () => {
    render(
      <Wrapper>
        <ContentListResultsSection {...baseProps} itemCount={0} listHeaderTitle="" />
      </Wrapper>
    );
    expect(screen.getByText("Vide")).toBeInTheDocument();
    expect(screen.getByText("Indice")).toBeInTheDocument();
  });

  it("renders optional icons on empty and error states", () => {
    const { rerender } = render(
      <Wrapper>
        <ContentListResultsSection
          {...baseProps}
          itemCount={0}
          listHeaderTitle=""
          emptyIcon={Puzzle}
        />
      </Wrapper>
    );
    expect(document.querySelector("svg")).toBeTruthy();

    rerender(
      <Wrapper>
        <ContentListResultsSection
          {...baseProps}
          error={new Error("x")}
          itemCount={0}
          listHeaderTitle=""
          errorIcon={Puzzle}
        />
      </Wrapper>
    );
    expect(document.querySelectorAll("svg").length).toBeGreaterThanOrEqual(1);
  });

  it("uses renderGrid in grid mode when items exist", () => {
    render(
      <Wrapper>
        <ContentListResultsSection {...baseProps} />
      </Wrapper>
    );
    expect(screen.getByTestId("grid-body")).toBeInTheDocument();
    expect(screen.queryByTestId("list-body")).not.toBeInTheDocument();
  });

  it("uses renderList in list mode when items exist", () => {
    render(
      <Wrapper>
        <ContentListResultsSection {...baseProps} viewMode="list" />
      </Wrapper>
    );
    expect(screen.getByTestId("list-body")).toBeInTheDocument();
    expect(screen.queryByTestId("grid-body")).not.toBeInTheDocument();
  });

  it("shows pagination only when totalPages > 1", () => {
    const { rerender } = render(
      <Wrapper>
        <ContentListResultsSection {...baseProps} totalPages={1} />
      </Wrapper>
    );
    expect(screen.queryByRole("navigation", { name: "Pagination" })).not.toBeInTheDocument();

    rerender(
      <Wrapper>
        <ContentListResultsSection {...baseProps} totalPages={3} currentPage={2} />
      </Wrapper>
    );
    expect(screen.getByRole("navigation", { name: "Pagination" })).toBeInTheDocument();
  });
});
