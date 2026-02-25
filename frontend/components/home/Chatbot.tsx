"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";
import { useChat, Message } from "@/hooks/useChat";
import { useTranslations } from "next-intl";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// ... (le reste du composant)

export function Chatbot() {
  const t = useTranslations("home.chatbot");
  const [isOpen, setIsOpen] = useState(true);

  // Utilisation du hook centralisé
  const {
    messages,
    input,
    setInput,
    handleSend,
    sendInputMessage,
    handleKeyPress,
    isLoading,
    suggestions,
  } = useChat({
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

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Scroll vers le bas quand de nouveaux messages arrivent (dans le conteneur, pas la page)
  useEffect(() => {
    if (isOpen && messagesContainerRef.current) {
      const container = messagesContainerRef.current;
      const scrollToBottom = () => {
        container.scrollTop = container.scrollHeight;
      };

      setTimeout(scrollToBottom, 100);
    }
  }, [messages, isOpen]);

  const [hasUserInteracted, setHasUserInteracted] = useState(false);

  useEffect(() => {
    if (isOpen && inputRef.current && hasUserInteracted) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, hasUserInteracted]);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3 md:space-y-4">
      <div className="text-center space-y-1 md:space-y-2">
        <h2 id="chatbot-title" className="text-2xl sm:text-3xl md:text-4xl font-bold">
          {t("title")}
        </h2>
        <p className="text-muted-foreground max-w-2xl mx-auto px-4 text-sm md:text-base">
          {t("description")}
        </p>
      </div>

      <Card
        className={cn(
          "w-full flex flex-col shadow-lg transition-all",
          isOpen ? "h-[500px]" : "h-16"
        )}
      >
        <div className="flex items-center justify-between p-4 border-b bg-primary/5">
          <div className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5 text-primary" />
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
            <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex items-end gap-2",
                    message.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  {message.role === "assistant" && (
                    <MessageCircle className="h-6 w-6 text-primary flex-shrink-0" />
                  )}
                  <div
                    className={cn(
                      "prose prose-sm dark:prose-invert max-w-[85%] rounded-lg px-4 py-2",
                      message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                    )}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  </div>
                  {message.role === "user" && <div className="h-6 w-6 flex-shrink-0" />}
                </div>
              ))}
              {isLoading && messages[messages.length - 1]?.role === "user" && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-4 py-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {messages.length <= 1 && suggestions.length > 0 && (
              <div className="p-4 border-t">
                <h4 className="text-sm font-semibold mb-2 text-muted-foreground">
                  {t("suggestions")}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {suggestions.map((s, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSend(s)}
                      className="text-xs"
                    >
                      {s}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            <div className="p-4 border-t bg-background">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t("inputPlaceholder")}
                  disabled={isLoading}
                  className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
                  aria-label={t("inputLabel")}
                />
                <Button
                  onClick={sendInputMessage}
                  disabled={!input.trim() || isLoading}
                  size="icon"
                  aria-label={t("sendButton")}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2">{t("info")}</p>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
