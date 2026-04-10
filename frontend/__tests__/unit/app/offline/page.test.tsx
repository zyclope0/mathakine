import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import OfflinePage from "@/app/offline/page";

const refresh = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh }),
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("OfflinePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche le titre et le bouton réessayer (messages FR)", () => {
    render(<OfflinePage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Hors ligne" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument();
    expect(screen.getByText(/Vous n'êtes pas connecté à Internet/i)).toBeInTheDocument();
  });

  it("appelle router.refresh au clic lorsque le navigateur est en ligne", () => {
    Object.defineProperty(navigator, "onLine", { value: true, configurable: true });
    render(<OfflinePage />, { wrapper: Wrapper });
    fireEvent.click(screen.getByRole("button", { name: "Réessayer" }));
    expect(refresh).toHaveBeenCalledTimes(1);
  });
});
