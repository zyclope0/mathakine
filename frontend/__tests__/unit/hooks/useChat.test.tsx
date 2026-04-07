import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useChat } from "@/hooks/chat/useChat";

const { streamChatMock } = vi.hoisted(() => ({
  streamChatMock: vi.fn(),
}));

vi.mock("@/lib/api/chat", () => ({
  streamChat: streamChatMock,
}));

describe("useChat (shared Chatbot / ChatbotFloating flow)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    streamChatMock.mockImplementation(
      async (
        _payload: unknown,
        callbacks: {
          onChunk: (c: { type: string; content?: string }) => void;
          onFinish: () => void;
          onError: (e: Error) => void;
        }
      ) => {
        callbacks.onChunk({ type: "chunk", content: "Hello" });
        callbacks.onFinish();
      }
    );
  });

  it("sends the current message and appends assistant chunks", async () => {
    const { result } = renderHook(() =>
      useChat({
        sendErrorText: "ERR",
        initialMessages: [{ id: "0", role: "assistant", content: "Hi" }],
      })
    );

    await act(async () => {
      await result.current.handleSend("Q1");
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("idle"));
    expect(streamChatMock).toHaveBeenCalledTimes(1);
    const firstCall = streamChatMock.mock.calls[0];
    expect(firstCall?.[0]).toMatchObject({
      message: "Q1",
      stream: true,
    });
    const assistant = result.current.messages.filter((m) => m.role === "assistant").pop();
    expect(assistant?.content).toContain("Hello");
  });

  it("invokes onUserMessageCommitted when a user message is accepted", async () => {
    const onUserMessageCommitted = vi.fn();
    const { result } = renderHook(() =>
      useChat({
        sendErrorText: "ERR",
        onUserMessageCommitted,
        initialMessages: [{ id: "0", role: "assistant", content: "Hi" }],
      })
    );

    await act(async () => {
      await result.current.handleSend("Hi");
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("idle"));
    expect(onUserMessageCommitted).toHaveBeenCalledTimes(1);
  });

  it("does not include synthetic welcome messages in conversation_history", async () => {
    const { result } = renderHook(() =>
      useChat({
        sendErrorText: "ERR",
        initialMessages: [{ id: "0", role: "assistant", content: "Hi", includeInHistory: false }],
      })
    );

    await act(async () => {
      await result.current.handleSend("Q1");
    });

    const firstCall = streamChatMock.mock.calls[0];
    expect(firstCall?.[0]).toMatchObject({
      message: "Q1",
      conversation_history: [],
    });
  });

  it("shows the translated error text on stream failure", async () => {
    streamChatMock.mockImplementationOnce(
      async (_payload: unknown, callbacks: { onError: (e: Error) => void }) => {
        callbacks.onError(new Error("network"));
      }
    );

    const { result } = renderHook(() =>
      useChat({
        sendErrorText: "ERR_UI",
        initialMessages: [],
      })
    );

    await act(async () => {
      await result.current.handleSend("x");
    });

    await waitFor(() => {
      expect(result.current.messages.some((m) => m.error)).toBe(true);
    });
    const errorMessage = result.current.messages.find((m) => m.error);
    expect(errorMessage?.content).toBe("ERR_UI");
  });

  it("does not re-enter while pending or streaming", async () => {
    let finish!: () => void;
    const done = new Promise<void>((resolve) => {
      finish = resolve;
    });
    streamChatMock.mockImplementationOnce(
      async (
        _payload: unknown,
        callbacks: {
          onChunk: (c: { type: string; content?: string }) => void;
          onFinish: () => void;
        }
      ) => {
        callbacks.onChunk({ type: "chunk", content: "a" });
        await done;
        callbacks.onFinish();
      }
    );

    const { result } = renderHook(() => useChat({ sendErrorText: "ERR", initialMessages: [] }));

    act(() => {
      void result.current.handleSend("one");
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("streaming"));

    await act(async () => {
      await result.current.handleSend("two");
    });

    expect(streamChatMock).toHaveBeenCalledTimes(1);

    await act(async () => {
      finish();
      await Promise.resolve();
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("idle"));
  });

  it("exposes waiting state while pending before the first chunk", async () => {
    let finish!: () => void;
    const done = new Promise<void>((resolve) => {
      finish = resolve;
    });
    streamChatMock.mockImplementationOnce(
      async (_payload: unknown, callbacks: { onFinish: () => void }) => {
        await done;
        callbacks.onFinish();
      }
    );

    const { result } = renderHook(() => useChat({ sendErrorText: "ERR", initialMessages: [] }));

    act(() => {
      void result.current.handleSend("pending");
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("pending"));
    expect(result.current.isAwaitingAssistant).toBe(true);

    await act(async () => {
      finish();
      await Promise.resolve();
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("idle"));
    expect(result.current.isAwaitingAssistant).toBe(false);
  });

  it("keeps the loader while only status events are received", async () => {
    let releaseFirstChunk!: () => void;
    const waitForFirstChunk = new Promise<void>((resolve) => {
      releaseFirstChunk = resolve;
    });
    streamChatMock.mockImplementationOnce(
      async (
        _payload: unknown,
        callbacks: {
          onChunk: (c: { type: string; content?: string; message?: string }) => void;
          onFinish: () => void;
        }
      ) => {
        callbacks.onChunk({ type: "status", message: "thinking" });
        await waitForFirstChunk;
        callbacks.onChunk({ type: "chunk", content: "Reponse" });
        callbacks.onFinish();
      }
    );

    const { result } = renderHook(() => useChat({ sendErrorText: "ERR", initialMessages: [] }));

    act(() => {
      void result.current.handleSend("status-first");
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("pending"));
    expect(result.current.isAwaitingAssistant).toBe(true);

    await act(async () => {
      releaseFirstChunk();
      await Promise.resolve();
    });

    await waitFor(() => expect(result.current.transportPhase).toBe("idle"));
    const assistant = result.current.messages.filter((m) => m.role === "assistant").pop();
    expect(assistant?.content).toContain("Reponse");
  });

  it("attaches chat image events to the assistant message", async () => {
    streamChatMock.mockImplementationOnce(
      async (
        _payload: unknown,
        callbacks: {
          onChunk: (c: { type: string; content?: string; url?: string }) => void;
          onFinish: () => void;
        }
      ) => {
        callbacks.onChunk({ type: "image", url: "https://cdn.example.com/generated.png" });
        callbacks.onChunk({ type: "chunk", content: "Voici l'image." });
        callbacks.onFinish();
      }
    );

    const { result } = renderHook(() => useChat({ sendErrorText: "ERR", initialMessages: [] }));

    await act(async () => {
      await result.current.handleSend("dessine");
    });

    const assistant = result.current.messages.filter((m) => m.role === "assistant").pop();
    expect(assistant?.imageUrl).toBe("https://cdn.example.com/generated.png");
    expect(assistant?.content).toContain("Voici l'image.");
  });
});
