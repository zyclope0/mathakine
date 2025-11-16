'use client';

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
  Sparkles
} from 'lucide-react';
import { PageLayout } from '@/components/layout';
import { useTranslations } from 'next-intl';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
import { cn } from '@/lib/utils/cn';
import dynamic from 'next/dynamic';

// Types TypeScript pour meilleure maintenabilité
interface Feature {
  icon: React.ComponentType<{ className?: string }>;
  titleKey: string;
  descriptionKey: string;
}

interface Step {
  number: string;
  titleKey: string;
  descriptionKey: string;
}

// Lazy loading du Chatbot pour optimiser les performances
const ChatbotLazy = dynamic(
  () => import('@/components/home/Chatbot').then(mod => ({ default: mod.Chatbot })),
  {
    loading: () => (
      <div className="h-[500px] flex items-center justify-center text-muted-foreground">
        Chargement de l'assistant...
      </div>
    ),
    ssr: false, // Chatbot nécessite du JS côté client
  }
);

/**
 * Page d'accueil Mathakine
 * 
 * Design sobre et accueillant avec :
 * - Hero section avec CTA
 * - Section "Comment ça marche" (3 étapes)
 * - Section fonctionnalités clés
 * - Chatbot intégré (lazy loaded)
 */
export default function HomePage() {
  const { isAuthenticated } = useAuth();
  const t = useTranslations('home');
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Features avec références aux clés de traduction
  const features: Feature[] = [
    {
      icon: BookOpen,
      titleKey: 'features.feature1.title',
      descriptionKey: 'features.feature1.description',
    },
    {
      icon: Zap,
      titleKey: 'features.feature2.title',
      descriptionKey: 'features.feature2.description',
    },
    {
      icon: Trophy,
      titleKey: 'features.feature3.title',
      descriptionKey: 'features.feature3.description',
    },
    {
      icon: Users,
      titleKey: 'features.feature4.title',
      descriptionKey: 'features.feature4.description',
    },
  ];

  // Steps avec références aux clés de traduction
  const steps: Step[] = [
    {
      number: '1',
      titleKey: 'howItWorks.step1.title',
      descriptionKey: 'howItWorks.step1.description',
    },
    {
      number: '2',
      titleKey: 'howItWorks.step2.title',
      descriptionKey: 'howItWorks.step2.description',
    },
    {
      number: '3',
      titleKey: 'howItWorks.step3.title',
      descriptionKey: 'howItWorks.step3.description',
    },
  ];

  return (
    <PageLayout>
      {/* Hero Section - Optimisé pour réduire scrolling */}
      <section 
        className="text-center py-8 md:py-12 lg:py-16 space-y-4 md:space-y-5"
        aria-labelledby="hero-title"
      >
        <div className="space-y-3 md:space-y-4">
          <h1 
            id="hero-title"
            className={cn(
              "text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent",
              !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4"
            )}
          >
            {t('hero.title')}
          </h1>
          <p 
            className={cn(
              "text-lg md:text-xl lg:text-2xl text-muted-foreground max-w-2xl mx-auto px-4",
              !shouldReduceMotion && "animate-in fade-in slide-in-from-bottom-4 animation-delay-200"
            )}
          >
            {t('hero.subtitle')}
          </p>
          <div 
            className={cn(
              "flex flex-col sm:flex-row gap-3 md:gap-4 justify-center items-center pt-2 md:pt-3",
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
          </div>
        </div>
      </section>

      {/* Section "Comment ça marche" - Optimisé */}
      <section 
        className="py-8 md:py-12 lg:py-16 space-y-6 md:space-y-8"
        aria-labelledby="how-it-works-title"
      >
        <div className="text-center space-y-2">
          <h2 id="how-it-works-title" className="text-2xl sm:text-3xl md:text-4xl font-bold">
            {t('howItWorks.title')}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto px-4 text-sm md:text-base">
            {t('howItWorks.description')}
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-4 md:gap-6">
          {steps.map((step) => (
            <Card key={step.number} className="relative overflow-hidden py-4 md:py-5">
              <div className="flex items-start gap-3 px-6">
                <div className="flex h-8 w-8 md:h-9 md:w-9 items-center justify-center rounded-full bg-primary/10 text-primary text-sm md:text-base font-bold shrink-0 mt-0.5" aria-hidden="true">
                  {step.number}
                </div>
                <div className="flex-1 min-w-0 space-y-1">
                  <h3 className="text-base md:text-lg font-semibold leading-tight">
                    {t(step.titleKey as any)}
                  </h3>
                  <p className="text-xs md:text-sm text-muted-foreground leading-snug">
                    {t(step.descriptionKey as any)}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </section>

      {/* Chatbot Mathématique - Optimisé (Lazy loaded) */}
      <section 
        className="py-8 md:py-12 lg:py-16"
        aria-labelledby="chatbot-title"
      >
        <ChatbotLazy />
      </section>

      {/* Section Fonctionnalités - Optimisé */}
      <section 
        className="py-8 md:py-12 lg:py-16 space-y-6 md:space-y-8"
        aria-labelledby="features-title"
      >
        <div className="text-center space-y-2">
          <h2 id="features-title" className="text-2xl sm:text-3xl md:text-4xl font-bold">
            {t('features.title')}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto px-4 text-sm md:text-base">
            {t('features.description')}
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.titleKey} className="text-center">
                <CardHeader className="pb-3 md:pb-4">
                  <div className="mx-auto mb-3 md:mb-4 flex h-10 w-10 md:h-12 md:w-12 items-center justify-center rounded-full bg-primary/10">
                    <Icon className="h-5 w-5 md:h-6 md:w-6 text-primary" aria-hidden="true" />
                  </div>
                  <CardTitle className="text-base md:text-lg">
                    {t(feature.titleKey as any)}
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <CardDescription className="text-sm md:text-base">
                    {t(feature.descriptionKey as any)}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Section CTA Final - Optimisé */}
      {!isAuthenticated && (
        <section 
          className="py-8 md:py-12 lg:py-16 text-center"
          aria-labelledby="cta-title"
        >
          <Card className="bg-gradient-to-r from-primary/10 via-accent/10 to-primary/10 border-primary/20">
            <CardHeader className="space-y-3 md:space-y-4">
              <div className="mx-auto flex h-12 w-12 md:h-16 md:w-16 items-center justify-center rounded-full bg-primary/20">
                <Sparkles className="h-6 w-6 md:h-8 md:w-8 text-primary" aria-hidden="true" />
              </div>
              <CardTitle id="cta-title" className="text-2xl md:text-3xl">
                {t('cta.title')}
              </CardTitle>
              <CardDescription className="text-base md:text-lg px-4">
                {t('cta.description')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button asChild size="lg">
                <Link href="/register">
                  {t('cta.button')}
                  <ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
                </Link>
              </Button>
            </CardContent>
          </Card>
        </section>
      )}

    </PageLayout>
  );
}
