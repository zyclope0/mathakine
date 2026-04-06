import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act, waitFor } from "@testing-library/react";
import type { User } from "@/types/api";

const mockGetSessions = vi.fn();
const mockRevokeSession = vi.fn();
const mockUpdateSettings = vi.fn();
const mockDeleteAccount = vi.fn();
const mockExportData = vi.fn();
const mockSetOnUpdateSuccess = vi.fn();
const mockApiGet = vi.fn();

vi.mock("@/lib/api/client", () => ({
  api: {
    get: (...args: unknown[]) => mockApiGet(...args),
  },
}));

vi.mock("@/hooks/useSettings", () => ({
  useSettings: () => ({
    updateSettings: mockUpdateSettings,
    isUpdatingSettings: false,
    setOnUpdateSuccess: mockSetOnUpdateSuccess,
    exportData: mockExportData,
    isExportingData: false,
    deleteAccount: mockDeleteAccount,
    isDeletingAccount: false,
    getSessions: mockGetSessions,
    revokeSession: mockRevokeSession,
    isRevokingSession: false,
  }),
}));

const mockUseAuth = vi.fn();
vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => mockUseAuth(),
}));

import { useSettingsPageController } from "@/hooks/useSettingsPageController";

function baseUser(overrides: Partial<User> = {}): User {
  return {
    id: 1,
    username: "tester",
    email: "t@t.com",
    role: "apprenant",
    is_active: true,
    language_preference: "fr",
    timezone: "UTC",
    ...overrides,
  };
}

describe("useSettingsPageController", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetSessions.mockResolvedValue([]);
    mockApiGet.mockResolvedValue({ has_completed: false, latest: null });
    mockUseAuth.mockReturnValue({ user: baseUser() });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("synchronise les formulaires depuis user au montage", async () => {
    const user = {
      ...baseUser({
        language_preference: "en",
        timezone: "Europe/Paris",
      }),
      accessibility_settings: {
        notification_preferences: {
          achievements: false,
          progress: true,
          recommendations: true,
          news: true,
        },
        privacy_settings: {
          is_public_profile: true,
          allow_friend_requests: false,
          show_in_leaderboards: true,
          data_retention_consent: true,
          marketing_consent: false,
        },
      } as unknown as NonNullable<User["accessibility_settings"]>,
    } as User;
    mockUseAuth.mockReturnValue({ user });

    const { result } = renderHook(() => useSettingsPageController());

    await waitFor(() => {
      expect(result.current.languageSettings.language_preference).toBe("en");
      expect(result.current.languageSettings.timezone).toBe("Europe/Paris");
      expect(result.current.notificationSettings.achievements).toBe(false);
      expect(result.current.privacySettings.is_public_profile).toBe(true);
    });
  });

  it("ré-applique la sync quand l’utilisateur change (id différent)", async () => {
    const u1 = baseUser({ id: 1, language_preference: "fr" });
    const u2 = baseUser({ id: 2, language_preference: "en" });
    mockUseAuth.mockReturnValue({ user: u1 });

    const { result, rerender } = renderHook(() => useSettingsPageController());

    await waitFor(() => {
      expect(result.current.languageSettings.language_preference).toBe("fr");
    });

    mockUseAuth.mockReturnValue({ user: u2 });
    rerender();

    await waitFor(() => {
      expect(result.current.languageSettings.language_preference).toBe("en");
    });
  });

  it("visibleSessionCount initial = SESSIONS_PAGE_SIZE", async () => {
    const { result } = renderHook(() => useSettingsPageController());
    await waitFor(() => {
      expect(result.current.visibleSessionCount).toBe(result.current.SESSIONS_PAGE_SIZE);
    });
  });

  it("confirmRevokeSession appelle revokeSession puis reset l’id", async () => {
    const { result } = renderHook(() => useSettingsPageController());

    await act(async () => {
      result.current.handleRevokeSession(42);
    });
    expect(result.current.sessionToRevoke).toBe(42);

    await act(async () => {
      result.current.confirmRevokeSession();
    });

    expect(mockRevokeSession).toHaveBeenCalledWith(42);
    expect(result.current.sessionToRevoke).toBeNull();
  });

  it("handleDeleteAccount: premier clic active la confirmation", async () => {
    const { result } = renderHook(() => useSettingsPageController());

    await act(async () => {
      result.current.handleDeleteAccount();
    });

    expect(result.current.showDeleteConfirm).toBe(true);
    expect(mockDeleteAccount).not.toHaveBeenCalled();
  });

  it("handleDeleteAccount: second clic appelle deleteAccount", async () => {
    const { result } = renderHook(() => useSettingsPageController());

    await act(async () => {
      result.current.handleDeleteAccount();
    });
    await act(async () => {
      result.current.handleDeleteAccount();
    });

    expect(mockDeleteAccount).toHaveBeenCalledTimes(1);
  });

  it("enregistre setOnUpdateSuccess au montage", async () => {
    renderHook(() => useSettingsPageController());
    await waitFor(() => {
      expect(mockSetOnUpdateSuccess).toHaveBeenCalled();
    });
  });

  it("charge les sessions et le diagnostic au montage", async () => {
    mockGetSessions.mockResolvedValue([
      {
        id: 9,
        last_activity: "2024-01-01",
        created_at: "2024-01-01",
        expires_at: "2025-01-01",
        is_active: true,
      },
    ]);
    mockApiGet.mockResolvedValue({
      has_completed: true,
      latest: { completed_at: "2024-01-01", scores: {} },
    });

    const { result } = renderHook(() => useSettingsPageController());

    await waitFor(() => {
      expect(mockGetSessions).toHaveBeenCalled();
      expect(result.current.sessions).toHaveLength(1);
      expect(result.current.diagnosticStatus?.has_completed).toBe(true);
    });
  });

  it("visibleSessions est dérivé de sessions et du plafond visibleSessionCount", async () => {
    mockGetSessions.mockResolvedValue([
      {
        id: 1,
        last_activity: "2024-01-01",
        created_at: "2024-01-01",
        expires_at: "2025-01-01",
        is_active: true,
      },
      {
        id: 2,
        last_activity: "2024-01-02",
        created_at: "2024-01-02",
        expires_at: "2025-01-02",
        is_active: true,
      },
      {
        id: 3,
        last_activity: "2024-01-03",
        created_at: "2024-01-03",
        expires_at: "2025-01-03",
        is_active: true,
      },
      {
        id: 4,
        last_activity: "2024-01-04",
        created_at: "2024-01-04",
        expires_at: "2025-01-04",
        is_active: true,
      },
    ]);

    const { result } = renderHook(() => useSettingsPageController());

    await waitFor(() => {
      expect(result.current.sessions).toHaveLength(4);
    });

    expect(result.current.visibleSessionCount).toBe(result.current.SESSIONS_PAGE_SIZE);
    expect(result.current.visibleSessions).toHaveLength(3);
    expect(result.current.visibleSessions.map((s) => s.id)).toEqual([1, 2, 3]);
  });
});
