'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle2, XCircle, Mail, AlertCircle } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { api } from '@/lib/api/client';

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const t = useTranslations('auth.verifyEmail');
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired' | 'resend'>('loading');
  const [message, setMessage] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [resendLoading, setResendLoading] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('resend');
      return;
    }

    verifyToken(token);
  }, [searchParams]);

  const verifyToken = async (token: string) => {
    try {
      interface VerifyEmailResponse {
        success?: boolean;
        message?: string;
        error?: string;
        user?: {
          id: number;
          username: string;
          email: string;
          is_email_verified: boolean;
        };
      }
      
      const response = await api.get<VerifyEmailResponse>(`/api/auth/verify-email?token=${token}`);
      
      if (response && response.success) {
        setStatus('success');
        setMessage(response.message || t('success'));
        if (response.user) {
          setEmail(response.user.email);
        }
      } else {
        setStatus('error');
        setMessage(response?.error || t('error'));
      }
    } catch (error: any) {
      const errorMessage = error?.message || error?.error || t('error');
      
      if (errorMessage.includes('expiré') || errorMessage.includes('expired')) {
        setStatus('expired');
        setMessage(errorMessage);
      } else {
        setStatus('error');
        setMessage(errorMessage);
      }
    }
  };

  const handleResend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const emailToUse = email.trim();
    if (!emailToUse) return;

    setResendLoading(true);
    setMessage('');
    try {
      interface ResendVerificationResponse {
        message?: string;
        error?: string;
      }
      
      await api.post<ResendVerificationResponse>('/api/auth/resend-verification', { email: emailToUse });
      setMessage(t('resendSuccess'));
      setStatus('success');
    } catch (error: unknown) {
      const err = error as { message?: string };
      setMessage(err?.message || t('resendError'));
      setStatus('error');
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1 text-center">
          {status === 'loading' && (
            <>
              <Loader2 className="h-12 w-12 text-primary mx-auto animate-spin" />
              <CardTitle className="text-3xl font-bold">{t('verifying')}</CardTitle>
              <CardDescription>{t('verifyingDescription')}</CardDescription>
            </>
          )}
          
          {status === 'resend' && (
            <>
              <Mail className="h-12 w-12 text-primary mx-auto" />
              <CardTitle className="text-3xl font-bold">{t('resendTitle')}</CardTitle>
              <CardDescription>{t('resendDescription')}</CardDescription>
            </>
          )}
          
          {status === 'success' && (
            <>
              <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto" />
              <CardTitle className="text-3xl font-bold text-green-600">{t('successTitle')}</CardTitle>
              <CardDescription>{message || t('successDescription')}</CardDescription>
            </>
          )}
          
          {(status === 'error' || status === 'expired') && (
            <>
              <XCircle className="h-12 w-12 text-red-500 mx-auto" />
              <CardTitle className="text-3xl font-bold text-red-600">{t('errorTitle')}</CardTitle>
              <CardDescription>{message}</CardDescription>
            </>
          )}
        </CardHeader>
        
        <CardContent className="space-y-4">
          {status === 'success' && (
            <div className="space-y-4">
              <p className="text-center text-muted-foreground">
                {t('successMessage')}
              </p>
              <Button
                onClick={() => router.push('/login')}
                className="w-full"
              >
                {t('goToLogin')}
              </Button>
            </div>
          )}
          
          {status === 'resend' && (
            <div className="space-y-4">
              <form onSubmit={handleResend} className="space-y-4">
                <div className="space-y-2">
                  <label htmlFor="resend-email" className="text-sm font-medium">
                    {t('emailLabel')}
                  </label>
                  <input
                    id="resend-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder={t('enterEmailPlaceholder')}
                    required
                    disabled={resendLoading}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  />
                </div>
                <Button type="submit" className="w-full" disabled={resendLoading}>
                  {resendLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
                  {t('resendEmail')}
                </Button>
              </form>
              
              <div className="text-center">
                <Link href="/login" className="text-sm text-primary hover:underline">
                  {t('backToLogin')}
                </Link>
              </div>
            </div>
          )}
          
          {(status === 'error' || status === 'expired') && (
            <div className="space-y-4">
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-yellow-800 dark:text-yellow-200">
                      {status === 'expired' ? t('expiredMessage') : t('errorMessage')}
                    </p>
                  </div>
                </div>
              </div>
              
              <form onSubmit={handleResend} className="space-y-2">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={t('enterEmailPlaceholder')}
                  required
                  disabled={resendLoading}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm mb-2"
                />
                <Button type="submit" variant="outline" className="w-full" disabled={resendLoading}>
                  {resendLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
                  {t('resendEmail')}
                </Button>
              </form>
              
              <div className="text-center">
                <Link href="/login" className="text-sm text-primary hover:underline">
                  {t('backToLogin')}
                </Link>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

