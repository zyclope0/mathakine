"use client";

/**
 * useProfilePageController — logique runtime locale de la page profil.
 *
 * Porte :
 *   - état local des formulaires (infos perso, préférences, mot de passe, accessibilité)
 *   - navigation entre sections
 *   - effects de sync depuis `user`
 *   - validation (email, mot de passe)
 *   - handlers de sauvegarde / reset
 *   - dérivés (recentBadges, formatDate)
 *
 * Ne fait aucun rendu JSX.
 * Réutilise useProfile, useThemeStore, useAgeGroupDisplay sans dupliquer.
 *
 * FFI-L11 — extraction hook controller depuis app/profile/page.tsx.
 */

import { useState, useCallback, useMemo, useEffect } from "react";
import { useProfile } from "@/hooks/useProfile";
import { useThemeStore } from "@/lib/stores/themeStore";
import { useAgeGroupDisplay } from "@/hooks/useChallengeTranslations";
import type { UserBadge } from "@/types/api";
import type { UserProfileAgeGroup } from "@/lib/constants/userProfileAgeGroup";
import { USER_PROFILE_AGE_GROUPS } from "@/lib/constants/userProfileAgeGroup";
import {
  type ProfileSection,
  type GradeSystem,
  type ValidProfileTheme,
  migrateLegacyTheme,
  safeProfileTheme,
  formatProfileDate,
  validateEmailFormat,
  validatePasswordFields,
} from "@/lib/profile/profilePage";

// ─── Types ────────────────────────────────────────────────────────────────────

export type { ProfileSection };

export interface PersonalInfoState {
  email: string;
  full_name: string;
}

export interface LearningPrefsState {
  grade_system: GradeSystem;
  grade_level: string;
  age_group: string;
  learning_style: string;
  preferred_difficulty: string;
  learning_goal: string;
  practice_rhythm: string;
}

export interface PasswordDataState {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AccessibilitySettingsState {
  preferred_theme: string;
  high_contrast: boolean;
  large_text: boolean;
  reduce_motion: boolean;
}

// Interface utilisateur minimale nécessaire au controller (inférée depuis useAuth)
interface UserLike {
  email?: string | null;
  full_name?: string | null;
  username?: string | null;
  role?: string | null;
  created_at?: string | null;
  grade_system?: string | null;
  grade_level?: number | null;
  age_group?: string | null;
  learning_style?: string | null;
  preferred_difficulty?: string | null;
  learning_goal?: string | null;
  practice_rhythm?: string | null;
  preferred_theme?: string | null;
  accessibility_settings?: {
    high_contrast?: boolean;
    large_text?: boolean;
    reduce_motion?: boolean;
  } | null;
  gamification_level?: unknown;
}

interface UseProfilePageControllerArgs {
  user: UserLike | null | undefined;
  earnedBadges: (UserBadge & { earned_at?: string | null | undefined })[] | undefined;
  tValidation: (key: string) => string;
  tSecurity: (key: string) => string;
}

export interface ProfilePageControllerState {
  // Section active
  activeSection: ProfileSection;
  setActiveSection: (section: ProfileSection) => void;

  // Formulaire infos perso
  isEditingPersonalInfo: boolean;
  setIsEditingPersonalInfo: (v: boolean) => void;
  personalInfo: PersonalInfoState;
  setPersonalInfo: React.Dispatch<React.SetStateAction<PersonalInfoState>>;
  handleSavePersonalInfo: () => Promise<void>;
  handleResetPersonalInfo: () => void;

  // Formulaire préférences apprentissage
  isEditingLearningPrefs: boolean;
  setIsEditingLearningPrefs: (v: boolean) => void;
  learningPrefs: LearningPrefsState;
  setLearningPrefs: React.Dispatch<React.SetStateAction<LearningPrefsState>>;
  handleSaveLearningPrefs: () => Promise<void>;
  handleResetLearningPrefs: () => void;

