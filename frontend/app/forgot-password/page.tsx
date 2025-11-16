'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Mail, Shield } from 'lucide-react';
import { AccessibilityToolbar } from '@/components/accessibility/AccessibilityToolbar';
import { useTranslations } from 'next-intl';

export default function ForgotPasswordPage() {
  const { forgotPasswordAsync, isForgotPasswordPending } = useAuth();
  const t = useTranslations('auth.forgotPassword');
  
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [emailError, setEmailError] = useState<string>('');

  const validateEmail = (emailValue: string): boolean => {
    if (!emailValue.trim()) {
      setEmailError(t('validation.emailRequired') || 'Email requis');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailValue)) {
      setEmailError(t('validation.emailInvalid') || 'Email invalide');
      return false;
    }
    setEmailError('');
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEmailError('');
    
    if (!validateEmail(email)) {
      return;
    }
    
    await forgotPasswordAsync({ email });
    setSubmitted(true);
    // Les toasts sont gérés dans useAuth
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <Shield className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-3xl font-bold">{t('title')}</CardTitle>
          <CardDescription>
            {t('description')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {submitted ? (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20" role="alert" aria-live="polite">
                <div className="flex items-start gap-3">
                  <Mail className="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5" aria-hidden="true" />
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-green-600 dark:text-green-400">
                      {t('success.title')}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {t('success.message')}
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2 text-sm text-muted-foreground">
                <p className="font-medium">{t('success.securityTips')}</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>{t('success.checkSpam')}</li>
                  <li>{t('success.linkExpires')}</li>
                  <li>{t('success.neverShare')}</li>
                </ul>
              </div>

              <Link href="/login">
                <Button variant="outline" className="w-full">
                  {t('backToLogin')}
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">{t('email')}</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (emailError) {
                        setEmailError('');
                      }
                    }}
                    onBlur={() => validateEmail(email)}
                    required
                    autoComplete="email"
                    disabled={isForgotPasswordPending}
                    placeholder={t('emailPlaceholder')}
                    aria-invalid={!!emailError}
                    aria-describedby={emailError ? 'email-error' : 'email-hint'}
                  />
                  {emailError ? (
                    <p id="email-error" className="text-sm text-destructive" role="alert" aria-live="polite">
                      {emailError}
                    </p>
                  ) : (
                    <p id="email-hint" className="text-xs text-muted-foreground">
                      {t('emailHint')}
                    </p>
                  )}
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={isForgotPasswordPending || !!emailError}
                  aria-label={isForgotPasswordPending ? t('sending') : t('submit')}
                  aria-busy={isForgotPasswordPending}
                >
                  {isForgotPasswordPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {t('sending')}
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      {t('submit')}
                    </>
                  )}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="text-sm text-muted-foreground hover:text-primary-on-dark underline"
                >
                  {t('backToLogin')}
                </Link>
              </div>
            </>
          )}
        </CardContent>
      </Card>
      
      <AccessibilityToolbar />
    </div>
  );
}

