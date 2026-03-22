import type { ComponentProps } from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AIGeneratorBase } from "@/components/shared/AIGeneratorBase";

function renderCompact(overrides: Partial<ComponentProps<typeof AIGeneratorBase>> = {}) {
  const onView = vi.fn();
  const props = {
    compact: true,
    title: "IA",
    description: "Desc",
    typeLabel: "Type",
    typeSelectId: "t",
    ageLabel: "Âge",
    promptLabel: "Prompt",
    promptPlaceholder: "…",
    generateLabel: "Générer",
    generatingLabel: "…",
    cancelLabel: "Annuler",
    viewItemLabel: "Voir la ressource",
    successLabel: "Succès",
    closeAriaLabel: "Fermer",
    typeOptions: [{ value: "a", label: "A" }],
    defaultType: "a",
    ageOptions: [{ value: "6-8", label: "6-8" }],
    defaultAge: "6-8",
    isGenerating: false,
    streamedText: "",
    generatedItem: null,
    onGenerate: vi.fn(),
    onCancel: vi.fn(),
    onViewItem: onView,
    onDismissResult: vi.fn(),
    isAuthenticated: true,
    ...overrides,
  } satisfies ComponentProps<typeof AIGeneratorBase>;
  render(<AIGeneratorBase {...props} />);
  return { onView };
}

describe("AIGeneratorBase — CTA fin de génération", () => {
  it("affiche le bouton Voir lorsque l'id persisté est présent", () => {
    const { onView } = renderCompact({
      generatedItem: { id: 12, title: "Exo créé" },
    });
    const btn = screen.getByRole("button", { name: "Voir la ressource" });
    expect(btn).toBeTruthy();
    fireEvent.click(btn);
    expect(onView).toHaveBeenCalledTimes(1);
  });

  it("n'affiche pas le bouton Voir sans id (pas de faux accès direct)", () => {
    renderCompact({
      generatedItem: { title: "Sans id" },
    });
    expect(screen.queryByRole("button", { name: "Voir la ressource" })).toBeNull();
  });
});
