import { fireEvent, render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { beforeEach, describe, expect, it, vi } from "vitest";
import fr from "@/messages/fr.json";
import ForgotPasswordPage from "@/app/forgot-password/page";

const forgotPasswordAsyncMock = vi.fn();

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    forgotPasswordAsync: forgotPasswordAsyncMock,
    isForgotPasswordPending: false,
  }),
}));

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    forgotPasswordAsyncMock.mockReset();
  });

  it("désactive la validation native du navigateur pour laisser la validation locale piloter le feedback", () => {
    const { container } = render(<ForgotPasswordPage />, { wrapper: TestWrapper });

    expect(container.querySelector("form")).toHaveAttribute("novalidate");
  });

  it("affiche l'erreur locale sur email invalide et ne soumet pas la requête", async () => {
    render(<ForgotPasswordPage />, { wrapper: TestWrapper });

    const emailInput = screen.getByLabelText(fr.auth.forgotPassword.email);
    fireEvent.change(emailInput, { target: { value: "invalid-email" } });
    fireEvent.click(
      screen.getByRole("button", {
        name: new RegExp(fr.auth.forgotPassword.submit, "i"),
      })
    );

    expect(await screen.findByText(fr.auth.forgotPassword.validation.emailInvalid)).toBeVisible();
    expect(forgotPasswordAsyncMock).not.toHaveBeenCalled();
  });
});
