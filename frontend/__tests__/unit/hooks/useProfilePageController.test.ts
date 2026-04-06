import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useProfilePageController } from "@/hooks/useProfilePageController";
import { useProfile } from "@/hooks/useProfile";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useAgeGroupDisplay } from "@/hooks/useChallengeTranslations";
import type { UserBadge } from "@/types/api";

vi.mock("@/hooks/useProfile", () => ({
  useProfile: vi.fn(),
}));

vi.mock("@/lib/stores/themeStore", () => ({
  useThemeStore: vi.fn(),
}));

vi.mock("@/hooks/useChallengeTranslations", () => ({
  useAgeGroupDisplay: vi.fn(),
}));

const mockUpdateProfile = vi.fn();
const mockUpdateProfileAsync = vi.fn();
const mockChangePassword = vi.fn();
const mockChangePasswordAsync = vi.fn();
const mockSetTheme = vi.fn();

function buildUser(overrides: Record<string, unknown> = {}) {
  return {
    email: "test@example.com",
    full_name: "Test User",
    username: "testuser",
    role: "apprenant",
    created_at: "2025-01-01T00:00:00Z",
    grade_system: "unifie",
    grade_level: 5,
    age_group: "9-11",
    learning_style: "visuel",
    preferred_difficulty: "normal",
    learning_goal: "progresser",
    practice_rhythm: "20min_jour",
    preferred_theme: "spatial",
    accessibility_settings: {
      high_contrast: false,
      large_text: false,
      reduce_motion: false,
    },
    gamification_level: { current: 3 },
    ...overrides,
  };
}

function buildBadge(
  id: number,
  earnedAt: string | null | undefined,
  overrides: Partial<UserBadge> = {}
): UserBadge & { earned_at?: string | null | undefined } {
  return {
    id,
    code: `badge-${id}`,
    name: `Badge ${id}`,
    description: `Description ${id}`,
    ...(earnedAt === undefined ? {} : { earned_at: earnedAt }),
    ...overrides,
  };
}

function renderProfileController({
  user = buildUser(),
  earnedBadges = [],
}: {
  user?: ReturnType<typeof buildUser> | null;
  earnedBadges?: (UserBadge & { earned_at?: string | null | undefined })[];
} = {}) {
  return renderHook((props) => useProfilePageController(props), {
    initialProps: {
      user,
      earnedBadges,
      tValidation: (key: string) => `validation:${key}`,
      tSecurity: (key: string) => `security:${key}`,
    },
  });
}

