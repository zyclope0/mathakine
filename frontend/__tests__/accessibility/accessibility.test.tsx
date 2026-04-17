import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { AccessibilityToolbar } from "@/components/accessibility/AccessibilityToolbar";
import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { vi } from "vitest";

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

// Mock store
vi.mock("@/lib/stores/accessibilityStore", () => ({
  useAccessibilityStore: vi.fn(),
}));

const mockStoreValue = {
  highContrast: false,
  largeText: false,
  reducedMotion: false,
  dyslexiaMode: false,
  focusMode: false,
  toggleHighContrast: vi.fn(),
  toggleLargeText: vi.fn(),
  toggleReducedMotion: vi.fn(),
  toggleDyslexiaMode: vi.fn(),
  toggleFocusMode: vi.fn(),
  resetAll: vi.fn(),
};

describe("AccessibilityToolbar", () => {
  it("affiche tous les boutons d'accessibilité", async () => {
    vi.mocked(useAccessibilityStore).mockReturnValue(mockStoreValue);

    render(<AccessibilityToolbar />, { wrapper: Wrapper });

    // Attendre le montage (portal) puis ouvrir le menu
    const mainButton = await screen.findByRole("button", { name: /options d'accessibilité/i });
    await userEvent.click(mainButton);

    // Les options sont des role="switch" avec les labels i18n (accessibility.toolbar.*)
    expect(screen.getByRole("switch", { name: /contraste élevé/i })).toBeInTheDocument();
    expect(screen.getByRole("switch", { name: /texte plus grand/i })).toBeInTheDocument();
    expect(screen.getByRole("switch", { name: /réduire les animations/i })).toBeInTheDocument();
    expect(screen.getByRole("switch", { name: /mode dyslexie/i })).toBeInTheDocument();
    expect(screen.getByRole("switch", { name: /mode focus/i })).toBeInTheDocument();
  });

  it("a des labels ARIA corrects", async () => {
    vi.mocked(useAccessibilityStore).mockReturnValue(mockStoreValue);

    render(<AccessibilityToolbar />, { wrapper: Wrapper });

    // Attendre le montage puis vérifier le bouton principal
    const mainButton = await screen.findByRole("button", { name: /options d'accessibilité/i });
    expect(mainButton).toHaveAttribute("aria-label");

    // Ouvrir le menu pour vérifier les options (role="switch")
    await userEvent.click(mainButton);
    const switches = screen.getAllByRole("switch");
    switches.forEach((switchEl) => {
      expect(switchEl).toHaveAttribute("aria-label");
    });
  });
});
