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

  // Variantes d'animation pour les transitions de page
  const variants = createVariants({
    initial: { opacity: 0, y: 10 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -10 },
  });

  const transition = createTransition({ duration: 0.2 });

  // Timeout de sécurité : forcer l'opacité à 1 si les animations ne se déclenchent pas (bug aléatoire)
  // Exécuter à 400ms, 800ms et 1200ms pour couvrir le chargement asynchrone (Suspense) et les délais d'animation
  useEffect(() => {
    if (shouldReduceMotion) return;

    const forceVisibility = () => {
      if (containerRef.current) {
        containerRef.current.style.opacity = '1';
      }
      const animatedElements = document.querySelectorAll('.animate-fade-in-up, .animate-fade-in-up-delay-1, .animate-fade-in-up-delay-2, .animate-fade-in-up-delay-3');
      animatedElements.forEach((el) => {
        (el as HTMLElement).style.opacity = '1';
      });
    };

    const t1 = setTimeout(forceVisibility, 400);
    const t2 = setTimeout(forceVisibility, 800);
    const t3 = setTimeout(forceVisibility, 1200);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
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
        onAnimationComplete={() => {
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

