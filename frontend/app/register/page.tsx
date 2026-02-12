'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Rocket } from 'lucide-react';
import { useTranslations } from 'next-intl';

export default function RegisterPage() {
  const { registerAsync, isRegistering } = useAuth();
  const t = useTranslations('auth.register');
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (formData.username.length < 3) {
      errors.username = t('validation.usernameMinLength');
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = t('validation.emailInvalid');
    }

    // Validation mot de passe selon les règles backend (8 caractères, chiffre, majuscule)
    if (formData.password.length < 8) {
      errors.password = t('validation.passwordMinLength');
    } else if (!/\d/.test(formData.password)) {
      errors.password = t('validation.passwordRequiresDigit');
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = t('validation.passwordRequiresUppercase');
    }

    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = t('validation.passwordsMismatch');
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationErrors({});

    if (!validateForm()) {
      return;
    }

    const registerPayload: Parameters<typeof registerAsync>[0] = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
    };
    
    if (formData.full_name.trim()) {
      registerPayload.full_name = formData.full_name;
    }
    
    try {
      await registerAsync(registerPayload);
    } catch {
      // Erreur déjà affichée via toast dans useAuth (409, 500, etc.)
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Effacer l'erreur de validation pour ce champ
    if (validationErrors[field]) {
      setValidationErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          <div className="flex justify-center mb-4">
            <Rocket className="h-12 w-12 text-primary" />
          </div>
          <CardTitle className="text-3xl font-bold">{t('title')}</CardTitle>
          <CardDescription>
            {t('description')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">{t('username')} *</Label>
              <Input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => handleChange('username', e.target.value)}
                required
                autoComplete="username"
                disabled={isRegistering}
                placeholder={t('usernamePlaceholder')}
                aria-invalid={!!validationErrors.username}
                aria-describedby={validationErrors.username ? 'username-error' : undefined}
              />
              {validationErrors.username && (
                <p id="username-error" className="text-sm text-destructive" role="alert" aria-live="polite">
                  {validationErrors.username}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">{t('email')} *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                required
                autoComplete="email"
                disabled={isRegistering}
                placeholder={t('emailPlaceholder')}
                aria-invalid={!!validationErrors.email}
                aria-describedby={validationErrors.email ? 'email-error' : undefined}
              />
              {validationErrors.email && (
                <p id="email-error" className="text-sm text-destructive" role="alert" aria-live="polite">
                  {validationErrors.email}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="full_name">{t('fullName')}</Label>
              <Input
                id="full_name"
                type="text"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                autoComplete="name"
                disabled={isRegistering}
                placeholder={t('fullNamePlaceholder')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('password')} *</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                required
                autoComplete="new-password"
                disabled={isRegistering}
                placeholder={t('passwordPlaceholder')}
                minLength={8}
                aria-invalid={!!validationErrors.password}
                aria-describedby={validationErrors.password ? 'password-error' : undefined}
              />
              {validationErrors.password && (
                <p id="password-error" className="text-sm text-destructive" role="alert" aria-live="polite">
                  {validationErrors.password}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">{t('confirmPassword')} *</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                required
                autoComplete="new-password"
                disabled={isRegistering}
                placeholder={t('confirmPasswordPlaceholder')}
                aria-invalid={!!validationErrors.confirmPassword}
                aria-describedby={validationErrors.confirmPassword ? 'confirmPassword-error' : undefined}
              />
              {validationErrors.confirmPassword && (
                <p id="confirmPassword-error" className="text-sm text-destructive" role="alert" aria-live="polite">
                  {validationErrors.confirmPassword}
                </p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isRegistering}
              aria-label={isRegistering ? t('registering') : t('submit')}
              aria-busy={isRegistering}
            >
              {isRegistering ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t('registering')}
                </>
              ) : (
                t('submit')
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              {t('hasAccount')}{' '}
              <Link href="/login" className="text-primary-on-dark hover:underline font-medium">
                {t('login')}
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

