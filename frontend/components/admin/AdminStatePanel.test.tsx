import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { AdminStatePanel } from "./AdminStatePanel";

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("AdminStatePanel", () => {
  it("shows error card when hasError", () => {
    render(
      <AdminStatePanel
        hasError
        errorMessage="Custom admin error"
        isLoading={false}
        loadingMessage="Loading…"
      >
        <p>success</p>
      </AdminStatePanel>,
      { wrapper: Wrapper }
    );
    expect(screen.getByText("Custom admin error")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent("Custom admin error");
    expect(screen.queryByText("success")).not.toBeInTheDocument();
  });

  it("shows loading when isLoading", () => {
    render(
      <AdminStatePanel hasError={false} errorMessage="err" isLoading loadingMessage="Please wait">
        <p>success</p>
      </AdminStatePanel>,
      { wrapper: Wrapper }
    );
    expect(screen.getByText("Please wait")).toBeInTheDocument();
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.queryByText("success")).not.toBeInTheDocument();
  });

  it("shows empty card when isEmpty", () => {
    render(
      <AdminStatePanel
        hasError={false}
        errorMessage="err"
        isLoading={false}
        loadingMessage="Loading…"
        isEmpty
        emptyMessage="Nothing here"
      >
        <p>success</p>
      </AdminStatePanel>,
      { wrapper: Wrapper }
    );
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("Nothing here");
    expect(screen.queryByText("success")).not.toBeInTheDocument();
  });

  it("renders children when ready", () => {
    render(
      <AdminStatePanel
        hasError={false}
        errorMessage="err"
        isLoading={false}
        loadingMessage="Loading…"
      >
        <p>KPI content</p>
      </AdminStatePanel>,
      { wrapper: Wrapper }
    );
    expect(screen.getByText("KPI content")).toBeInTheDocument();
  });
});
