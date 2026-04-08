"use client";

/**
 * Privacy card + active sessions (security tab).
 * Order preserved: confidentiality first, then sessions.
 * FFI-L13 lot B; sessions split FFI-L20E.
 */

import { useMemo, type Dispatch, type SetStateAction } from "react";
import { useTranslations } from "next-intl";
import { Shield } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { SaveButton } from "@/components/settings/SaveButton";
import type { UserSession } from "@/hooks/useSettings";
import type { PrivacySettingsState } from "@/lib/settings/settingsPage";
import { buildPrivacyToggleRows, type PrivacyToggleLabels } from "@/lib/settings/settingsSecurity";
import { SettingsSessionsList } from "@/components/settings/SettingsSessionsList";

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

  const privacyLabels: PrivacyToggleLabels = useMemo(
    () => ({
      is_public_profile: {
        label: tPrivacy("publicProfile"),
        desc: tPrivacy("publicProfileDescription"),
      },
      allow_friend_requests: {
        label: tPrivacy("friendRequests"),
        desc: tPrivacy("friendRequestsDescription"),
      },
      show_in_leaderboards: {
        label: tPrivacy("leaderboards"),
        desc: tPrivacy("leaderboardsDescription"),
      },
      data_retention_consent: {
        label: tPrivacy("dataRetention"),
        desc: tPrivacy("dataRetentionDescription"),
      },
      marketing_consent: {
        label: tPrivacy("marketing"),
        desc: tPrivacy("marketingDescription"),
      },
    }),
    [tPrivacy]
  );

  const privacyRows = useMemo(
    () => buildPrivacyToggleRows(privacySettings, privacyLabels),
    [privacySettings, privacyLabels]
  );

  return (
    <div className="space-y-8">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
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
                  <p id={`${item.id}-description`} className="text-xs text-muted-foreground">
                    {item.desc}
                  </p>
                </div>
                <Switch
                  id={item.id}
                  checked={item.checked}
                  aria-describedby={`${item.id}-description`}
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

      <SettingsSessionsList
        sessions={sessions}
        visibleSessions={visibleSessions}
        isLoadingSessions={isLoadingSessions}
        sessionToRevoke={sessionToRevoke}
        setSessionToRevoke={setSessionToRevoke}
        onRevokeSession={onRevokeSession}
        onConfirmRevokeSession={onConfirmRevokeSession}
        visibleSessionCount={visibleSessionCount}
        setVisibleSessionCount={setVisibleSessionCount}
        sessionsPageSize={sessionsPageSize}
        isRevokingSession={isRevokingSession}
      />
    </div>
  );
}
