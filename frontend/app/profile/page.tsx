"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useProfile } from "@/hooks/useProfile";
import { useUserStats } from "@/hooks/useUserStats";
import { useBadges } from "@/hooks/useBadges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader, PageSection, EmptyState } from "@/components/layout";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge as UIBadge } from "@/components/ui/badge";
import type { UserBadge } from "@/types/api";
import {
  User,
  Mail,
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
} from "lucide-react";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { LevelIndicator } from "@/components/dashboard/LevelIndicator";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { cn } from "@/lib/utils/cn";
import { format } from "date-fns";
import { AGE_GROUPS, type AgeGroup } from "@/lib/constants/exercises";
import { useAgeGroupDisplay } from "@/hooks/useChallengeTranslations";
import { fr } from "date-fns/locale";
import { useThemeStore } from "@/lib/stores/themeStore";

function ProfilePageContent() {
  const { user } = useAuth();
  const { updateProfile, isUpdatingProfile, changePassword, isChangingPassword } = useProfile();
  const { stats, isLoading: isLoadingStats, error: statsError } = useUserStats("30");
  const { earnedBadges, isLoading: isLoadingBadges, error: badgesError } = useBadges();
  const { setTheme } = useThemeStore();
  const getAgeDisplay = useAgeGroupDisplay();
  const router = useRouter();
  const t = useTranslations("profile");
  const tPersonal = useTranslations("profile.personalInfo");
  const tLearning = useTranslations("profile.learningPreferences");
  const tSecurity = useTranslations("profile.security");
  const tAccessibility = useTranslations("profile.accessibility");
  const tStatistics = useTranslations("profile.statistics");
  const tBadges = useTranslations("profile.badges");
  const tActions = useTranslations("profile.actions");
  const tValidation = useTranslations("profile.validation");
  const tTheme = useTranslations("theme");

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

  // Données du formulaire préférences d'apprentissage
  const [learningPrefs, setLearningPrefs] = useState({
    grade_level: user?.grade_level?.toString() || "",
    learning_style: user?.learning_style || "",
    preferred_difficulty: user?.preferred_difficulty || "",
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

  // Synchroniser les états locaux avec les données utilisateur
  useEffect(() => {
    if (user) {
      setPersonalInfo({
        email: user.email || "",
        full_name: user.full_name || "",
      });
      setLearningPrefs({
        grade_level: user.grade_level?.toString() || "",
        learning_style: user.learning_style || "",
        preferred_difficulty: user.preferred_difficulty || "",
      });
      // Migration: neutral → dune
      const userThemeRaw = user.preferred_theme || "spatial";
      const userTheme = userThemeRaw === "neutral" ? "dune" : userThemeRaw;
      const validThemes = ["spatial", "minimalist", "ocean", "dune", "forest", "peach", "dino"] as const;
      setAccessibilitySettings({
        preferred_theme: userTheme,
        high_contrast: user.accessibility_settings?.high_contrast || false,
        large_text: user.accessibility_settings?.large_text || false,
        reduce_motion: user.accessibility_settings?.reduce_motion || false,
      });
      const safeTheme = validThemes.includes(
        userTheme as (typeof validThemes)[number]
      )
        ? (userTheme as (typeof validThemes)[number])
        : "spatial";
      setTheme(safeTheme);
    }
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

  // Validation mot de passe
  const validatePassword = (): boolean => {
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
  };

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
      ...(learningPrefs.grade_level ? { grade_level: parseInt(learningPrefs.grade_level) } : {}),
      ...(learningPrefs.learning_style ? { learning_style: learningPrefs.learning_style } : {}),
      ...(learningPrefs.preferred_difficulty
        ? { preferred_difficulty: learningPrefs.preferred_difficulty }
        : {}),
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
        setTheme(settings.preferred_theme as "spatial" | "minimalist" | "ocean" | "dune" | "forest" | "peach" | "dino");
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

  return (
    <PageLayout maxWidth="2xl">
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

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3 h-auto" aria-label="Sections du profil">
          <TabsTrigger value="profile" className="flex items-center gap-2 py-2.5 text-sm">
            <User className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">{tPersonal("title")}</span>
            <span className="sm:hidden">Profil</span>
          </TabsTrigger>
          <TabsTrigger value="preferences" className="flex items-center gap-2 py-2.5 text-sm">
            <Palette className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">{tAccessibility("title")}</span>
            <span className="sm:hidden">Prefs</span>
          </TabsTrigger>
          <TabsTrigger value="statistics" className="flex items-center gap-2 py-2.5 text-sm">
            <BarChart3 className="h-4 w-4" aria-hidden="true" />
            <span className="hidden sm:inline">{tStatistics("title")}</span>
            <span className="sm:hidden">Stats</span>
          </TabsTrigger>
        </TabsList>

        {/* ═══════════ ONGLET PROFIL ═══════════ */}
        <TabsContent value="profile" className="space-y-6">
          {/* Informations personnelles */}
          <PageSection className="animate-fade-in-up">
            <Card className="transition-all duration-300 hover:shadow-lg hover:border-primary/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5 text-primary" />
                    {tPersonal("title")}
                  </CardTitle>
                  {!isEditingPersonalInfo && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsEditingPersonalInfo(true)}
                      aria-label={tActions("edit")}
                    >
                      {tActions("edit")}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="username">{tPersonal("username")}</Label>
                  <Input
                    id="username"
                    value={user.username}
                    disabled
                    aria-label={tPersonal("username")}
                    aria-describedby="username-description"
                  />
                  <p id="username-description" className="text-xs text-muted-foreground">
                    {tPersonal("usernameDescription")}
                  </p>
                </div>

                {isEditingPersonalInfo ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="email">{tPersonal("email")} *</Label>
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
                          className="text-sm text-destructive"
                          role="alert"
                          aria-live="polite"
                        >
                          {errors.email}
                        </p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="full_name">{tPersonal("fullName")}</Label>
                      <Input
                        id="full_name"
                        type="text"
                        value={personalInfo.full_name}
                        onChange={(e) =>
                          setPersonalInfo((prev) => ({ ...prev, full_name: e.target.value }))
                        }
                        placeholder={tPersonal("fullNamePlaceholder")}
                        disabled={isUpdatingProfile}
                      />
                    </div>

                    <div className="flex gap-2">
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
                    </div>
                  </>
                ) : (
                  <>
                    <div className="space-y-2">
                      <Label>{tPersonal("email")}</Label>
                      <p className="text-sm text-foreground">{user.email || "-"}</p>
                    </div>
                    <div className="space-y-2">
                      <Label>{tPersonal("fullName")}</Label>
                      <p className="text-sm text-foreground">{user.full_name || "-"}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4 pt-2">
                      <div>
                        <Label className="text-xs text-muted-foreground">{tPersonal("role")}</Label>
                        <p className="text-sm font-medium capitalize">{user.role || "-"}</p>
                      </div>
                      <div>
                        <Label className="text-xs text-muted-foreground">
                          {tPersonal("memberSince")}
                        </Label>
                        <p className="text-sm font-medium">{formatDate(user.created_at)}</p>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </PageSection>

          {/* Préférences d'apprentissage */}
          <PageSection className="animate-fade-in-up-delay-1">
            <Card className="transition-all duration-300 hover:shadow-lg hover:border-primary/20">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5 text-primary" />
                    {tLearning("title")}
                  </CardTitle>
                  {!isEditingLearningPrefs && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsEditingLearningPrefs(true)}
                      aria-label={tActions("edit")}
                    >
                      {tActions("edit")}
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {isEditingLearningPrefs ? (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="grade_level">{tLearning("gradeLevel")}</Label>
                      <Select
                        value={learningPrefs.grade_level}
                        onValueChange={(value) =>
                          setLearningPrefs((prev) => ({ ...prev, grade_level: value }))
                        }
                        disabled={isUpdatingProfile}
                      >
                        <SelectTrigger id="grade_level" aria-label={tLearning("gradeLevel")}>
                          <SelectValue placeholder={tLearning("gradeLevelPlaceholder")} />
                        </SelectTrigger>
                        <SelectContent>
                          {Array.from({ length: 12 }, (_, i) => i + 1).map((level) => (
                            <SelectItem key={level} value={level.toString()}>
                              {level}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="learning_style">{tLearning("learningStyle")}</Label>
                      <Select
                        value={learningPrefs.learning_style}
                        onValueChange={(value) =>
                          setLearningPrefs((prev) => ({ ...prev, learning_style: value }))
                        }
                        disabled={isUpdatingProfile}
                      >
                        <SelectTrigger id="learning_style" aria-label={tLearning("learningStyle")}>
                          <SelectValue placeholder={tLearning("learningStylePlaceholder")} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="visuel">{t("learningStyles.visuel")}</SelectItem>
                          <SelectItem value="auditif">{t("learningStyles.auditif")}</SelectItem>
                          <SelectItem value="kinesthésique">
                            {t("learningStyles.kinesthésique")}
                          </SelectItem>
                          <SelectItem value="lecture">{t("learningStyles.lecture")}</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="preferred_age_group">{tLearning("preferredAgeGroup")}</Label>
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
                        >
                          <SelectValue placeholder={tLearning("preferredAgeGroupPlaceholder")} />
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

                    <div className="flex gap-2">
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
                      <Button
                        variant="outline"
                        onClick={() => {
                          setIsEditingLearningPrefs(false);
                          setLearningPrefs({
                            grade_level: user.grade_level?.toString() || "",
                            learning_style: user.learning_style || "",
                            preferred_difficulty: user.preferred_difficulty || "",
                          });
                        }}
                        disabled={isUpdatingProfile}
                        aria-label={tActions("cancel")}
                      >
                        <X className="mr-2 h-4 w-4" />
                        {tActions("cancel")}
                      </Button>
                    </div>
                  </>
                ) : (
                  <div className="space-y-3">
                    <div>
                      <Label className="text-xs text-muted-foreground">
                        {tLearning("gradeLevel")}
                      </Label>
                      <p className="text-sm font-medium">{user.grade_level || "-"}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">
                        {tLearning("learningStyle")}
                      </Label>
                      <p className="text-sm font-medium capitalize">{user.learning_style || "-"}</p>
                    </div>
                    <div>
                      <Label className="text-xs text-muted-foreground">
                        {tLearning("preferredAgeGroup")}
                      </Label>
                      <p className="text-sm font-medium">
                        {user.preferred_difficulty
                          ? Object.values(AGE_GROUPS).includes(
                              user.preferred_difficulty as AgeGroup
                            )
                            ? getAgeDisplay(user.preferred_difficulty)
                            : user.preferred_difficulty
                          : "-"}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </PageSection>

          {/* Sécurité */}
          <PageSection className="animate-fade-in-up-delay-2">
            <Card className="transition-all duration-300 hover:shadow-lg hover:border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lock className="h-5 w-5 text-primary" />
                  {tSecurity("title")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!showPasswordForm ? (
                  <Button
                    onClick={() => setShowPasswordForm(true)}
                    variant="outline"
                    aria-label={tSecurity("changePassword")}
                  >
                    {tSecurity("changePassword")}
                  </Button>
                ) : (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current_password">{tSecurity("currentPassword")} *</Label>
                      <div className="relative">
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

                    <div className="space-y-2">
                      <Label htmlFor="new_password">{tSecurity("newPassword")} *</Label>
                      <div className="relative">
                        <Input
                          id="new_password"
                          type={showNewPassword ? "text" : "password"}
                          value={passwordData.new_password}
                          onChange={(e) => {
                            setPasswordData((prev) => ({ ...prev, new_password: e.target.value }));
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
                          aria-describedby={errors.new_password ? "new-password-error" : undefined}
                          disabled={isChangingPassword}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-0 top-0 h-full px-3"
                          onClick={() => setShowNewPassword(!showNewPassword)}
                          aria-label={
                            showNewPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"
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

                    <div className="space-y-2">
                      <Label htmlFor="confirm_password">{tSecurity("confirmPassword")} *</Label>
                      <div className="relative">
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

                    <div className="flex gap-2">
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
          </PageSection>
        </TabsContent>

        {/* ═══════════ ONGLET PRÉFÉRENCES ═══════════ */}
        <TabsContent value="preferences" className="space-y-6">
          {/* Accessibilité */}
          <PageSection className="animate-fade-in-up">
            <Card className="transition-all duration-300 hover:shadow-lg hover:border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-primary" />
                  {tAccessibility("title")}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="theme">{tAccessibility("theme")}</Label>
                    <p className="text-xs text-muted-foreground">
                      {tAccessibility("themeDescription")}
                    </p>
                  </div>
                  <Select
                    value={accessibilitySettings.preferred_theme}
                    onValueChange={(value) => {
                      const theme = value as "spatial" | "minimalist" | "ocean" | "dune" | "forest" | "peach" | "dino";
                      setAccessibilitySettings((prev) => ({ ...prev, preferred_theme: theme }));
                      handleSaveAccessibility({ preferred_theme: theme });
                    }}
                  >
                    <SelectTrigger
                      id="theme"
                      className="w-[200px]"
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

                <Separator />

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="high_contrast">{tAccessibility("highContrast")}</Label>
                    <p className="text-xs text-muted-foreground">
                      {tAccessibility("highContrastDescription")}
                    </p>
                  </div>
                  <Switch
                    id="high_contrast"
                    checked={accessibilitySettings.high_contrast}
                    onCheckedChange={(checked) => {
                      setAccessibilitySettings((prev) => ({ ...prev, high_contrast: checked }));
                      handleSaveAccessibility({ high_contrast: checked });
                    }}
                    aria-label={tAccessibility("highContrast")}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="large_text">{tAccessibility("largeText")}</Label>
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
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="reduce_motion">{tAccessibility("reduceMotion")}</Label>
                    <p className="text-xs text-muted-foreground">
                      {tAccessibility("reduceMotionDescription")}
                    </p>
                  </div>
                  <Switch
                    id="reduce_motion"
                    checked={accessibilitySettings.reduce_motion}
                    onCheckedChange={(checked) => {
                      setAccessibilitySettings((prev) => ({ ...prev, reduce_motion: checked }));
                      handleSaveAccessibility({ reduce_motion: checked });
                    }}
                    aria-label={tAccessibility("reduceMotion")}
                  />
                </div>
              </CardContent>
            </Card>
          </PageSection>
        </TabsContent>

        {/* ═══════════ ONGLET STATISTIQUES ═══════════ */}
        <TabsContent value="statistics" className="space-y-6">
          {/* Statistiques */}
          {statsError ? (
            <PageSection className="animate-fade-in-up">
              <EmptyState title={t("error.title")} description={t("error.description")} />
            </PageSection>
          ) : isLoadingStats ? (
            <PageSection className="animate-fade-in-up">
              <div className="grid gap-4 md:grid-cols-2">
                <Card className="animate-pulse">
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
                <Card className="animate-pulse">
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
            </PageSection>
          ) : stats ? (
            <PageSection className="animate-fade-in-up">
              <div className="grid gap-4 md:grid-cols-2">
                {stats.level && <LevelIndicator level={stats.level} />}
                <Card className="transition-all duration-300 hover:shadow-lg hover:border-primary/20">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-primary" />
                      {tStatistics("overallPerformance")}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">
                          {tStatistics("totalAttempts")}
                        </span>
                        <span className="text-lg font-semibold">{stats.total_exercises || 0}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">
                          {tStatistics("successRate")}
                        </span>
                        <span className="text-lg font-semibold text-primary">
                          {Math.round((stats.success_rate || 0) * 10) / 10}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </PageSection>
          ) : null}

          {/* Activité récente */}
          {stats?.recent_activity && stats.recent_activity.length > 0 && (
            <PageSection className="animate-fade-in-up-delay-1">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-primary" aria-hidden="true" />
                {t("recentActivity.title")}
              </h3>
              <RecentActivity activities={stats.recent_activity} />
            </PageSection>
          )}

          {/* Badges récents */}
          {recentBadges.length > 0 && (
            <PageSection className="animate-fade-in-up-delay-2">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Award className="h-5 w-5 text-primary" aria-hidden="true" />
                {tBadges("title")}
              </h3>
              <div className="grid gap-4 md:grid-cols-3">
                {recentBadges.map((badge: UserBadge & { earned_at: string }, index: number) => (
                  <Card
                    key={badge.id}
                    className={cn(
                      "relative overflow-hidden transition-all duration-300",
                      "hover:shadow-lg hover:border-primary/20 hover:scale-[1.02]",
                      `animate-fade-in-up-delay-${Math.min(index + 1, 3)}`
                    )}
                  >
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <Award className="h-8 w-8 text-primary" />
                        <UIBadge variant="secondary" className="font-semibold">
                          {badge.points} pts
                        </UIBadge>
                      </div>
                      <CardTitle className="text-lg mt-2">{badge.name}</CardTitle>
                      <CardDescription className="mt-1">{badge.description}</CardDescription>
                    </CardHeader>
                    {badge.earned_at && (
                      <CardContent>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {formatDate(badge.earned_at)}
                        </div>
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
              <div className="mt-6 text-center">
                <Button
                  variant="outline"
                  onClick={() => router.push("/badges")}
                  aria-label={tBadges("viewAll")}
                  className="transition-all duration-300 hover:scale-105"
                >
                  {tBadges("viewAll")}
                </Button>
              </div>
            </PageSection>
          )}
        </TabsContent>
      </Tabs>
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
