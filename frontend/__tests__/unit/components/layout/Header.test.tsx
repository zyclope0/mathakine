"use client";

import type { AnchorHTMLAttributes, ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { Header } from "@/components/layout/Header";
import { useAuth } from "@/hooks/useAuth";

const { mockSetChatOpen } = vi.hoisted(() => ({
  mockSetChatOpen: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

vi.mock("@/components/ui/button", () => ({
  Button: ({
    children,
    asChild,
    ...props
  }: ButtonHTMLAttributes<HTMLButtonElement> & {
    asChild?: boolean;
    children: ReactNode;
  }) => (asChild ? <>{children}</> : <button {...props}>{children}</button>),
}));

vi.mock("@/components/theme/ThemeSelectorCompact", () => ({
  ThemeSelectorCompact: () => <div data-testid="theme-selector" />,
}));

vi.mock("@/components/theme/DarkModeToggle", () => ({
  DarkModeToggle: () => <div data-testid="dark-mode-toggle" />,
}));

vi.mock("@/components/locale/LanguageSelector", () => ({
  LanguageSelector: () => <div data-testid="language-selector" />,
}));

vi.mock("@/components/LogoMathakine", () => ({
  LogoMathakine: () => <div data-testid="logo-mathakine" />,
}));

vi.mock("@/components/ui/dropdown-menu", () => ({
  DropdownMenu: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  DropdownMenuTrigger: ({ children }: { children: ReactNode }) => <>{children}</>,
  DropdownMenuContent: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  DropdownMenuItem: ({
    children,
    asChild,
    ...props
  }: HTMLAttributes<HTMLDivElement> & { asChild?: boolean; children: ReactNode }) =>
    asChild ? <>{children}</> : <div {...props}>{children}</div>,
  DropdownMenuLabel: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  DropdownMenuSeparator: () => <hr />,
}));

vi.mock("next-intl", () => ({
  useTranslations: (namespace: string) => (key: string) => {
    const messages: Record<string, Record<string, string>> = {
      navigation: {
        home: "Accueil",
        homeLearner: "Mon espace",
        dashboard: "Tableau de bord",
        exercises: "Exercices",
        challenges: "Defis logiques",
        badges: "Badges",
        leaderboard: "Classement",
        profile: "Profil",
        settings: "Parametres",
        admin: "Admin",
      },
      auth: {
        logout: "Se deconnecter",
        "login.title": "Connexion",
        "register.title": "Inscription",
      },
      home: {
        "hero.ctaAssistant": "Assistant",
      },
    };

    return messages[namespace]?.[key] ?? `${namespace}.${key}`;
  },
}));

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({
    shouldReduceMotion: false,
    createTransition: () => ({ duration: 0.15 }),
  }),
}));

vi.mock("@/lib/stores/chatStore", () => ({
  useChatStore: () => ({ setOpen: mockSetChatOpen }),
}));

vi.mock("framer-motion", () => ({
  AnimatePresence: ({ children }: { children: ReactNode }) => <>{children}</>,
  LazyMotion: ({ children }: { children: ReactNode }) => <>{children}</>,
  domAnimation: {},
  m: {
    div: ({ children, ...props }: HTMLAttributes<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}));

describe("Header", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("invité : pas de bouton Assistant dans le header (accès via le FAB global)", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      logout: vi.fn(),
      isAuthenticated: false,
    } as unknown as ReturnType<typeof useAuth>);

    render(<Header />);
    expect(screen.queryByRole("button", { name: "Assistant" })).not.toBeInTheDocument();
  });

  it("affiche la navigation apprenant avec classement et dashboard discret dans le menu", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        username: "luke",
        role: "apprenant",
        is_email_verified: true,
        access_scope: "full",
      },
      logout: vi.fn(),
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(<Header />);

    expect(screen.getByText("Mon espace")).toBeInTheDocument();
    expect(screen.getByText("Classement")).toBeInTheDocument();
    expect(screen.getByText("Exercices")).toBeInTheDocument();
    expect(screen.getByText("Badges")).toBeInTheDocument();
    expect(screen.getAllByText("Tableau de bord")).toHaveLength(1);
  });

  it("affiche la navigation adulte et le lien admin pour un admin", () => {
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 2,
        username: "obiwan",
        role: "admin",
        is_email_verified: true,
        access_scope: "full",
      },
      logout: vi.fn(),
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(<Header />);

    expect(screen.getByText("Tableau de bord")).toBeInTheDocument();
    expect(screen.getByText("Classement")).toBeInTheDocument();
    expect(screen.getByText("Admin")).toBeInTheDocument();
    expect(screen.queryByText("Mon espace")).not.toBeInTheDocument();
  });

  it("ouvre et ferme le menu mobile", async () => {
    const user = userEvent.setup();
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        username: "luke",
        role: "apprenant",
        is_email_verified: true,
        access_scope: "full",
      },
      logout: vi.fn(),
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(<Header />);

    await user.click(screen.getByRole("button", { name: "Ouvrir le menu" }));
    expect(screen.getByRole("button", { name: "Fermer le menu" })).toBeInTheDocument();
    expect(screen.getByRole("menu")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Fermer le menu" }));
    expect(screen.queryByRole("menu")).not.toBeInTheDocument();
  });

  it("CTA assistant desktop appelle setChatOpen(true)", async () => {
    const user = userEvent.setup();
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: 1,
        username: "luke",
        role: "apprenant",
        is_email_verified: true,
        access_scope: "full",
      },
      logout: vi.fn(),
      isAuthenticated: true,
    } as unknown as ReturnType<typeof useAuth>);

    render(<Header />);

    await user.click(screen.getByRole("button", { name: "Assistant" }));

    expect(mockSetChatOpen).toHaveBeenCalledWith(true);
  });
});
