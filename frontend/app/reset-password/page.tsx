"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, CheckCircle2, XCircle, Shield } from "lucide-react";
import { useTranslations } from "next-intl";
import { api } from "@/lib/api/client";

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const t = useTranslations("auth.resetPassword");

  const [token, setToken] = useState<string | null>(null);
  const [status, setStatus] = useState<"form" | "loading" | "success" | "error">("form");
  const [message, setMessage] = useState<string>("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [passwordError, setPasswordError] = useState<string>("");

  useEffect(() => {
    const tokenParam = searchParams.get("token");
    if (!tokenParam) {
      setStatus("error");
      setMessage(t("noToken"));
    } else {
      setToken(tokenParam);
    }
  }, [searchParams, t]);

  const validateForm = (): boolean => {
    if (password.length < 6) {
      setPasswordError(t("validation.passwordMinLength"));
      return false;
    }
    if (password !== passwordConfirm) {
      setPasswordError(t("validation.passwordsMismatch"));
      return false;
    }
    setPasswordError("");
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    if (!validateForm()) return;

    setStatus("loading");
    setMessage("");

    try {
      const response = await api.post<{ message?: string; success?: boolean }>(
        "/api/auth/reset-password",
        { token, password, password_confirm: passwordConfirm }
      );

      if (response?.success) {
        setStatus("success");
        setMessage(response.message || t("success"));
        setTimeout(() => router.push("/login"), 2000);
      } else {
        setStatus("error");
        setMessage(t("error"));
      }
    } catch (error: unknown) {
      const err = error as { message?: string; details?: { error?: string } };
      setStatus("error");
      setMessage(err?.message ?? err?.details?.error ?? t("error"));
    }
  };

  if (!token && status === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1 text-center">
            <XCircle className="h-12 w-12 text-red-500 mx-auto" />
            <CardTitle className="text-2xl font-bold text-red-600">{t("errorTitle")}</CardTitle>
            <CardDescription>{message}</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Link href="/forgot-password">
              <Button variant="outline">{t("requestNewLink")}</Button>
            </Link>
            <div className="mt-4">
              <Link href="/login" className="text-sm text-primary hover:underline">
                {t("backToLogin")}
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="space-y-1 text-center">
            <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto" />
            <CardTitle className="text-2xl font-bold text-green-600">{t("successTitle")}</CardTitle>
            <CardDescription>{message}</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">{t("redirecting")}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <Shield className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-3xl font-bold">{t("title")}</CardTitle>
          <CardDescription>{t("description")}</CardDescription>
        </CardHeader>
        <CardContent>
          {status === "error" && (
            <div className="mb-4 p-4 rounded-lg bg-red-500/10 border border-red-500/20">
              <p className="text-sm text-red-600 dark:text-red-400">{message}</p>
              <Link
                href="/forgot-password"
                className="text-sm text-primary hover:underline mt-2 block"
              >
                {t("requestNewLink")}
              </Link>
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">{t("password")}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (passwordError) setPasswordError("");
                }}
                required
                minLength={6}
                autoComplete="new-password"
                disabled={status === "loading"}
                placeholder={t("passwordPlaceholder")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="passwordConfirm">{t("passwordConfirm")}</Label>
              <Input
                id="passwordConfirm"
                type="password"
                value={passwordConfirm}
                onChange={(e) => {
                  setPasswordConfirm(e.target.value);
                  if (passwordError) setPasswordError("");
                }}
                required
                minLength={6}
                autoComplete="new-password"
                disabled={status === "loading"}
                placeholder={t("passwordConfirmPlaceholder")}
              />
              {passwordError && (
                <p className="text-sm text-destructive" role="alert">
                  {passwordError}
                </p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={status === "loading"}>
              {status === "loading" ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("submitting")}
                </>
              ) : (
                t("submit")
              )}
            </Button>
          </form>
          <div className="mt-6 text-center">
            <Link
              href="/login"
              className="text-sm text-muted-foreground hover:text-primary underline"
            >
              {t("backToLogin")}
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <ResetPasswordContent />
    </Suspense>
  );
}