describe("useProfilePageController", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockUpdateProfile.mockResolvedValue(undefined);
    mockUpdateProfileAsync.mockResolvedValue(undefined);
    mockChangePassword.mockResolvedValue(undefined);
    mockChangePasswordAsync.mockResolvedValue(undefined);

    vi.mocked(useProfile).mockReturnValue({
      updateProfile: mockUpdateProfile,
      updateProfileAsync: mockUpdateProfileAsync,
      isUpdatingProfile: false,
      changePassword: mockChangePassword,
      changePasswordAsync: mockChangePasswordAsync,
      isChangingPassword: false,
    } as unknown as ReturnType<typeof useProfile>);

    vi.mocked(useThemeStore).mockReturnValue({
      setTheme: mockSetTheme,
    } as ReturnType<typeof useThemeStore>);

    vi.mocked(useAgeGroupDisplay).mockReturnValue(
      (group: string | null | undefined) => `age:${group ?? ""}`
    );
  });

  it("syncs personal info, learning prefs and migrated theme from user", async () => {
    const { result } = renderProfileController({
      user: buildUser({
        email: "neutral@example.com",
        preferred_theme: "neutral",
        accessibility_settings: {
          high_contrast: true,
          large_text: true,
          reduce_motion: false,
        },
      }),
    });

    await waitFor(() => {
      expect(result.current.personalInfo.email).toBe("neutral@example.com");
      expect(result.current.learningPrefs.grade_system).toBe("unifie");
      expect(result.current.accessibilitySettings.preferred_theme).toBe("dune");
    });

    expect(mockSetTheme).toHaveBeenCalledWith("dune");
  });

  it("resyncs state when the user changes", async () => {
    const { result, rerender } = renderProfileController({
      user: buildUser({
        email: "first@example.com",
        preferred_theme: "spatial",
      }),
    });

    await waitFor(() => {
      expect(result.current.personalInfo.email).toBe("first@example.com");
    });

    rerender({
      user: buildUser({
        email: "second@example.com",
        full_name: "Second User",
        preferred_theme: "peach",
        grade_system: "suisse",
      }),
      earnedBadges: [],
      tValidation: (key: string) => `validation:${key}`,
      tSecurity: (key: string) => `security:${key}`,
    });

    await waitFor(() => {
      expect(result.current.personalInfo.email).toBe("second@example.com");
      expect(result.current.personalInfo.full_name).toBe("Second User");
      expect(result.current.learningPrefs.grade_system).toBe("suisse");
      expect(result.current.accessibilitySettings.preferred_theme).toBe("aurora");
    });

    expect(mockSetTheme).toHaveBeenLastCalledWith("aurora");
  });

  it("resets personal info to the latest user values", async () => {
    const user = buildUser({
      email: "reset@example.com",
      full_name: "Reset User",
    });
    const { result } = renderProfileController({ user });

    await waitFor(() => {
      expect(result.current.personalInfo.email).toBe("reset@example.com");
    });

    act(() => {
      result.current.setIsEditingPersonalInfo(true);
      result.current.setPersonalInfo({
        email: "changed@example.com",
        full_name: "Changed User",
      });
      result.current.setErrors({ email: "validation:emailInvalid" });
    });

    act(() => {
      result.current.handleResetPersonalInfo();
    });

    expect(result.current.isEditingPersonalInfo).toBe(false);
    expect(result.current.personalInfo).toEqual({
      email: "reset@example.com",
      full_name: "Reset User",
    });
    expect(result.current.errors).toEqual({});
  });

  it("resets learning preferences to the latest user values", async () => {
    const user = buildUser({
      grade_system: "suisse",
      grade_level: 8,
      age_group: "12-14",
      learning_goal: "reviser",
    });
    const { result } = renderProfileController({ user });

    await waitFor(() => {
      expect(result.current.learningPrefs.grade_system).toBe("suisse");
    });

    act(() => {
      result.current.setIsEditingLearningPrefs(true);
      result.current.setLearningPrefs({
        grade_system: "unifie",
        grade_level: "5",
        age_group: "9-11",
        learning_style: "auditif",
        preferred_difficulty: "facile",
        learning_goal: "samuser",
        practice_rhythm: "flexible",
      });
    });

    act(() => {
      result.current.handleResetLearningPrefs();
    });

    expect(result.current.isEditingLearningPrefs).toBe(false);
    expect(result.current.learningPrefs.grade_system).toBe("suisse");
    expect(result.current.learningPrefs.grade_level).toBe("8");
    expect(result.current.learningPrefs.age_group).toBe("12-14");
    expect(result.current.learningPrefs.learning_goal).toBe("reviser");
  });

  it("stores a validation error for an invalid email", async () => {
    const { result } = renderProfileController();

    await waitFor(() => {
      expect(result.current.personalInfo.email).toBe("test@example.com");
    });

    act(() => {
      expect(result.current.validateEmail("bad-email")).toBe(false);
    });

    expect(result.current.errors.email).toBe("validation:emailInvalid");
  });

  it("blocks password change when the new password is too short", async () => {
    const { result } = renderProfileController();

    act(() => {
      result.current.setShowPasswordForm(true);
      result.current.setPasswordData({
        current_password: "oldpass123",
        new_password: "short",
        confirm_password: "short",
      });
    });

    await act(async () => {
      await result.current.handleChangePassword();
    });

    expect(result.current.errors.new_password).toBe("security:passwordMinLength");
    expect(mockChangePassword).not.toHaveBeenCalled();
    expect(result.current.showPasswordForm).toBe(true);
  });

  it("blocks password change when confirmation mismatches", async () => {
    const { result } = renderProfileController();

    act(() => {
      result.current.setPasswordData({
        current_password: "oldpass123",
        new_password: "newpass123",
        confirm_password: "different",
      });
    });

    await act(async () => {
      await result.current.handleChangePassword();
    });

    expect(result.current.errors.confirm_password).toBe("security:passwordMismatch");
    expect(mockChangePassword).not.toHaveBeenCalled();
  });

  it("changes password and resets the form when fields are valid", async () => {
    const { result } = renderProfileController();

    act(() => {
      result.current.setShowPasswordForm(true);
      result.current.setPasswordData({
        current_password: "oldpass123",
        new_password: "newpass123",
        confirm_password: "newpass123",
      });
    });

    await act(async () => {
      await result.current.handleChangePassword();
    });

    expect(mockChangePassword).toHaveBeenCalledWith({
      current_password: "oldpass123",
      new_password: "newpass123",
    });
    expect(result.current.showPasswordForm).toBe(false);
    expect(result.current.passwordData).toEqual({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });
    expect(result.current.errors).toEqual({});
  });

  it("sorts recent badges by earned_at descending and limits them to 3", async () => {
    const { result } = renderProfileController({
      earnedBadges: [
        buildBadge(1, "2025-01-01T00:00:00Z"),
        buildBadge(2, "2025-02-01T00:00:00Z"),
        buildBadge(3, "2025-03-01T00:00:00Z"),
        buildBadge(4, "2025-04-01T00:00:00Z"),
        buildBadge(5, null),
      ],
    });

    await waitFor(() => {
      expect(result.current.recentBadges.map((badge) => badge.id)).toEqual([4, 3, 2]);
    });
  });
});
