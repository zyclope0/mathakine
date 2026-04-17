import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import fr from "@/messages/fr.json";

import AdminAuditLogPage from "./audit-log/page";
import AdminConfigPage from "./config/page";
import AdminFeedbackPage from "./feedback/page";
import AdminModerationPage from "./moderation/page";
import AdminUsersPage from "./users/page";

vi.mock("@/hooks/useAdminAuditLog", () => ({
  useAdminAuditLog: () => ({
    items: [],
    total: 0,
    isLoading: false,
    error: null,
  }),
}));

vi.mock("@/hooks/useAdminConfig", () => ({
  useAdminConfig: () => ({
    settings: [
      {
        key: "test_flag",
        label: "Test",
        type: "bool" as const,
        value: true,
        category: "autres",
      },
    ],
    isLoading: false,
    error: null,
    updateSettings: vi.fn(),
    isUpdating: false,
  }),
}));

vi.mock("@/hooks/useAdminFeedback", () => ({
  useAdminFeedback: () => ({
    feedback: [],
    isLoading: false,
    error: null,
  }),
}));

vi.mock("@/hooks/useAdminModeration", () => ({
  useAdminModeration: () => ({
    exercises: [],
    challenges: [],
    totalExercises: 0,
    totalChallenges: 0,
    isLoading: false,
    error: null,
    refetch: vi.fn(),
  }),
}));

vi.mock("@/hooks/useAdminUsers", () => ({
  useAdminUsers: () => ({
    users: [],
    total: 0,
    isLoading: false,
    error: null,
    updateUserActive: vi.fn(),
    updateUserRole: vi.fn(),
    sendResetPassword: vi.fn(),
    resendVerification: vi.fn(),
    deleteUser: vi.fn(),
    isUpdating: false,
    isSendingReset: false,
    isResendingVerification: false,
    isDeleting: false,
  }),
}));

vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({ user: { id: 1 } }),
}));

vi.mock("@/components/admin/ExerciseEditModal", () => ({
  ExerciseEditModal: () => null,
}));
vi.mock("@/components/admin/ChallengeEditModal", () => ({
  ChallengeEditModal: () => null,
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("Admin route pages i18n smoke (QF-03)", () => {
  it("audit-log: titre depuis les messages", () => {
    render(<AdminAuditLogPage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Journal d'audit" })).toBeInTheDocument();
  });

  it("config: titre depuis les messages", () => {
    render(<AdminConfigPage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Paramètres globaux" })).toBeInTheDocument();
  });

  it("feedback: titre depuis les messages", () => {
    render(<AdminFeedbackPage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Signalements" })).toBeInTheDocument();
  });

  it("moderation: titre depuis les messages", () => {
    render(<AdminModerationPage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Modération IA" })).toBeInTheDocument();
  });

  it("users: titre depuis les messages", () => {
    render(<AdminUsersPage />, { wrapper: Wrapper });
    expect(screen.getByRole("heading", { name: "Utilisateurs" })).toBeInTheDocument();
  });
});
