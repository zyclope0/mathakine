import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";

import { ChatbotFloating } from "@/components/chat/ChatbotFloating";
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

  it("affiche l’appel à connexion pour un invité (CHAT-AUTH-01)", async () => {
    render(
      <Wrapper>
        <ChatbotFloating isOpen onOpenChange={vi.fn()} />
      </Wrapper>
    );

    const cta = fr.home.chatbot.guestLimitCta;
    await waitFor(() => {
      expect(screen.getByText(cta)).toBeInTheDocument();
    });

    expect(screen.getByRole("link", { name: "Connexion" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Inscription" })).toBeInTheDocument();
  });

  it("ne déclenche pas streamChat pour un invité (composer et envoi bloqués)", async () => {
    render(
      <Wrapper>
        <ChatbotFloating isOpen onOpenChange={vi.fn()} />
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(fr.home.chatbot.guestLimitCta)).toBeInTheDocument();
    });

    const textbox = screen.getByRole("textbox", { name: /message/i });
    expect(textbox).toBeDisabled();

    const sendButton = screen.getByRole("button", { name: /envoyer le message/i });
    expect(sendButton).toBeDisabled();
    fireEvent.click(sendButton);

    expect(streamChatMock).not.toHaveBeenCalled();
  });
});
