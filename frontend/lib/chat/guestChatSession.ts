/**
 * Session-scoped guest chat message count (browser tab session).
 * Server-side rate limits remain authoritative; this only bounds UX for anonymous users.
 */
export const GUEST_CHAT_SESSION_STORAGE_KEY = "mathakine_guest_chat_user_messages_sent";
export const GUEST_CHAT_MESSAGE_QUOTA = 5;

export function readGuestChatMessageCount(): number {
  if (typeof window === "undefined") return 0;
  try {
    const raw = sessionStorage.getItem(GUEST_CHAT_SESSION_STORAGE_KEY);
    if (raw === null) return 0;
    const n = Number.parseInt(raw, 10);
    return Number.isFinite(n) && n >= 0 ? n : 0;
  } catch {
    return 0;
  }
}

export function writeGuestChatMessageCount(count: number): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, String(count));
  } catch {
    /* quota / private mode — ignore */
  }
}
