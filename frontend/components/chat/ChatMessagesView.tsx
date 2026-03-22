"use client";

import { MessageCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage } from "@/lib/chat/types";

export type ChatMessagesLayoutVariant = "embedded" | "drawer";

export interface ChatMessagesViewProps {
  messages: ChatMessage[];
  variant: ChatMessagesLayoutVariant;
  isAwaitingAssistant: boolean;
}

export function ChatMessagesView({
  messages,
  variant,
  isAwaitingAssistant,
}: ChatMessagesViewProps) {
  const isDrawer = variant === "drawer";
  const visibleMessages = messages.filter(
    (message) =>
      !(
        message.role === "assistant" &&
        !message.error &&
        !message.imageUrl &&
        message.content.trim().length === 0
      )
  );

  return (
    <>
      {visibleMessages.map((message) => (
        <div
          key={message.id}
          className={cn(
            isDrawer ? "flex gap-3" : "flex items-end gap-2",
            message.role === "user" ? "justify-end" : "justify-start"
          )}
        >
          {message.role === "assistant" &&
            (isDrawer ? (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                <MessageCircle className="h-4 w-4 text-primary" aria-hidden />
              </div>
            ) : (
              <MessageCircle className="h-6 w-6 shrink-0 text-primary" aria-hidden />
            ))}
          <div
            className={cn(
              "prose prose-sm dark:prose-invert max-w-[85%]",
              isDrawer
                ? cn(
                    "rounded-2xl px-4 py-3",
                    message.role === "user"
                      ? "rounded-br-md bg-primary text-primary-foreground"
                      : "rounded-bl-md bg-muted"
                  )
                : cn(
                    "rounded-lg px-4 py-2",
                    message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                  ),
              message.error && "border border-destructive/50"
            )}
            role={message.error ? "alert" : undefined}
            data-testid={message.error ? "chat-message-error" : undefined}
          >
            {message.imageUrl ? (
              <div className={message.content.trim().length > 0 ? "mb-3" : undefined}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={message.imageUrl}
                  alt="Illustration générée par l'assistant"
                  className="max-h-64 w-full rounded-lg object-cover"
                />
              </div>
            ) : null}
            {message.content.trim().length > 0 || message.error ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
            ) : null}
          </div>
          {!isDrawer && message.role === "user" && <div className="h-6 w-6 shrink-0" aria-hidden />}
        </div>
      ))}
      {isAwaitingAssistant &&
        (isDrawer ? (
          <div className="flex justify-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
              <MessageCircle className="h-4 w-4 text-primary" aria-hidden />
            </div>
            <div className="rounded-2xl rounded-bl-md bg-muted px-4 py-3">
              <Loader2
                className="h-5 w-5 animate-spin text-muted-foreground"
                aria-label="loading"
              />
            </div>
          </div>
        ) : (
          <div className="flex justify-start">
            <div className="rounded-lg bg-muted px-4 py-2">
              <Loader2 className="h-4 w-4 animate-spin" aria-label="loading" />
            </div>
          </div>
        ))}
    </>
  );
}
