"use client";

import { useState, useRef, useCallback, type KeyboardEvent } from "react";
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

export function Chatbot() {
  const t = useTranslations("home.chatbot");
  const tAuth = useTranslations("auth");
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(true);

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
    initialSuggestions: [
      "Qu'est-ce que Mathakine ?",
      "Comment puis-je progresser ?",
      "Crée un exercice sur les fractions",
    ],
  });

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

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

  const guestComposerBlocked = !isAuthenticated;
  const suggestionDisabled = isLoading || guestComposerBlocked;

  useChatAutoScroll(messagesContainerRef, isOpen, messages);

  return (
    <div className="mx-auto w-full max-w-4xl space-y-3 md:space-y-4">
      <div className="space-y-1 text-center md:space-y-2">
        <h2 id="chatbot-title" className="text-2xl font-bold sm:text-3xl md:text-4xl">
          {t("title")}
        </h2>
        <p className="text-muted-foreground mx-auto max-w-2xl px-4 text-sm md:text-base">
          {t("description")}
        </p>
      </div>

      <Card
        className={cn(
          "flex w-full flex-col shadow-lg transition-all",
          isOpen ? "h-[500px]" : "h-16"
        )}
      >
        <div className="bg-primary/5 flex items-center justify-between border-b p-4">
          <div className="flex items-center gap-2">
            <MessageCircle className="text-primary h-5 w-5" />
            <h3 className="font-semibold">{t("title")}</h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? t("collapseLabel") : t("expandLabel")}
          >
            {isOpen ? <X className="h-4 w-4" /> : <MessageCircle className="h-4 w-4" />}
          </Button>
        </div>

        {isOpen && (
          <>
            <div ref={messagesContainerRef} className="flex-1 space-y-4 overflow-y-auto p-4">
              <ChatMessagesView
                messages={messages}
                variant="embedded"
                isAwaitingAssistant={isAwaitingAssistant}
              />
            </div>

            {guestComposerBlocked ? (
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
              variant="embedded"
              suggestions={suggestions}
              suggestionsTitle={t("suggestions")}
              onPick={guardedHandleSend}
              disabled={suggestionDisabled}
            />

            <ChatComposer
              variant="embedded"
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
              footerHint={t("info")}
            />
          </>
        )}
      </Card>
    </div>
  );
}
