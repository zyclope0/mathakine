import { describe, it, expect, beforeEach } from "vitest";
import { renderHook, waitFor, act } from "@testing-library/react";
import { useGuestChatAccess } from "@/hooks/chat/useGuestChatAccess";
import {
  GUEST_CHAT_MESSAGE_QUOTA,
  GUEST_CHAT_SESSION_STORAGE_KEY,
} from "@/lib/chat/guestChatSession";

describe("useGuestChatAccess", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("applies the stored guest quota immediately on first client render", () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, String(GUEST_CHAT_MESSAGE_QUOTA));
    const { result } = renderHook(() => useGuestChatAccess(false));

    expect(result.current.hydrated).toBe(true);
    expect(result.current.sentCount).toBe(GUEST_CHAT_MESSAGE_QUOTA);
    expect(result.current.guestLimitReached).toBe(true);
    expect(result.current.canSendGuestMessage).toBe(false);
  });

  it("hydrates guest count from sessionStorage", async () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, "2");
    const { result } = renderHook(() => useGuestChatAccess(false));

    await waitFor(() => expect(result.current.hydrated).toBe(true));
    expect(result.current.sentCount).toBe(2);
    expect(result.current.canSendGuestMessage).toBe(true);
    expect(result.current.remainingMessages).toBe(GUEST_CHAT_MESSAGE_QUOTA - 2);
    expect(result.current.guestLimitReached).toBe(false);
  });

  it("incrementGuestMessageCount reaches limit at quota", async () => {
    const { result } = renderHook(() => useGuestChatAccess(false));
    await waitFor(() => expect(result.current.hydrated).toBe(true));

    act(() => {
      for (let i = 0; i < GUEST_CHAT_MESSAGE_QUOTA; i++) {
        result.current.incrementGuestMessageCount();
      }
    });

    expect(result.current.sentCount).toBe(GUEST_CHAT_MESSAGE_QUOTA);
    expect(result.current.guestLimitReached).toBe(true);
    expect(result.current.canSendGuestMessage).toBe(false);
    expect(sessionStorage.getItem(GUEST_CHAT_SESSION_STORAGE_KEY)).toBe(
      String(GUEST_CHAT_MESSAGE_QUOTA)
    );
  });

  it("authenticated users are not limited by guest quota", async () => {
    sessionStorage.setItem(GUEST_CHAT_SESSION_STORAGE_KEY, "99");
    const { result } = renderHook(() => useGuestChatAccess(true));
    await waitFor(() => expect(result.current.hydrated).toBe(true));

    expect(result.current.canSendGuestMessage).toBe(true);
    expect(result.current.guestLimitReached).toBe(false);

    act(() => {
      result.current.incrementGuestMessageCount();
    });

    expect(sessionStorage.getItem(GUEST_CHAT_SESSION_STORAGE_KEY)).toBe("99");
  });
});
