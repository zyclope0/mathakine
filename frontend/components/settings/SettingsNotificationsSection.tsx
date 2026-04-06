"use client";

/**
 * Notification toggles + save.
 * FFI-L13 lot B.
 */

import { useTranslations } from "next-intl";
import { Bell } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { SaveButton } from "@/components/settings/SaveButton";
import type { NotificationSettingsState } from "@/lib/settings/settingsPage";
import type { Dispatch, SetStateAction } from "react";

export interface SettingsNotificationsSectionProps {
  notificationSettings: NotificationSettingsState;
  setNotificationSettings: Dispatch<SetStateAction<NotificationSettingsState>>;
  onSaveNotifications: () => void;
  isUpdatingSettings: boolean;
}

export function SettingsNotificationsSection({
  notificationSettings,
  setNotificationSettings,
  onSaveNotifications,
  isUpdatingSettings,
}: SettingsNotificationsSectionProps) {
  const tNotifications = useTranslations("settings.notifications");

  return (
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
              <Label htmlFor="notifications-news" className="text-sm font-medium text-foreground">
                {tNotifications("news")}
              </Label>
              <p className="text-xs text-muted-foreground">{tNotifications("newsDescription")}</p>
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
            <SaveButton onClick={onSaveNotifications} isLoading={isUpdatingSettings} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
