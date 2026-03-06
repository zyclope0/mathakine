"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useSettings, type UserSession } from "@/hooks/useSettings";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader } from "@/components/layout";
import { Button } from "@/components/ui/button";
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
import { SaveButton } from "@/components/settings/SaveButton";
import {
  Globe,
  Bell,
  Shield,
  Monitor,
  Download,
  Trash2,
  Loader2,
  Settings,
  BarChart2,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { api } from "@/lib/api/client";
import { cn } from "@/lib/utils";

type SettingsSection = "general" | "notifications" | "security" | "data";

function SettingsPageContent() {
  const { user } = useAuth();
  const {
    updateSettings,
    isUpdatingSettings,
    setOnUpdateSuccess,
    exportData,
    isExportingData,
    deleteAccount,
    isDeletingAccount,
    getSessions,
    revokeSession,
    isRevokingSession,
  } = useSettings();

  const t = useTranslations("settings");
  const tLanguage = useTranslations("settings.language");
  const tNotifications = useTranslations("settings.notifications");
  const tPrivacy = useTranslations("settings.privacy");
  const tSessions = useTranslations("settings.sessions");
  const tDiagnostic = useTranslations("settings.diagnostic");
  const tData = useTranslations("settings.data");
  const tActions = useTranslations("settings.actions");

  const [activeSection, setActiveSection] = useState<SettingsSection>("general");

  // États pour les formulaires
  const [languageSettings, setLanguageSettings] = useState({
    language_preference: String(
      user?.accessibility_settings?.language_preference || user?.language_preference || "fr"
    ),
    timezone: String(user?.accessibility_settings?.timezone || user?.timezone || "UTC"),
  });

  const getNotificationPref = (key: string): boolean => {
    const prefs = user?.accessibility_settings?.notification_preferences;
    if (prefs && typeof prefs === "object" && !Array.isArray(prefs)) {
      return (prefs as Record<string, boolean>)[key] ?? (key === "news" ? false : true);
    }
    return key === "news" ? false : true;
  };

  const [notificationSettings, setNotificationSettings] = useState({
    achievements: getNotificationPref("achievements"),
    progress: getNotificationPref("progress"),
    recommendations: getNotificationPref("recommendations"),
    news: getNotificationPref("news"),
  });

  const getPrivacyPref = (key: string, defaultValue: boolean): boolean => {
    const prefs = user?.accessibility_settings?.privacy_settings;
    if (prefs && typeof prefs === "object" && !Array.isArray(prefs)) {
      return (prefs as Record<string, boolean>)[key] ?? defaultValue;
    }
    return defaultValue;
  };

  const [privacySettings, setPrivacySettings] = useState({
    is_public_profile: getPrivacyPref("is_public_profile", false),
    allow_friend_requests: getPrivacyPref("allow_friend_requests", true),
    show_in_leaderboards: getPrivacyPref("show_in_leaderboards", true),
    data_retention_consent: getPrivacyPref("data_retention_consent", true),
    marketing_consent: getPrivacyPref("marketing_consent", false),
  });

  const router = useRouter();
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const SESSIONS_PAGE_SIZE = 3;
  const [visibleSessionCount, setVisibleSessionCount] = useState(SESSIONS_PAGE_SIZE);
  const [diagnosticStatus, setDiagnosticStatus] = useState<{
    has_completed: boolean;
    latest: { completed_at: string; scores: Record<string, { difficulty: string }> } | null;
  } | null>(null);

  const isUpdatingFromServer = useRef(false);
  const lastSyncedUserId = useRef<number | null>(null);
  const isInitialMount = useRef(true);

  useEffect(() => {
    if (user && (isInitialMount.current || user.id !== lastSyncedUserId.current)) {
      if (isUpdatingFromServer.current) return;

      setLanguageSettings({
        language_preference: String(
          user.accessibility_settings?.language_preference || user.language_preference || "fr"
        ),
        timezone: String(user.accessibility_settings?.timezone || user.timezone || "UTC"),
      });
      const getPriv = (key: string, def: boolean): boolean => {
        const p = user.accessibility_settings?.privacy_settings;
        if (p && typeof p === "object" && !Array.isArray(p)) {
          return (p as Record<string, boolean>)[key] ?? def;
        }
        return def;
      };
      setPrivacySettings({
        is_public_profile: getPriv("is_public_profile", false),
        allow_friend_requests: getPriv("allow_friend_requests", true),
        show_in_leaderboards: getPriv("show_in_leaderboards", true),
        data_retention_consent: getPriv("data_retention_consent", true),
        marketing_consent: getPriv("marketing_consent", false),
      });
      const getPref = (key: string): boolean => {
        const prefs = user.accessibility_settings?.notification_preferences;
        if (prefs && typeof prefs === "object" && !Array.isArray(prefs)) {
          return (prefs as Record<string, boolean>)[key] ?? (key === "news" ? false : true);
        }
        return key === "news" ? false : true;
      };
      setNotificationSettings({
        achievements: getPref("achievements"),
        progress: getPref("progress"),
        recommendations: getPref("recommendations"),
        news: getPref("news"),
      });

      lastSyncedUserId.current = user.id;
      isInitialMount.current = false;
    }
  }, [user]);

  useEffect(() => {
    setOnUpdateSuccess(() => {
      isUpdatingFromServer.current = false;
    });
  }, [setOnUpdateSuccess]);

  useEffect(() => {
    const loadSessions = async () => {
      setIsLoadingSessions(true);
      try {
        const userSessions = await getSessions();
        setSessions(userSessions);
      } catch (error) {
        console.error("Erreur lors du chargement des sessions:", error);
      } finally {
        setIsLoadingSessions(false);
      }
    };
    const loadDiagnosticStatus = async () => {
      try {
        const status = await api.get<typeof diagnosticStatus>("/api/diagnostic/status");
        setDiagnosticStatus(status);
      } catch {
        // Non bloquant
      }
    };
    loadSessions();
    loadDiagnosticStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSaveLanguage = useCallback(() => {
    if (isUpdatingSettings) return;
    isUpdatingFromServer.current = true;
    updateSettings(languageSettings);
  }, [languageSettings, updateSettings, isUpdatingSettings]);

  const handleSavePrivacy = useCallback(() => {
    if (isUpdatingSettings) return;
    isUpdatingFromServer.current = true;
    updateSettings(privacySettings);
  }, [privacySettings, updateSettings, isUpdatingSettings]);

  const handleSaveNotifications = useCallback(() => {
    if (isUpdatingSettings) return;
    isUpdatingFromServer.current = true;
    updateSettings({
      notification_preferences: notificationSettings,
    });
  }, [notificationSettings, updateSettings, isUpdatingSettings]);

  const handleExportData = useCallback(() => exportData(), [exportData]);

  const handleDeleteAccount = useCallback(() => {
    if (showDeleteConfirm) deleteAccount();
    else setShowDeleteConfirm(true);
  }, [showDeleteConfirm, deleteAccount]);

  const [sessionToRevoke, setSessionToRevoke] = useState<number | null>(null);
  const handleRevokeSession = useCallback((sessionId: number) => setSessionToRevoke(sessionId), []);
  const confirmRevokeSession = useCallback(() => {
    if (sessionToRevoke !== null) {
      revokeSession(sessionToRevoke);
      setSessionToRevoke(null);
    }
  }, [sessionToRevoke, revokeSession]);

  const languages = [
    { value: "fr", label: "Français" },
    { value: "en", label: "English" },
  ];

  const timezones = [
    { value: "UTC", label: "UTC (Coordinated Universal Time)" },
    { value: "Europe/Paris", label: "Europe/Paris (CET/CEST)" },
    { value: "America/New_York", label: "America/New_York (EST/EDT)" },
    { value: "America/Los_Angeles", label: "America/Los_Angeles (PST/PDT)" },
    { value: "Asia/Tokyo", label: "Asia/Tokyo (JST)" },
    { value: "Australia/Sydney", label: "Australia/Sydney (AEDT/AEST)" },
  ];

  const menuItems: { id: SettingsSection; label: string; icon: typeof Globe }[] = [
    { id: "general", label: t("menu.general"), icon: Globe },
    { id: "notifications", label: t("menu.notifications"), icon: Bell },
    { id: "security", label: t("menu.security"), icon: Shield },
    { id: "data", label: t("menu.data"), icon: Download },
  ];

  return (
    <PageLayout maxWidth="lg">
      <PageHeader title={t("title")} description={t("description")} icon={Settings} />

      <div className="flex flex-col md:grid md:grid-cols-12 gap-8 md:gap-12 max-w-6xl mx-auto">
        {/* Mobile: Select ou Tabs scrollables */}
        <div className="md:hidden">
          <Select value={activeSection} onValueChange={(v) => setActiveSection(v as SettingsSection)}>
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
          {/* ═══ GÉNÉRAL ═══ */}
          {activeSection === "general" && (
            <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
              <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Globe className="h-5 w-5 text-primary" />
                  {tLanguage("title")}
                </CardTitle>
                <CardDescription className="mt-1">{tLanguage("description")}</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="flex flex-col">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label htmlFor="language" className="text-sm font-medium text-foreground">
                        {tLanguage("language")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tLanguage("languageDescription")}
                      </p>
                    </div>
                    <Select
                      value={languageSettings.language_preference}
                      onValueChange={(value) =>
                        setLanguageSettings((prev) => ({ ...prev, language_preference: value }))
                      }
                    >
                      <SelectTrigger id="language" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {languages.map((lang) => (
                          <SelectItem key={lang.value} value={lang.value}>
                            {lang.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label htmlFor="timezone" className="text-sm font-medium text-foreground">
                        {tLanguage("timezone")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tLanguage("timezoneDescription")}
                      </p>
                    </div>
                    <Select
                      value={languageSettings.timezone}
                      onValueChange={(value) =>
                        setLanguageSettings((prev) => ({ ...prev, timezone: value }))
                      }
                    >
                      <SelectTrigger id="timezone" className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {timezones.map((tz) => (
                          <SelectItem key={tz.value} value={tz.value}>
                            {tz.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex justify-end pt-6">
                    <SaveButton onClick={handleSaveLanguage} isLoading={isUpdatingSettings} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ═══ NOTIFICATIONS ═══ */}
          {activeSection === "notifications" && (
            <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
              <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Bell className="h-5 w-5 text-primary" />
                  {tNotifications("title")}
                </CardTitle>
                <CardDescription className="mt-1">{tNotifications("description")}</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="flex flex-col">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label
                        htmlFor="notifications-achievements"
                        className="text-sm font-medium text-foreground"
                      >
                        {tNotifications("achievements")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tNotifications("achievementsDescription")}
                      </p>
                    </div>
                    <Switch
                      id="notifications-achievements"
                      checked={notificationSettings.achievements}
                      onCheckedChange={(checked) =>
                        setNotificationSettings((prev) => ({ ...prev, achievements: checked }))
                      }
                      className="mt-3 sm:mt-0 shrink-0"
                    />
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label
                        htmlFor="notifications-progress"
                        className="text-sm font-medium text-foreground"
                      >
                        {tNotifications("progress")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tNotifications("progressDescription")}
                      </p>
                    </div>
                    <Switch
                      id="notifications-progress"
                      checked={notificationSettings.progress}
                      onCheckedChange={(checked) =>
                        setNotificationSettings((prev) => ({ ...prev, progress: checked }))
                      }
                      className="mt-3 sm:mt-0 shrink-0"
                    />
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label
                        htmlFor="notifications-recommendations"
                        className="text-sm font-medium text-foreground"
                      >
                        {tNotifications("recommendations")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tNotifications("recommendationsDescription")}
                      </p>
                    </div>
                    <Switch
                      id="notifications-recommendations"
                      checked={notificationSettings.recommendations}
                      onCheckedChange={(checked) =>
                        setNotificationSettings((prev) => ({ ...prev, recommendations: checked }))
                      }
                      className="mt-3 sm:mt-0 shrink-0"
                    />
                  </div>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <Label
                        htmlFor="notifications-news"
                        className="text-sm font-medium text-foreground"
                      >
                        {tNotifications("news")}
                      </Label>
                      <p className="text-xs text-muted-foreground">
                        {tNotifications("newsDescription")}
                      </p>
                    </div>
                    <Switch
                      id="notifications-news"
                      checked={notificationSettings.news}
                      onCheckedChange={(checked) =>
                        setNotificationSettings((prev) => ({ ...prev, news: checked }))
                      }
                      className="mt-3 sm:mt-0 shrink-0"
                    />
                  </div>
                  <div className="flex justify-end pt-6">
                    <SaveButton onClick={handleSaveNotifications} isLoading={isUpdatingSettings} />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ═══ SÉCURITÉ & SESSIONS ═══ */}
          {activeSection === "security" && (
            <div className="space-y-8">
              {/* Confidentialité */}
              <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <Shield className="h-5 w-5 text-primary" />
                    {tPrivacy("title")}
                  </CardTitle>
                  <CardDescription className="mt-1">{tPrivacy("description")}</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="flex flex-col">
                    {[
                      {
                        id: "privacy-public-profile",
                        label: tPrivacy("publicProfile"),
                        desc: tPrivacy("publicProfileDescription"),
                        checked: privacySettings.is_public_profile,
                        key: "is_public_profile" as const,
                      },
                      {
                        id: "privacy-friend-requests",
                        label: tPrivacy("friendRequests"),
                        desc: tPrivacy("friendRequestsDescription"),
                        checked: privacySettings.allow_friend_requests,
                        key: "allow_friend_requests" as const,
                      },
                      {
                        id: "privacy-leaderboards",
                        label: tPrivacy("leaderboards"),
                        desc: tPrivacy("leaderboardsDescription"),
                        checked: privacySettings.show_in_leaderboards,
                        key: "show_in_leaderboards" as const,
                      },
                      {
                        id: "privacy-data-retention",
                        label: tPrivacy("dataRetention"),
                        desc: tPrivacy("dataRetentionDescription"),
                        checked: privacySettings.data_retention_consent,
                        key: "data_retention_consent" as const,
                      },
                      {
                        id: "privacy-marketing",
                        label: tPrivacy("marketing"),
                        desc: tPrivacy("marketingDescription"),
                        checked: privacySettings.marketing_consent,
                        key: "marketing_consent" as const,
                      },
                    ].map((item) => (
                      <div
                        key={item.id}
                        className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0"
                      >
                        <div className="flex flex-col gap-1 pr-4">
                          <Label htmlFor={item.id} className="text-sm font-medium text-foreground">
                            {item.label}
                          </Label>
                          <p className="text-xs text-muted-foreground">{item.desc}</p>
                        </div>
                        <Switch
                          id={item.id}
                          checked={item.checked}
                          onCheckedChange={(checked) =>
                            setPrivacySettings((prev) => ({ ...prev, [item.key]: checked }))
                          }
                          className="mt-3 sm:mt-0 shrink-0"
                        />
                      </div>
                    ))}
                    <div className="flex justify-end pt-6">
                      <SaveButton onClick={handleSavePrivacy} isLoading={isUpdatingSettings} />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Sessions actives */}
              <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <Monitor className="h-5 w-5 text-primary" />
                    {tSessions("title")}
                  </CardTitle>
                  <CardDescription className="mt-1">{tSessions("description")}</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  {isLoadingSessions ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                  ) : sessions.length === 0 ? (
                    <div className="py-8 text-center text-muted-foreground">
                      <p>{tSessions("noSessions")}</p>
                    </div>
                  ) : (
                    <div className="flex flex-col">
                      {sessions.slice(0, visibleSessionCount).map((session) => (
                        <div
                          key={session.id}
                          className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0"
                        >
                          <div className="flex flex-col gap-1 pr-4">
                            <p className="text-sm font-medium text-foreground">
                              {session.device_info?.device || tSessions("device")}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {session.location_data?.city && session.location_data?.country
                                ? `${session.location_data.city}, ${session.location_data.country}`
                                : session.ip_address || tSessions("location")}
                              {" · "}
                              {tSessions("lastActivity")}:{" "}
                              {format(new Date(session.last_activity), "PPpp", { locale: fr })}
                            </p>
                          </div>
                          {!session.is_current &&
                            (sessionToRevoke === session.id ? (
                              <div className="flex gap-2 shrink-0 mt-3 sm:mt-0">
                                <Button
                                  variant="destructive"
                                  size="sm"
                                  onClick={confirmRevokeSession}
                                  disabled={isRevokingSession}
                                >
                                  {isRevokingSession ? (
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                  ) : (
                                    tSessions("revoke")
                                  )}
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => setSessionToRevoke(null)}
                                  disabled={isRevokingSession}
                                >
                                  {tActions("cancel")}
                                </Button>
                              </div>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleRevokeSession(session.id)}
                                className="shrink-0 mt-3 sm:mt-0"
                              >
                                {tSessions("revoke")}
                              </Button>
                            ))}
                        </div>
                      ))}
                      {sessions.length > SESSIONS_PAGE_SIZE && (
                        <div className="flex justify-center pt-4">
                          {visibleSessionCount < sessions.length ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() =>
                                setVisibleSessionCount((n) =>
                                  Math.min(n + SESSIONS_PAGE_SIZE, sessions.length)
                                )
                              }
                            >
                              <ChevronDown className="mr-2 h-4 w-4" />
                              {tSessions("showMore", {
                                count: sessions.length - visibleSessionCount,
                              })}
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setVisibleSessionCount(SESSIONS_PAGE_SIZE)}
                            >
                              <ChevronUp className="mr-2 h-4 w-4" />
                              {tSessions("showLess")}
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}

          {/* ═══ DONNÉES & COMPTE ═══ */}
          {activeSection === "data" && (
            <div className="space-y-8">
              {/* Évaluation de niveau */}
              <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
                  <CardTitle className="flex items-center gap-2 text-xl">
                    <BarChart2 className="h-5 w-5 text-primary" />
                    {tDiagnostic("title")}
                  </CardTitle>
                  <CardDescription className="mt-1">{tDiagnostic("description")}</CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <p className="text-sm font-medium text-foreground">
                        {diagnosticStatus?.has_completed
                          ? tDiagnostic("lastDone", {
                              date: format(
                                new Date(diagnosticStatus.latest!.completed_at),
                                "dd/MM/yyyy",
                                { locale: fr }
                              ),
                            })
                          : tDiagnostic("notDone")}
                      </p>
                      {diagnosticStatus?.has_completed && diagnosticStatus.latest?.scores && (
                        <p className="text-xs text-muted-foreground">
                          {tDiagnostic("scores", {
                            summary: Object.entries(diagnosticStatus.latest.scores)
                              .map(([type, s]) => `${type}: ${s.difficulty}`)
                              .join(" · "),
                          })}
                        </p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant={diagnosticStatus?.has_completed ? "outline" : "default"}
                      onClick={() => router.push("/diagnostic")}
                      className="shrink-0 mt-3 sm:mt-0"
                    >
                      {diagnosticStatus?.has_completed ? tDiagnostic("redo") : tDiagnostic("start")}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Export */}
              <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
                <CardContent className="p-0">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                    <div className="flex flex-col gap-1 pr-4">
                      <p className="text-sm font-medium text-foreground">{tData("export")}</p>
                      <p className="text-xs text-muted-foreground">{tData("exportDescription")}</p>
                    </div>
                    <Button
                      onClick={handleExportData}
                      disabled={isExportingData}
                      variant="outline"
                      className="shrink-0 mt-3 sm:mt-0"
                    >
                      {isExportingData ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          {tData("exporting")}
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          {tData("export")}
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Suppression */}
              <Card className="bg-card/60 backdrop-blur-md border border-destructive/50 shadow-sm rounded-2xl p-6 md:p-8">
                <CardContent className="p-0">
                  {showDeleteConfirm ? (
                    <div className="space-y-4">
                      <div className="py-4 border-b border-border/50">
                        <p className="text-sm text-destructive font-medium">{tData("deleteWarning")}</p>
                      </div>
                      <div className="flex gap-2 pt-4">
                        <Button
                          onClick={handleDeleteAccount}
                          disabled={isDeletingAccount}
                          variant="destructive"
                          className="flex-1"
                        >
                          {isDeletingAccount ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              {tData("deleting")}
                            </>
                          ) : (
                            <>
                              <Trash2 className="mr-2 h-4 w-4" />
                              {tData("deleteConfirm")}
                            </>
                          )}
                        </Button>
                        <Button
                          onClick={() => setShowDeleteConfirm(false)}
                          variant="outline"
                          disabled={isDeletingAccount}
                        >
                          {tActions("cancel")}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                      <div className="flex flex-col gap-1 pr-4">
                        <p className="text-sm font-medium text-foreground">{tData("delete")}</p>
                        <p className="text-xs text-muted-foreground">{tData("deleteDescription")}</p>
                      </div>
                      <Button
                        onClick={handleDeleteAccount}
                        variant="destructive"
                        className="shrink-0 mt-3 sm:mt-0"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        {tData("delete")}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
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
