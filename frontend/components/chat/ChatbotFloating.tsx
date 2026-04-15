"use client";

import { useRef, useEffect, useCallback } from "react";
import type { KeyboardEvent } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { MessageCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useChat } from "@/hooks/useChat";
import { useChatAutoScroll } from "@/hooks/chat/useChatAutoScroll";
import { useTranslations } from "next-intl";
import { ChatMessagesView } from "@/components/chat/ChatMessagesView";
import { ChatSuggestionsBar } from "@/components/chat/ChatSuggestionsBar";
import { ChatComposer } from "@/components/chat/ChatComposer";
import { useAuth } from "@/hooks/useAuth";

interface ChatbotFloatingProps {
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/**
 * Global shell chatbot: portal + drawer. Stream logic via `useChat`.
 * CHAT-AUTH-01: sending requires an authenticated session (backend + Next proxy enforce).
 */
export function ChatbotFloating({ isOpen = false, onOpenChange }: ChatbotFloatingProps) {
  const t = useTranslations("home.chatbot");
  const tAuth = useTranslations("auth");
  const { isAuthenticated } = useAuth();

  const {
    messages,
    input,
    setInput,
    handleSend,
    sendInputMessage,
    isLoading,
    isAwaitingAssistant,
    suggestions,
  } = useChat({
    sendErrorText: t("sendError"),
    initialMessages: [
      {
        id: "1",
        role: "assistant",
        content: t("initialMessage"),
        includeInHistory: false,
      },
    ],
    initialSuggestions: ["Qu'est-ce que Mathakine ?", "Comment progresser ?", "Créer un exercice"],
  });

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleOpenChange = (open: boolean) => {
    onOpenChange?.(open);
  };

  const guardedHandleSend = useCallback(
    async (messageContent: string) => {
      if (!isAuthenticated) return;
      await handleSend(messageContent);
    },
    [handleSend, isAuthenticated]
  );

  const guardedSendInputMessage = useCallback(() => {
    if (!isAuthenticated) return;
    sendInputMessage();
  }, [isAuthenticated, sendInputMessage]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        guardedSendInputMessage();
      }
    },
    [guardedSendInputMessage]
  );

  useChatAutoScroll(messagesContainerRef, isOpen, messages);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const guestComposerBlocked = !isAuthenticated;
  const suggestionDisabled = isLoading || guestComposerBlocked;
  const showGuestAuthPanel = !isAuthenticated;

  if (typeof document === "undefined") return null;

  return createPortal(
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-[9990] animate-in fade-in bg-zinc-950/30 duration-200"
          onClick={() => handleOpenChange(false)}
          aria-hidden="true"
        />
      )}

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="chatbot-title"
        className={cn(
          "fixed right-0 top-0 z-[9991] h-full w-full border-l bg-background shadow-2xl transition-all duration-300 ease-out sm:w-[400px]",
          isOpen ? "visible translate-x-0 opacity-100" : "invisible translate-x-full opacity-0"
        )}
        aria-hidden={!isOpen ? "true" : undefined}
      >
        <Card className="flex h-full flex-col rounded-none border-0">
          <div className="bg-primary/5 flex items-center justify-between border-b p-4">
            <div className="flex items-center gap-3">
              <div className="bg-primary/10 flex h-10 w-10 items-center justify-center rounded-full">
                <MessageCircle className="text-primary h-5 w-5" aria-hidden />
              </div>
              <div>
                <h2 id="chatbot-title" className="font-semibold">
                  {t("title")}
                </h2>
                <p className="text-muted-foreground text-xs">{t("subtitle")}</p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="h-10 w-10"
              onClick={() => handleOpenChange(false)}
              aria-label={t("closeAssistant")}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <div ref={messagesContainerRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            <ChatMessagesView
              messages={messages}
              variant="drawer"
              isAwaitingAssistant={isAwaitingAssistant}
            />
          </div>

          {showGuestAuthPanel ? (
            <div
              className="border-t px-4 py-3 text-sm text-muted-foreground"
              role="status"
              aria-live="polite"
            >
              <p className="mb-3">{t("guestLimitCta")}</p>
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" asChild>
                  <Link href="/login">{tAuth("login.title")}</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link href="/register">{tAuth("register.title")}</Link>
                </Button>
              </div>
            </div>
          ) : null}

          <ChatSuggestionsBar
            visible={messages.length <= 1}
            variant="drawer"
            suggestions={suggestions}
            suggestionsTitle={t("suggestions")}
            onPick={guardedHandleSend}
            disabled={suggestionDisabled}
          />

          <ChatComposer
            variant="drawer"
            inputRef={inputRef}
            value={input}
            onChange={setInput}
            onKeyDown={handleKeyDown}
            onSend={guardedSendInputMessage}
            disabled={isLoading || guestComposerBlocked}
            canSend={Boolean(input.trim()) && isAuthenticated}
            placeholder={t("inputPlaceholder")}
            inputAriaLabel={t("inputLabel")}
            sendAriaLabel={t("sendButton")}
          />
        </Card>
      </div>

      <Button
        type="button"
        onClick={() => handleOpenChange(!isOpen)}
        className={cn(
          "bg-primary text-primary-foreground border-primary/20 fixed bottom-6 right-24 z-[9998] h-14 w-14 rounded-full border-4",
          "shadow-[0_0_20px_color-mix(in_srgb,var(--color-primary)_40%,transparent)]",
          "transition-all duration-200 hover:scale-110",
          "hover:shadow-[0_0_30px_color-mix(in_srgb,var(--color-primary)_60%,transparent)]",
          isOpen && "pointer-events-none opacity-0"
        )}
        aria-label={t("openFabAria")}
      >
        <MessageCircle className="h-7 w-7" />
      </Button>
    </>,
    document.body
  );
}
