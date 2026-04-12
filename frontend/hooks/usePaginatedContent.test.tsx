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

  it("déduit hasMore à true quand skip + items.length < total même sans champ hasMore API", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      items: Array.from({ length: 15 }, (_, i) => ({ id: i })),
      total: 40,
    });

    const { result } = renderHook(
      () =>
        usePaginatedContent<{ id: number }>(
          { skip: 0, limit: 15 },
          {
            endpoint: "/api/paginated-has-more",
            queryKey: "paginated-has-more",
            staleTime: 60_000,
          }
        ),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.items).toHaveLength(15));
    expect(result.current.total).toBe(40);
    expect(result.current.hasMore).toBe(true);
  });

  it("déduit hasMore à false quand skip + items.length >= total", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      items: [{ id: 1 }],
      total: 1,
    });

    const { result } = renderHook(
      () =>
        usePaginatedContent<{ id: number }>(
          { skip: 0, limit: 15 },
          {
            endpoint: "/api/paginated-end",
            queryKey: "paginated-end",
            staleTime: 60_000,
          }
        ),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.items).toHaveLength(1));
    expect(result.current.hasMore).toBe(false);
  });

  it("déduit hasMore à false sur la dernière page partielle", async () => {
    const { api } = await import("@/lib/api/client");
    vi.mocked(api.get).mockResolvedValue({
      items: [{ id: 3 }],
      total: 3,
    });

    const { result } = renderHook(
      () =>
        usePaginatedContent<{ id: number }>(
          { skip: 2, limit: 15 },
          {
            endpoint: "/api/paginated-last-page",
            queryKey: "paginated-last-page",
            staleTime: 60_000,
          }
        ),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.items).toHaveLength(1));
    expect(result.current.hasMore).toBe(false);
  });
});
