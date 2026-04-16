import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";

const { mockPost, mockToastSuccess, mockToastError, getMockPathname, setMockPathname } = vi.hoisted(
  () => {
    let mockPathname = "/";
    return {
      mockPost: vi.fn(),
      mockToastSuccess: vi.fn(),
      mockToastError: vi.fn(),
      getMockPathname: () => mockPathname,
      setMockPathname: (value: string) => {
        mockPathname = value;
      },
    };
  }
);

vi.mock("next/navigation", () => ({
  usePathname: () => getMockPathname(),
}));

vi.mock("@/lib/api/client", () => ({
  api: {
    post: mockPost,
  },
}));

vi.mock("sonner", () => ({
  toast: {
    success: mockToastSuccess,
    error: mockToastError,
  },
}));

import { useAccessibilityStore } from "@/lib/stores/accessibilityStore";
import { useThemeStore } from "@/lib/stores/themeStore";
import { FeedbackFab } from "./FeedbackFab";

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("FeedbackFab", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setMockPathname("/");
    window.history.pushState({}, "", "http://localhost:3000/");
    useThemeStore.setState({ theme: "spatial" });
    useAccessibilityStore.setState({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      dyslexiaMode: false,
      focusMode: false,
    });
    mockPost.mockResolvedValue({ success: true, id: 123 });
  });

  it("envoie le contexte debug avec component_id par défaut sans user_role client", async () => {
    setMockPathname("/challenge/42");
    window.history.pushState({}, "", "http://localhost:3000/challenge/42");
    useThemeStore.setState({ theme: "aurora" });
    useAccessibilityStore.setState({
      highContrast: false,
      largeText: false,
      reducedMotion: true,
      dyslexiaMode: false,
      focusMode: false,
    });

    const user = userEvent.setup();
    render(<FeedbackFab />, { wrapper: Wrapper });

    await user.click(screen.getByRole("button", { name: /signaler|probl[eè]me/i }));
    await user.click(screen.getByRole("button", { name: /d[ée]fi incorrect/i }));
    await user.type(await screen.findByRole("textbox"), "Contexte debug A2");
    await user.click(screen.getByRole("button", { name: /envoyer/i }));

    await waitFor(() => expect(mockPost).toHaveBeenCalledTimes(1));

    const payload = mockPost.mock.calls[0]?.[1];
    expect(mockPost).toHaveBeenCalledWith("/api/feedback", payload);
    expect(payload).toMatchObject({
      feedback_type: "challenge",
      description: "Contexte debug A2",
      page_url: "http://localhost:3000/challenge/42",
      challenge_id: 42,
      active_theme: "aurora",
      ni_state: "on",
      component_id: "FeedbackFab",
    });
    expect(payload.user_role).toBeUndefined();
    expect(mockToastSuccess).toHaveBeenCalled();
  });

  it("préfère context et componentId explicites avec ni_state à off", async () => {
    setMockPathname("/challenge/99");
    window.history.pushState({}, "", "http://localhost:3000/challenge/99");
    useThemeStore.setState({ theme: "dino" });

    const user = userEvent.setup();
    render(<FeedbackFab context={{ exerciseId: 7 }} componentId="ExerciseCard" />, {
      wrapper: Wrapper,
    });

    await user.click(screen.getByRole("button", { name: /signaler|probl[eè]me/i }));
    await user.click(screen.getByRole("button", { name: /exercice incorrect/i }));
    await user.type(await screen.findByRole("textbox"), "Contexte explicite");
    await user.click(screen.getByRole("button", { name: /envoyer/i }));

    await waitFor(() => expect(mockPost).toHaveBeenCalledTimes(1));

    expect(mockPost.mock.calls[0]?.[1]).toMatchObject({
      feedback_type: "exercise",
      description: "Contexte explicite",
      page_url: "http://localhost:3000/challenge/99",
      exercise_id: 7,
      challenge_id: undefined,
      active_theme: "dino",
      ni_state: "off",
      component_id: "ExerciseCard",
    });
  });
});
