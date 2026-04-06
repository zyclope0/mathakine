"use client";

import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader } from "@/components/layout";
import { Globe, Bell, Shield, Download, Settings } from "lucide-react";
import { useTranslations } from "next-intl";
import { useSettingsPageController, type SettingsSection } from "@/hooks/useSettingsPageController";
import { SettingsSidebarNav } from "@/components/settings/SettingsSidebarNav";
import { SettingsGeneralSection } from "@/components/settings/SettingsGeneralSection";
import { SettingsNotificationsSection } from "@/components/settings/SettingsNotificationsSection";
import { SettingsSecuritySection } from "@/components/settings/SettingsSecuritySection";
import { SettingsDataSection } from "@/components/settings/SettingsDataSection";

function SettingsPageContent() {
  const router = useRouter();
  const {
    activeSection,
    setActiveSection,
    languageSettings,
    setLanguageSettings,
    notificationSettings,
    setNotificationSettings,
    privacySettings,
    setPrivacySettings,
    sessions,
    visibleSessions,
    isLoadingSessions,
    showDeleteConfirm,
    setShowDeleteConfirm,
    visibleSessionCount,
    setVisibleSessionCount,
    diagnosticStatus,
    sessionToRevoke,
    setSessionToRevoke,
    SESSIONS_PAGE_SIZE,
    handleSaveLanguage,
    handleSavePrivacy,
    handleSaveNotifications,
    handleExportData,
    handleDeleteAccount,
    handleRevokeSession,
    confirmRevokeSession,
    isUpdatingSettings,
    isExportingData,
    isDeletingAccount,
    isRevokingSession,
  } = useSettingsPageController();

  const t = useTranslations("settings");

  const menuItems = [
    { id: "general" as const, label: t("menu.general"), icon: Globe },
    { id: "notifications" as const, label: t("menu.notifications"), icon: Bell },
    { id: "security" as const, label: t("menu.security"), icon: Shield },
    { id: "data" as const, label: t("menu.data"), icon: Download },
  ] satisfies Array<{ id: SettingsSection; label: string; icon: typeof Globe }>;

  return (
    <PageLayout maxWidth="lg">
      <PageHeader title={t("title")} description={t("description")} icon={Settings} />

      <div className="flex flex-col md:grid md:grid-cols-12 gap-8 md:gap-12 max-w-6xl mx-auto">
        <SettingsSidebarNav
          menuItems={menuItems}
          activeSection={activeSection}
          onSectionChange={setActiveSection}
        />

        <div className="md:col-span-9 space-y-8">
          {activeSection === "general" && (
            <SettingsGeneralSection
              languageSettings={languageSettings}
              setLanguageSettings={setLanguageSettings}
              onSaveLanguage={handleSaveLanguage}
              isUpdatingSettings={isUpdatingSettings}
            />
          )}

          {activeSection === "notifications" && (
            <SettingsNotificationsSection
              notificationSettings={notificationSettings}
              setNotificationSettings={setNotificationSettings}
              onSaveNotifications={handleSaveNotifications}
              isUpdatingSettings={isUpdatingSettings}
            />
          )}

          {activeSection === "security" && (
            <SettingsSecuritySection
              privacySettings={privacySettings}
              setPrivacySettings={setPrivacySettings}
              onSavePrivacy={handleSavePrivacy}
              isUpdatingSettings={isUpdatingSettings}
              sessions={sessions}
              visibleSessions={visibleSessions}
              isLoadingSessions={isLoadingSessions}
              sessionToRevoke={sessionToRevoke}
              setSessionToRevoke={setSessionToRevoke}
              onRevokeSession={handleRevokeSession}
              onConfirmRevokeSession={confirmRevokeSession}
              visibleSessionCount={visibleSessionCount}
              setVisibleSessionCount={setVisibleSessionCount}
              sessionsPageSize={SESSIONS_PAGE_SIZE}
              isRevokingSession={isRevokingSession}
            />
          )}

          {activeSection === "data" && (
            <SettingsDataSection
              diagnosticStatus={diagnosticStatus}
              showDeleteConfirm={showDeleteConfirm}
              setShowDeleteConfirm={setShowDeleteConfirm}
              onNavigateToDiagnostic={() => router.push("/diagnostic")}
              onExportData={handleExportData}
              onDeleteAccount={handleDeleteAccount}
              isExportingData={isExportingData}
              isDeletingAccount={isDeletingAccount}
            />
          )}
        </div>
      </div>
    </PageLayout>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsPageContent />
    </ProtectedRoute>
  );
}
