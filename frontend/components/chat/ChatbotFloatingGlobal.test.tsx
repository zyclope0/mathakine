import { describe, it, expect, vi } from "vitest";
import { render, waitFor } from "@testing-library/react";
import { ChatbotFloatingGlobal } from "@/components/chat/ChatbotFloatingGlobal";

vi.mock("@/lib/stores/chatStore", () => ({
  useChatStore: () => ({ isOpen: false, setOpen: vi.fn() }),
}));

describe("ChatbotFloatingGlobal", () => {
  it("affiche le placeholder lazy du shell global", async () => {
    const { container } = render(<ChatbotFloatingGlobal />);
    await waitFor(() => {
      expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
    });
  });
});
