import { describe, it, expect, vi, beforeEach } from "vitest";
import { toast } from "sonner";
import { dispatchChallengeAiSseEvent } from "./dispatchChallengeAiSseEvent";
import type { Challenge } from "@/types/api";

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  },
}));

const t = (key: string) => key;

describe("dispatchChallengeAiSseEvent (IA5c)", () => {
  beforeEach(() => {
    vi.mocked(toast.success).mockClear();
    vi.mocked(toast.error).mockClear();
    vi.mocked(toast.warning).mockClear();
  });

  it("warning → toast.warning, pas de success, pas de setGeneratedChallenge", () => {
    const setStreamedText = vi.fn();
    const setGeneratedChallenge = vi.fn();
    const onInvalidateLists = vi.fn();

    dispatchChallengeAiSseEvent(
      { type: "warning", message: "Attention pipeline" },
      {
        t,
        setStreamedText,
        setGeneratedChallenge,
        onInvalidateLists,
      }
    );

    expect(toast.warning).toHaveBeenCalledTimes(1);
    expect(toast.success).not.toHaveBeenCalled();
    expect(setGeneratedChallenge).not.toHaveBeenCalled();
    expect(onInvalidateLists).not.toHaveBeenCalled();
  });

  it("challenge valide → success + invalidate, pas warning", () => {
    const setStreamedText = vi.fn();
    const setGeneratedChallenge = vi.fn();
    const onInvalidateLists = vi.fn();
    const ch = { id: 1, title: "Mon défi" } as unknown as Challenge;

    dispatchChallengeAiSseEvent(
      { type: "challenge", challenge: ch },
      {
        t,
        setStreamedText,
        setGeneratedChallenge,
        onInvalidateLists,
      }
    );

    expect(toast.success).toHaveBeenCalledTimes(1);
    expect(toast.warning).not.toHaveBeenCalled();
    expect(setGeneratedChallenge).toHaveBeenCalledWith(ch);
    expect(onInvalidateLists).toHaveBeenCalledTimes(1);
  });
});
