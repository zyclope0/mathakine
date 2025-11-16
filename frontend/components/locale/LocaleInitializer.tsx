'use client';

import { useEffect } from 'react';
import { useLocaleStore } from '@/lib/stores/localeStore';

/**
 * Composant pour initialiser la locale au chargement
 * Détecte la langue du navigateur et applique la locale appropriée
 */
export function LocaleInitializer() {
  const { locale, setLocale } = useLocaleStore();

  useEffect(() => {
    // Initialiser la locale seulement si elle n'est pas déjà définie
    if (typeof window !== 'undefined' && !localStorage.getItem('locale-preferences')) {
      // Détecter la langue du navigateur
      const browserLang = navigator.language?.split('-')[0] || 'fr';
      const supportedLocales: ('fr' | 'en')[] = ['fr', 'en'];
      const detectedLocale: 'fr' | 'en' = supportedLocales.includes(browserLang as 'fr' | 'en') 
        ? (browserLang as 'fr' | 'en') 
        : 'fr';
      
      setLocale(detectedLocale);
    }

    // Appliquer la locale au document
    if (typeof document !== 'undefined') {
      document.documentElement.lang = locale;
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return null;
}

