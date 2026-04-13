import type { ReactElement } from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";

function renderWithFr(ui: ReactElement) {
  return render(
    <NextIntlClientProvider locale="fr" messages={fr}>
      {ui}
    </NextIntlClientProvider>
  );
}

describe("LevelIndicator (F42-P3)", () => {
  it("affiche Niveau {n} comme titre principal, pas level.title API", () => {
    renderWithFr(
      <LevelIndicator
        level={{
          current: 6,
          title: "Commandant",
          current_xp: 10,
          next_level_xp: 100,
          jedi_rank: "explorer",
        }}
      />
    );

    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent("Niveau 6");
    expect(screen.queryByText("Commandant")).not.toBeInTheDocument();
    expect(screen.getByText(/Palier de progression\s*:/)).toBeInTheDocument();
    expect(screen.getByText("Explorateur")).toBeInTheDocument();
  });

  it("priorise progression_rank sur jedi_rank (F43-A3)", () => {
    renderWithFr(
      <LevelIndicator
        level={{
          current: 6,
          title: "X",
          current_xp: 10,
          next_level_xp: 100,
          jedi_rank: "cadet",
          progression_rank: "explorer",
        }}
      />
    );
    expect(screen.getByText("Explorateur")).toBeInTheDocument();
  });

  it("n'affiche pas le palier si jedi_rank est absent", () => {
    renderWithFr(
      <LevelIndicator
        level={{
          current: 2,
          title: "Éclaireur",
          current_xp: 0,
          next_level_xp: 100,
        }}
      />
    );

    expect(screen.getByRole("heading", { level: 3 })).toHaveTextContent("Niveau 2");
    expect(screen.queryByText(/Palier de progression/)).not.toBeInTheDocument();
    expect(screen.queryByText("Éclaireur")).not.toBeInTheDocument();
  });
});
