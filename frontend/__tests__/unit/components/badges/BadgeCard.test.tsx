import type { ReactNode } from "react";
import { createElement } from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";
import { BadgeCard } from "@/components/badges/BadgeCard";
import type { Badge, UserBadge } from "@/types/api";

vi.mock("framer-motion", () => ({
  motion: {
    div: ({
      children,
      className,
      ...rest
    }: {
      children?: ReactNode;
      className?: string;
      [key: string]: unknown;
    }) => createElement("div", { className, ...rest }, children),
  },
}));

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({
    createVariants: (v: Record<string, unknown>) => v,
    createTransition: (t: Record<string, unknown>) => t,
    shouldReduceMotion: true,
  }),
}));

const badgeBronze = {
  id: 1,
  name: "Test Badge",
  code: "test_badge",
  description: "Desc",
  difficulty: "bronze",
  category: "progression",
  points_reward: 25,
  exercise_type: "ADDITION",
} as Badge;

function wrap(node: ReactNode) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {node}
    </NextIntlClientProvider>
  );
}

describe("BadgeCard", () => {
  it("renders earned state with check indicator", () => {
    const ub = { id: 1, earned_at: "2024-01-01" } as UserBadge;
    render(wrap(<BadgeCard badge={badgeBronze} userBadge={ub} isEarned progress={null} />));
    expect(screen.getByRole("article")).toBeInTheDocument();
    expect(screen.getByText(/Obtenu le/)).toBeInTheDocument();
  });

  it("renders locked state with lock overlay on icon", () => {
    render(wrap(<BadgeCard badge={badgeBronze} isEarned={false} progress={null} />));
    expect(screen.getByRole("article")).toBeInTheDocument();
    expect(screen.getByLabelText(/Verrouillé/i)).toBeInTheDocument();
  });

  it("shows pin control when canPin and onTogglePin", () => {
    const ub = { id: 1 } as UserBadge;
    const onToggle = vi.fn();
    render(
      wrap(
        <BadgeCard
          badge={badgeBronze}
          userBadge={ub}
          isEarned
          progress={null}
          compact
          canPin
          onTogglePin={onToggle}
          isPinned={false}
        />
      )
    );
    const pinBtn = screen.getByRole("button", { name: /Épingler/i });
    expect(pinBtn).toBeInTheDocument();
  });

  it("renders progress bar for locked badge with progress", () => {
    render(
      wrap(
        <BadgeCard
          badge={{ ...badgeBronze, criteria_text: "Faire 5 exos" }}
          isEarned={false}
          progress={{
            current: 2,
            target: 5,
            progress: 0.4,
          }}
        />
      )
    );
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("progressbar aria-label utilise le code si le nom est vide", () => {
    render(
      wrap(
        <BadgeCard
          badge={{ ...badgeBronze, name: "", criteria_text: "Critère" }}
          isEarned={false}
          progress={{ current: 1, target: 5, progress: 0.2 }}
        />
      )
    );
    const bar = screen.getByRole("progressbar");
    expect(bar.getAttribute("aria-label")).toMatch(/test_badge/);
    expect(bar.getAttribute("aria-label")).toMatch(/20/);
  });
});
