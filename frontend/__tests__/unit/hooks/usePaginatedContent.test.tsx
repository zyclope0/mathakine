import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { usePaginatedContent } from "@/hooks/usePaginatedContent";
import type { ReactNode } from "react";

vi.mock("@/lib/api/client", () => ({
  api: {
    get: vi.fn(),
  },
}));

const localeRef = { locale: "fr" };

vi.mock("@/lib/stores/localeStore", () => ({
  useLocaleStore: () => ({ locale: localeRef.locale }),
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("usePaginatedContent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localeRef.locale = "fr";
  });

  it("n’effectue qu’un seul GET après montage (pas d’invalidation locale redondante)", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      items: [{ id: 1 }],
      total: 1,
      hasMore: false,
    });

    const { result } = renderHook(
      () =>
        usePaginatedContent<{ id: number }>(
          { skip: 0, limit: 15 },
          {
            endpoint: "/api/test-items",
            queryKey: "paginated-test-items",
            paramKeys: { kind: "kind" },
            staleTime: 60_000,
          }
        ),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.total).toBe(1));
    expect(api.get).toHaveBeenCalledTimes(1);
    expect(api.get).toHaveBeenCalledWith(expect.stringContaining("/api/test-items?"));
  });

  it("refetch quand la locale change (nouvelle queryKey)", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      items: [],
      total: 0,
      hasMore: false,
    });

    const { rerender } = renderHook(
      () =>
        usePaginatedContent(
          { skip: 0, limit: 10 },
          {
            endpoint: "/api/test-items",
            queryKey: "paginated-test-locale",
            staleTime: 60_000,
          }
        ),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(1));

    localeRef.locale = "en";
    rerender();

    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
  });
});
