"use client";

import { useState, useRef } from "react";
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

export function Chatbot() {
  const t = useTranslations("home.chatbot");
  const [isOpen, setIsOpen] = useState(true);

  const {
    messages,
    input,
    setInput,
    handleSend,
    sendInputMessage,
    handleKeyDown,
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

            <ChatSuggestionsBar
              visible={messages.length <= 1}
              variant="embedded"
              suggestions={suggestions}
              suggestionsTitle={t("suggestions")}
              onPick={handleSend}
              disabled={isLoading}
            />

            <ChatComposer
              variant="embedded"
              inputRef={inputRef}
              value={input}
              onChange={setInput}
              onKeyDown={handleKeyDown}
              onSend={sendInputMessage}
              disabled={isLoading}
              canSend={Boolean(input.trim())}
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
