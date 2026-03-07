import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import ResetPasswordPage from "@/app/reset-password/page";

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ResetPasswordPage", () => {
  it("affiche une erreur explicite quand aucun token n'est fourni", async () => {
    render(<ResetPasswordPage />, { wrapper: TestWrapper });

    expect(await screen.findByText("Lien invalide ou manquant.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Demander un nouveau lien/i })).toBeInTheDocument();
  });
});
