import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { beforeEach, describe, expect, it, vi } from "vitest";
import fr from "@/messages/fr.json";
import AdminLayout from "./layout";

const mockUsePathname = vi.fn();

vi.mock("next/navigation", () => ({
  usePathname: () => mockUsePathname(),
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("AdminLayout", () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue("/admin/config");
  });

  it("renders translated admin navigation labels", () => {
    render(
      <AdminLayout>
        <div>child</div>
      </AdminLayout>,
      { wrapper: Wrapper }
    );

    expect(screen.getByRole("navigation", { name: "Navigation admin" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Vue d'ensemble" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Paramètres" })).toHaveAttribute(
      "aria-current",
      "page"
    );
  });
});
