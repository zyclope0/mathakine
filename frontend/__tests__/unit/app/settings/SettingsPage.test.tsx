import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import type { UseSettingsPageControllerResult } from "@/hooks/useSettingsPageController";
import { getVisibleSessions } from "@/lib/settings/settingsPage";

const navMocks = vi.hoisted(() => ({
  push: vi.fn(),
}));

vi.mock("@/components/auth/ProtectedRoute", () => ({
  ProtectedRoute: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: navMocks.push }),
}));

vi.mock("next-intl", () => ({
  useTranslations: (ns?: string) => (key: string) => (ns ? `${ns}.${key}` : key),
}));

const mockController = vi.fn();
vi.mock("@/hooks/useSettingsPageController", () => ({
  useSettingsPageController: () => mockController(),
}));

import SettingsPage from "@/app/settings/page";

function buildController(
  overrides: Partial<UseSettingsPageControllerResult> = {}
): UseSettingsPageControllerResult {
  const noop = () => {};
  const base: UseSettingsPageControllerResult = {
    activeSection: "general",
    setActiveSection: vi.fn(),
    languageSettings: { language_preference: "fr", timezone: "UTC" },
    setLanguageSettings: vi.fn(),
    notificationSettings: {
      achievements: true,
      progress: true,
      recommendations: true,
      news: false,
    },
    setNotificationSettings: vi.fn(),
    privacySettings: {
      is_public_profile: false,
      allow_friend_requests: true,
      show_in_leaderboards: true,
      data_retention_consent: true,
      marketing_consent: false,
    },
    setPrivacySettings: vi.fn(),
    sessions: [],
    visibleSessions: [],
    isLoadingSessions: false,
    showDeleteConfirm: false,
    setShowDeleteConfirm: vi.fn(),
    visibleSessionCount: 3,
    setVisibleSessionCount: vi.fn(),
    diagnosticStatus: null,
    sessionToRevoke: null,
    setSessionToRevoke: vi.fn(),
    SESSIONS_PAGE_SIZE: 3,
    handleSaveLanguage: noop,
    handleSavePrivacy: noop,
    handleSaveNotifications: noop,
    handleExportData: noop,
    handleDeleteAccount: noop,
    handleRevokeSession: noop,
    confirmRevokeSession: noop,
    isUpdatingSettings: false,
    isExportingData: false,
    isDeletingAccount: false,
    isRevokingSession: false,
  };
  const merged = { ...base, ...overrides };
  return {
    ...merged,
    visibleSessions:
      overrides.visibleSessions !== undefined
        ? overrides.visibleSessions
        : getVisibleSessions(merged.sessions, merged.visibleSessionCount),
  };
}

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockController.mockImplementation(() => buildController());
  });

  it("rend le PageHeader (titre settings)", () => {
    render(<SettingsPage />);
    expect(screen.getByText("settings.title")).toBeInTheDocument();
  });

  it("section générale: titre langue visible", () => {
    render(<SettingsPage />);
    expect(screen.getByText("settings.language.title")).toBeInTheDocument();
  });

  it("navigation mobile: Select présent", () => {
    const { container } = render(<SettingsPage />);
    const triggers = container.querySelectorAll('[role="combobox"]');
    expect(triggers.length).toBeGreaterThanOrEqual(1);
  });

  it("navigation desktop: boutons de menu", () => {
    render(<SettingsPage />);
    expect(screen.getByRole("button", { name: "settings.menu.general" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "settings.menu.notifications" })).toBeInTheDocument();
  });

  it("section sécurité: état chargement sessions affiche un spinner", () => {
    mockController.mockImplementation(() =>
      buildController({ activeSection: "security", isLoadingSessions: true })
    );
    const { container } = render(<SettingsPage />);
    expect(container.querySelector(".animate-spin")).toBeTruthy();
  });

  it("section données: bloc diagnostic visible", () => {
    mockController.mockImplementation(() =>
      buildController({
        activeSection: "data",
        diagnosticStatus: {
          has_completed: false,
          latest: null,
        },
      })
    );
    render(<SettingsPage />);
    expect(screen.getByText("settings.diagnostic.title")).toBeInTheDocument();
  });

  it("navigation desktop appelle setActiveSection", async () => {
    const user = userEvent.setup();
    const setActiveSection = vi.fn();
    mockController.mockImplementation(() => buildController({ setActiveSection }));
    render(<SettingsPage />);
    await user.click(screen.getByRole("button", { name: "settings.menu.notifications" }));
    expect(setActiveSection).toHaveBeenCalledWith("notifications");
  });

  it("section sécurité: titre sessions visible", () => {
    mockController.mockImplementation(() => buildController({ activeSection: "security" }));
    render(<SettingsPage />);
    expect(screen.getByText("settings.sessions.title")).toBeInTheDocument();
  });

  it("section sécurité: bloc confidentialité (titre privacy)", () => {
    mockController.mockImplementation(() => buildController({ activeSection: "security" }));
    render(<SettingsPage />);
    expect(screen.getByText("settings.privacy.title")).toBeInTheDocument();
  });

  it("section données: lancement diagnostic appelle router.push", async () => {
    const user = userEvent.setup();
    navMocks.push.mockClear();
    mockController.mockImplementation(() =>
      buildController({
        activeSection: "data",
        diagnosticStatus: { has_completed: false, latest: null },
      })
    );
    render(<SettingsPage />);
    await user.click(screen.getByRole("button", { name: "settings.diagnostic.start" }));
    expect(navMocks.push).toHaveBeenCalledWith("/diagnostic");
  });

  it("section données: bouton export déclenche handleExportData", async () => {
    const user = userEvent.setup();
    const handleExportData = vi.fn();
    mockController.mockImplementation(() =>
      buildController({
        activeSection: "data",
        diagnosticStatus: { has_completed: false, latest: null },
        handleExportData,
      })
    );
    render(<SettingsPage />);
    const exportButtons = screen.getAllByRole("button", { name: "settings.data.export" });
    await user.click(exportButtons[0]!);
    expect(handleExportData).toHaveBeenCalled();
  });

  it("section données: bouton suppression visible hors confirmation", () => {
    mockController.mockImplementation(() =>
      buildController({
        activeSection: "data",
        showDeleteConfirm: false,
        diagnosticStatus: { has_completed: false, latest: null },
      })
    );
    render(<SettingsPage />);
    const deleteButtons = screen.getAllByRole("button", { name: "settings.data.delete" });
    expect(deleteButtons.length).toBeGreaterThan(0);
  });
});
