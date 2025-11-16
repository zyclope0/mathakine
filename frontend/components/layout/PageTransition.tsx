'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
import { ReactNode, useEffect, useRef } from 'react';

interface PageTransitionProps {
  children: ReactNode;
}

export function PageTransition({ children }: PageTransitionProps) {
  const pathname = usePathname();
  const { shouldReduceMotion, createVariants, createTransition } = useAccessibleAnimation();
  const containerRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Variantes d'animation pour les transitions de page
  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -10 },
  });

  const transition = createTransition({ duration: 0.2 });

  // Timeout de sécurité : forcer l'opacité à 1 après 500ms si l'animation ne se déclenche pas
  useEffect(() => {
    if (shouldReduceMotion) return;

    // Nettoyer le timeout précédent
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Forcer la visibilité après 500ms maximum
    timeoutRef.current = setTimeout(() => {
      if (containerRef.current) {
        containerRef.current.style.opacity = '1';
      }
      // Forcer aussi toutes les animations CSS à se déclencher
      const animatedElements = document.querySelectorAll('.animate-fade-in-up, .animate-fade-in-up-delay-1, .animate-fade-in-up-delay-2, .animate-fade-in-up-delay-3');
      animatedElements.forEach((el) => {
        (el as HTMLElement).style.opacity = '1';
      });
    }, 500);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [pathname, shouldReduceMotion]);

  // Si reduced motion, pas d'animation - afficher directement avec opacité 1
  if (shouldReduceMotion) {
    return <div className="relative z-10" style={{ opacity: 1 }}>{children}</div>;
  }

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        ref={containerRef}
        key={pathname}
        variants={variants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={transition}
        className="relative z-10"
        style={{ 
          willChange: 'opacity, transform',
        }}
        onAnimationComplete={() => {
          // Nettoyer le timeout car l'animation s'est terminée
          if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
          }
          // S'assurer que le contenu est toujours visible après l'animation
          if (containerRef.current) {
            containerRef.current.style.opacity = '1';
          }
        }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

