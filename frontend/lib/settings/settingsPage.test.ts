import { describe, it, expect } from "vitest";
import { fr } from "date-fns/locale";
import type { User } from "@/types/api";
import type { UserSession } from "@/hooks/useSettings";
import {
  SESSIONS_PAGE_SIZE,
  normalizeLanguageSettings,
  normalizeNotificationSettings,
  normalizePrivacySettings,
  formatSessionDate,
  getVisibleSessions,
  canShowMoreSessions,
} from "./settingsPage";

describe("SESSIONS_PAGE_SIZE", () => {
  it("vaut 3 (aligné page settings)", () => {
    expect(SESSIONS_PAGE_SIZE).toBe(3);
  });
});

describe("normalizeLanguageSettings", () => {
  it("utilise les champs top-level si absents de accessibility", () => {
    const user: User = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant",
      is_active: true,
      language_preference: "en",
      timezone: "Europe/Paris",
    };
    const out = normalizeLanguageSettings(user);
    expect(out.language_preference).toBe("en");
    expect(out.timezone).toBe("Europe/Paris");
  });

  it("priorise accessibility_settings quand présent", () => {
    const user = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant" as const,
      is_active: true,
      language_preference: "en",
      timezone: "UTC",
      accessibility_settings: {
        language_preference: "fr",
        timezone: "Australia/Sydney",
      } as unknown as NonNullable<User["accessibility_settings"]>,
    } as User;
    const out = normalizeLanguageSettings(user);
    expect(out.language_preference).toBe("fr");
    expect(out.timezone).toBe("Australia/Sydney");
  });

  it("fallback fr / UTC si user absent", () => {
    expect(normalizeLanguageSettings(undefined)).toEqual({
      language_preference: "fr",
      timezone: "UTC",
    });
  });
});

describe("normalizeNotificationSettings", () => {
  it("applique les défauts si pas de prefs", () => {
    const user: User = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant",
      is_active: true,
    };
    expect(normalizeNotificationSettings(user)).toEqual({
      achievements: true,
      progress: true,
      recommendations: true,
      news: false,
    });
  });

  it("lit notification_preferences imbriqué", () => {
    const user = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant" as const,
      is_active: true,
      accessibility_settings: {
        notification_preferences: {
          achievements: false,
          progress: false,
          recommendations: true,
          news: true,
        },
      } as unknown as NonNullable<User["accessibility_settings"]>,
    } as User;
    expect(normalizeNotificationSettings(user)).toEqual({
      achievements: false,
      progress: false,
      recommendations: true,
      news: true,
    });
  });
});

describe("normalizePrivacySettings", () => {
  it("applique les défauts documentés si pas de prefs", () => {
    const user: User = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant",
      is_active: true,
    };
    expect(normalizePrivacySettings(user)).toEqual({
      is_public_profile: false,
      allow_friend_requests: true,
      show_in_leaderboards: true,
      data_retention_consent: true,
      marketing_consent: false,
    });
  });

  it("lit privacy_settings imbriqué", () => {
    const user = {
      id: 1,
      username: "u",
      email: "u@x.com",
      role: "apprenant" as const,
      is_active: true,
      accessibility_settings: {
        privacy_settings: {
          is_public_profile: true,
          allow_friend_requests: false,
          show_in_leaderboards: false,
          data_retention_consent: false,
          marketing_consent: true,
        },
      } as unknown as NonNullable<User["accessibility_settings"]>,
    } as User;
    expect(normalizePrivacySettings(user)).toEqual({
      is_public_profile: true,
      allow_friend_requests: false,
      show_in_leaderboards: false,
      data_retention_consent: false,
      marketing_consent: true,
    });
  });
});

describe("formatSessionDate", () => {
  it("produit une chaîne non vide pour une date ISO", () => {
    const s = formatSessionDate("2024-06-15T12:00:00.000Z", fr);
    expect(s.length).toBeGreaterThan(0);
  });
});

describe("getVisibleSessions", () => {
  const sessions: UserSession[] = [
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
  ];

  it("retourne les N premières sessions", () => {
    expect(getVisibleSessions(sessions, 2)).toHaveLength(2);
    expect(getVisibleSessions(sessions, 2)[0]?.id).toBe(1);
    expect(getVisibleSessions(sessions, 2)[1]?.id).toBe(2);
  });

  it("ne plante pas si visibleCount négatif (slice)", () => {
    expect(getVisibleSessions(sessions, -1)).toEqual([]);
  });
});

describe("canShowMoreSessions", () => {
  const sessions: UserSession[] = [
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
  ];

  it("true si visibleCount < longueur", () => {
    expect(canShowMoreSessions(sessions, 1)).toBe(true);
  });

  it("false si tout est visible", () => {
    expect(canShowMoreSessions(sessions, 2)).toBe(false);
  });
});
