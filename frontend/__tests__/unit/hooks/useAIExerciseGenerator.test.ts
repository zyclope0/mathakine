/**
 * Unit tests for useAIExerciseGenerator (TEST-AI-GENERATOR-01) — orchestration only; SSE helpers have dedicated tests.
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
import { useAIExerciseGenerator } from "@/hooks/useAIExerciseGenerator";

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
  useTranslations: () => (key: string) => `exercises.${key}`,
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

async function primeStreamedText(
  generate: (type: string, ageGroup: string, prompt: string) => Promise<void>,
  getStreamedText: () => string,
  message = "chunk-before-error"
) {
  mockPost.mockResolvedValueOnce(sseResponse());
  mockConsume.mockImplementationOnce(async (_response, onEvent) => {
    await onEvent({ type: "status", message });
  });

  await act(async () => {
    await generate("addition", "6-8", "");
  });

  expect(getStreamedText()).toBe(message);
}

describe("useAIExerciseGenerator", () => {
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

  it("non authentifié : toast auth, action login -> router.push, postAiGenerationSse non appelé", async () => {
    authMock.user = null;
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });

    expect(mockPost).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.authRequired",
      expect.objectContaining({
        description: "exercises.aiGenerator.authRequiredDescription",
        action: expect.objectContaining({ label: "exercises.aiGenerator.login" }),
      })
    );
    const opts = mockToastError.mock.calls[0]?.[1] as {
      action?: { onClick?: () => void };
    };
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("paramètres exercice invalides : toast validation, post non appelé", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("not_a_valid_type", "6-8", "");
    });

    expect(mockPost).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.validationError",
      expect.objectContaining({ description: expect.stringContaining("Type") })
    );
  });

  it("prompt invalide (caractère interdit) : toast promptValidation, post non appelé", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("addition", "6-8", "bad<chars");
    });

    expect(mockPost).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.promptValidationError",
      expect.objectContaining({
        description: expect.stringContaining("interdits"),
      })
    );
  });

  it("prompt trop long : toast promptValidation, post non appelé", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("addition", "6-8", "x".repeat(501));
    });

    expect(mockPost).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.promptValidationError",
      expect.objectContaining({
        description: expect.stringContaining("500"),
      })
    );
  });

  it("succès SSE nominal : post path + body trim + signal, consume + dispatch réel, états, invalidate 100ms, onExerciseGenerated", async () => {
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });

    const onExerciseGenerated = vi.fn();
    const { Wrapper, invalidateSpy } = createWrapper();
    mockPost.mockResolvedValueOnce(sseResponse());
    mockConsume.mockImplementation(async (_response, onEvent) => {
      await onEvent({ type: "status", message: "chunk" });
      await onEvent({
        type: "exercise",
        exercise: {
          id: 7,
          title: "CreatedEx",
          question: "q",
          correct_answer: "a",
          exercise_type: "addition",
        },
      });
    });

    const { result } = renderHook(() => useAIExerciseGenerator({ onExerciseGenerated }), {
      wrapper: Wrapper,
    });

    await act(async () => {
      await result.current.generate("addition", "6-8", "  hello  ");
    });

    expect(mockPost).toHaveBeenCalledTimes(1);
    expect(mockPost).toHaveBeenCalledWith(
      AI_GENERATION_SSE_PATH.exercise,
      { exercise_type: "addition", age_group: "6-8", prompt: "hello" },
      expect.any(AbortSignal)
    );
    expect(mockConsume).toHaveBeenCalledTimes(1);
    const consumeOpts = mockConsume.mock.calls[0]?.[2] as { signal?: AbortSignal } | undefined;
    expect(consumeOpts?.signal).toBeInstanceOf(AbortSignal);

    expect(result.current.generatedExercise?.id).toBe(7);
    expect(result.current.generatedExercise?.title).toBe("CreatedEx");
    expect(onExerciseGenerated).toHaveBeenCalledWith(
      expect.objectContaining({ id: 7, title: "CreatedEx" })
    );

    await act(async () => {
      await vi.advanceTimersByTimeAsync(100);
    });
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ["exercises"] });

    expect(result.current.isGenerating).toBe(false);
  });

  it("réponse non SSE : toast connectionError, consume non appelé, isGenerating false", async () => {
    const { Wrapper } = createWrapper();
    mockPost.mockResolvedValueOnce(nonSseResponse());
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });

    expect(mockConsume).not.toHaveBeenCalled();
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.connectionError",
      expect.objectContaining({
        description: "exercises.aiGenerator.connectionErrorDescription",
      })
    );
    expect(result.current.isGenerating).toBe(false);
  });

  it("AiGenerationRequestError http_401 : streamedText vidé, toast avec action login", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await primeStreamedText(result.current.generate, () => result.current.streamedText);
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("http_401", 401));

    await act(async () => {
      await result.current.generate("division", "9-11", "ok");
    });

    expect(result.current.streamedText).toBe("");
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.errorSessionTitle",
      expect.objectContaining({
        description: "exercises.aiGenerator.errorSessionDescription",
        action: expect.objectContaining({ label: "exercises.aiGenerator.login" }),
      })
    );
    const opts = mockToastError.mock.calls[0]?.[1] as {
      action?: { onClick?: () => void };
    };
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("AiGenerationRequestError csrf_token_missing : action login", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await primeStreamedText(result.current.generate, () => result.current.streamedText);
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("csrf_token_missing", 0));

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });

    expect(result.current.streamedText).toBe("");
    const opts = mockToastError.mock.calls[0]?.[1] as {
      action?: { label?: string; onClick?: () => void };
    };
    expect(opts?.action?.label).toBe("exercises.aiGenerator.login");
    opts?.action?.onClick?.();
    expect(mockPush).toHaveBeenCalledWith("/login");
  });

  it("AiGenerationRequestError http_403 : toast sans action login", async () => {
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("http_403", 403));
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });

    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.errorAccessTitle",
      expect.objectContaining({
        description: "exercises.aiGenerator.errorAccessDescription",
      })
    );
    const opts = mockToastError.mock.calls[0]?.[1] as { action?: unknown };
    expect(opts?.action).toBeUndefined();
    expect(result.current.isGenerating).toBe(false);
  });

  it("AiGenerationRequestError http_backend : toast sans action login", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await primeStreamedText(result.current.generate, () => result.current.streamedText);
    mockPost.mockRejectedValueOnce(new AiGenerationRequestError("http_backend", 502));

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });

    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.errorBackendTitle",
      expect.objectContaining({
        description: "exercises.aiGenerator.errorBackendDescription",
      })
    );
    const opts = mockToastError.mock.calls[0]?.[1] as { action?: unknown };
    expect(opts?.action).toBeUndefined();
    expect(result.current.streamedText).toBe("");
  });

  it("erreur générique : streamedText vidé, toast connectionError", async () => {
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    await primeStreamedText(result.current.generate, () => result.current.streamedText);
    mockPost.mockRejectedValueOnce(new Error("network down"));

    await act(async () => {
      await result.current.generate("addition", "6-8", "p");
    });

    expect(result.current.streamedText).toBe("");
    expect(mockToastError).toHaveBeenCalledWith(
      "exercises.aiGenerator.connectionError",
      expect.objectContaining({
        description: "exercises.aiGenerator.connectionErrorDescription",
      })
    );
  });

  it("cancel : abort le flux, isGenerating false, streamedText vide, pas de toast erreur parasite", async () => {
    mockPost.mockImplementation((_path, _body, signal: AbortSignal) => {
      return new Promise<Response>((_resolve, reject) => {
        signal.addEventListener("abort", () => {
          reject(new DOMException("Aborted", "AbortError"));
        });
      });
    });
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    act(() => {
      void result.current.generate("addition", "6-8", "");
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(true));
    act(() => {
      result.current.cancel();
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(false));

    expect(result.current.streamedText).toBe("");
    expect(mockToastError).not.toHaveBeenCalled();
  });

  it("unmount : abort le contrôleur en cours", async () => {
    let capturedSignal: AbortSignal | null = null;
    mockPost.mockImplementation((_path, _body, signal: AbortSignal) => {
      capturedSignal = signal;
      return new Promise<Response>(() => {
        /* hang until abort */
      });
    });
    const { Wrapper } = createWrapper();
    const { result, unmount } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    act(() => {
      void result.current.generate("addition", "6-8", "");
    });
    await waitFor(() => {
      expect(capturedSignal).not.toBeNull();
    });
    unmount();
    expect(capturedSignal).not.toBeNull();
    expect((capturedSignal as unknown as AbortSignal).aborted).toBe(true);
  });

  it("garde anti-double génération : second generate ignoré pendant isGenerating", async () => {
    let resolvePost!: (value: Response) => void;
    const postPromise = new Promise<Response>((resolve) => {
      resolvePost = resolve;
    });
    mockPost.mockImplementation(() => postPromise);
    const { Wrapper } = createWrapper();
    const { result } = renderHook(() => useAIExerciseGenerator(), { wrapper: Wrapper });

    act(() => {
      void result.current.generate("addition", "6-8", "");
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(true));

    await act(async () => {
      await result.current.generate("addition", "6-8", "");
    });
    expect(mockPost).toHaveBeenCalledTimes(1);

    mockConsume.mockImplementation(async (_response, onEvent) => {
      await onEvent({ type: "status", message: "done" });
    });
    await act(async () => {
      resolvePost(sseResponse());
    });
    await waitFor(() => expect(result.current.isGenerating).toBe(false));
  });
});
