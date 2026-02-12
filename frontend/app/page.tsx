'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { 
  BookOpen, 
  Zap, 
  Trophy, 
  Users, 
  ArrowRight,
  MessageCircle,
} from 'lucide-react';
import { PageLayout } from '@/components/layout';
import { useTranslations } from 'next-intl';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
import { cn } from '@/lib/utils/cn';
import dynamic from 'next/dynamic';

// Lazy loading des composants non-critiques
const AcademyStatsWidgetLazy = dynamic(
  () => import('@/components/home/AcademyStatsWidget').then(mod => ({ default: mod.AcademyStatsWidget })),
  { loading: () => null, ssr: false }
);

const ChatbotFloatingLazy = dynamic(
  () => import('@/components/home/ChatbotFloating').then(mod => ({ default: mod.ChatbotFloating })),
  { loading: () => null, ssr: false }
);

// Types
interface Feature {
  icon: React.ComponentType<{ className?: string }>;
  titleKey: string;
  descriptionKey: string;
}

/**
 * Page d'accueil Mathakine - Version optimisée
 */
export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const t = useTranslations('home');
  const tNav = useTranslations('navigation');
  const { shouldReduceMotion } = useAccessibleAnimation();
  const [isChatOpen, setIsChatOpen] = useState(false);

  const features: Feature[] = [
    { icon: BookOpen, titleKey: 'features.feature1.title', descriptionKey: 'features.feature1.description' },
    { icon: Zap, titleKey: 'features.feature2.title', descriptionKey: 'features.feature2.description' },
    { icon: Trophy, titleKey: 'features.feature3.title', descriptionKey: 'features.feature3.description' },
    { icon: Users, titleKey: 'features.feature4.title', descriptionKey: 'features.feature4.description' },
  ];

  return (
    <PageLayout>
      {/* Hero Section */}
      <section className="text-center py-8 md:py-12 space-y-4" aria-labelledby="hero-title">
        <h1 
          id="hero-title"
          className={cn(
            "text-4xl sm:text-5xl md:text-6xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
          )}
        >
          {t('hero.title')}
        </h1>
        <p 
          className={cn(
            "text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-200"
          )}
        >
          {t('hero.subtitle')}
        </p>
        
        {/* Boutons principaux */}
        <div 
          className={cn(
            "flex flex-col sm:flex-row gap-3 justify-center items-center pt-2",
            !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-400"
          )}
        >
          {isAuthenticated ? (
            <>
              <Button asChild size="lg" className="w-full sm:w-auto">
                <Link href="/dashboard">
                  {t('hero.ctaDashboard')}
                  <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                <Link href="/exercises">{t('hero.ctaExercises')}</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                <Link href="/challenges">{tNav('challenges')}</Link>
              </Button>
            </>
          ) : (
            <>
              <Button asChild size="lg" className="w-full sm:w-auto">
                <Link href="/register">
                  {t('hero.ctaStart')}
                  <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                <Link href="/login">{t('hero.ctaLogin')}</Link>
              </Button>
            </>
          )}
          
          {/* Bouton Assistant - Toujours visible */}
          <Button 
            variant="secondary" 
            size="lg" 
            className="w-full sm:w-auto gap-2"
            onClick={() => setIsChatOpen(true)}
            aria-expanded={isChatOpen}
            aria-haspopup="dialog"
          >
            <MessageCircle className="h-4 w-4" aria-hidden="true" />
            {t('hero.ctaAssistant')}
          </Button>
        </div>
      </section>

      {/* Stats de l'Académie */}
      <section className="py-4" aria-label="Statistiques de l'Académie">
        <AcademyStatsWidgetLazy />
      </section>

      {/* Fonctionnalités */}
      <section className="py-8 md:py-12 space-y-4" aria-labelledby="features-title">
        <div className="text-center space-y-2">
          <h2 id="features-title" className="text-2xl md:text-3xl font-bold">
            {t('features.title')}
          </h2>
          <p className="text-muted-foreground max-w-xl mx-auto text-sm">
            {t('features.description')}
          </p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.titleKey} className="text-center py-4">
                <CardHeader className="pb-2 pt-0 px-3">
                  <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
                  </div>
                  <CardTitle className="text-sm md:text-base">
                    {t(feature.titleKey as any)}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0 px-3">
                  <CardDescription className="text-xs md:text-sm">
                    {t(feature.descriptionKey as any)}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Chatbot Flottant */}
      <ChatbotFloatingLazy 
        isOpen={isChatOpen} 
        onOpenChange={setIsChatOpen} 
      />
    </PageLayout>
  );
}
