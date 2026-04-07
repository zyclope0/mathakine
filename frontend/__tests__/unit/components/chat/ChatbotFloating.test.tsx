import type { ReactNode } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { ChatbotFloating } from "@/components/chat/ChatbotFloating";
import fr from "@/messages/fr.json";
import { GUEST_CHAT_SESSION_STORAGE_KEY } from "@/lib/chat/guestChatSession";

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
        cbs: { onChunk: (c: { type: string; content?: string }) => void; onFinish: () => void }
      ) => {
        cbs.onChunk({ type: "chunk", content: "ok" });
        cbs.onFinish();
      }
    );
  });

  it("affiche le panneau limite invité lorsque le quota session est atteint", async () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, "5");
    render(
      <Wrapper>
        <ChatbotFloating isOpen onOpenChange={vi.fn()} />
      </Wrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/limite de messages en mode invité/i)).toBeInTheDocument();
    });
    expect(screen.getByRole("link", { name: "Connexion" })).toBeInTheDocument();
  });
});
