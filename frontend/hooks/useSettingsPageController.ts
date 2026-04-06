"use client";

/**
 * Local runtime state and side effects for the settings page.
 * No JSX. FFI-L13 lot A.
 */

import {
  useState,
  useCallback,
  useEffect,
  useRef,
  type Dispatch,
  type SetStateAction,
} from "react";
import { useAuth } from "@/hooks/useAuth";
import { useSettings, type UserSession } from "@/hooks/useSettings";
import { api } from "@/lib/api/client";
import {
  SESSIONS_PAGE_SIZE,
  type LanguageSettingsState,
  type NotificationSettingsState,
  type PrivacySettingsState,
  type SettingsSection,
  type DiagnosticStatusPayload,
  normalizeLanguageSettings,
  normalizeNotificationSettings,
  normalizePrivacySettings,
} from "@/lib/settings/settingsPage";

export type {
  SettingsSection,
  LanguageSettingsState,
  NotificationSettingsState,
  PrivacySettingsState,
};

export interface UseSettingsPageControllerResult {
  activeSection: SettingsSection;
  setActiveSection: (s: SettingsSection) => void;

  languageSettings: LanguageSettingsState;
  setLanguageSettings: Dispatch<SetStateAction<LanguageSettingsState>>;
  notificationSettings: NotificationSettingsState;
  setNotificationSettings: Dispatch<SetStateAction<NotificationSettingsState>>;
  privacySettings: PrivacySettingsState;
  setPrivacySettings: Dispatch<SetStateAction<PrivacySettingsState>>;

  sessions: UserSession[];
  isLoadingSessions: boolean;
  showDeleteConfirm: boolean;
  setShowDeleteConfirm: (v: boolean) => void;
  visibleSessionCount: number;
  setVisibleSessionCount: Dispatch<SetStateAction<number>>;
  diagnosticStatus: DiagnosticStatusPayload | null;
  sessionToRevoke: number | null;
  setSessionToRevoke: (id: number | null) => void;

  SESSIONS_PAGE_SIZE: typeof SESSIONS_PAGE_SIZE;

  handleSaveLanguage: () => void;
  handleSavePrivacy: () => void;
  handleSaveNotifications: () => void;
  handleExportData: () => void;
  handleDeleteAccount: () => void;
  handleRevokeSession: (sessionId: number) => void;
  confirmRevokeSession: () => void;

  isUpdatingSettings: boolean;
  isExportingData: boolean;
  isDeletingAccount: boolean;
  isRevokingSession: boolean;
}

function emptyLanguage(): LanguageSettingsState {
  return { language_preference: "fr", timezone: "UTC" };
}

function emptyNotification(): NotificationSettingsState {
  return {
    achievements: true,
    progress: true,
    recommendations: true,
    news: false,
  };
}

function emptyPrivacy(): PrivacySettingsState {
  return {
    is_public_profile: false,
    allow_friend_requests: true,
    show_in_leaderboards: true,
    data_retention_consent: true,
    marketing_consent: false,
  };
}

export function useSettingsPageController(): UseSettingsPageControllerResult {
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

  const [activeSection, setActiveSection] = useState<SettingsSection>("general");

  const [languageSettings, setLanguageSettings] = useState<LanguageSettingsState>(() =>
    user ? normalizeLanguageSettings(user) : emptyLanguage()
  );
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettingsState>(() =>
    user ? normalizeNotificationSettings(user) : emptyNotification()
  );
  const [privacySettings, setPrivacySettings] = useState<PrivacySettingsState>(() =>
    user ? normalizePrivacySettings(user) : emptyPrivacy()
  );

  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [visibleSessionCount, setVisibleSessionCount] = useState(SESSIONS_PAGE_SIZE);
  const [diagnosticStatus, setDiagnosticStatus] = useState<DiagnosticStatusPayload | null>(null);
  const [sessionToRevoke, setSessionToRevoke] = useState<number | null>(null);

  const isUpdatingFromServer = useRef(false);
  const lastSyncedUserId = useRef<number | null>(null);
  const isInitialMount = useRef(true);

  useEffect(() => {
    if (user && (isInitialMount.current || user.id !== lastSyncedUserId.current)) {
      if (isUpdatingFromServer.current) return;

      setLanguageSettings(normalizeLanguageSettings(user));
      setPrivacySettings(normalizePrivacySettings(user));
      setNotificationSettings(normalizeNotificationSettings(user));

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
        const status = await api.get<DiagnosticStatusPayload>("/api/diagnostic/status");
        setDiagnosticStatus(status);
      } catch {
        // Non bloquant
      }
    };
    loadSessions();
    loadDiagnosticStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- mount-only load; useSettings callbacks are unstable
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
      notification_preferences: { ...notificationSettings },
    });
  }, [notificationSettings, updateSettings, isUpdatingSettings]);

  const handleExportData = useCallback(() => exportData(), [exportData]);

  const handleDeleteAccount = useCallback(() => {
    if (showDeleteConfirm) deleteAccount();
    else setShowDeleteConfirm(true);
  }, [showDeleteConfirm, deleteAccount]);

  const handleRevokeSession = useCallback((sessionId: number) => setSessionToRevoke(sessionId), []);

  const confirmRevokeSession = useCallback(() => {
    if (sessionToRevoke !== null) {
      revokeSession(sessionToRevoke);
      setSessionToRevoke(null);
    }
  }, [sessionToRevoke, revokeSession]);

  return {
    activeSection,
    setActiveSection,
    languageSettings,
    setLanguageSettings,
    notificationSettings,
    setNotificationSettings,
    privacySettings,
    setPrivacySettings,
    sessions,
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
  };
}
