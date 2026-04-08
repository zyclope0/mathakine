"use client";

import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { UserSession } from "@/hooks/useSettings";

export interface SettingsSessionRowProps {
  session: UserSession;
  sessionToRevoke: number | null;
  setSessionToRevoke: (id: number | null) => void;
  onRevokeSession: (sessionId: number) => void;
  onConfirmRevokeSession: () => void;
  isRevokingSession: boolean;
  deviceFallbackLabel: string;
  locationLine: string;
  lastActivityLabel: string;
  revokeLabel: string;
  cancelLabel: string;
}

export function SettingsSessionRow({
  session,
  sessionToRevoke,
  setSessionToRevoke,
  onRevokeSession,
  onConfirmRevokeSession,
  isRevokingSession,
  deviceFallbackLabel,
  locationLine,
  lastActivityLabel,
  revokeLabel,
  cancelLabel,
}: SettingsSessionRowProps) {
  const deviceTitle = session.device_info?.device || deviceFallbackLabel;

  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
      <div className="flex flex-col gap-1 pr-4">
        <p className="text-sm font-medium text-foreground">{deviceTitle}</p>
        <p className="text-xs text-muted-foreground">
          {locationLine}
          {" · "}
          {lastActivityLabel}
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
              {isRevokingSession ? <Loader2 className="h-3 w-3 animate-spin" /> : revokeLabel}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSessionToRevoke(null)}
              disabled={isRevokingSession}
            >
              {cancelLabel}
            </Button>
          </div>
        ) : (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onRevokeSession(session.id)}
            className="shrink-0 mt-3 sm:mt-0"
          >
            {revokeLabel}
          </Button>
        ))}
    </div>
  );
}
