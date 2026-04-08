/**
 * Pure helpers for the settings security / privacy / sessions UI.
 * No React, no side effects. FFI-L20E.
 */

import type { UserSession } from "@/hooks/useSettings";
import type { PrivacySettingsState } from "@/lib/settings/settingsPage";

/** Ordered privacy toggles (ids stable for a11y / tests). */
export const PRIVACY_TOGGLE_CONFIG = [
  { id: "privacy-public-profile", key: "is_public_profile" },
  { id: "privacy-friend-requests", key: "allow_friend_requests" },
  { id: "privacy-leaderboards", key: "show_in_leaderboards" },
  { id: "privacy-data-retention", key: "data_retention_consent" },
  { id: "privacy-marketing", key: "marketing_consent" },
] as const satisfies ReadonlyArray<{
  id: string;
  key: keyof PrivacySettingsState;
}>;

export type PrivacyToggleConfigKey = (typeof PRIVACY_TOGGLE_CONFIG)[number]["key"];

export type PrivacyToggleLabels = Record<PrivacyToggleConfigKey, { label: string; desc: string }>;

export interface PrivacyToggleRow {
  id: string;
  label: string;
  desc: string;
  checked: boolean;
  key: keyof PrivacySettingsState;
}

export function buildPrivacyToggleRows(
  privacySettings: PrivacySettingsState,
  labels: PrivacyToggleLabels
): PrivacyToggleRow[] {
  return PRIVACY_TOGGLE_CONFIG.map((c) => ({
    id: c.id,
    key: c.key,
    label: labels[c.key].label,
    desc: labels[c.key].desc,
    checked: privacySettings[c.key],
  }));
}

/**
 * City + country when both present; otherwise first non-empty of IP; otherwise fallback label.
 */
export function resolveSessionLocationDisplay(
  session: UserSession,
  unknownLocationLabel: string
): string {
  const city = session.location_data?.city;
  const country = session.location_data?.country;
  if (city && country) {
    return `${city}, ${country}`;
  }
  if (session.ip_address && session.ip_address.length > 0) {
    return session.ip_address;
  }
  return unknownLocationLabel;
}

export function computeVisibleCountAfterShowMore(
  visibleCount: number,
  pageSize: number,
  totalSessions: number
): number {
  return Math.min(visibleCount + pageSize, totalSessions);
}
