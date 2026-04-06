"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User, Save, X, Loader2, Pencil } from "lucide-react";
import { useTranslations } from "next-intl";
import type { PersonalInfoState } from "@/hooks/useProfilePageController";

interface ProfilePersonalInfoSectionProps {
  user: {
    username?: string | null;
    email?: string | null;
    full_name?: string | null;
    role?: string | null;
    created_at?: string | null;
  };
  isEditing: boolean;
  personalInfo: PersonalInfoState;
  errors: Record<string, string>;
  isUpdatingProfile: boolean;
  formatDate: (d: string | null | undefined) => string;
  onStartEditing: () => void;
  onPersonalInfoChange: (field: keyof PersonalInfoState, value: string) => void;
  onEmailBlur: () => void;
  onClearFieldError: (field: string) => void;
  onSave: () => void;
  onCancel: () => void;
}

/**
 * Section informations personnelles (lecture + édition).
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfilePersonalInfoSection({
  user,
  isEditing,
  personalInfo,
  errors,
  isUpdatingProfile,
  formatDate,
  onStartEditing,
  onPersonalInfoChange,
  onEmailBlur,
  onClearFieldError,
  onSave,
  onCancel,
}: ProfilePersonalInfoSectionProps) {
  const tPersonal = useTranslations("profile.personalInfo");
  const tActions = useTranslations("profile.actions");

  return (
    <div className="animate-fade-in-up">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-xl">
              <User className="h-5 w-5 text-primary" />
              {tPersonal("title")}
            </CardTitle>
            {!isEditing && (
              <Button
                variant="outline"
                size="sm"
                onClick={onStartEditing}
                aria-label={tActions("edit")}
                className="inline-flex items-center gap-2 border-border hover:bg-accent hover:text-accent-foreground rounded-lg h-9 px-3"
              >
                <Pencil className="h-3.5 w-3.5" />
                {tActions("edit")}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-0">
          {isEditing ? (
            <div className="flex flex-col">
              {/* Username (non modifiable) */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="username" className="text-sm font-medium text-foreground">
                    {tPersonal("username")}
                  </Label>
                  <p id="username-description" className="text-xs text-muted-foreground">
                    {tPersonal("usernameDescription")}
                  </p>
                </div>
                <Input
                  id="username"
                  value={user.username ?? ""}
                  disabled
                  aria-label={tPersonal("username")}
                  aria-describedby="username-description"
                  className="bg-muted/30 border-border/50 w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                />
              </div>

              {/* Email */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="email" className="text-sm font-medium text-foreground">
                    {tPersonal("email")} *
                  </Label>
                </div>
                <div className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
                  <Input
                    id="email"
                    type="email"
                    value={personalInfo.email}
                    onChange={(e) => {
                      onPersonalInfoChange("email", e.target.value);
                      if (errors.email) onClearFieldError("email");
                    }}
                    onBlur={onEmailBlur}
                    placeholder={tPersonal("emailPlaceholder")}
                    aria-invalid={!!errors.email}
                    aria-describedby={errors.email ? "email-error" : undefined}
                    disabled={isUpdatingProfile}
                  />
                  {errors.email && (
                    <p
                      id="email-error"
                      className="text-sm text-destructive mt-1"
                      role="alert"
                      aria-live="polite"
                    >
                      {errors.email}
                    </p>
                  )}
                </div>
              </div>

              {/* Full name */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
                <div className="flex flex-col gap-1 pr-4">
                  <Label htmlFor="full_name" className="text-sm font-medium text-foreground">
                    {tPersonal("fullName")}
                  </Label>
                </div>
                <Input
                  id="full_name"
                  type="text"
                  value={personalInfo.full_name}
                  onChange={(e) => onPersonalInfoChange("full_name", e.target.value)}
                  placeholder={tPersonal("fullNamePlaceholder")}
                  disabled={isUpdatingProfile}
                  className="w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2 justify-end pt-6">
                <Button
                  variant="outline"
                  onClick={onCancel}
                  disabled={isUpdatingProfile}
                  aria-label={tActions("cancel")}
                >
                  <X className="mr-2 h-4 w-4" />
                  {tActions("cancel")}
                </Button>
                <Button
                  onClick={onSave}
                  disabled={isUpdatingProfile}
                  aria-label={tActions("save")}
                  aria-busy={isUpdatingProfile}
                >
                  {isUpdatingProfile ? (
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
            </div>
          ) : (
            <div className="flex flex-col">
              {(
                [
                  { label: tPersonal("username"), value: user.username },
                  { label: tPersonal("email"), value: user.email },
                  { label: tPersonal("fullName"), value: user.full_name },
                  { label: tPersonal("role"), value: user.role, capitalize: true },
                  { label: tPersonal("memberSince"), value: formatDate(user.created_at) },
                ] as const
              ).map((row, i) => (
                <div
                  key={i}
                  className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0"
                >
                  <div className="flex flex-col gap-1 pr-4">
                    <p className="text-sm font-medium text-foreground">{row.label}</p>
                  </div>
                  <p
                    className={`text-base font-medium text-foreground sm:text-right mt-3 sm:mt-0 shrink-0${
                      "capitalize" in row && row.capitalize ? " capitalize" : ""
                    }`}
                  >
                    {row.value || "-"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
