/**
 * Pure helpers for the settings page domain.
 * No React, no side effects.
 * FFI-L13 lot A.
 */

import { format } from "date-fns";
import type { Locale } from "date-fns";
import type { User } from "@/types/api";
import type { UserSession } from "@/hooks/useSettings";

export type SettingsSection = "general" | "notifications" | "security" | "data";

export const SESSIONS_PAGE_SIZE = 3;

export interface LanguageSettingsState {
  language_preference: string;
  timezone: string;
}

export interface NotificationSettingsState {
  achievements: boolean;
  progress: boolean;
  recommendations: boolean;
  news: boolean;
}

export interface PrivacySettingsState {
  is_public_profile: boolean;
  allow_friend_requests: boolean;
  show_in_leaderboards: boolean;
  data_retention_consent: boolean;
  marketing_consent: boolean;
}

export interface DiagnosticStatusPayload {
  has_completed: boolean;
  latest: { completed_at: string; scores: Record<string, { difficulty: string }> } | null;
}

function readAccObject(user: User | null | undefined): Record<string, unknown> | undefined {
  const raw = user?.accessibility_settings;
  if (raw && typeof raw === "object" && !Array.isArray(raw)) {
    return raw as Record<string, unknown>;
  }
  return undefined;
}

function readStringFromAcc(
  user: User | null | undefined,
  accKey: string,
  topLevel: keyof Pick<User, "language_preference" | "timezone">,
  fallback: string
): string {
  const acc = readAccObject(user);
  const fromAcc = acc?.[accKey];
  if (typeof fromAcc === "string" && fromAcc.length > 0) return fromAcc;
  const top = user?.[topLevel];
  if (typeof top === "string" && top.length > 0) return top;
  return fallback;
}

/**
 * Derives language + timezone form state from the current user (API + nested accessibility).
 */
export function normalizeLanguageSettings(user: User | null | undefined): LanguageSettingsState {
  return {
    language_preference: String(
      readStringFromAcc(user, "language_preference", "language_preference", "fr")
    ),
    timezone: String(readStringFromAcc(user, "timezone", "timezone", "UTC")),
  };
}

function readNotificationBoolean(user: User | null | undefined, key: string): boolean {
  const acc = readAccObject(user);
  const prefs = acc?.notification_preferences;
  if (prefs && typeof prefs === "object" && !Array.isArray(prefs)) {
    const v = (prefs as Record<string, boolean | undefined>)[key];
    return v ?? (key === "news" ? false : true);
  }
  return key === "news" ? false : true;
}

/**
 * Derives notification toggles from user.accessibility_settings.notification_preferences.
 */
export function normalizeNotificationSettings(
  user: User | null | undefined
): NotificationSettingsState {
  return {
    achievements: readNotificationBoolean(user, "achievements"),
    progress: readNotificationBoolean(user, "progress"),
    recommendations: readNotificationBoolean(user, "recommendations"),
    news: readNotificationBoolean(user, "news"),
  };
}

function readPrivacyBoolean(
  user: User | null | undefined,
  key: string,
  defaultValue: boolean
): boolean {
  const acc = readAccObject(user);
  const prefs = acc?.privacy_settings;
  if (prefs && typeof prefs === "object" && !Array.isArray(prefs)) {
    const v = (prefs as Record<string, boolean | undefined>)[key];
    return v ?? defaultValue;
  }
  return defaultValue;
}

/**
 * Derives privacy toggles from user.accessibility_settings.privacy_settings.
 */
export function normalizePrivacySettings(user: User | null | undefined): PrivacySettingsState {
  return {
    is_public_profile: readPrivacyBoolean(user, "is_public_profile", false),
    allow_friend_requests: readPrivacyBoolean(user, "allow_friend_requests", true),
    show_in_leaderboards: readPrivacyBoolean(user, "show_in_leaderboards", true),
    data_retention_consent: readPrivacyBoolean(user, "data_retention_consent", true),
    marketing_consent: readPrivacyBoolean(user, "marketing_consent", false),
  };
}

/**
 * Formats a session timestamp for display (same pattern as settings page: PPpp).
 */
export function formatSessionDate(isoDate: string, locale: Locale): string {
  return format(new Date(isoDate), "PPpp", { locale });
}

/**
 * Visible slice of sessions for progressive disclosure.
 */
export function getVisibleSessions(sessions: UserSession[], visibleCount: number): UserSession[] {
  return sessions.slice(0, Math.max(0, visibleCount));
}

/**
 * Whether more sessions exist beyond the current visible window.
 */
export function canShowMoreSessions(sessions: UserSession[], visibleCount: number): boolean {
  return visibleCount < sessions.length;
}
