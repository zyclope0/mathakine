'use client';

import { useEffect } from 'react';
import React from 'react';

/**
 * Composant d'audit WCAG avec @axe-core/react
 * Uniquement actif en développement pour éviter les warnings en production
 */
export function WCAGAudit() {
  useEffect(() => {
    // Charger @axe-core uniquement en développement
    if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
      import('react-dom').then((ReactDOM) => {
        import('@axe-core/react').then((axe) => {
          // Configuration simplifiée - @axe-core active toutes les règles par défaut
          // Le délai de 1000ms évite les warnings trop fréquents
          axe.default(React, ReactDOM, 1000);
        }).catch((error) => {
          console.warn('Impossible de charger @axe-core/react:', error);
        });
      }).catch((error) => {
        console.warn('Impossible de charger react-dom:', error);
      });
    }
  }, []);

  return null;
}

