import { describe, it, expect } from "vitest";
import type { UserSession } from "@/hooks/useSettings";
import {
  PRIVACY_TOGGLE_CONFIG,
  buildPrivacyToggleRows,
  resolveSessionLocationDisplay,
  computeVisibleCountAfterShowMore,
} from "@/lib/settings/settingsSecurity";
import type { PrivacySettingsState } from "@/lib/settings/settingsPage";

const labels = {
  is_public_profile: { label: "L1", desc: "D1" },
  allow_friend_requests: { label: "L2", desc: "D2" },
  show_in_leaderboards: { label: "L3", desc: "D3" },
  data_retention_consent: { label: "L4", desc: "D4" },
  marketing_consent: { label: "L5", desc: "D5" },
};

const basePrivacy: PrivacySettingsState = {
  is_public_profile: true,
  allow_friend_requests: false,
  show_in_leaderboards: true,
  data_retention_consent: false,
  marketing_consent: true,
};

describe("PRIVACY_TOGGLE_CONFIG", () => {
  it("has 5 stable ids matching legacy order", () => {
    expect(PRIVACY_TOGGLE_CONFIG.map((c) => c.id)).toEqual([
      "privacy-public-profile",
      "privacy-friend-requests",
      "privacy-leaderboards",
      "privacy-data-retention",
      "privacy-marketing",
    ]);
  });
});

describe("buildPrivacyToggleRows", () => {
  it("maps settings and labels in config order", () => {
    const rows = buildPrivacyToggleRows(basePrivacy, labels);
    expect(rows).toHaveLength(5);
    expect(rows[0]).toMatchObject({
      id: "privacy-public-profile",
      key: "is_public_profile",
      label: "L1",
      desc: "D1",
      checked: true,
    });
    expect(rows[1]?.checked).toBe(false);
  });
});

describe("resolveSessionLocationDisplay", () => {
  it("returns city, country when both set", () => {
    const s = {
      id: 1,
      last_activity: "2024-01-01T00:00:00Z",
      created_at: "2024-01-01T00:00:00Z",
      expires_at: "2025-01-01T00:00:00Z",
      is_active: true,
      location_data: { city: "Paris", country: "FR" },
    } as UserSession;
    expect(resolveSessionLocationDisplay(s, "unknown")).toBe("Paris, FR");
  });

  it("falls back to ip when location incomplete", () => {
    const s = {
      id: 1,
      ip_address: "203.0.113.1",
      last_activity: "2024-01-01T00:00:00Z",
      created_at: "2024-01-01T00:00:00Z",
      expires_at: "2025-01-01T00:00:00Z",
      is_active: true,
      location_data: { city: "Paris" },
    } as UserSession;
    expect(resolveSessionLocationDisplay(s, "unknown")).toBe("203.0.113.1");
  });

  it("uses unknown label when no location and no ip", () => {
    const s = {
      id: 1,
      last_activity: "2024-01-01T00:00:00Z",
      created_at: "2024-01-01T00:00:00Z",
      expires_at: "2025-01-01T00:00:00Z",
      is_active: true,
    } as UserSession;
    expect(resolveSessionLocationDisplay(s, "fallback")).toBe("fallback");
  });
});

describe("computeVisibleCountAfterShowMore", () => {
  it("caps at total sessions", () => {
    expect(computeVisibleCountAfterShowMore(3, 3, 7)).toBe(6);
    expect(computeVisibleCountAfterShowMore(6, 3, 7)).toBe(7);
  });
});
