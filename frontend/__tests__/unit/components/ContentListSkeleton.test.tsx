import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ContentListSkeleton } from "@/components/shared/ContentListSkeleton";

describe("ContentListSkeleton", () => {
  it("expose un statut de chargement accessible en grille", () => {
    render(
      <ContentListSkeleton variant="grid" loadingLabel="Chargement des exercices" count={3} />
    );
    const region = screen.getByRole("status", { name: "Chargement des exercices" });
    expect(region).toHaveAttribute("aria-busy", "true");
  });

  it("fonctionne en variante liste", () => {
    render(<ContentListSkeleton variant="list" loadingLabel="Chargement" count={2} />);
    expect(screen.getByRole("status", { name: "Chargement" })).toBeInTheDocument();
  });
});
