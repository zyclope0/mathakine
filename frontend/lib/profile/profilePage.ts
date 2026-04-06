/**
 * lib/profile/profilePage.ts
 *
 * Constantes et helpers purs du domaine profil.
 * Zéro React, zéro side-effect.
 *
 * FFI-L11 — extraction des constantes et helpers depuis app/profile/page.tsx.
 */

import { format } from "date-fns";
import { fr } from "date-fns/locale";

// ─── Types ────────────────────────────────────────────────────────────────────

export type ProfileSection = "profile" | "preferences" | "statistics";

export type ValidProfileTheme =
  | "spatial"
  | "minimalist"
  | "ocean"
  | "dune"
  | "forest"
  | "aurora"
  | "dino"
  | "unicorn";

// ─── Constantes ───────────────────────────────────────────────────────────────

export const GRADE_SYSTEMS = ["suisse", "unifie"] as const;
export type GradeSystem = (typeof GRADE_SYSTEMS)[number];

export const LEARNING_GOALS = [
  "reviser",
  "preparer_exam",
  "progresser",
  "samuser",
  "autre",
] as const;
export type LearningGoal = (typeof LEARNING_GOALS)[number];

export const PRACTICE_RHYTHMS = [
  "10min_jour",
  "20min_jour",
  "30min_semaine",
  "1h_semaine",
  "flexible",
] as const;
export type PracticeRhythm = (typeof PRACTICE_RHYTHMS)[number];

export const VALID_PROFILE_THEMES: readonly ValidProfileTheme[] = [
  "spatial",
  "minimalist",
  "ocean",
  "dune",
  "forest",
  "aurora",
  "dino",
  "unicorn",
] as const;

// ─── Helpers purs ─────────────────────────────────────────────────────────────

/**
 * Migration thème legacy → thème courant.
 * neutral → dune, peach → aurora (refonte 2026-03-30).
 */
export function migrateLegacyTheme(raw: string | null | undefined): string {
  const theme = raw ?? "spatial";
  if (theme === "neutral") return "dune";
  if (theme === "peach") return "aurora";
  return theme;
}

/**
 * Valide un thème et retourne un thème sûr (fallback "spatial").
 */
export function safeProfileTheme(theme: string): ValidProfileTheme {
  return VALID_PROFILE_THEMES.includes(theme as ValidProfileTheme)
    ? (theme as ValidProfileTheme)
    : "spatial";
}

/**
 * Formatage de date en français.
 */
export function formatProfileDate(dateString: string | null | undefined): string {
  if (!dateString) return "-";
  try {
    return format(new Date(dateString), "dd MMMM yyyy", { locale: fr });
  } catch {
    return dateString;
  }
}

/**
 * Validation email basique.
 * Retourne null si valide, sinon le code d'erreur i18n à utiliser.
 */
export function validateEmailFormat(email: string): "emailRequired" | "emailInvalid" | null {
  if (!email.trim()) return "emailRequired";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "emailInvalid";
  return null;
}

/**
 * Validation des champs de changement de mot de passe.
 * Retourne un record vide si valide, sinon les clés d'erreur i18n.
 */
export function validatePasswordFields(data: {
  current_password: string;
  new_password: string;
  confirm_password: string;
}): Record<
  string,
  "currentPasswordRequired" | "newPasswordRequired" | "confirmPasswordRequired" | "passwordMismatch"
> {
  const errors: Record<
    string,
    | "currentPasswordRequired"
    | "newPasswordRequired"
    | "confirmPasswordRequired"
    | "passwordMismatch"
  > = {};

  if (!data.current_password.trim()) errors.current_password = "currentPasswordRequired";
  if (!data.new_password.trim()) errors.new_password = "newPasswordRequired";
  if (!data.confirm_password.trim()) errors.confirm_password = "confirmPasswordRequired";
  else if (data.new_password !== data.confirm_password)
    errors.confirm_password = "passwordMismatch";

  return errors;
}
