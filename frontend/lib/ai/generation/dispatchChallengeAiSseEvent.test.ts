import { describe, it, expect, vi, beforeEach } from "vitest";
import { dispatchChallengeAiSseEvent } from "./dispatchChallengeAiSseEvent";
import { toast } from "sonner";

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
  },
}));

const t = (key: string) => key;

describe("dispatchChallengeAiSseEvent", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("challenge persisté avec id : succès et état pour CTA", () => {
    const setChallenge = vi.fn();
    dispatchChallengeAiSseEvent(
      {
        type: "challenge",
        challenge: {
          id: 55,
          title: "Défi",
          description: "Desc",
          challenge_type: "sequence",
          age_group: "9-11",
        },
      },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedChallenge: setChallenge,
        onInvalidateLists: vi.fn(),
      }
    );
    expect(setChallenge).toHaveBeenCalledWith(expect.objectContaining({ id: 55, title: "Défi" }));
    expect(toast.success).toHaveBeenCalled();
  });

  it("challenge avec warning ou sans id : pas de bannière succès navigable", () => {
    const setChallenge = vi.fn();
    dispatchChallengeAiSseEvent(
      {
        type: "challenge",
        challenge: {
          title: "Défi",
          description: "Desc",
          challenge_type: "sequence",
          age_group: "9-11",
        },
        warning: "Non sauvegardé en base",
      },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedChallenge: setChallenge,
        onInvalidateLists: vi.fn(),
      }
    );
    expect(setChallenge).toHaveBeenCalledWith(null);
    expect(toast.warning).toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
  });

  it("warning type dédié : pas de succès", () => {
    dispatchChallengeAiSseEvent(
      { type: "warning", message: "Attention" },
      {
        t,
        setStreamedText: vi.fn(),
        setGeneratedChallenge: vi.fn(),
        onInvalidateLists: vi.fn(),
      }
    );
    expect(toast.warning).toHaveBeenCalled();
    expect(toast.success).not.toHaveBeenCalled();
  });
});
