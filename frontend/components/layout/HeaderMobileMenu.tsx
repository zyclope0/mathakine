"use client";

import Link from "next/link";
import type { Transition } from "framer-motion";
import { AnimatePresence, LazyMotion, domAnimation, m } from "framer-motion";
import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeSelectorCompact } from "@/components/theme/ThemeSelectorCompact";
import { cn } from "@/lib/utils";
import type { HeaderNavPrimaryItem, HeaderNavSecondaryItem } from "@/lib/layout/headerNavigation";

export interface HeaderMobileMenuProps {
  open: boolean;
  navPrimary: HeaderNavPrimaryItem[];
  navSecondary: HeaderNavSecondaryItem[];
  isActive: (href: string) => boolean;
  onNavigate: () => void;
  shouldReduceMotion: boolean;
  createTransition: (opts: { duration: number; delay?: number }) => Transition;
  showAssistantCta?: boolean;
  ctaAssistantLabel: string;
  onOpenAssistant: () => void;
}

export function HeaderMobileMenu({
  open,
  navPrimary,
  navSecondary,
  isActive,
  onNavigate,
  shouldReduceMotion,
  createTransition,
  showAssistantCta = true,
  ctaAssistantLabel,
  onOpenAssistant,
}: HeaderMobileMenuProps) {
  return (
    <LazyMotion features={domAnimation}>
      <AnimatePresence>
        {open ? (
          <m.div
            id="mobile-nav-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-border overflow-hidden"
            role="menu"
          >
            <div className="space-y-1 py-4">
              {navPrimary.map((item, index) => {
                const Icon = item.icon;
                const transition = createTransition({ duration: 0.15, delay: index * 0.05 });
                return (
                  <m.div
                    key={item.href}
                    initial={!shouldReduceMotion ? { opacity: 0, x: -10 } : false}
                    animate={!shouldReduceMotion ? { opacity: 1, x: 0 } : false}
                    transition={transition}
                  >
                    <Link
                      href={item.href}
                      onClick={onNavigate}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-md transition-colors",
                        isActive(item.href)
                          ? "bg-primary/10 text-primary"
                          : "text-foreground/80 hover:text-foreground hover:bg-accent/10"
                      )}
                      role="menuitem"
                      aria-current={isActive(item.href) ? "page" : undefined}
                    >
                      {Icon !== undefined ? <Icon className="h-4 w-4" aria-hidden="true" /> : null}
                      {item.name}
                    </Link>
                  </m.div>
                );
              })}

              {navSecondary.length > 0 ? (
                <div className="my-1 border-t border-border/60" role="separator" />
              ) : null}

              {navSecondary.map((item, index) => {
                const transition = createTransition({
                  duration: 0.15,
                  delay: (navPrimary.length + index) * 0.05,
                });
                return (
                  <m.div
                    key={item.href}
                    initial={!shouldReduceMotion ? { opacity: 0, x: -10 } : false}
                    animate={!shouldReduceMotion ? { opacity: 1, x: 0 } : false}
                    transition={transition}
                  >
                    <Link
                      href={item.href}
                      onClick={onNavigate}
                      className={cn(
                        "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors",
                        isActive(item.href)
                          ? "bg-primary/10 text-primary font-medium"
                          : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
                      )}
                      role="menuitem"
                      aria-current={isActive(item.href) ? "page" : undefined}
                    >
                      {item.name}
                    </Link>
                  </m.div>
                );
              })}

              {showAssistantCta ? (
                <m.div
                  initial={!shouldReduceMotion ? { opacity: 0, x: -10 } : false}
                  animate={!shouldReduceMotion ? { opacity: 1, x: 0 } : false}
                  transition={createTransition({
                    duration: 0.15,
                    delay: (navPrimary.length + navSecondary.length) * 0.05,
                  })}
                >
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10 mt-1"
                    onClick={() => {
                      onOpenAssistant();
                      onNavigate();
                    }}
                    aria-haspopup="dialog"
                    role="menuitem"
                  >
                    <MessageCircle className="h-4 w-4" aria-hidden="true" />
                    {ctaAssistantLabel}
                  </Button>
                </m.div>
              ) : null}
              <m.div
                initial={!shouldReduceMotion ? { opacity: 0 } : false}
                animate={!shouldReduceMotion ? { opacity: 1 } : false}
                transition={createTransition({
                  duration: 0.15,
                  delay:
                    (navPrimary.length + navSecondary.length + (showAssistantCta ? 1 : 0)) * 0.05,
                })}
                className="pt-2 border-t border-border"
              >
                <ThemeSelectorCompact />
              </m.div>
            </div>
          </m.div>
        ) : null}
      </AnimatePresence>
    </LazyMotion>
  );
}
