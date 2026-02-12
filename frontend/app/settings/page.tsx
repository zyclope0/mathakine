"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useSettings } from "@/hooks/useSettings";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PageLayout, PageHeader, PageSection } from "@/components/layout";
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
import { Separator } from "@/components/ui/separator";
import {
  Globe,
  Bell,
  Shield,
  Monitor,
  Download,
  Trash2,
  Save,
  Loader2,
  AlertTriangle,
  Settings,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { cn } from "@/lib/utils/cn";
import { format } from "date-fns";
import { fr } from "date-fns/locale";

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
  const tData = useTranslations("settings.data");
  const tActions = useTranslations("settings.actions");

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

  const [sessions, setSessions] = useState<any[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Refs pour éviter les boucles infinies
  const isUpdatingFromServer = useRef(false);
  const lastSyncedUserId = useRef<number | null>(null);
  const isInitialMount = useRef(true);

  // Synchroniser les états avec les données utilisateur UNIQUEMENT au montage initial
  // Ne pas synchroniser automatiquement après les mises à jour pour éviter les boucles
  useEffect(() => {
    // Synchroniser seulement au montage initial ou si l'utilisateur change (nouvelle connexion)
    if (user && (isInitialMount.current || user.id !== lastSyncedUserId.current)) {
      // Ignorer si on est en train de mettre à jour depuis le serveur
      if (isUpdatingFromServer.current) {
        return;
      }

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

  // Configurer le callback pour réinitialiser le flag après mise à jour réussie
  useEffect(() => {
    setOnUpdateSuccess(() => {
      isUpdatingFromServer.current = false;
    });
  }, [setOnUpdateSuccess]);

  // Charger les sessions
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
    loadSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Charger une seule fois au montage

  // Sauvegarder les paramètres de langue
  const handleSaveLanguage = useCallback(() => {
    if (isUpdatingSettings) return; // Éviter les appels multiples
    isUpdatingFromServer.current = true;
    updateSettings(languageSettings);
    // Réinitialiser le flag après la mise à jour réussie
    // Le flag sera réinitialisé dans le onSuccess de la mutation
  }, [languageSettings, updateSettings, isUpdatingSettings]);

  // Sauvegarder les paramètres de confidentialité
  const handleSavePrivacy = useCallback(() => {
    if (isUpdatingSettings) return; // Éviter les appels multiples
    isUpdatingFromServer.current = true;
    updateSettings(privacySettings);
  }, [privacySettings, updateSettings, isUpdatingSettings]);

  // Sauvegarder les paramètres de notifications
  const handleSaveNotifications = useCallback(() => {
    if (isUpdatingSettings) return; // Éviter les appels multiples
    isUpdatingFromServer.current = true;
    updateSettings({
      notification_preferences: notificationSettings,
    });
  }, [notificationSettings, updateSettings, isUpdatingSettings]);

  // Gérer l'export de données
  const handleExportData = useCallback(() => {
    exportData();
  }, [exportData]);

  // Gérer la suppression de compte
  const handleDeleteAccount = useCallback(() => {
    if (showDeleteConfirm) {
      deleteAccount();
    } else {
      setShowDeleteConfirm(true);
    }
  }, [showDeleteConfirm, deleteAccount]);

  // Révoquer une session
  const [sessionToRevoke, setSessionToRevoke] = useState<number | null>(null);
  const handleRevokeSession = useCallback((sessionId: number) => {
    setSessionToRevoke(sessionId);
  }, []);
  const confirmRevokeSession = useCallback(() => {
    if (sessionToRevoke !== null) {
      revokeSession(sessionToRevoke);
      setSessionToRevoke(null);
    }
  }, [sessionToRevoke, revokeSession]);

  // Liste des langues disponibles
  const languages = [
    { value: "fr", label: "Français" },
    { value: "en", label: "English" },
  ];

  // Liste des fuseaux horaires courants
  const timezones = [
    { value: "UTC", label: "UTC (Coordinated Universal Time)" },
    { value: "Europe/Paris", label: "Europe/Paris (CET/CEST)" },
    { value: "America/New_York", label: "America/New_York (EST/EDT)" },
    { value: "America/Los_Angeles", label: "America/Los_Angeles (PST/PDT)" },
    { value: "Asia/Tokyo", label: "Asia/Tokyo (JST)" },
    { value: "Australia/Sydney", label: "Australia/Sydney (AEDT/AEST)" },
  ];

  return (
    <PageLayout>
      <PageHeader title={t("title")} description={t("description")} icon={Settings} />

      <div className="space-y-6">
        {/* Section Langue et Région */}
        <PageSection
          title={tLanguage("title")}
          description={tLanguage("description")}
          icon={Globe}
          className="animate-fade-in-up-delay-1"
        >
          <Card>
            <CardHeader>
              <CardTitle>{tLanguage("title")}</CardTitle>
              <CardDescription>{tLanguage("description")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="language">{tLanguage("language")}</Label>
                <p className="text-xs text-muted-foreground">{tLanguage("languageDescription")}</p>
                <Select
                  value={languageSettings.language_preference}
                  onValueChange={(value) => {
                    setLanguageSettings((prev) => ({ ...prev, language_preference: value }));
                  }}
                >
                  <SelectTrigger id="language" className="w-full">
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

              <Separator />

              <div className="space-y-2">
                <Label htmlFor="timezone">{tLanguage("timezone")}</Label>
                <p className="text-xs text-muted-foreground">{tLanguage("timezoneDescription")}</p>
                <Select
                  value={languageSettings.timezone}
                  onValueChange={(value) => {
                    setLanguageSettings((prev) => ({ ...prev, timezone: value }));
                  }}
                >
                  <SelectTrigger id="timezone" className="w-full">
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

              <div className="flex justify-end pt-4">
                <Button onClick={handleSaveLanguage} disabled={isUpdatingSettings} size="sm">
                  {isUpdatingSettings ? (
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
            </CardContent>
          </Card>
        </PageSection>

        {/* Section Notifications */}
        <PageSection
          title={tNotifications("title")}
          description={tNotifications("description")}
          icon={Bell}
          className="animate-fade-in-up-delay-2"
        >
          <Card>
            <CardHeader>
              <CardTitle>{tNotifications("title")}</CardTitle>
              <CardDescription>{tNotifications("description")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications-achievements">
                    {tNotifications("achievements")}
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    {tNotifications("achievementsDescription")}
                  </p>
                </div>
                <Switch
                  id="notifications-achievements"
                  checked={notificationSettings.achievements}
                  onCheckedChange={(checked) => {
                    setNotificationSettings((prev) => ({ ...prev, achievements: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications-progress">{tNotifications("progress")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tNotifications("progressDescription")}
                  </p>
                </div>
                <Switch
                  id="notifications-progress"
                  checked={notificationSettings.progress}
                  onCheckedChange={(checked) => {
                    setNotificationSettings((prev) => ({ ...prev, progress: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications-recommendations">
                    {tNotifications("recommendations")}
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    {tNotifications("recommendationsDescription")}
                  </p>
                </div>
                <Switch
                  id="notifications-recommendations"
                  checked={notificationSettings.recommendations}
                  onCheckedChange={(checked) => {
                    setNotificationSettings((prev) => ({ ...prev, recommendations: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications-news">{tNotifications("news")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tNotifications("newsDescription")}
                  </p>
                </div>
                <Switch
                  id="notifications-news"
                  checked={notificationSettings.news}
                  onCheckedChange={(checked) => {
                    setNotificationSettings((prev) => ({ ...prev, news: checked }));
                  }}
                />
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={handleSaveNotifications} disabled={isUpdatingSettings} size="sm">
                  {isUpdatingSettings ? (
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
            </CardContent>
          </Card>
        </PageSection>

        {/* Section Confidentialité */}
        <PageSection
          title={tPrivacy("title")}
          description={tPrivacy("description")}
          icon={Shield}
          className="animate-fade-in-up-delay-3"
        >
          <Card>
            <CardHeader>
              <CardTitle>{tPrivacy("title")}</CardTitle>
              <CardDescription>{tPrivacy("description")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="privacy-public-profile">{tPrivacy("publicProfile")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tPrivacy("publicProfileDescription")}
                  </p>
                </div>
                <Switch
                  id="privacy-public-profile"
                  checked={privacySettings.is_public_profile}
                  onCheckedChange={(checked) => {
                    setPrivacySettings((prev) => ({ ...prev, is_public_profile: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="privacy-friend-requests">{tPrivacy("friendRequests")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tPrivacy("friendRequestsDescription")}
                  </p>
                </div>
                <Switch
                  id="privacy-friend-requests"
                  checked={privacySettings.allow_friend_requests}
                  onCheckedChange={(checked) => {
                    setPrivacySettings((prev) => ({ ...prev, allow_friend_requests: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="privacy-leaderboards">{tPrivacy("leaderboards")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tPrivacy("leaderboardsDescription")}
                  </p>
                </div>
                <Switch
                  id="privacy-leaderboards"
                  checked={privacySettings.show_in_leaderboards}
                  onCheckedChange={(checked) => {
                    setPrivacySettings((prev) => ({ ...prev, show_in_leaderboards: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="privacy-data-retention">{tPrivacy("dataRetention")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tPrivacy("dataRetentionDescription")}
                  </p>
                </div>
                <Switch
                  id="privacy-data-retention"
                  checked={privacySettings.data_retention_consent}
                  onCheckedChange={(checked) => {
                    setPrivacySettings((prev) => ({ ...prev, data_retention_consent: checked }));
                  }}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="privacy-marketing">{tPrivacy("marketing")}</Label>
                  <p className="text-xs text-muted-foreground">
                    {tPrivacy("marketingDescription")}
                  </p>
                </div>
                <Switch
                  id="privacy-marketing"
                  checked={privacySettings.marketing_consent}
                  onCheckedChange={(checked) => {
                    setPrivacySettings((prev) => ({ ...prev, marketing_consent: checked }));
                  }}
                />
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={handleSavePrivacy} disabled={isUpdatingSettings} size="sm">
                  {isUpdatingSettings ? (
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
            </CardContent>
          </Card>
        </PageSection>

        {/* Section Sessions */}
        <PageSection
          title={tSessions("title")}
          description={tSessions("description")}
          icon={Monitor}
          className="animate-fade-in-up-delay-4"
        >
          <Card>
            <CardHeader>
              <CardTitle>{tSessions("title")}</CardTitle>
              <CardDescription>{tSessions("description")}</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingSessions ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                </div>
              ) : sessions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>{tSessions("noSessions")}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {sessions.map((session) => (
                    <div
                      key={session.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="space-y-1">
                        <p className="font-medium">
                          {session.device_info?.device || tSessions("device")}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {session.location_data?.city && session.location_data?.country
                            ? `${session.location_data.city}, ${session.location_data.country}`
                            : session.ip_address || tSessions("location")}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {tSessions("lastActivity")}:{" "}
                          {format(new Date(session.last_activity), "PPpp", { locale: fr })}
                        </p>
                      </div>
                      {!session.is_current &&
                        (sessionToRevoke === session.id ? (
                          <div className="flex gap-2">
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
                          >
                            {tSessions("revoke")}
                          </Button>
                        ))}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </PageSection>

        {/* Section Données et Compte */}
        <PageSection
          title={tData("title")}
          description={tData("description")}
          icon={Download}
          className="animate-fade-in-up-delay-5"
        >
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{tData("export")}</CardTitle>
                <CardDescription>{tData("exportDescription")}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={handleExportData}
                  disabled={isExportingData}
                  variant="outline"
                  className="w-full sm:w-auto"
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
              </CardContent>
            </Card>

            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="text-destructive flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  {tData("delete")}
                </CardTitle>
                <CardDescription>{tData("deleteDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {showDeleteConfirm ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
                      <p className="text-sm text-destructive font-medium">
                        {tData("deleteWarning")}
                      </p>
                    </div>
                    <div className="flex gap-2">
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
                  <Button
                    onClick={handleDeleteAccount}
                    variant="destructive"
                    className="w-full sm:w-auto"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    {tData("delete")}
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </PageSection>
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
