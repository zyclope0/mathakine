"use client";

/**
 * Privacy card + active sessions (security tab).
 * Order preserved: confidentiality first, then sessions.
 * FFI-L13 lot B.
 */

import { useTranslations } from "next-intl";
import { Shield, Monitor, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { SaveButton } from "@/components/settings/SaveButton";
import type { UserSession } from "@/hooks/useSettings";
import { formatSessionDate, type PrivacySettingsState } from "@/lib/settings/settingsPage";
import type { Dispatch, SetStateAction } from "react";
import { fr } from "date-fns/locale";

type PrivacyToggleKey = keyof PrivacySettingsState;

export interface SettingsSecuritySectionProps {
  privacySettings: PrivacySettingsState;
  setPrivacySettings: Dispatch<SetStateAction<PrivacySettingsState>>;
  onSavePrivacy: () => void;
  isUpdatingSettings: boolean;

  sessions: UserSession[];
  visibleSessions: UserSession[];
  isLoadingSessions: boolean;
  sessionToRevoke: number | null;
  setSessionToRevoke: (id: number | null) => void;
  onRevokeSession: (sessionId: number) => void;
  onConfirmRevokeSession: () => void;
  visibleSessionCount: number;
  setVisibleSessionCount: Dispatch<SetStateAction<number>>;
  sessionsPageSize: number;
  isRevokingSession: boolean;
}

export function SettingsSecuritySection({
  privacySettings,
  setPrivacySettings,
  onSavePrivacy,
  isUpdatingSettings,
  sessions,
  visibleSessions,
  isLoadingSessions,
  sessionToRevoke,
  setSessionToRevoke,
  onRevokeSession,
  onConfirmRevokeSession,
  visibleSessionCount,
  setVisibleSessionCount,
  sessionsPageSize,
  isRevokingSession,
}: SettingsSecuritySectionProps) {
  const tPrivacy = useTranslations("settings.privacy");
  const tSessions = useTranslations("settings.sessions");
  const tActions = useTranslations("settings.actions");

  const privacyRows: Array<{
    id: string;
    label: string;
    desc: string;
    checked: boolean;
    key: PrivacyToggleKey;
  }> = [
    {
      id: "privacy-public-profile",
      label: tPrivacy("publicProfile"),
      desc: tPrivacy("publicProfileDescription"),
      checked: privacySettings.is_public_profile,
      key: "is_public_profile",
    },
    {
      id: "privacy-friend-requests",
      label: tPrivacy("friendRequests"),
      desc: tPrivacy("friendRequestsDescription"),
      checked: privacySettings.allow_friend_requests,
      key: "allow_friend_requests",
    },
    {
      id: "privacy-leaderboards",
      label: tPrivacy("leaderboards"),
      desc: tPrivacy("leaderboardsDescription"),
      checked: privacySettings.show_in_leaderboards,
      key: "show_in_leaderboards",
    },
    {
      id: "privacy-data-retention",
      label: tPrivacy("dataRetention"),
      desc: tPrivacy("dataRetentionDescription"),
      checked: privacySettings.data_retention_consent,
      key: "data_retention_consent",
    },
    {
      id: "privacy-marketing",
      label: tPrivacy("marketing"),
      desc: tPrivacy("marketingDescription"),
      checked: privacySettings.marketing_consent,
      key: "marketing_consent",
    },
  ];

  return (
    <div className="space-y-8">
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
            {privacyRows.map((item) => (
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
              <SaveButton onClick={onSavePrivacy} isLoading={isUpdatingSettings} />
            </div>
          </div>
        </CardContent>
      </Card>

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
              {visibleSessions.map((session) => (
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
                      {tSessions("lastActivity")}: {formatSessionDate(session.last_activity, fr)}
                    </p>
                  </div>
                  {!session.is_current &&
                    (sessionToRevoke === session.id ? (
                      <div className="flex gap-2 shrink-0 mt-3 sm:mt-0">
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={onConfirmRevokeSession}
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
                        onClick={() => onRevokeSession(session.id)}
                        className="shrink-0 mt-3 sm:mt-0"
                      >
                        {tSessions("revoke")}
                      </Button>
                    ))}
                </div>
              ))}
              {sessions.length > sessionsPageSize && (
                <div className="flex justify-center pt-4">
                  {visibleSessionCount < sessions.length ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() =>
                        setVisibleSessionCount((n) =>
                          Math.min(n + sessionsPageSize, sessions.length)
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
                      onClick={() => setVisibleSessionCount(sessionsPageSize)}
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
  );
}
