import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { AdminAcademyStatsSection } from "@/components/admin/AdminAcademyStatsSection";
import { useAcademyStats } from "@/hooks/useAcademyStats";

vi.mock("@/hooks/useAcademyStats", () => ({
  useAcademyStats: vi.fn(),
}));

describe("AdminAcademyStatsSection", () => {
  it("affiche les KPI academie et les top listes a partir du hook existant", () => {
    vi.mocked(useAcademyStats).mockReturnValue({
      stats: {
        archive_status: "active",
        academy_statistics: {
          total_exercises: 120,
          total_challenges: 18,
          total_content: 138,
          archived_exercises: 4,
          ai_generated: 12,
          ai_generated_exercises: 9,
          ai_generated_challenges: 3,
          ai_generated_percentage: 8.7,
        },
        by_discipline: {
          algebra: { count: 50, discipline_name: "Algebre", percentage: 41.6 },
          geometry: { count: 35, discipline_name: "Geometrie", percentage: 29.1 },
          logic: { count: 20, discipline_name: "Logique", percentage: 16.6 },
        },
        by_rank: {
          initiate: {
            count: 60,
            rank_name: "Initie",
            description: "Debutant",
            min_age: 6,
            percentage: 50,
          },
          padawan: {
            count: 30,
            rank_name: "Padawan",
            description: "Intermediaire",
            min_age: 8,
            percentage: 25,
          },
        },
        by_apprentice_group: {},
        global_performance: {
          total_attempts: 640,
          exercise_attempts: 500,
          challenge_attempts: 140,
          successful_attempts: 420,
          mastery_rate: 65.6,
          challenge_mastery_rate: 52.0,
          message: "Stable",
        },
        legendary_challenges: [],
        sage_wisdom: "Toujours en mouvement est l'avenir.",
      },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    });

    render(<AdminAcademyStatsSection />);

    expect(screen.getByText("Statistiques academie")).toBeInTheDocument();
    expect(screen.getByText("120")).toBeInTheDocument();
    expect(screen.getByText("18")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("640")).toBeInTheDocument();
    expect(screen.getByText("Disciplines dominantes")).toBeInTheDocument();
    expect(screen.getByText("Algebre")).toBeInTheDocument();
    expect(screen.getByText("Repartition par rang")).toBeInTheDocument();
    expect(screen.getByText("Initie")).toBeInTheDocument();
  });
});
