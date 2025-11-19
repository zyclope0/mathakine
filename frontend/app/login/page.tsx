'use client';

import { useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Rocket, Sparkles } from 'lucide-react';
import { AccessibilityToolbar } from '@/components/accessibility/AccessibilityToolbar';
import { useTranslations } from 'next-intl';

function LoginForm() {
  const searchParams = useSearchParams();
  const { loginAsync, isLoggingIn } = useAuth();
  const t = useTranslations('auth.login');
  const tRegister = useTranslations('auth.register');
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const registered = searchParams.get('registered') === 'true';
  const verify = searchParams.get('verify') === 'true';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await loginAsync({ username, password });
    // La redirection et les toasts sont gérés dans useAuth
  };

  const fillDemoCredentials = () => {
    setUsername('ObiWan');
    setPassword('HelloThere123!');
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
          {registered && (
            <div className={`mb-4 p-3 rounded-lg border text-sm ${
              verify 
                ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-600 dark:text-yellow-400'
                : 'bg-green-500/10 border-green-500/20 text-green-600 dark:text-green-400'
            }`}>
              {verify ? (
                <>
                  📧 Un email de vérification a été envoyé à votre adresse. 
                  Veuillez vérifier votre boîte de réception et cliquer sur le lien pour activer votre compte.
                </>
              ) : (
                <>✅ {tRegister('successMessage')}</>
              )}
            </div>
          )}

          {/* MODE DÉMONSTRATION */}
          <div className="mb-6 p-4 rounded-lg bg-primary/10 border border-primary/20">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm">{t('demoModeTitle')}</h3>
            </div>
            <p className="text-xs text-muted-foreground mb-3">
              {t('demoDescription')}
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">{t('userLabel')}</span>
                <span className="font-mono font-medium">ObiWan</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">{t('passwordLabel')}</span>
                <span className="font-mono font-medium">HelloThere123!</span>
              </div>
            </div>
            <Button
              type="button"
              variant="outline"
              onClick={fillDemoCredentials}
              className="w-full mt-3 text-xs"
              disabled={isLoggingIn}
            >
              <Sparkles className="mr-2 h-3 w-3" />
              {t('fillAuto')}
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">{t('username')}</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                autoComplete="username"
                disabled={isLoggingIn}
                placeholder={t('usernamePlaceholder')}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">{t('password')}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                disabled={isLoggingIn}
                placeholder={t('passwordPlaceholder')}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoggingIn}
            >
              {isLoggingIn ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t('connecting')}
                </>
              ) : (
                t('submit')
              )}
            </Button>
          </form>

          <div className="mt-6 text-center space-y-2">
            <Link
              href="/forgot-password"
              className="text-sm text-muted-foreground hover:text-primary-on-dark underline"
            >
              {t('forgotPassword')}
            </Link>
            <div className="text-sm text-muted-foreground">
              {t('noAccount')}{' '}
              <Link href="/register" className="text-primary-on-dark hover:underline font-medium">
                {t('register')}
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <AccessibilityToolbar />
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}

