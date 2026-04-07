"use client";

import dynamic from "next/dynamic";
import { useChatStore } from "@/lib/stores/chatStore";

const ChatbotFloatingLazy = dynamic(
  () =>
    import("@/components/chat/ChatbotFloating").then((mod) => ({ default: mod.ChatbotFloating })),
  {
    ssr: false,
    loading: () => (
      <div
        className="fixed bottom-6 right-24 z-[9998] h-14 w-14 rounded-full bg-muted animate-pulse"
        aria-hidden="true"
      />
    ),
  }
);

/**
 * Global floating chatbot (shell) — opened via {@link useChatStore} (e.g. Header CTA for signed-in users).
 */
export function ChatbotFloatingGlobal() {
  const { isOpen, setOpen } = useChatStore();
  return <ChatbotFloatingLazy isOpen={isOpen} onOpenChange={setOpen} />;
}
