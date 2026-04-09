import { useQueryClient } from "@tanstack/react-query";
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

  it("keeps the same QueryClient instance when Providers re-renders (stable per mount)", () => {
    const clients: ReturnType<typeof useQueryClient>[] = [];

    function QueryClientProbe() {
      clients.push(useQueryClient());
      return null;
    }

    const { rerender } = render(
      <Providers>
        <QueryClientProbe />
        <span data-testid="tick">1</span>
      </Providers>
    );

    expect(clients).toHaveLength(1);
    const first = clients[0];
    expect(first).toBeDefined();

    rerender(
      <Providers>
        <QueryClientProbe />
        <span data-testid="tick">2</span>
      </Providers>
    );

    expect(screen.getByTestId("tick")).toHaveTextContent("2");
    expect(clients).toHaveLength(2);
    expect(clients[1]).toBe(first);
  });
});
