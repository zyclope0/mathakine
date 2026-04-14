import { describe, expect, it } from "vitest";
import { toApiConversationHistory } from "./conversationHistory";
import type { ChatMessage } from "./types";

function msg(
  partial: Partial<ChatMessage> & Pick<ChatMessage, "id" | "role" | "content">
): ChatMessage {
  return partial as ChatMessage;
}

describe("toApiConversationHistory", () => {
  it("exclut les messages assistant vides (placeholder stream)", () => {
    const messages: ChatMessage[] = [
      msg({ id: "1", role: "assistant", content: "Salut" }),
      msg({ id: "2", role: "user", content: "Q" }),
      msg({ id: "3", role: "assistant", content: "" }),
    ];
    expect(toApiConversationHistory(messages, { maxMessages: 5 })).toEqual([
      { role: "assistant", content: "Salut" },
      { role: "user", content: "Q" },
    ]);
  });

  it("limite aux maxMessages derniers messages non vides", () => {
    const messages: ChatMessage[] = [
      msg({ id: "1", role: "user", content: "a" }),
      msg({ id: "2", role: "assistant", content: "A" }),
      msg({ id: "3", role: "user", content: "b" }),
      msg({ id: "4", role: "assistant", content: "B" }),
      msg({ id: "5", role: "user", content: "c" }),
      msg({ id: "6", role: "assistant", content: "C" }),
    ];
    const h = toApiConversationHistory(messages, { maxMessages: 3 });
    expect(h).toEqual([
      { role: "assistant", content: "B" },
      { role: "user", content: "c" },
      { role: "assistant", content: "C" },
    ]);
  });
});
