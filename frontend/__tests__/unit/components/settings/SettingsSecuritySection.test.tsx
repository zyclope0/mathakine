import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SettingsSecuritySection } from "@/components/settings/SettingsSecuritySection";
import type { PrivacySettingsState } from "@/lib/settings/settingsPage";
import type { UserSession } from "@/hooks/useSettings";

vi.mock("next-intl", () => ({
  useTranslations: (ns?: string) => (key: string, values?: { count?: number }) => {
    if (ns === "settings.sessions" && key === "showMore" && values?.count !== undefined) {
      return `showMore:${values.count}`;
    }
    return ns ? `${ns}.${key}` : key;
  },
}));

vi.mock("@/components/settings/SaveButton", () => ({
  SaveButton: ({ onClick, isLoading }: { onClick: () => void; isLoading: boolean }) => (
    <button type="button" onClick={onClick} data-loading={isLoading}>
      save-privacy
    </button>
  ),
}));

const privacy: PrivacySettingsState = {
  is_public_profile: false,
  allow_friend_requests: true,
  show_in_leaderboards: true,
  data_retention_consent: true,
  marketing_consent: false,
};

const sessionBase = {
  last_activity: "2024-06-01T12:00:00.000Z",
  created_at: "2024-01-01T00:00:00Z",
  expires_at: "2025-01-01T00:00:00Z",
  is_active: true,
};

function renderSection(
  overrides: Partial<React.ComponentProps<typeof SettingsSecuritySection>> = {}
) {
  const setPrivacySettings = vi.fn();
  const setSessionToRevoke = vi.fn();
  const setVisibleSessionCount = vi.fn();
  const onSavePrivacy = vi.fn();
  const onRevokeSession = vi.fn();
  const onConfirmRevokeSession = vi.fn();

  const props: React.ComponentProps<typeof SettingsSecuritySection> = {
    privacySettings: privacy,
    setPrivacySettings,
    onSavePrivacy,
    isUpdatingSettings: false,
    sessions: [],
    visibleSessions: [],
    isLoadingSessions: false,
    sessionToRevoke: null,
    setSessionToRevoke,
    onRevokeSession,
    onConfirmRevokeSession,
    visibleSessionCount: 3,
    setVisibleSessionCount,
    sessionsPageSize: 3,
    isRevokingSession: false,
    ...overrides,
  };

  const view = render(<SettingsSecuritySection {...props} />);
  return {
    ...view,
    setPrivacySettings,
    setSessionToRevoke,
    onRevokeSession,
    onConfirmRevokeSession,
    setVisibleSessionCount,
  };
}

describe("SettingsSecuritySection", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders privacy card title and toggle ids", () => {
    renderSection();
    expect(screen.getByText("settings.privacy.title")).toBeInTheDocument();
    expect(screen.getByLabelText("settings.privacy.publicProfile")).toBeInTheDocument();
  });

  it("calls setPrivacySettings when a switch toggles", async () => {
    const user = userEvent.setup();
    const { setPrivacySettings } = renderSection();
    await user.click(screen.getByLabelText("settings.privacy.publicProfile"));
    expect(setPrivacySettings).toHaveBeenCalled();
  });

  it("shows loading state for sessions", () => {
    renderSection({ isLoadingSessions: true });
    expect(document.querySelector(".animate-spin")).toBeTruthy();
  });

  it("shows empty sessions message", () => {
    renderSection({ sessions: [], visibleSessions: [] });
    expect(screen.getByText("settings.sessions.noSessions")).toBeInTheDocument();
  });

  it("calls onRevokeSession with session id when revoke is clicked", async () => {
    const user = userEvent.setup();
    const s: UserSession = {
      id: 42,
      ...sessionBase,
      is_current: false,
    };
    const { onRevokeSession } = renderSection({
      sessions: [s],
      visibleSessions: [s],
    });
    await user.click(screen.getByRole("button", { name: "settings.sessions.revoke" }));
    expect(onRevokeSession).toHaveBeenCalledWith(42);
  });

  it("calls onConfirmRevokeSession when destructive revoke is confirmed", async () => {
    const user = userEvent.setup();
    const s: UserSession = {
      id: 42,
      ...sessionBase,
      is_current: false,
    };
    const onConfirmRevokeSession = vi.fn();
    renderSection({
      sessions: [s],
      visibleSessions: [s],
      sessionToRevoke: 42,
      onConfirmRevokeSession,
    });
    await user.click(screen.getByRole("button", { name: "settings.sessions.revoke" }));
    expect(onConfirmRevokeSession).toHaveBeenCalled();
  });

  it("calls setSessionToRevoke(null) when cancel is clicked in revoke mode", async () => {
    const user = userEvent.setup();
    const s: UserSession = {
      id: 42,
      ...sessionBase,
      is_current: false,
    };
    const { setSessionToRevoke } = renderSection({
      sessions: [s],
      visibleSessions: [s],
      sessionToRevoke: 42,
    });
    await user.click(screen.getByRole("button", { name: "settings.actions.cancel" }));
    expect(setSessionToRevoke).toHaveBeenCalledWith(null);
  });

  it("does not show revoke for current session", () => {
    const s: UserSession = {
      id: 1,
      ...sessionBase,
      is_current: true,
    };
    renderSection({
      sessions: [s],
      visibleSessions: [s],
    });
    expect(screen.queryByRole("button", { name: "settings.sessions.revoke" })).toBeNull();
  });
});
