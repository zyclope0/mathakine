"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";
import { useUserStats } from "@/hooks/useUserStats";
import { useBadges } from "@/hooks/useBadges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader, EmptyState } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Badge as UIBadge } from "@/components/ui/badge";
import type { UserBadge } from "@/types/api";
import {
  User,
  Lock,
  Settings,
  Award,
  TrendingUp,
  Calendar,
  Save,
  X,
  Eye,
  EyeOff,
  Loader2,
  BarChart3,
  Palette,
  Pencil,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { AGE_GROUPS, type AgeGroup } from "@/lib/constants/exercises";
import { useAgeGroupDisplay } from "@/hooks/useChallengeTranslations";
import { fr } from "date-fns/locale";
import { useThemeStore } from "@/lib/stores/themeStore";

function ProfilePageContent() {
  type ProfileSection = "profile" | "preferences" | "statistics";

  const { user } = useAuth();
  const { updateProfile, isUpdatingProfile, changePassword, isChangingPassword } = useProfile();
  const { stats, isLoading: isLoadingStats, error: statsError } = useUserStats("30");
  const { earnedBadges } = useBadges();
  const { setTheme } = useThemeStore();
  const getAgeDisplay = useAgeGroupDisplay();
  const router = useRouter();
  const t = useTranslations("profile");
  const tOnboarding = useTranslations("onboarding");
  const tPersonal = useTranslations("profile.personalInfo");
  const tLearning = useTranslations("profile.learningPreferences");
  const tSecurity = useTranslations("profile.security");
  const tAccessibility = useTranslations("profile.accessibility");
  const tStatistics = useTranslations("profile.statistics");
  const tBadges = useTranslations("profile.badges");
  const tActions = useTranslations("profile.actions");
  const tValidation = useTranslations("profile.validation");
  const tTheme = useTranslations("theme");
  const tDashboard = useTranslations("dashboard");

  // État pour les formulaires
  const [isEditingPersonalInfo, setIsEditingPersonalInfo] = useState(false);
  const [isEditingLearningPrefs, setIsEditingLearningPrefs] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Données du formulaire informations personnelles
  const [personalInfo, setPersonalInfo] = useState({
    email: user?.email || "",
    full_name: user?.full_name || "",
  });

  const GRADE_SYSTEMS = ["suisse", "unifie"] as const;
  const LEARNING_GOALS = ["reviser", "preparer_exam", "progresser", "samuser", "autre"] as const;
  const PRACTICE_RHYTHMS = [
    "10min_jour",
    "20min_jour",
    "30min_semaine",
    "1h_semaine",
    "flexible",
  ] as const;

  // Données du formulaire préférences d'apprentissage
  const [learningPrefs, setLearningPrefs] = useState({
    grade_system: (user?.grade_system as "suisse" | "unifie") || "unifie",
    grade_level: user?.grade_level?.toString() || "",
    learning_style: user?.learning_style || "",
    preferred_difficulty: user?.preferred_difficulty || "",
    learning_goal: user?.learning_goal || "",
    practice_rhythm: user?.practice_rhythm || "",
  });

  // Données du formulaire changement de mot de passe
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });

  // Données du formulaire accessibilité
  const [accessibilitySettings, setAccessibilitySettings] = useState({
    preferred_theme: user?.preferred_theme || "spatial",
    high_contrast: user?.accessibility_settings?.high_contrast || false,
    large_text: user?.accessibility_settings?.large_text || false,
    reduce_motion: user?.accessibility_settings?.reduce_motion || false,
  });

  // Erreurs de validation
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activeSection, setActiveSection] = useState<ProfileSection>("profile");

  // Synchroniser les états locaux avec les données utilisateur
  useEffect(() => {
    if (!user) return;

    const nextPersonalInfo = {
      email: user.email || "",
      full_name: user.full_name || "",
    };
    const nextLearningPrefs = {
      grade_system: (user.grade_system as "suisse" | "unifie") || "unifie",
      grade_level: user.grade_level?.toString() || "",
      learning_style: user.learning_style || "",
      preferred_difficulty: user.preferred_difficulty || "",
      learning_goal: user.learning_goal || "",
      practice_rhythm: user.practice_rhythm || "",
    };

    // Migration: neutral -> dune
    const userThemeRaw = user.preferred_theme || "spatial";
    const userTheme = userThemeRaw === "neutral" ? "dune" : userThemeRaw;
    const validThemes = [
      "spatial",
      "minimalist",
      "ocean",
      "dune",
      "forest",
      "peach",
      "dino",
    ] as const;
    const nextAccessibilitySettings = {
      preferred_theme: userTheme,
      high_contrast: user.accessibility_settings?.high_contrast || false,
      large_text: user.accessibility_settings?.large_text || false,
      reduce_motion: user.accessibility_settings?.reduce_motion || false,
    };
    const safeTheme = validThemes.includes(userTheme as (typeof validThemes)[number])
      ? (userTheme as (typeof validThemes)[number])
      : "spatial";

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

  // Validation email
  const validateEmail = useCallback(
    (email: string): boolean => {
      if (!email.trim()) {
        setErrors((prev) => ({ ...prev, email: tValidation("emailRequired") }));
        return false;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        setErrors((prev) => ({ ...prev, email: tValidation("emailInvalid") }));
        return false;
      }
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors.email;
        return newErrors;
      });
      return true;
    },
    [tValidation]
  );

  // Validation mot de passe (useCallback pour stabilité des deps)
  const validatePassword = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    if (!passwordData.current_password.trim()) {
      newErrors.current_password = tValidation("currentPasswordRequired");
    }
    if (!passwordData.new_password.trim()) {
      newErrors.new_password = tValidation("newPasswordRequired");
    } else if (passwordData.new_password.length < 8) {
      newErrors.new_password = tSecurity("passwordMinLength");
    }
    if (!passwordData.confirm_password.trim()) {
      newErrors.confirm_password = tValidation("confirmPasswordRequired");
    } else if (passwordData.new_password !== passwordData.confirm_password) {
      newErrors.confirm_password = tSecurity("passwordMismatch");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [passwordData, tValidation, tSecurity]);

  // Sauvegarder informations personnelles
  const handleSavePersonalInfo = useCallback(async () => {
    if (!validateEmail(personalInfo.email)) {
      return;
    }

    await updateProfile({
      email: personalInfo.email,
      ...(personalInfo.full_name ? { full_name: personalInfo.full_name } : {}),
    });
    setIsEditingPersonalInfo(false);
  }, [personalInfo, updateProfile, validateEmail]);

  // Sauvegarder préférences d'apprentissage
  const handleSaveLearningPrefs = useCallback(async () => {
    await updateProfile({
      grade_system: learningPrefs.grade_system,
      ...(learningPrefs.grade_level ? { grade_level: parseInt(learningPrefs.grade_level) } : {}),
      ...(learningPrefs.learning_style ? { learning_style: learningPrefs.learning_style } : {}),
      ...(learningPrefs.preferred_difficulty
        ? { preferred_difficulty: learningPrefs.preferred_difficulty }
        : {}),
      ...(learningPrefs.learning_goal ? { learning_goal: learningPrefs.learning_goal } : {}),
      ...(learningPrefs.practice_rhythm ? { practice_rhythm: learningPrefs.practice_rhythm } : {}),
    });
    setIsEditingLearningPrefs(false);
  }, [learningPrefs, updateProfile]);

  // Sauvegarder accessibilité avec les valeurs passées directement (évite stale closure)
  const handleSaveAccessibility = useCallback(
    async (overrides?: Partial<typeof accessibilitySettings>) => {
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
        setTheme(
          settings.preferred_theme as
            | "spatial"
            | "minimalist"
            | "ocean"
            | "dune"
            | "forest"
            | "peach"
            | "dino"
        );
      }
    },
    [accessibilitySettings, updateProfile, setTheme]
  );

  // Changer le mot de passe
  const handleChangePassword = useCallback(async () => {
    if (!validatePassword()) {
      return;
    }

    await changePassword({
      current_password: passwordData.current_password,
      new_password: passwordData.new_password,
    });

    // Réinitialiser le formulaire
    setPasswordData({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });
    setShowPasswordForm(false);
  }, [passwordData, changePassword, validatePassword]);

  // Badges récents (3 derniers)
  const recentBadges = useMemo(() => {
    if (!earnedBadges || earnedBadges.length === 0) return [];
    return earnedBadges
      .filter((badge): badge is typeof badge & { earned_at: string } => Boolean(badge.earned_at))
      .sort((a, b) => {
        const dateA = new Date(a.earned_at).getTime();
        const dateB = new Date(b.earned_at).getTime();
        return dateB - dateA;
      })
      .slice(0, 3);
  }, [earnedBadges]);

  // Formatage de la date
  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return "-";
    try {
      return format(new Date(dateString), "dd MMMM yyyy", { locale: fr });
    } catch {
      return dateString;
    }
  };

  if (!user) {
    return (
      <PageLayout>
        <EmptyState
          title={t("error.title", { default: "Profil non disponible" })}
          description={t("error.description", {
            default: "Impossible de charger vos informations de profil.",
          })}
        />
      </PageLayout>
    );
  }

  const menuItems: { id: ProfileSection; label: string; icon: typeof User }[] = [
    { id: "profile", label: tPersonal("title"), icon: User },
    { id: "preferences", label: tAccessibility("title"), icon: Palette },
    { id: "statistics", label: tStatistics("title"), icon: BarChart3 },
  ];

  return (
    <PageLayout maxWidth="lg">
      <PageHeader
        title={t("title")}
        description={t("description")}
        icon={User}
        actions={
          <Button
            variant="outline"
            onClick={() => router.push("/dashboard")}
            aria-label={tActions("viewDashboard")}
          >
            {tActions("viewDashboard")}
          </Button>
        }
      />

      <div className="flex flex-col md:grid md:grid-cols-12 gap-8 md:gap-12 max-w-6xl mx-auto">
        {/* Mobile: Select */}
        <div className="md:hidden">
          <Select
            value={activeSection}
            onValueChange={(v) => setActiveSection(v as ProfileSection)}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {menuItems.map((item) => (
                <SelectItem key={item.id} value={item.id}>
                  <span className="flex items-center gap-2">
                    <item.icon className="h-4 w-4" />
                    {item.label}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Sidebar (desktop) */}
        <nav className="hidden md:flex md:col-span-3 flex-col gap-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setActiveSection(item.id)}
              className={cn(
                "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                activeSection === item.id
                  ? "text-foreground bg-muted/80"
                  : "text-muted-foreground hover:bg-muted/50"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </button>
          ))}
        </nav>

        {/* Contenu dynamique */}
        <div className="md:col-span-9 space-y-8">
          {/* ═══════════ SECTION PROFIL ═══════════ */}
          {activeSection === "profile" && (
            <div className="space-y-6">
              {/* Informations personnelles */}
              <div className="animate-fade-in-up">
                <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                  <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2 text-xl">
                        <User className="h-5 w-5 text-primary" />
                        {tPersonal("title")}
                      </CardTitle>
                      {!isEditingPersonalInfo && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setIsEditingPersonalInfo(true)}
                          aria-label={tActions("edit")}
                          className="inline-flex items-center gap-2 border-border hover:bg-accent hover:text-accent-foreground rounded-lg h-9 px-3"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                          {tActions("edit")}
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    {isEditingPersonalInfo ? (
                      <div className="flex flex-col">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="username"
                              className="text-sm font-medium text-foreground"
                            >
                              {tPersonal("username")}
                            </Label>
                            <p id="username-description" className="text-xs text-muted-foreground">
                              {tPersonal("usernameDescription")}
                            </p>
                          </div>
                          <Input
                            id="username"
                            value={user.username}
                            disabled
                            aria-label={tPersonal("username")}
                            aria-describedby="username-description"
                            className="bg-muted/30 border-border/50 w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                          />
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label htmlFor="email" className="text-sm font-medium text-foreground">
                              {tPersonal("email")} *
                            </Label>
                          </div>
                          <div className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                            <Input
                              id="email"
                              type="email"
                              value={personalInfo.email}
                              onChange={(e) => {
                                setPersonalInfo((prev) => ({ ...prev, email: e.target.value }));
                                if (errors.email) {
                                  setErrors((prev) => {
                                    const newErrors = { ...prev };
                                    delete newErrors.email;
                                    return newErrors;
                                  });
                                }
                              }}
                              onBlur={() => validateEmail(personalInfo.email)}
                              placeholder={tPersonal("emailPlaceholder")}
                              aria-invalid={!!errors.email}
                              aria-describedby={errors.email ? "email-error" : undefined}
                              disabled={isUpdatingProfile}
                            />
                            {errors.email && (
                              <p
                                id="email-error"
                                className="text-sm text-destructive mt-1"
                                role="alert"
                                aria-live="polite"
                              >
                                {errors.email}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="full_name"
                              className="text-sm font-medium text-foreground"
                            >
                              {tPersonal("fullName")}
                            </Label>
                          </div>
                          <Input
                            id="full_name"
                            type="text"
                            value={personalInfo.full_name}
                            onChange={(e) =>
                              setPersonalInfo((prev) => ({ ...prev, full_name: e.target.value }))
                            }
                            placeholder={tPersonal("fullNamePlaceholder")}
                            disabled={isUpdatingProfile}
                            className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                          />
                        </div>
                        <div className="flex gap-2 justify-end pt-6">
                          <Button
                            variant="outline"
                            onClick={() => {
                              setIsEditingPersonalInfo(false);
                              setPersonalInfo({
                                email: user.email || "",
                                full_name: user.full_name || "",
                              });
                              setErrors({});
                            }}
                            disabled={isUpdatingProfile}
                            aria-label={tActions("cancel")}
                          >
                            <X className="mr-2 h-4 w-4" />
                            {tActions("cancel")}
                          </Button>
                          <Button
                            onClick={handleSavePersonalInfo}
                            disabled={isUpdatingProfile}
                            aria-label={tActions("save")}
                            aria-busy={isUpdatingProfile}
                          >
                            {isUpdatingProfile ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                {tActions("saving")}
                              </>
                            ) : (
                              <>
                                <Save className="mr-2 h-4 w-4" />
                                {tActions("save")}
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tPersonal("username")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {user.username || "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tPersonal("email")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {user.email || "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tPersonal("fullName")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {user.full_name || "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tPersonal("role")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right capitalize mt-3 sm:mt-0 shrink-0">
                            {user.role || "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tPersonal("memberSince")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {formatDate(user.created_at)}
                          </p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Préférences d'apprentissage */}
              <div className="animate-fade-in-up-delay-1">
                <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                  <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2 text-xl">
                        <Settings className="h-5 w-5 text-primary" />
                        {tLearning("title")}
                      </CardTitle>
                      {!isEditingLearningPrefs && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setIsEditingLearningPrefs(true)}
                          aria-label={tActions("edit")}
                          className="inline-flex items-center gap-2 border-border hover:bg-accent hover:text-accent-foreground rounded-lg h-9 px-3"
                        >
                          <Pencil className="h-3.5 w-3.5" />
                          {tActions("edit")}
                        </Button>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    {isEditingLearningPrefs ? (
                      <div className="flex flex-col">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="grade_system"
                              className="text-sm font-medium text-foreground"
                            >
                              {tOnboarding("gradeSystem")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.grade_system}
                            onValueChange={(v) => {
                              const next = v as "suisse" | "unifie";
                              const max = next === "suisse" ? 11 : 12;
                              setLearningPrefs((prev) => ({
                                ...prev,
                                grade_system: next,
                                grade_level:
                                  prev.grade_level && parseInt(prev.grade_level, 10) > max
                                    ? ""
                                    : prev.grade_level,
                              }));
                            }}
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="grade_system"
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {GRADE_SYSTEMS.map((sys) => (
                                <SelectItem key={sys} value={sys}>
                                  {tOnboarding(`gradeSystems.${sys}`)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="grade_level"
                              className="text-sm font-medium text-foreground"
                            >
                              {tLearning("gradeLevel")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.grade_level}
                            onValueChange={(value) =>
                              setLearningPrefs((prev) => ({ ...prev, grade_level: value }))
                            }
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="grade_level"
                              aria-label={tLearning("gradeLevel")}
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue placeholder={tLearning("gradeLevelPlaceholder")} />
                            </SelectTrigger>
                            <SelectContent>
                              {Array.from(
                                { length: learningPrefs.grade_system === "suisse" ? 11 : 12 },
                                (_, i) => i + 1
                              ).map((level) => (
                                <SelectItem key={level} value={level.toString()}>
                                  {learningPrefs.grade_system === "suisse" ? `${level}H` : level}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="learning_style"
                              className="text-sm font-medium text-foreground"
                            >
                              {tLearning("learningStyle")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.learning_style}
                            onValueChange={(value) =>
                              setLearningPrefs((prev) => ({ ...prev, learning_style: value }))
                            }
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="learning_style"
                              aria-label={tLearning("learningStyle")}
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue placeholder={tLearning("learningStylePlaceholder")} />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="visuel">{t("learningStyles.visuel")}</SelectItem>
                              <SelectItem value="auditif">{t("learningStyles.auditif")}</SelectItem>
                              <SelectItem value="kinesthésique">
                                {t("learningStyles.kinesthésique")}
                              </SelectItem>
                              <SelectItem value="lecture">
                                {t("learningStyles.lecture")}{" "}
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="preferred_age_group"
                              className="text-sm font-medium text-foreground"
                            >
                              {tLearning("preferredAgeGroup")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.preferred_difficulty}
                            onValueChange={(value) =>
                              setLearningPrefs((prev) => ({ ...prev, preferred_difficulty: value }))
                            }
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="preferred_age_group"
                              aria-label={tLearning("preferredAgeGroup")}
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue
                                placeholder={tLearning("preferredAgeGroupPlaceholder")}
                              />
                            </SelectTrigger>
                            <SelectContent>
                              {Object.values(AGE_GROUPS).map((group) => (
                                <SelectItem key={group} value={group}>
                                  {getAgeDisplay(group)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="learning_goal"
                              className="text-sm font-medium text-foreground"
                            >
                              {tOnboarding("learningGoal")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.learning_goal || "none"}
                            onValueChange={(v) =>
                              setLearningPrefs((prev) => ({
                                ...prev,
                                learning_goal: v === "none" ? "" : v,
                              }))
                            }
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="learning_goal"
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue placeholder={tOnboarding("learningGoalPlaceholder")} />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="none">—</SelectItem>
                              {LEARNING_GOALS.map((g) => (
                                <SelectItem key={g} value={g}>
                                  {tOnboarding(`goals.${g}`)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="practice_rhythm"
                              className="text-sm font-medium text-foreground"
                            >
                              {tOnboarding("practiceRhythm")}
                            </Label>
                          </div>
                          <Select
                            value={learningPrefs.practice_rhythm || "none"}
                            onValueChange={(v) =>
                              setLearningPrefs((prev) => ({
                                ...prev,
                                practice_rhythm: v === "none" ? "" : v,
                              }))
                            }
                            disabled={isUpdatingProfile}
                          >
                            <SelectTrigger
                              id="practice_rhythm"
                              className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            >
                              <SelectValue placeholder={tOnboarding("practiceRhythmPlaceholder")} />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="none">—</SelectItem>
                              {PRACTICE_RHYTHMS.map((r) => (
                                <SelectItem key={r} value={r}>
                                  {tOnboarding(`rhythms.${r}`)}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex gap-2 justify-end pt-6">
                          <Button
                            variant="outline"
                            onClick={() => {
                              setIsEditingLearningPrefs(false);
                              setLearningPrefs({
                                grade_system:
                                  (user.grade_system as "suisse" | "unifie") || "unifie",
                                grade_level: user.grade_level?.toString() || "",
                                learning_style: user.learning_style || "",
                                preferred_difficulty: user.preferred_difficulty || "",
                                learning_goal: user.learning_goal || "",
                                practice_rhythm: user.practice_rhythm || "",
                              });
                            }}
                            disabled={isUpdatingProfile}
                            aria-label={tActions("cancel")}
                          >
                            <X className="mr-2 h-4 w-4" />
                            {tActions("cancel")}
                          </Button>
                          <Button
                            onClick={handleSaveLearningPrefs}
                            disabled={isUpdatingProfile}
                            aria-label={tActions("save")}
                            aria-busy={isUpdatingProfile}
                          >
                            {isUpdatingProfile ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                {tActions("saving")}
                              </>
                            ) : (
                              <>
                                <Save className="mr-2 h-4 w-4" />
                                {tActions("save")}
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col">
                        {user.grade_system && (
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                            <div className="flex flex-col gap-1 pr-4">
                              <p className="text-sm font-medium text-foreground">
                                {tOnboarding("gradeSystem")}
                              </p>
                            </div>
                            <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                              {tOnboarding(`gradeSystems.${user.grade_system}`)}
                            </p>
                          </div>
                        )}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tLearning("gradeLevel")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {user.grade_level
                              ? user.grade_system === "suisse"
                                ? `${user.grade_level}H`
                                : user.grade_level
                              : "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tLearning("learningStyle")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right capitalize mt-3 sm:mt-0 shrink-0">
                            {user.learning_style || "-"}
                          </p>
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {tLearning("preferredAgeGroup")}
                            </p>
                          </div>
                          <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                            {user.preferred_difficulty
                              ? Object.values(AGE_GROUPS).includes(
                                  user.preferred_difficulty as AgeGroup
                                )
                                ? getAgeDisplay(user.preferred_difficulty)
                                : user.preferred_difficulty
                              : "-"}
                          </p>
                        </div>
                        {user.learning_goal && (
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                            <div className="flex flex-col gap-1 pr-4">
                              <p className="text-sm font-medium text-foreground">
                                {tOnboarding("learningGoal")}
                              </p>
                            </div>
                            <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                              {LEARNING_GOALS.includes(
                                user.learning_goal as (typeof LEARNING_GOALS)[number]
                              )
                                ? tOnboarding(`goals.${user.learning_goal}`)
                                : user.learning_goal}
                            </p>
                          </div>
                        )}
                        {user.practice_rhythm && (
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                            <div className="flex flex-col gap-1 pr-4">
                              <p className="text-sm font-medium text-foreground">
                                {tOnboarding("practiceRhythm")}
                              </p>
                            </div>
                            <p className="text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                              {PRACTICE_RHYTHMS.includes(
                                user.practice_rhythm as (typeof PRACTICE_RHYTHMS)[number]
                              )
                                ? tOnboarding(`rhythms.${user.practice_rhythm}`)
                                : user.practice_rhythm}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Sécurité */}
              <div className="animate-fade-in-up-delay-2">
                <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                  <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                    <CardTitle className="flex items-center gap-2 text-xl">
                      <Lock className="h-5 w-5 text-primary" />
                      {tSecurity("title")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    {!showPasswordForm ? (
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                        <div className="flex flex-col gap-1 pr-4">
                          <p className="text-sm font-medium text-foreground">
                            {tSecurity("changePassword")}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {tSecurity("description")}
                          </p>
                        </div>
                        <Button
                          onClick={() => setShowPasswordForm(true)}
                          variant="outline"
                          aria-label={tSecurity("changePassword")}
                          className="mt-3 sm:mt-0 shrink-0"
                        >
                          {tSecurity("changePassword")}
                        </Button>
                      </div>
                    ) : (
                      <div className="flex flex-col">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="current_password"
                              className="text-sm font-medium text-foreground"
                            >
                              {tSecurity("currentPassword")} *
                            </Label>
                          </div>
                          <div className="relative w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                            <Input
                              id="current_password"
                              type={showCurrentPassword ? "text" : "password"}
                              value={passwordData.current_password}
                              onChange={(e) => {
                                setPasswordData((prev) => ({
                                  ...prev,
                                  current_password: e.target.value,
                                }));
                                if (errors.current_password) {
                                  setErrors((prev) => {
                                    const newErrors = { ...prev };
                                    delete newErrors.current_password;
                                    return newErrors;
                                  });
                                }
                              }}
                              placeholder={tSecurity("currentPasswordPlaceholder")}
                              aria-invalid={!!errors.current_password}
                              aria-describedby={
                                errors.current_password ? "current-password-error" : undefined
                              }
                              disabled={isChangingPassword}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3"
                              onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                              aria-label={
                                showCurrentPassword
                                  ? "Masquer le mot de passe"
                                  : "Afficher le mot de passe"
                              }
                            >
                              {showCurrentPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                          {errors.current_password && (
                            <p
                              id="current-password-error"
                              className="text-sm text-destructive"
                              role="alert"
                              aria-live="polite"
                            >
                              {errors.current_password}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="new_password"
                              className="text-sm font-medium text-foreground"
                            >
                              {tSecurity("newPassword")} *
                            </Label>
                          </div>
                          <div className="relative w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                            <Input
                              id="new_password"
                              type={showNewPassword ? "text" : "password"}
                              value={passwordData.new_password}
                              onChange={(e) => {
                                setPasswordData((prev) => ({
                                  ...prev,
                                  new_password: e.target.value,
                                }));
                                if (errors.new_password) {
                                  setErrors((prev) => {
                                    const newErrors = { ...prev };
                                    delete newErrors.new_password;
                                    return newErrors;
                                  });
                                }
                              }}
                              placeholder={tSecurity("newPasswordPlaceholder")}
                              aria-invalid={!!errors.new_password}
                              aria-describedby={
                                errors.new_password ? "new-password-error" : undefined
                              }
                              disabled={isChangingPassword}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3"
                              onClick={() => setShowNewPassword(!showNewPassword)}
                              aria-label={
                                showNewPassword
                                  ? "Masquer le mot de passe"
                                  : "Afficher le mot de passe"
                              }
                            >
                              {showNewPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                          {errors.new_password && (
                            <p
                              id="new-password-error"
                              className="text-sm text-destructive"
                              role="alert"
                              aria-live="polite"
                            >
                              {errors.new_password}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                          <div className="flex flex-col gap-1 pr-4">
                            <Label
                              htmlFor="confirm_password"
                              className="text-sm font-medium text-foreground"
                            >
                              {tSecurity("confirmPassword")} *
                            </Label>
                          </div>
                          <div className="relative w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                            <Input
                              id="confirm_password"
                              type={showConfirmPassword ? "text" : "password"}
                              value={passwordData.confirm_password}
                              onChange={(e) => {
                                setPasswordData((prev) => ({
                                  ...prev,
                                  confirm_password: e.target.value,
                                }));
                                if (errors.confirm_password) {
                                  setErrors((prev) => {
                                    const newErrors = { ...prev };
                                    delete newErrors.confirm_password;
                                    return newErrors;
                                  });
                                }
                              }}
                              placeholder={tSecurity("confirmPasswordPlaceholder")}
                              aria-invalid={!!errors.confirm_password}
                              aria-describedby={
                                errors.confirm_password ? "confirm-password-error" : undefined
                              }
                              disabled={isChangingPassword}
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                              aria-label={
                                showConfirmPassword
                                  ? "Masquer le mot de passe"
                                  : "Afficher le mot de passe"
                              }
                            >
                              {showConfirmPassword ? (
                                <EyeOff className="h-4 w-4" />
                              ) : (
                                <Eye className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                          {errors.confirm_password && (
                            <p
                              id="confirm-password-error"
                              className="text-sm text-destructive"
                              role="alert"
                              aria-live="polite"
                            >
                              {errors.confirm_password}
                            </p>
                          )}
                        </div>
                        <div className="flex gap-2 pt-6">
                          <Button
                            onClick={handleChangePassword}
                            disabled={isChangingPassword}
                            aria-label={tActions("changePassword")}
                            aria-busy={isChangingPassword}
                          >
                            {isChangingPassword ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                {tActions("changingPassword")}
                              </>
                            ) : (
                              <>
                                <Lock className="mr-2 h-4 w-4" />
                                {tActions("changePassword")}
                              </>
                            )}
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => {
                              setShowPasswordForm(false);
                              setPasswordData({
                                current_password: "",
                                new_password: "",
                                confirm_password: "",
                              });
                              setErrors({});
                            }}
                            disabled={isChangingPassword}
                            aria-label={tActions("cancel")}
                          >
                            <X className="mr-2 h-4 w-4" />
                            {tActions("cancel")}
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* ═══════════ SECTION ACCESSIBILITÉ ═══════════ */}
          {activeSection === "preferences" && (
            <div className="space-y-6">
              {/* Accessibilité */}
              <div className="animate-fade-in-up">
                <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                  <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                    <CardTitle className="flex items-center gap-2 text-xl">
                      <Settings className="h-5 w-5 text-primary" />
                      {tAccessibility("title")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="flex flex-col">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                        <div className="flex flex-col gap-1 pr-4">
                          <Label htmlFor="theme" className="text-sm font-medium text-foreground">
                            {tAccessibility("theme")}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {tAccessibility("themeDescription")}
                          </p>
                        </div>
                        <Select
                          value={accessibilitySettings.preferred_theme}
                          onValueChange={(value) => {
                            const theme = value as
                              | "spatial"
                              | "minimalist"
                              | "ocean"
                              | "dune"
                              | "forest"
                              | "peach"
                              | "dino";
                            setAccessibilitySettings((prev) => ({
                              ...prev,
                              preferred_theme: theme,
                            }));
                            handleSaveAccessibility({ preferred_theme: theme });
                          }}
                        >
                          <SelectTrigger
                            id="theme"
                            className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                            aria-label={tAccessibility("theme")}
                          >
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="spatial">
                              <span className="flex items-center gap-2">
                                <span>🚀</span>
                                <span>{tTheme("spatial")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="minimalist">
                              <span className="flex items-center gap-2">
                                <span>⚪</span>
                                <span>{tTheme("minimalist")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="ocean">
                              <span className="flex items-center gap-2">
                                <span>🌊</span>
                                <span>{tTheme("ocean")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="dune">
                              <span className="flex items-center gap-2">
                                <span>🏜️</span>
                                <span>{tTheme("dune")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="forest">
                              <span className="flex items-center gap-2">
                                <span>🌲</span>
                                <span>{tTheme("forest")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="peach">
                              <span className="flex items-center gap-2">
                                <span>🍑</span>
                                <span>{tTheme("peach")}</span>
                              </span>
                            </SelectItem>
                            <SelectItem value="dino">
                              <span className="flex items-center gap-2">
                                <span>🦖</span>
                                <span>{tTheme("dino")}</span>
                              </span>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                        <div className="flex flex-col gap-1 pr-4">
                          <Label
                            htmlFor="high_contrast"
                            className="text-sm font-medium text-foreground"
                          >
                            {tAccessibility("highContrast")}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {tAccessibility("highContrastDescription")}
                          </p>
                        </div>
                        <Switch
                          id="high_contrast"
                          checked={accessibilitySettings.high_contrast}
                          onCheckedChange={(checked) => {
                            setAccessibilitySettings((prev) => ({
                              ...prev,
                              high_contrast: checked,
                            }));
                            handleSaveAccessibility({ high_contrast: checked });
                          }}
                          aria-label={tAccessibility("highContrast")}
                          className="mt-3 sm:mt-0 shrink-0"
                        />
                      </div>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                        <div className="flex flex-col gap-1 pr-4">
                          <Label
                            htmlFor="large_text"
                            className="text-sm font-medium text-foreground"
                          >
                            {tAccessibility("largeText")}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {tAccessibility("largeTextDescription")}
                          </p>
                        </div>
                        <Switch
                          id="large_text"
                          checked={accessibilitySettings.large_text}
                          onCheckedChange={(checked) => {
                            setAccessibilitySettings((prev) => ({ ...prev, large_text: checked }));
                            handleSaveAccessibility({ large_text: checked });
                          }}
                          aria-label={tAccessibility("largeText")}
                          className="mt-3 sm:mt-0 shrink-0"
                        />
                      </div>
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                        <div className="flex flex-col gap-1 pr-4">
                          <Label
                            htmlFor="reduce_motion"
                            className="text-sm font-medium text-foreground"
                          >
                            {tAccessibility("reduceMotion")}
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            {tAccessibility("reduceMotionDescription")}
                          </p>
                        </div>
                        <Switch
                          id="reduce_motion"
                          checked={accessibilitySettings.reduce_motion}
                          onCheckedChange={(checked) => {
                            setAccessibilitySettings((prev) => ({
                              ...prev,
                              reduce_motion: checked,
                            }));
                            handleSaveAccessibility({ reduce_motion: checked });
                          }}
                          aria-label={tAccessibility("reduceMotion")}
                          className="mt-3 sm:mt-0 shrink-0"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {/* ═══════════ SECTION STATISTIQUES ═══════════ */}
          {activeSection === "statistics" && (
            <div className="space-y-8">
              {/* Statistiques */}
              {statsError ? (
                <div className="animate-fade-in-up">
                  <EmptyState title={t("error.title")} description={t("error.description")} />
                </div>
              ) : isLoadingStats ? (
                <div className="animate-fade-in-up">
                  <div className="grid gap-4 md:grid-cols-2">
                    <Card className="animate-pulse bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl h-[200px]">
                      <CardHeader>
                        <div className="h-6 w-32 bg-muted rounded" />
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="h-4 w-full bg-muted rounded" />
                          <div className="h-4 w-3/4 bg-muted rounded" />
                        </div>
                      </CardContent>
                    </Card>
                    <Card className="animate-pulse bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl h-[200px]">
                      <CardHeader>
                        <div className="h-6 w-40 bg-muted rounded" />
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="h-4 w-full bg-muted rounded" />
                          <div className="h-4 w-2/3 bg-muted rounded" />
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              ) : stats ? (
                <div className="animate-fade-in-up space-y-8">
                  <div className="space-y-3">
                    <p className="text-xs text-muted-foreground">
                      {tDashboard("profile.statsPeriodHint", {
                        period: tDashboard("timeRange.30days"),
                      })}
                    </p>
                    <div className="grid gap-6 md:grid-cols-2">
                      {user?.gamification_level ? (
                        <LevelIndicator level={user.gamification_level} />
                      ) : (
                        <Card className="border-dashed bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl">
                          <CardContent className="p-6 sm:p-8">
                            <p className="text-sm font-semibold text-foreground">
                              {tDashboard("profile.levelUnavailableTitle")}
                            </p>
                            <p className="mt-2 text-sm text-muted-foreground">
                              {tDashboard("profile.levelUnavailableDescription")}
                            </p>
                          </CardContent>
                        </Card>
                      )}
                      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8 flex flex-col justify-center">
                        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                          <CardTitle className="flex items-center gap-2 text-xl">
                            <TrendingUp className="h-5 w-5 text-primary" />
                            {tStatistics("overallPerformance")}
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="p-0">
                          <div className="flex flex-col">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                              <div className="flex flex-col gap-1 pr-4">
                                <p className="text-sm font-medium text-foreground">
                                  {tStatistics("totalAttempts")}
                                </p>
                              </div>
                              <p className="text-base font-semibold text-foreground sm:text-right mt-3 sm:mt-0 shrink-0">
                                {stats.total_exercises || 0}
                              </p>
                            </div>
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                              <div className="flex flex-col gap-1 pr-4">
                                <p className="text-sm font-medium text-foreground">
                                  {tStatistics("successRate")}
                                </p>
                              </div>
                              <p className="text-base font-semibold text-primary sm:text-right mt-3 sm:mt-0 shrink-0">
                                {Math.round((stats.success_rate || 0) * 10) / 10}%
                              </p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>

                  {/* Activité récente */}
                  {stats?.recent_activity && stats.recent_activity.length > 0 && (
                    <div className="animate-fade-in-up-delay-1">
                      {/* RecentActivity has its own internal card style, just rendering it */}
                      <RecentActivity activities={stats.recent_activity} />
                    </div>
                  )}
                </div>
              ) : null}

              {/* Badges récents */}
              {recentBadges.length > 0 && (
                <div className="animate-fade-in-up-delay-2">
                  <h3 className="text-xl font-semibold mb-6 flex items-center gap-2 px-1">
                    <Award className="h-5 w-5 text-primary" aria-hidden="true" />
                    {tBadges("title")}
                  </h3>
                  <div className="grid gap-6 md:grid-cols-3">
                    {recentBadges.map((badge: UserBadge & { earned_at: string }, index: number) => (
                      <Card
                        key={badge.id}
                        className={cn(
                          "bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6",
                          "relative overflow-hidden transition-all duration-300",
                          "hover:shadow-md hover:border-primary/20 hover:scale-[1.02]",
                          `animate-fade-in-up-delay-${Math.min(index + 1, 3)}`
                        )}
                      >
                        <CardHeader className="p-0 mb-4 space-y-0">
                          <div className="flex items-center justify-between mb-3">
                            <div className="p-2 rounded-full bg-primary/10 text-primary">
                              <Award className="h-6 w-6" />
                            </div>
                            <UIBadge variant="secondary" className="font-semibold bg-secondary/50">
                              {badge.points} pts
                            </UIBadge>
                          </div>
                          <CardTitle className="text-lg font-bold">{badge.name}</CardTitle>
                          <CardDescription className="mt-1 text-sm text-muted-foreground leading-relaxed">
                            {badge.description}
                          </CardDescription>
                        </CardHeader>
                        {badge.earned_at && (
                          <CardContent className="p-0 mt-auto">
                            <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground pt-4 border-t border-border/50">
                              <Calendar className="h-3.5 w-3.5" />
                              {formatDate(badge.earned_at)}
                            </div>
                          </CardContent>
                        )}
                      </Card>
                    ))}
                  </div>
                  <div className="mt-8 text-center">
                    <Button
                      variant="outline"
                      onClick={() => router.push("/badges")}
                      aria-label={tBadges("viewAll")}
                      className="transition-all duration-300 hover:scale-105 rounded-full px-6"
                    >
                      {tBadges("viewAll")}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </PageLayout>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePageContent />
    </ProtectedRoute>
  );
}
