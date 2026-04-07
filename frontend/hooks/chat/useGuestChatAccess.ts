"use client";

import { useCallback, useEffect, useState } from "react";
import {
  GUEST_CHAT_MESSAGE_QUOTA,
  readGuestChatMessageCount,
  writeGuestChatMessageCount,
} from "@/lib/chat/guestChatSession";

export interface GuestChatAccessState {
  /** True after reading sessionStorage on the client (avoids SSR flash). */
  hydrated: boolean;
  /** Count of user messages committed this session (guest only). */
  sentCount: number;
  remainingMessages: number;
  guestLimitReached: boolean;
  canSendGuestMessage: boolean;
  incrementGuestMessageCount: () => void;
}

function getInitialGuestSentCount(): number {
  if (typeof window === "undefined") return 0;
  return readGuestChatMessageCount();
}

function getInitialHydrated(): boolean {
  return typeof window !== "undefined";
}

/**
 * Frontend-only guest chat quota per browser session (sessionStorage).
 * Authenticated users are not subject to this quota.
 */
export function useGuestChatAccess(isAuthenticated: boolean): GuestChatAccessState {
  const [sentCount, setSentCount] = useState(getInitialGuestSentCount);
  const [hydrated, setHydrated] = useState(getInitialHydrated);

  useEffect(() => {
    if (hydrated) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional post-hydration sync from sessionStorage (guest quota)
    setSentCount(readGuestChatMessageCount());
    setHydrated(true);
  }, [hydrated]);

  const incrementGuestMessageCount = useCallback(() => {
    if (isAuthenticated) return;
    const next = readGuestChatMessageCount() + 1;
    writeGuestChatMessageCount(next);
    setSentCount(next);
  }, [isAuthenticated]);

  const guestLimitReached = !isAuthenticated && sentCount >= GUEST_CHAT_MESSAGE_QUOTA;
  const remainingMessages = isAuthenticated
    ? GUEST_CHAT_MESSAGE_QUOTA
    : Math.max(0, GUEST_CHAT_MESSAGE_QUOTA - sentCount);
  const canSendGuestMessage = isAuthenticated || (hydrated && sentCount < GUEST_CHAT_MESSAGE_QUOTA);

  return {
    hydrated,
    sentCount,
    remainingMessages,
    guestLimitReached,
    canSendGuestMessage,
    incrementGuestMessageCount,
  };
}
