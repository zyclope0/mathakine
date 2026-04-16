/**
 * Unit tests for useAIChallengeGenerator — orchestration; SSE helpers covered elsewhere.
 */

import { createElement, type ReactNode } from "react";
import { act, renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import {
  AiGenerationRequestError,
  AI_GENERATION_SSE_PATH,
  postAiGenerationSse,
} from "@/lib/ai/generation/postAiGenerationSse";
import { consumeSseJsonEvents } from "@/lib/utils/ssePostStream";
import { CHALLENGE_AI_AGE_USE_PROFILE } from "@/lib/constants/challenges";
import { useAIChallengeGenerator } from "@/hooks/useAIChallengeGenerator";

const authMock = vi.hoisted(() => ({
  user: null as { id: number } | null,
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({ user: authMock.user }),
}));

const mockPush = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
}));

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => `challenges.${key}`,
}));

vi.mock("sonner", () => ({
  toast: {
    error: vi.fn(),
    success: vi.fn(),
    warning: vi.fn(),
  },
}));

vi.mock("@/lib/ai/generation/postAiGenerationSse", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/lib/ai/generation/postAiGenerationSse")>();
  return {
    ...mod,
    postAiGenerationSse: vi.fn(),
  };
});

vi.mock("@/lib/utils/ssePostStream", () => ({
  consumeSseJsonEvents: vi.fn(),
}));

const mockPost = vi.mocked(postAiGenerationSse);
const mockConsume = vi.mocked(consumeSseJsonEvents);
const mockToastError = vi.mocked(toast.error);

function sseResponse(): Response {
  return {
    ok: true,
    headers: {
      get: (name: string) =>
        name.toLowerCase() === "content-type" ? "text/event-stream; charset=utf-8" : null,
    },
  } as unknown as Response;
}

function nonSseResponse(): Response {
  return {
    ok: true,
    headers: {
      get: (name: string) => (name.toLowerCase() === "content-type" ? "application/json" : null),
    },
  } as unknown as Response;
}

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  const invalidateSpy = vi.spyOn(queryClient, "invalidateQueries");
  function Wrapper({ children }: { children: ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return { Wrapper, invalidateSpy };
}

describe("useAIChallengeGenerator", () => {
  beforeEach(() => {
    mockToastError.mockClear();
    mockPush.mockClear();
    mockConsume.mockClear();
    mockPost.mockReset();
    authMock.user = { id: 1 };
    mockConsume.mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("unauthenticated: toast + login action, post not called", async () => {
    authMock.user = null;
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "p");
    });

    expect(mockPost).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "challenges.aiGenerator.authRequired",
      expect.objectContaining({
        description: "challenges.aiGenerator.authRequiredDescription",
        action: expect.objectContaining({ label: "challenges.aiGenerator.login" }),
      })
    );
    const opts = mockToastError.mock.calls[0]?.[1] as { action?: { onClick?: () => void } };
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("skips age_group in body when using profile sentinel", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockResolvedValueOnce(sseResponse());
    mockConsume.mockResolvedValue(undefined);

    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", CHALLENGE_AI_AGE_USE_PROFILE, "text");
    });

    expect(mockPost).toHaveBeenCalledWith(
      AI_GENERATION_SSE_PATH.challenge,
      { challenge_type: "sequence", prompt: "text" },
      expect.any(AbortSignal)
    );
  });

  it("includes age_group when not profile sentinel", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockResolvedValueOnce(sseResponse());
    mockConsume.mockResolvedValue(undefined);

    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "9-11", "a");
    });

    expect(mockPost).toHaveBeenCalledWith(
      AI_GENERATION_SSE_PATH.challenge,
      { challenge_type: "sequence", prompt: "a", age_group: "9-11" },
      expect.any(AbortSignal)
    );
  });

  it("non-SSE response: connection error toast, consume not called", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockResolvedValueOnce(nonSseResponse());
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "");
    });

    expect(mockConsume).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "challenges.aiGenerator.connectionError",
      expect.objectContaining({ description: "challenges.aiGenerator.connectionErrorDescription" })
    );
    expect(result.current.isGenerating).toBe(false);
  });

  it("success path: challenge SSE event updates state and invalidates lists", async () => {
    const onChallengeGenerated = vi.fn();
    const { Wrapper, invalidateSpy } = createWrapper();
    mockPost.mockResolvedValueOnce(sseResponse());
    mockConsume.mockImplementation(async (_response, onEvent) => {
      await onEvent({
        type: "challenge",
        challenge: {
          id: 9,
          title: "T",
          challenge_type: "sequence",
          age_group: "6-8",
        },
      });
    });

    const { result } = renderHook(() => useAIChallengeGenerator({ onChallengeGenerated }), {
      wrapper: Wrapper,
    });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "  hi  ");
    });

    expect(mockPost).toHaveBeenCalledWith(
      AI_GENERATION_SSE_PATH.challenge,
      expect.objectContaining({ prompt: "hi" }),
      expect.any(AbortSignal)
    );
    expect(result.current.generatedChallenge?.id).toBe(9);
    expect(onChallengeGenerated).toHaveBeenCalled();
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["challenges"] });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["completed-challenges"] });
  });

  it("AiGenerationRequestError http_401: toast with login action", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("http_401", 401));
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "x");
    });

    expect(result.current.streamedText).toBe("");
    const opts = mockToastError.mock.calls[0]?.[1] as { action?: { onClick?: () => void } };
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("AiGenerationRequestError csrf_token_missing: login action", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("csrf_token_missing", 0));
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "");
    });

    const opts = mockToastError.mock.calls[0]?.[1] as { action?: { onClick?: () => void } };
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("generic error: connection toast", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockRejectedValueOnce(new Error("network"));
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("sequence", "6-8", "p");
    });

    expect(mockToastError).toHaveBeenCalledWith(
      "challenges.aiGenerator.connectionError",
      expect.any(Object)
    );
    expect(result.current.isGenerating).toBe(false);
  });

  it("cancel aborts in-flight generation", async () => {
    mockPost.mockImplementation((_path, _body, signal: AbortSignal) => {
      return new Promise<Response>((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          reject(new DOMException("Aborted", "AbortError"));
        });
      });
    });
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    act(() => {
      void result.current.generate("sequence", "6-8", "");
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(true));
    act(() => {
      result.current.cancel();
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(false));
    expect(result.current.streamedText).toBe("");
  });

  it("returns early when already generating", async () => {
    mockPost.mockImplementation(
      () =>
        new Promise<Response>(() => {
          /* never resolves */
        })
    );
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIChallengeGenerator(), { wrapper: Wrapper });

    act(() => {
      void result.current.generate("sequence", "6-8", "a");
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(true));

    await act(async () => {
      await result.current.generate("sequence", "6-8", "b");
    });

    expect(mockPost).toHaveBeenCalledTimes(1);
  });
});
