"use client";

import type { Dispatch, SetStateAction } from "react";
import { useTranslations } from "next-intl";
import { Monitor, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { UserSession } from "@/hooks/useSettings";
import { formatSessionDate } from "@/lib/settings/settingsPage";
import {
  computeVisibleCountAfterShowMore,
  resolveSessionLocationDisplay,
} from "@/lib/settings/settingsSecurity";
import { fr } from "date-fns/locale";
import { SettingsSessionRow } from "@/components/settings/SettingsSessionRow";

export interface SettingsSessionsListProps {
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

export function SettingsSessionsList({
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
}: SettingsSessionsListProps) {
  const tSessions = useTranslations("settings.sessions");
  const tActions = useTranslations("settings.actions");
  const tCommon = useTranslations("common");

  return (
    <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
      <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Monitor className="h-5 w-5 text-primary" aria-hidden="true" />
          {tSessions("title")}
        </CardTitle>
        <CardDescription className="mt-1">{tSessions("description")}</CardDescription>
      </CardHeader>
      <CardContent className="p-0">
        {isLoadingSessions ? (
          <div
            className="flex flex-col items-center justify-center gap-2 py-8"
            role="status"
            aria-live="polite"
            aria-busy="true"
          >
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" aria-hidden="true" />
            <span className="sr-only">{tCommon("loading")}</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground" role="status">
            <p>{tSessions("noSessions")}</p>
          </div>
        ) : (
          <div className="flex flex-col">
            {visibleSessions.map((session) => (
              <SettingsSessionRow
                key={session.id}
                session={session}
                sessionToRevoke={sessionToRevoke}
                setSessionToRevoke={setSessionToRevoke}
                onRevokeSession={onRevokeSession}
                onConfirmRevokeSession={onConfirmRevokeSession}
                isRevokingSession={isRevokingSession}
                deviceFallbackLabel={tSessions("device")}
                locationLine={resolveSessionLocationDisplay(session, tSessions("location"))}
                lastActivityLabel={`${tSessions("lastActivity")}: ${formatSessionDate(session.last_activity, fr)}`}
                revokeLabel={tSessions("revoke")}
                cancelLabel={tActions("cancel")}
              />
            ))}
            {sessions.length > sessionsPageSize && (
              <div className="flex justify-center pt-4">
                {visibleSessionCount < sessions.length ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      setVisibleSessionCount((n) =>
                        computeVisibleCountAfterShowMore(n, sessionsPageSize, sessions.length)
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
  );
}
