"use client";

import { useCallback, useRef, useState, type KeyboardEvent } from "react";
import { nanoid } from "nanoid";
import { streamChat } from "@/lib/api/chat";
import { toApiConversationHistory } from "@/lib/chat/conversationHistory";
import type { ChatMessage } from "@/lib/chat/types";
import type { ChatTransportPhase } from "@/lib/chat/types";

export type { ChatMessage as Message } from "@/lib/chat/types";

export interface UseChatOptions {
  initialMessages?: ChatMessage[];
  initialSuggestions?: string[];
  /** Texte du message assistant en cas d’échec réseau / stream (i18n côté shell). */
  sendErrorText: string;
  /** Appelé une fois que le message utilisateur est accepté et ajouté à l’historique local (avant stream). */
  onUserMessageCommitted?: () => void;
}

export function useChat(options: UseChatOptions) {
  const {
    initialMessages = [],
    initialSuggestions = [],
    sendErrorText,
    onUserMessageCommitted,
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [suggestions, setSuggestions] = useState<string[]>(initialSuggestions);
  const [input, setInput] = useState("");
  const [transportPhase, setTransportPhase] = useState<ChatTransportPhase>("idle");

  const abortRef = useRef<AbortController | null>(null);

  const handleSend = useCallback(
    async (messageContent: string) => {
      if (transportPhase !== "idle") return;

      const trimmed = messageContent.trim();
      if (!trimmed) return;

      if (suggestions.length > 0) {
        setSuggestions([]);
      }

      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;

      setTransportPhase("pending");

      const userMessage: ChatMessage = {
        id: nanoid(),
        role: "user",
        content: trimmed,
      };

      setMessages((prev) => {
        const next = [...prev, userMessage];
        return next;
      });
      onUserMessageCommitted?.();

      const assistantMessageId = nanoid();
      setMessages((prev) => [...prev, { id: assistantMessageId, role: "assistant", content: "" }]);

      /** État conversationnel avant ce tour : le texte courant est dans `message`, pas dans l’historique. */
      const historyForApi = toApiConversationHistory(messages, {
        maxMessages: 5,
      });

      let hasVisibleAssistantOutput = false;
      await streamChat(
        {
          message: trimmed,
          conversation_history: historyForApi,
          stream: true,
        },
        {
          onChunk: (chunk) => {
            if (ac.signal.aborted) return;
            if (chunk.type === "chunk") {
              if (!hasVisibleAssistantOutput) {
                hasVisibleAssistantOutput = true;
                setTransportPhase("streaming");
              }
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: msg.content + chunk.content }
                    : msg
                )
              );
              return;
            }
            if (chunk.type === "image") {
              if (!hasVisibleAssistantOutput) {
                hasVisibleAssistantOutput = true;
                setTransportPhase("streaming");
              }
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId ? { ...msg, imageUrl: chunk.url } : msg
                )
              );
            }
          },
          onFinish: () => {
            if (ac.signal.aborted) return;
            setTransportPhase("idle");
          },
          onError: () => {
            if (ac.signal.aborted) return;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content: sendErrorText,
                      error: true,
                    }
                  : msg
              )
            );
            setTransportPhase("idle");
          },
        },
        { signal: ac.signal }
      );

      if (ac.signal.aborted) {
        setTransportPhase("idle");
      }
    },
    [messages, onUserMessageCommitted, sendErrorText, suggestions.length, transportPhase]
  );

  const sendInputMessage = useCallback(() => {
    const currentInput = input.trim();
    if (currentInput) {
      setInput("");
      void handleSend(currentInput);
    }
  }, [handleSend, input]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendInputMessage();
      }
    },
    [sendInputMessage]
  );

  const isLoading = transportPhase !== "idle";
  const isAwaitingAssistant = transportPhase === "pending";

  return {
    messages,
    suggestions,
    input,
    setInput,
    transportPhase,
    isLoading,
    isAwaitingAssistant,
    handleSend,
    sendInputMessage,
    /** @deprecated Préférer handleKeyDown (onKeyDown). */
    handleKeyPress: handleKeyDown,
    handleKeyDown,
  };
}
