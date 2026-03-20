import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QuickStartActions } from "@/components/dashboard/QuickStartActions";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";

vi.mock("@/hooks/useRecommendations", () => ({
  useRecommendations: vi.fn(),
}));
vi.mock("@/lib/analytics/edtech", () => ({
  trackDashboardView: vi.fn(),
  trackQuickStartClick: vi.fn(),
}));

import { useRecommendations } from "@/hooks/useRecommendations";
import { trackDashboardView, trackQuickStartClick } from "@/lib/analytics/edtech";

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("QuickStartActions", () => {
  beforeEach(() => {
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: [],
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen: vi.fn(),
      isRecordingOpen: false,
    } as ReturnType<typeof useRecommendations>);
  });

  it("affiche le titre et les 3 CTA", () => {
    render(<QuickStartActions />, { wrapper: TestWrapper });

    expect(screen.getByText("Que veux-tu faire ?")).toBeInTheDocument();
    expect(screen.getByText("Un exercice")).toBeInTheDocument();
    expect(screen.getByText("Un défi")).toBeInTheDocument();
    expect(screen.getByText("Session entrelacée")).toBeInTheDocument();
  });

  it("liens vers /exercises et /challenges quand aucune recommandation", () => {
    render(<QuickStartActions />, { wrapper: TestWrapper });

    const exerciseLink = screen.getByRole("link", { name: /Un exercice/i });
    const challengeLink = screen.getByRole("link", { name: /Un défi/i });

    expect(exerciseLink).toHaveAttribute("href", "/exercises");
    expect(challengeLink).toHaveAttribute("href", "/challenges");
  });

  it("liens vers recommandations si dispo (exercise_id, challenge_id)", () => {
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: [
        {
          id: 1,
          exercise_id: 42,
          priority: 9,
          exercise_type: "ADDITION",
          exercise_title: "Addition test",
          reason: "",
          difficulty: "",
        },
        {
          id: 2,
          exercise_type: "",
          challenge_id: 99,
          priority: 8,
          challenge_title: "Suite logique",
          reason: "",
          difficulty: "",
        },
      ] as ReturnType<typeof useRecommendations>["recommendations"],
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen: vi.fn(),
      isRecordingOpen: false,
    } as ReturnType<typeof useRecommendations>);

    render(<QuickStartActions />, { wrapper: TestWrapper });

    const exerciseLink = screen.getByRole("link", { name: /Un exercice/i });
    const challengeLink = screen.getByRole("link", { name: /Un défi/i });

    expect(exerciseLink).toHaveAttribute("href", "/exercises/42");
    expect(challengeLink).toHaveAttribute("href", "/challenge/99");
  });

  it("a les attributs data-quick-start pour instrumentation", () => {
    render(<QuickStartActions />, { wrapper: TestWrapper });

    const block = document.querySelector('[data-quick-start-block="true"]');
    expect(block).toBeInTheDocument();

    const exerciseCta = document.querySelector('[data-quick-start="exercise"]');
    const challengeCta = document.querySelector('[data-quick-start="challenge"]');
    const interleavedCta = document.querySelector('[data-quick-start="interleaved"]');
    expect(exerciseCta).toBeInTheDocument();
    expect(challengeCta).toBeInTheDocument();
    expect(interleavedCta).toBeInTheDocument();
  });

  it("lien Session entrelacée vers /exercises/interleaved", () => {
    render(<QuickStartActions />, { wrapper: TestWrapper });

    const interleavedLink = screen.getByRole("link", { name: /Session entrelacée/i });
    expect(interleavedLink).toHaveAttribute("href", "/exercises/interleaved");
  });

  it("appelle trackDashboardView au montage", () => {
    vi.mocked(trackDashboardView).mockClear();
    render(<QuickStartActions />, { wrapper: TestWrapper });
    expect(trackDashboardView).toHaveBeenCalled();
  });

  it("appelle trackQuickStartClick au clic sur un CTA", async () => {
    vi.mocked(trackQuickStartClick).mockClear();
    render(<QuickStartActions />, { wrapper: TestWrapper });

    const exerciseLink = screen.getByRole("link", { name: /Un exercice/i });
    await userEvent.click(exerciseLink);

    expect(trackQuickStartClick).toHaveBeenCalledWith({
      type: "exercise",
      guided: false,
    });
  });

  it("R4b — n'appelle pas recordOpen sans parcours guidé (liste exercices)", async () => {
    const recordOpen = vi.fn();
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: [],
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen,
      isRecordingOpen: false,
    } as ReturnType<typeof useRecommendations>);

    render(<QuickStartActions />, { wrapper: TestWrapper });
    await userEvent.click(screen.getByRole("link", { name: /Un exercice/i }));

    expect(recordOpen).not.toHaveBeenCalled();
  });

  it("R4b — appelle recordOpen(recommendationId) au clic guidé exercice et défi", async () => {
    const recordOpen = vi.fn().mockResolvedValue({
      id: 1,
      clicked_count: 1,
      last_clicked_at: "2026-03-20T00:00:00+00:00",
    });
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: [
        {
          id: 10,
          exercise_id: 42,
          priority: 9,
          exercise_type: "ADDITION",
          exercise_title: "Addition test",
          reason: "",
          difficulty: "",
        },
        {
          id: 20,
          exercise_type: "SEQUENCE",
          challenge_id: 99,
          priority: 8,
          challenge_title: "Suite logique",
          reason: "",
          difficulty: "",
        },
      ] as ReturnType<typeof useRecommendations>["recommendations"],
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen,
      isRecordingOpen: false,
    } as ReturnType<typeof useRecommendations>);

    render(<QuickStartActions />, { wrapper: TestWrapper });

    await userEvent.click(screen.getByRole("link", { name: /Un exercice/i }));
    expect(recordOpen).toHaveBeenCalledWith(10);

    await userEvent.click(screen.getByRole("link", { name: /Un défi/i }));
    expect(recordOpen).toHaveBeenCalledWith(20);
  });

  it("R4b — Session entrelacée ne déclenche pas recordOpen", async () => {
    const recordOpen = vi.fn();
    vi.mocked(useRecommendations).mockReturnValue({
      recommendations: [
        {
          id: 10,
          exercise_id: 42,
          priority: 9,
          exercise_type: "ADDITION",
          exercise_title: "X",
          reason: "",
          difficulty: "",
        },
      ] as ReturnType<typeof useRecommendations>["recommendations"],
      isLoading: false,
      error: null,
      generate: vi.fn(),
      isGenerating: false,
      complete: vi.fn(),
      isCompleting: false,
      recordOpen,
      isRecordingOpen: false,
    } as ReturnType<typeof useRecommendations>);

    render(<QuickStartActions />, { wrapper: TestWrapper });
    recordOpen.mockClear();
    await userEvent.click(screen.getByRole("link", { name: /Session entrelacée/i }));

    expect(recordOpen).not.toHaveBeenCalled();
  });
});
