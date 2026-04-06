"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Lock, Loader2, Eye, EyeOff, X } from "lucide-react";
import { useTranslations } from "next-intl";
import type { PasswordDataState } from "@/hooks/useProfilePageController";

interface ProfileSecuritySectionProps {
  showPasswordForm: boolean;
  showCurrentPassword: boolean;
  showNewPassword: boolean;
  showConfirmPassword: boolean;
  passwordData: PasswordDataState;
  errors: Record<string, string>;
  isChangingPassword: boolean;
  onShowForm: () => void;
  onToggleCurrentPassword: () => void;
  onToggleNewPassword: () => void;
  onToggleConfirmPassword: () => void;
  onPasswordFieldChange: (field: keyof PasswordDataState, value: string) => void;
  onClearFieldError: (field: string) => void;
  onSave: () => void;
  onCancel: () => void;
}

/**
 * Section sécurité / changement de mot de passe.
 * Composant purement visuel + callbacks.
 *
 * FFI-L11.
 */
export function ProfileSecuritySection({
  showPasswordForm,
  showCurrentPassword,
  showNewPassword,
  showConfirmPassword,
  passwordData,
  errors,
  isChangingPassword,
  onShowForm,
  onToggleCurrentPassword,
  onToggleNewPassword,
  onToggleConfirmPassword,
  onPasswordFieldChange,
  onClearFieldError,
  onSave,
  onCancel,
}: ProfileSecuritySectionProps) {
  const tSecurity = useTranslations("profile.security");
  const tActions = useTranslations("profile.actions");

  return (
    <div className="animate-fade-in-up-delay-2">
      <Card className="bg-card/60 backdrop-blur-md border border-border/50 shadow-sm rounded-2xl p-6 md:p-8">
        <CardHeader className="border-b border-border/50 pb-4 mb-6 p-0 space-y-0">
          <CardTitle className="flex items-center gap-2 text-xl">
            <Lock className="h-5 w-5 text-primary" />
            {tSecurity("title")}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {!showPasswordForm ? (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
              <div className="flex flex-col gap-1 pr-4">
                <p className="text-sm font-medium text-foreground">{tSecurity("changePassword")}</p>
                <p className="text-xs text-muted-foreground">{tSecurity("description")}</p>
              </div>
              <Button
                onClick={onShowForm}
                variant="outline"
                aria-label={tSecurity("changePassword")}
                className="mt-3 sm:mt-0 shrink-0"
              >
                {tSecurity("changePassword")}
              </Button>
            </div>
          ) : (
            <div className="flex flex-col">
              {/* Mot de passe actuel */}
              <PasswordField
                id="current_password"
                label={`${tSecurity("currentPassword")} *`}
                value={passwordData.current_password}
                show={showCurrentPassword}
                error={errors.current_password}
                errorId="current-password-error"
                placeholder={tSecurity("currentPasswordPlaceholder")}
                disabled={isChangingPassword}
                onChange={(v) => {
                  onPasswordFieldChange("current_password", v);
                  if (errors.current_password) onClearFieldError("current_password");
                }}
                onToggleShow={onToggleCurrentPassword}
              />

              {/* Nouveau mot de passe */}
              <PasswordField
                id="new_password"
                label={`${tSecurity("newPassword")} *`}
                value={passwordData.new_password}
                show={showNewPassword}
                error={errors.new_password}
                errorId="new-password-error"
                placeholder={tSecurity("newPasswordPlaceholder")}
                disabled={isChangingPassword}
                onChange={(v) => {
                  onPasswordFieldChange("new_password", v);
                  if (errors.new_password) onClearFieldError("new_password");
                }}
                onToggleShow={onToggleNewPassword}
              />

              {/* Confirmation */}
              <PasswordField
                id="confirm_password"
                label={`${tSecurity("confirmPassword")} *`}
                value={passwordData.confirm_password}
                show={showConfirmPassword}
                error={errors.confirm_password}
                errorId="confirm-password-error"
                placeholder={tSecurity("confirmPasswordPlaceholder")}
                disabled={isChangingPassword}
                onChange={(v) => {
                  onPasswordFieldChange("confirm_password", v);
                  if (errors.confirm_password) onClearFieldError("confirm_password");
                }}
                onToggleShow={onToggleConfirmPassword}
              />

              {/* Actions */}
              <div className="flex gap-2 pt-6">
                <Button
                  onClick={onSave}
                  disabled={isChangingPassword}
                  aria-label={tActions("changePassword")}
                  aria-busy={isChangingPassword}
                >
                  {isChangingPassword ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {tActions("changingPassword")}
                    </>
                  ) : (
                    <>
                      <Lock className="mr-2 h-4 w-4" />
                      {tActions("changePassword")}
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={onCancel}
                  disabled={isChangingPassword}
                  aria-label={tActions("cancel")}
                >
                  <X className="mr-2 h-4 w-4" />
                  {tActions("cancel")}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ─── Sous-composant champ mot de passe ────────────────────────────────────────

interface PasswordFieldProps {
  id: string;
  label: string;
  value: string;
  show: boolean;
  error?: string | undefined;
  errorId: string;
  placeholder: string;
  disabled: boolean;
  onChange: (v: string) => void;
  onToggleShow: () => void;
}

function PasswordField({
  id,
  label,
  value,
  show,
  error,
  errorId,
  placeholder,
  disabled,
  onChange,
  onToggleShow,
}: PasswordFieldProps) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between py-4 border-b border-border/50 last:border-0">
      <div className="flex flex-col gap-1 pr-4">
        <Label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </Label>
      </div>
      <div className="relative w-full sm:w-[250px] mt-3 sm:mt-0 shrink-0">
        <Input
          id={id}
          type={show ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : undefined}
          disabled={disabled}
        />
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="absolute right-0 top-0 h-full px-3"
          onClick={onToggleShow}
          aria-label={show ? "Masquer le mot de passe" : "Afficher le mot de passe"}
        >
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </Button>
      </div>
      {error && (
        <p id={errorId} className="text-sm text-destructive" role="alert" aria-live="polite">
          {error}
        </p>
      )}
    </div>
  );
}
