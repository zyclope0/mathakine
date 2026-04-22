import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";

import { PuzzleRenderer } from "@/components/challenges/visualizations/PuzzleRenderer";
import { SequenceRenderer } from "@/components/challenges/visualizations/SequenceRenderer";
import { RiddleRenderer } from "@/components/challenges/visualizations/RiddleRenderer";

/**
 * Lot M étape 1 — anti-régression globale.
 *
 * Les items/pieces/clues produits par le LLM peuvent arriver sous plusieurs
 * formes (string / objet `{id,...}` / objet `{label,...}` / objet avec champs
 * métier exotiques). Aucun renderer ne doit jamais afficher une repr brute
 * (`{'id'...}`, `{"id"...}`, `[object Object]`) dans le DOM rendu.
 */

const BANNED_PATTERNS = [/\{\s*['"]id['"]/, /\[object Object\]/];

function expectNoRawLeak(container: Element): void {
  const text = container.textContent ?? "";
  for (const pattern of BANNED_PATTERNS) {
    expect(text).not.toMatch(pattern);
  }
}

const messages = {
  challenges: {
    visualizations: {
      puzzle: { hintsHeading: "Indices" },
    },
  },
} as const;

function withIntl(children: React.ReactNode): React.ReactElement {
  return (
    <NextIntlClientProvider locale="fr" messages={messages}>
      {children as React.ReactElement}
    </NextIntlClientProvider>
  );
}

describe("Contrat d'affichage unifié — aucune repr brute dans l'UI", () => {
  it("PuzzleRenderer : pieces avec {id} (contrat LLM puzzle 4070-bis)", () => {
    const { container } = render(
      withIntl(
        <PuzzleRenderer
          visualData={{
            pieces: [
              { id: "P1", left: "11", right: "13" },
              { id: "P2", left: "3", right: "5" },
              { id: "P3", left: "17", right: "19" },
            ],
            hints: [
              "Chaque côté droit rejoint le côté gauche suivant.",
              { text: "Départ au plus petit premier." },
            ],
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("P1");
    expect(container.textContent).toContain("P2");
    expect(container.textContent).toContain("P3");
    expect(container.textContent).toContain("Départ au plus petit premier.");
  });

  it("PuzzleRenderer : pieces mixtes string + label + id", () => {
    const { container } = render(
      withIntl(
        <PuzzleRenderer
          visualData={{
            pieces: ["Alpha", { label: "Beta" }, { value: 3 }, { id: "Gamma" }, { foo: "bar" }],
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Alpha");
    expect(container.textContent).toContain("Beta");
    expect(container.textContent).toContain("Gamma");
    // Fallback visible pour l'item sans champ reconnu : numérotation seulement,
    // jamais ``{'foo'`` ni ``[object Object]``.
    expect(container.textContent).toContain("#5");
  });

  it("SequenceRenderer : items mixtes (string/number/objet)", () => {
    const { container } = render(
      <SequenceRenderer
        visualData={{
          sequence: [
            2,
            { value: 4 },
            { label: "six" },
            { id: "X" },
            "10",
            { unknown_field: "leak ?" },
          ],
        }}
      />
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("six");
    expect(container.textContent).toContain("X");
  });

  it("RiddleRenderer : clues avec objets text/description/id", () => {
    const { container } = render(
      <RiddleRenderer
        visualData={{
          clues: [
            "Indice plat.",
            { text: "Indice avec text." },
            { description: "Indice avec description." },
            { id: "clue-3" },
            { payload: "nope" },
          ],
          hints: [{ value: "hint-object" }, "hint plat"],
        }}
      />
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Indice plat.");
    expect(container.textContent).toContain("Indice avec text.");
    expect(container.textContent).toContain("Indice avec description.");
    expect(container.textContent).toContain("clue-3");
  });
});