  // Formulaire mot de passe
  showPasswordForm: boolean;
  setShowPasswordForm: (v: boolean) => void;
  showCurrentPassword: boolean;
  setShowCurrentPassword: (v: boolean) => void;
  showNewPassword: boolean;
  setShowNewPassword: (v: boolean) => void;
  showConfirmPassword: boolean;
  setShowConfirmPassword: (v: boolean) => void;
  passwordData: PasswordDataState;
  setPasswordData: React.Dispatch<React.SetStateAction<PasswordDataState>>;
  handleChangePassword: () => Promise<void>;
  handleResetPasswordForm: () => void;

  // Accessibilité
  accessibilitySettings: AccessibilitySettingsState;
  setAccessibilitySettings: React.Dispatch<React.SetStateAction<AccessibilitySettingsState>>;
  handleSaveAccessibility: (overrides?: Partial<AccessibilitySettingsState>) => Promise<void>;

  // Erreurs de validation
  errors: Record<string, string>;
  setErrors: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  clearFieldError: (field: string) => void;
  validateEmail: (email: string) => boolean;

  // Dérivés
  recentBadges: (UserBadge & { earned_at: string })[];
  formatDate: (dateString: string | null | undefined) => string;
  getAgeDisplay: (group: string) => string;

  // Passthrough des états de mutation
  isUpdatingProfile: boolean;
  isChangingPassword: boolean;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useProfilePageController({
  user,
  earnedBadges,
  tValidation,
  tSecurity,
}: UseProfilePageControllerArgs): ProfilePageControllerState {
  const { updateProfile, isUpdatingProfile, changePassword, isChangingPassword } = useProfile();
  const { setTheme } = useThemeStore();
  const getAgeDisplay = useAgeGroupDisplay();

  // ─── State ─────────────────────────────────────────────────────────────────

  const [activeSection, setActiveSection] = useState<ProfileSection>("profile");

  const [isEditingPersonalInfo, setIsEditingPersonalInfo] = useState(false);
  const [isEditingLearningPrefs, setIsEditingLearningPrefs] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [personalInfo, setPersonalInfo] = useState<PersonalInfoState>({
    email: user?.email ?? "",
    full_name: user?.full_name ?? "",
  });

  const [learningPrefs, setLearningPrefs] = useState<LearningPrefsState>({
    grade_system: (user?.grade_system as GradeSystem) ?? "unifie",
    grade_level: user?.grade_level?.toString() ?? "",
    age_group: (user?.age_group as UserProfileAgeGroup | undefined) ?? "",
    learning_style: user?.learning_style ?? "",
    preferred_difficulty: user?.preferred_difficulty ?? "",
    learning_goal: user?.learning_goal ?? "",
    practice_rhythm: user?.practice_rhythm ?? "",
  });

  const [passwordData, setPasswordData] = useState<PasswordDataState>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  const [accessibilitySettings, setAccessibilitySettings] = useState<AccessibilitySettingsState>({
    preferred_theme: migrateLegacyTheme(user?.preferred_theme),
    high_contrast: user?.accessibility_settings?.high_contrast ?? false,
    large_text: user?.accessibility_settings?.large_text ?? false,
    reduce_motion: user?.accessibility_settings?.reduce_motion ?? false,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  // ─── Sync depuis user ───────────────────────────────────────────────────────

  useEffect(() => {
    if (!user) return;

    const nextPersonalInfo: PersonalInfoState = {
      email: user.email ?? "",
      full_name: user.full_name ?? "",
    };
    const nextLearningPrefs: LearningPrefsState = {
      grade_system: (user.grade_system as GradeSystem) ?? "unifie",
      grade_level: user.grade_level?.toString() ?? "",
      age_group: (user.age_group as UserProfileAgeGroup | undefined) ?? "",
      learning_style: user.learning_style ?? "",
      preferred_difficulty: user.preferred_difficulty ?? "",
      learning_goal: user.learning_goal ?? "",
      practice_rhythm: user.practice_rhythm ?? "",
    };

    const migratedTheme = migrateLegacyTheme(user.preferred_theme);
    const nextAccessibilitySettings: AccessibilitySettingsState = {
      preferred_theme: migratedTheme,
      high_contrast: user.accessibility_settings?.high_contrast ?? false,
      large_text: user.accessibility_settings?.large_text ?? false,
      reduce_motion: user.accessibility_settings?.reduce_motion ?? false,
    };
    const safeTheme = safeProfileTheme(migratedTheme);

    let cancelled = false;

    queueMicrotask(() => {
      if (cancelled) return;
      setPersonalInfo(nextPersonalInfo);
      setLearningPrefs(nextLearningPrefs);
      setAccessibilitySettings(nextAccessibilitySettings);
      setTheme(safeTheme);
    });

    return () => {
      cancelled = true;
    };
  }, [user, setTheme]);

  // ─── Helpers ────────────────────────────────────────────────────────────────

  const clearFieldError = useCallback((field: string) => {
    setErrors((prev) => {
      if (!(field in prev)) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const validateEmail = useCallback(
    (email: string): boolean => {
      const errorKey = validateEmailFormat(email);
      if (errorKey) {
        setErrors((prev) => ({ ...prev, email: tValidation(errorKey) }));
        return false;
      }
      clearFieldError("email");
      return true;
    },
    [tValidation, clearFieldError]
  );

  // ─── Handlers infos perso ───────────────────────────────────────────────────

  const handleSavePersonalInfo = useCallback(async () => {
    if (!validateEmail(personalInfo.email)) return;
    await updateProfile({
      email: personalInfo.email,
      ...(personalInfo.full_name ? { full_name: personalInfo.full_name } : {}),
    });
    setIsEditingPersonalInfo(false);
  }, [personalInfo, updateProfile, validateEmail]);

  const handleResetPersonalInfo = useCallback(() => {
    setIsEditingPersonalInfo(false);
    setPersonalInfo({
      email: user?.email ?? "",
      full_name: user?.full_name ?? "",
    });
    setErrors({});
  }, [user]);

  // ─── Handlers préférences apprentissage ────────────────────────────────────

  const handleSaveLearningPrefs = useCallback(async () => {
    await updateProfile({
      grade_system: learningPrefs.grade_system,
      ...(learningPrefs.grade_level ? { grade_level: parseInt(learningPrefs.grade_level) } : {}),
      ...(learningPrefs.grade_system === "unifie"
        ? {
            age_group:
              learningPrefs.age_group &&
              USER_PROFILE_AGE_GROUPS.includes(learningPrefs.age_group as UserProfileAgeGroup)
                ? (learningPrefs.age_group as UserProfileAgeGroup)
                : null,
          }
        : {}),
      ...(learningPrefs.learning_style ? { learning_style: learningPrefs.learning_style } : {}),
      ...(learningPrefs.preferred_difficulty
        ? { preferred_difficulty: learningPrefs.preferred_difficulty }
        : {}),
      ...(learningPrefs.learning_goal ? { learning_goal: learningPrefs.learning_goal } : {}),
      ...(learningPrefs.practice_rhythm ? { practice_rhythm: learningPrefs.practice_rhythm } : {}),
    });
    setIsEditingLearningPrefs(false);
  }, [learningPrefs, updateProfile]);

  const handleResetLearningPrefs = useCallback(() => {
    setIsEditingLearningPrefs(false);
    setLearningPrefs({
      grade_system: (user?.grade_system as GradeSystem) ?? "unifie",
      grade_level: user?.grade_level?.toString() ?? "",
      age_group: (user?.age_group as UserProfileAgeGroup | undefined) ?? "",
      learning_style: user?.learning_style ?? "",
      preferred_difficulty: user?.preferred_difficulty ?? "",
      learning_goal: user?.learning_goal ?? "",
      practice_rhythm: user?.practice_rhythm ?? "",
    });
  }, [user]);

  // ─── Handlers accessibilité ─────────────────────────────────────────────────

  const handleSaveAccessibility = useCallback(
    async (overrides?: Partial<AccessibilitySettingsState>) => {
      const settings = overrides
        ? { ...accessibilitySettings, ...overrides }
        : accessibilitySettings;

      await updateProfile({
        preferred_theme: settings.preferred_theme,
        accessibility_settings: {
          high_contrast: settings.high_contrast,
          large_text: settings.large_text,
          reduce_motion: settings.reduce_motion,
        },
      });

      if (settings.preferred_theme) {
        const safeTheme = safeProfileTheme(settings.preferred_theme);
        setTheme(safeTheme);
      }
    },
    [accessibilitySettings, updateProfile, setTheme]
  );

  // ─── Handlers mot de passe ──────────────────────────────────────────────────

  const handleResetPasswordForm = useCallback(() => {
    setShowPasswordForm(false);
    setPasswordData({ current_password: "", new_password: "", confirm_password: "" });
    setErrors({});
  }, []);

  const handleChangePassword = useCallback(async () => {
    const passwordErrors = validatePasswordFields(passwordData);
    const resolved: Record<string, string> = {};

    if (passwordErrors.current_password) {
      resolved.current_password = tValidation(passwordErrors.current_password);
    }
    if (passwordErrors.new_password) {
      const key = passwordErrors.new_password;
      resolved.new_password =
        key === "newPasswordRequired" ? tValidation(key) : tSecurity("passwordMinLength");
    }
    if (passwordErrors.confirm_password) {
      const key = passwordErrors.confirm_password;
      resolved.confirm_password =
        key === "confirmPasswordRequired" ? tValidation(key) : tSecurity("passwordMismatch");
    }

    if (Object.keys(resolved).length > 0) {
      setErrors(resolved);
      return;
    }

    await changePassword({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    });

    handleResetPasswordForm();
  }, [passwordData, changePassword, tValidation, tSecurity, handleResetPasswordForm]);

  // ─── Dérivés ────────────────────────────────────────────────────────────────

  const recentBadges = useMemo(() => {
    if (!earnedBadges || earnedBadges.length === 0) return [];
    return earnedBadges
      .filter(
        (badge): badge is typeof badge & { earned_at: string } =>
          typeof badge.earned_at === "string" && badge.earned_at.length > 0
      )
      .sort((a, b) => new Date(b.earned_at).getTime() - new Date(a.earned_at).getTime())
      .slice(0, 3);
  }, [earnedBadges]);

  // ─── Retour ─────────────────────────────────────────────────────────────────

  return {
    activeSection,
    setActiveSection,

    isEditingPersonalInfo,
    setIsEditingPersonalInfo,
    personalInfo,
    setPersonalInfo,
    handleSavePersonalInfo,
    handleResetPersonalInfo,

    isEditingLearningPrefs,
    setIsEditingLearningPrefs,
    learningPrefs,
    setLearningPrefs,
    handleSaveLearningPrefs,
    handleResetLearningPrefs,

    showPasswordForm,
    setShowPasswordForm,
    showCurrentPassword,
    setShowCurrentPassword,
    showNewPassword,
    setShowNewPassword,
    showConfirmPassword,
    setShowConfirmPassword,
    passwordData,
    setPasswordData,
    handleChangePassword,
    handleResetPasswordForm,

    accessibilitySettings,
    setAccessibilitySettings,
    handleSaveAccessibility,

    errors,
    setErrors,
    clearFieldError,
    validateEmail,

    recentBadges,
    formatDate: formatProfileDate,
    getAgeDisplay,

    isUpdatingProfile,
    isChangingPassword,
  };
}

// Re-export des types utiles pour les composants
export type { ValidProfileTheme };
