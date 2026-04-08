import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Providers } from "@/components/providers/Providers";

vi.mock("@tanstack/react-query-devtools", () => ({
  ReactQueryDevtools: () => null,
}));

describe("Providers", () => {
  it("renders children within the provider tree", () => {
    render(
      <Providers>
        <div data-testid="provider-child">ok</div>
      </Providers>
    );

    expect(screen.getByTestId("provider-child")).toHaveTextContent("ok");
  });
});
