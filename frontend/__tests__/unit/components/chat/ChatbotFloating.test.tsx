import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";

import { ChatbotFloating } from "@/components/chat/ChatbotFloating";
import { GUEST_CHAT_SESSION_STORAGE_KEY } from "@/lib/chat/guestChatSession";
import fr from "@/messages/fr.json";

vi.mock("react-dom", async () => {
  const actual = await vi.importActual<typeof import("react-dom")>("react-dom");
  return {
    ...actual,
    createPortal: (node: ReactNode) => node,
  };
});

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({ isAuthenticated: false }),
}));

const { streamChatMock } = vi.hoisted(() => ({
  streamChatMock: vi.fn(),
}));

vi.mock("@/lib/api/chat", () => ({
  streamChat: streamChatMock,
}));

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ChatbotFloating", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
    streamChatMock.mockImplementation(
      async (
        _payload: unknown,
        callbacks: {
          onChunk: (c: { type: string; content?: string }) => void;
          onFinish: () => void;
        }
      ) => {
        callbacks.onChunk({ type: "chunk", content: "ok" });
        callbacks.onFinish();
      }
    );
  });

  it("affiche le panneau limite invite lorsque le quota session est atteint", async () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, "5");
    render(
      <Wrapper>
        <ChatbotFloating isOpen onOpenChange={vi.fn()} />
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/limite de messages en mode/i)).toBeInTheDocument();
    });

    expect(screen.getByRole("link", { name: "Connexion" })).toBeInTheDocument();
  });

  it("bloque l'envoi quand le quota invite est deja atteint", async () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, "5");
    render(
      <Wrapper>
        <ChatbotFloating isOpen onOpenChange={vi.fn()} />
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/limite de messages en mode/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByRole("textbox", { name: /message/i }), {
      target: { value: "Bonjour" },
    });

    const sendButton = screen.getByRole("button", { name: /envoyer le message/i });
    expect(sendButton).toBeDisabled();
    fireEvent.click(sendButton);

    expect(streamChatMock).not.toHaveBeenCalled();
  });
});
