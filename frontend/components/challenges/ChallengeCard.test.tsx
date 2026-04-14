import { describe, it, expect, vi } from "vitest";
import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ChallengeCard } from "./ChallengeCard";
import type { Challenge } from "@/types/api";
import fr from "@/messages/fr.json";

vi.mock("next/link", () => ({
  default: function MockLink({
    children,
    href,
    ...rest
  }: {
    children: ReactNode;
    href: string;
    className?: string;
    "aria-label"?: string;
  }) {
    return (
      <a href={href} {...rest}>
        {children}
      </a>
    );
  },
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </NextIntlClientProvider>
  );
}

describe("ChallengeCard", () => {
  const mockChallenge: Challenge = {
    id: 42,
    title: "Defi test",
    description: "Description du defi pour le test.",
    challenge_type: "sequence",
    age_group: "9-11",
    view_count: 3,
    tags: null,
  };

  it("affiche le titre et la description du defi", () => {
    render(<ChallengeCard challenge={mockChallenge} completed={false} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByText("Defi test")).toBeInTheDocument();
    expect(screen.getByText("Description du defi pour le test.")).toBeInTheDocument();
  });

  it("pointe vers la page detail du defi", () => {
    render(<ChallengeCard challenge={mockChallenge} completed={false} />, {
      wrapper: TestWrapper,
    });
    const link = screen.getByRole("link", { name: /résoudre/i });
    expect(link).toHaveAttribute("href", "/challenge/42");
  });

  it("expose la carte avec aria-labelledby et aria-describedby stables", () => {
    render(<ChallengeCard challenge={mockChallenge} completed={false} />, {
      wrapper: TestWrapper,
    });
    const card = screen.getByRole("article");
    expect(card).toHaveAttribute("aria-labelledby", "challenge-title-42");
    expect(card).toHaveAttribute("aria-describedby", "challenge-description-42");
  });

  it("affiche l'icone IA lorsque les tags indiquent une generation IA", () => {
    const withAi: Challenge = {
      ...mockChallenge,
      tags: "ai",
    };
    render(<ChallengeCard challenge={withAi} completed={false} />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByLabelText(/intelligence artificielle/i)).toBeInTheDocument();
  });

  it("n'affiche pas le badge resolu quand completed est false", () => {
    render(<ChallengeCard challenge={mockChallenge} completed={false} />, {
      wrapper: TestWrapper,
    });
    expect(screen.queryByLabelText(/^résolu$/i)).not.toBeInTheDocument();
  });

  it("affiche le badge resolu accessible quand completed est true", () => {
    render(<ChallengeCard challenge={mockChallenge} completed />, {
      wrapper: TestWrapper,
    });
    expect(screen.getByLabelText(/^résolu$/i)).toBeInTheDocument();
  });
});
