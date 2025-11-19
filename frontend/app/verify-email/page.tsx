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
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading');
  const [message, setMessage] = useState<string>('');
  const [email, setEmail] = useState<string>('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage(t('noToken'));
      return;
    }

    // Vérifier le token
    verifyToken(token);
  }, [searchParams]);

  const verifyToken = async (token: string) => {
    try {
      const response = await api.get(`/api/auth/verify-email?token=${token}`);
      
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

  const handleResend = async () => {
    if (!email) {
      // Demander l'email à l'utilisateur
      const userEmail = prompt(t('enterEmail'));
      if (!userEmail) return;
      setEmail(userEmail);
    }

    try {
      await api.post('/api/auth/resend-verification', { email });
      setMessage(t('resendSuccess'));
      setStatus('success');
    } catch (error: any) {
      setMessage(error?.message || t('resendError'));
      setStatus('error');
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
              
              <Button
                onClick={handleResend}
                variant="outline"
                className="w-full"
              >
                <Mail className="mr-2 h-4 w-4" />
                {t('resendEmail')}
              </Button>
              
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

