"use client";

import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { User, Palette, BarChart3 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useUserStats } from "@/hooks/useUserStats";
import { useBadges } from "@/hooks/useBadges";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader, EmptyState } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { useProfilePageController } from "@/hooks/useProfilePageController";
import { ProfileSidebarNav } from "@/components/profile/ProfileSidebarNav";
import { ProfilePersonalInfoSection } from "@/components/profile/ProfilePersonalInfoSection";
import { ProfileLearningPreferencesSection } from "@/components/profile/ProfileLearningPreferencesSection";
import { ProfileSecuritySection } from "@/components/profile/ProfileSecuritySection";
import { ProfileAccessibilitySection } from "@/components/profile/ProfileAccessibilitySection";
import { ProfileStatisticsSection } from "@/components/profile/ProfileStatisticsSection";
import type { ProfileSection, ValidProfileTheme } from "@/lib/profile/profilePage";
import type { NavItem } from "@/components/profile/ProfileSidebarNav";
import type { GamificationLevelIndicator } from "@/types/api";

function ProfilePageContent() {
  const { user } = useAuth();
  const { stats, isLoading: isLoadingStats, error: statsError } = useUserStats("30");
  const { earnedBadges } = useBadges();
  const router = useRouter();

  const t = useTranslations("profile");
  const tPersonal = useTranslations("profile.personalInfo");
  const tAccessibility = useTranslations("profile.accessibility");
  const tStatistics = useTranslations("profile.statistics");
  const tActions = useTranslations("profile.actions");
  const tValidation = useTranslations("profile.validation");
  const tSecurity = useTranslations("profile.security");

  const ctrl = useProfilePageController({
    user,
    earnedBadges: earnedBadges as Parameters<typeof useProfilePageController>[0]["earnedBadges"],
    tValidation: (key) => tValidation(key),
    tSecurity: (key) => tSecurity(key),
  });

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

  const menuItems: NavItem[] = [
    { id: "profile" as ProfileSection, label: tPersonal("title"), icon: User },
    { id: "preferences" as ProfileSection, label: tAccessibility("title"), icon: Palette },
    { id: "statistics" as ProfileSection, label: tStatistics("title"), icon: BarChart3 },
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
        <ProfileSidebarNav
          activeSection={ctrl.activeSection}
          onSectionChange={ctrl.setActiveSection}
          items={menuItems}
        />

        <div className="md:col-span-9 space-y-8">
          {/* ═══════════ SECTION PROFIL ═══════════ */}
          {ctrl.activeSection === "profile" && (
            <div className="space-y-6">
              <ProfilePersonalInfoSection
                user={user}
                isEditing={ctrl.isEditingPersonalInfo}
                personalInfo={ctrl.personalInfo}
                errors={ctrl.errors}
                isUpdatingProfile={ctrl.isUpdatingProfile}
                formatDate={ctrl.formatDate}
                onStartEditing={() => ctrl.setIsEditingPersonalInfo(true)}
                onPersonalInfoChange={(field, value) =>
                  ctrl.setPersonalInfo((prev) => ({ ...prev, [field]: value }))
                }
                onEmailBlur={() => ctrl.validateEmail(ctrl.personalInfo.email)}
                onClearFieldError={ctrl.clearFieldError}
                onSave={ctrl.handleSavePersonalInfo}
                onCancel={ctrl.handleResetPersonalInfo}
              />

              <ProfileLearningPreferencesSection
                user={user}
                isEditing={ctrl.isEditingLearningPrefs}
                learningPrefs={ctrl.learningPrefs}
                isUpdatingProfile={ctrl.isUpdatingProfile}
                getAgeDisplay={ctrl.getAgeDisplay}
                onStartEditing={() => ctrl.setIsEditingLearningPrefs(true)}
                onLearningPrefsChange={(update) =>
                  ctrl.setLearningPrefs((prev) => ({ ...prev, ...update }))
                }
                onSave={ctrl.handleSaveLearningPrefs}
                onCancel={ctrl.handleResetLearningPrefs}
              />

              <ProfileSecuritySection
                showPasswordForm={ctrl.showPasswordForm}
                showCurrentPassword={ctrl.showCurrentPassword}
                showNewPassword={ctrl.showNewPassword}
                showConfirmPassword={ctrl.showConfirmPassword}
                passwordData={ctrl.passwordData}
                errors={ctrl.errors}
                isChangingPassword={ctrl.isChangingPassword}
                onShowForm={() => ctrl.setShowPasswordForm(true)}
                onToggleCurrentPassword={() =>
                  ctrl.setShowCurrentPassword(!ctrl.showCurrentPassword)
                }
                onToggleNewPassword={() => ctrl.setShowNewPassword(!ctrl.showNewPassword)}
                onToggleConfirmPassword={() =>
                  ctrl.setShowConfirmPassword(!ctrl.showConfirmPassword)
                }
                onPasswordFieldChange={(field, value) =>
                  ctrl.setPasswordData((prev) => ({ ...prev, [field]: value }))
                }
                onClearFieldError={ctrl.clearFieldError}
                onSave={ctrl.handleChangePassword}
                onCancel={ctrl.handleResetPasswordForm}
              />
            </div>
          )}

          {/* ═══════════ SECTION ACCESSIBILITÉ ═══════════ */}
          {ctrl.activeSection === "preferences" && (
            <div className="space-y-6">
              <ProfileAccessibilitySection
                accessibilitySettings={ctrl.accessibilitySettings}
                onThemeChange={(theme: ValidProfileTheme) => {
                  ctrl.setAccessibilitySettings((prev) => ({
                    ...prev,
                    preferred_theme: theme,
                  }));
                  ctrl.handleSaveAccessibility({ preferred_theme: theme });
                }}
                onToggle={(field, checked) => {
                  ctrl.setAccessibilitySettings((prev) => ({ ...prev, [field]: checked }));
                  ctrl.handleSaveAccessibility({ [field]: checked });
                }}
              />
            </div>
          )}

          {/* ═══════════ SECTION STATISTIQUES ═══════════ */}
          {ctrl.activeSection === "statistics" && (
            <ProfileStatisticsSection
              stats={stats}
              isLoadingStats={isLoadingStats}
              statsError={statsError}
              gamificationLevel={user.gamification_level as GamificationLevelIndicator | undefined}
              recentBadges={ctrl.recentBadges}
              formatDate={ctrl.formatDate}
            />
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
