import { describe, it, expect, vi, beforeEach } from "vitest";
import { render } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";

import { PuzzleRenderer } from "@/components/challenges/visualizations/PuzzleRenderer";
import { SequenceRenderer } from "@/components/challenges/visualizations/SequenceRenderer";
import { RiddleRenderer } from "@/components/challenges/visualizations/RiddleRenderer";
import { DeductionRenderer } from "@/components/challenges/visualizations/DeductionRenderer";
import { CodingRenderer } from "@/components/challenges/visualizations/CodingRenderer";
import { ProbabilityRenderer } from "@/components/challenges/visualizations/ProbabilityRenderer";
import { VisualRenderer } from "@/components/challenges/visualizations/VisualRenderer";
import frMessages from "@/messages/fr.json";

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({ shouldReduceMotion: false }),
}));

beforeEach(() => {
  window.requestAnimationFrame = vi.fn((cb: FrameRequestCallback) => {
    cb(0);
    return 1;
  });
  window.cancelAnimationFrame = vi.fn();
});

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

function withIntl(children: React.ReactNode): React.ReactElement {
  return (
    <NextIntlClientProvider locale="fr" messages={frMessages}>
      {children as React.ReactElement}
    </NextIntlClientProvider>
  );
}

describe("Contrat d'affichage unifié — aucune repr brute dans l'UI", () => {
  it("PuzzleRenderer : pieces avec {id, left, right} — displayLabel expose le contenu pédagogique (défi #4071)", () => {
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
    // Les id restent visibles (clé d'ordre pour correct_answer).
    expect(container.textContent).toContain("P1");
    expect(container.textContent).toContain("P2");
    expect(container.textContent).toContain("P3");
    // Le contenu pédagogique (left/right) DOIT être visible sinon le puzzle
    // devient insoluble — regression guard pour le défi #4071.
    expect(container.textContent).toContain("11 ↔ 13");
    expect(container.textContent).toContain("3 ↔ 5");
    expect(container.textContent).toContain("17 ↔ 19");
    expect(container.textContent).toContain("Départ au plus petit premier.");
  });

  it("PuzzleRenderer : onOrderChange reçoit les ids courts, JAMAIS les displayLabel (contrat correct_answer)", async () => {
    // Régression garde : correct_answer côté backend compare sur les ids
    // courts ("P1, P2, ..."). Si le front envoie les displayLabel riches
    // ("P1 · 11 ↔ 13, P2 · 3 ↔ 5, ..."), la validation échoue silencieusement.
    const handler = vi.fn();
    render(
      withIntl(
        <PuzzleRenderer
          visualData={{
            pieces: [
              { id: "P1", left: "11", right: "13" },
              { id: "P2", left: "3", right: "5" },
              { id: "P3", left: "17", right: "19" },
            ],
          }}
          onOrderChange={handler}
        />
      )
    );
    // Flush microtasks (queueMicrotask dans le mount effect).
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    expect(handler).toHaveBeenCalled();
    const lastCall = handler.mock.calls[handler.mock.calls.length - 1]?.[0];
    expect(lastCall).toEqual(["P1", "P2", "P3"]);
  });

  it("PuzzleRenderer : orderKey reste l'id même si 'name' éditorial présent (miroir #4071)", async () => {
    // Miroir du bug #4071 : itemLabel classique prioriserait ``name`` avant
    // ``id`` (ordre officiel). Le backend attend des ids courts → il FAUT
    // que orderKey soit "P1", pas "paire première".
    const handler = vi.fn();
    render(
      withIntl(
        <PuzzleRenderer
          visualData={{
            pieces: [
              { id: "P1", name: "paire première", left: "11", right: "13" },
              { id: "P2", name: "paire seconde", left: "3", right: "5" },
            ],
          }}
          onOrderChange={handler}
        />
      )
    );
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    const lastCall = handler.mock.calls[handler.mock.calls.length - 1]?.[0];
    expect(lastCall).toEqual(["P1", "P2"]);
  });

  it("PuzzleRenderer : pieces avec {id, pattern} — displayLabel expose le pattern", () => {
    const { container } = render(
      withIntl(
        <PuzzleRenderer
          visualData={{
            pieces: [
              { id: "A", pattern: ["NW: rouge", "NE: vide"] },
              { id: "B", pattern: ["NW: bleu", "NE: rouge"] },
            ],
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("B");
    expect(container.textContent).toContain("NW: rouge");
    expect(container.textContent).toContain("NW: bleu");
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

  it("DeductionRenderer : entities/attributes arrays mixtes", () => {
    const { container } = render(
      withIntl(
        <DeductionRenderer
          visualData={{
            entities: [
              "Alice",
              { name: "Bob" },
              { value: "Claire" },
              { id: "D" },
              { payload: "nope" },
            ],
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("Claire");
    expect(container.textContent).toContain("D");
  });

  it("DeductionRenderer : logic grid avec entities objet", () => {
    const { container } = render(
      withIntl(
        <DeductionRenderer
          visualData={{
            type: "logic_grid",
            entities: {
              eleves: [{ name: "Alice" }, { name: "Bob" }, { id: "Z" }],
              matieres: ["Maths", { label: "Physique" }],
            },
            clues: ["Clue 1."],
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Alice");
    expect(container.textContent).toContain("Bob");
    expect(container.textContent).toContain("Z");
    expect(container.textContent).toContain("Physique");
  });

  it("CodingRenderer : fallback meta/arrays objet — pas de leak", () => {
    const { container } = render(
      <CodingRenderer
        visualData={{
          custom_field: [{ name: "Alpha" }, { id: "Beta" }, "plain", { foo: "bar" }],
          summary: { label: "Résumé" },
        }}
      />
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Alpha");
    expect(container.textContent).toContain("Beta");
    expect(container.textContent).toContain("Résumé");
  });

  it("ProbabilityRenderer : fallback propriété objet — pas de leak", () => {
    const { container } = render(
      withIntl(
        <ProbabilityRenderer
          visualData={{
            // Type inconnu → chemin fallback Object.entries qui rendait JSON.
            custom_meta: { label: "Détails d'urne" },
            tag: { name: "Tag principal" },
          }}
        />
      )
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Détails d'urne");
    expect(container.textContent).toContain("Tag principal");
  });

  it("VisualRenderer mode rawData : pas de leak JSON dans les valeurs objet", () => {
    const { container } = render(
      <VisualRenderer
        visualData={{
          // Pas de grid/shapes/layout → fallback rawData.
          meta: { label: "Contexte A" },
          note: { name: "Observation B" },
          legend: { id: "L1" },
        }}
      />
    );
    expectNoRawLeak(container);
    expect(container.textContent).toContain("Contexte A");
    expect(container.textContent).toContain("Observation B");
    expect(container.textContent).toContain("L1");
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
