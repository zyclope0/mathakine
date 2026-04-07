"use client";

import Link from "next/link";
import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { HeaderNavPrimaryItem, HeaderNavSecondaryItem } from "@/lib/layout/headerNavigation";

export interface HeaderDesktopNavProps {
  navPrimary: HeaderNavPrimaryItem[];
  navSecondary: HeaderNavSecondaryItem[];
  isActive: (href: string) => boolean;
  /** When false, hide header CTA (guests use global FAB only). */
  showAssistantCta?: boolean;
  ctaAssistantLabel: string;
  onOpenAssistant: () => void;
}

export function HeaderDesktopNav({
  navPrimary,
  navSecondary,
  isActive,
  showAssistantCta = true,
  ctaAssistantLabel,
  onOpenAssistant,
}: HeaderDesktopNavProps) {
  return (
    <div className="hidden md:flex md:items-center md:space-x-1">
      {navPrimary.map((item) => {
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "px-3 py-2 text-sm font-medium rounded-md transition-colors",
              isActive(item.href)
                ? "bg-primary/10 text-primary"
                : "text-foreground/80 hover:text-foreground hover:bg-accent/10"
            )}
            aria-current={isActive(item.href) ? "page" : undefined}
          >
            <span className="flex items-center gap-2">
              {Icon !== undefined ? <Icon className="h-4 w-4" aria-hidden="true" /> : null}
              {item.name}
            </span>
          </Link>
        );
      })}

      {navSecondary.length > 0 ? (
        <span className="mx-1 h-4 w-px bg-border" aria-hidden="true" />
      ) : null}

      {navSecondary.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={cn(
            "px-3 py-2 text-sm rounded-md transition-colors",
            isActive(item.href)
              ? "bg-primary/10 text-primary font-medium"
              : "text-muted-foreground hover:text-foreground hover:bg-accent/10"
          )}
          aria-current={isActive(item.href) ? "page" : undefined}
        >
          {item.name}
        </Link>
      ))}

      {showAssistantCta ? (
        <>
          <span className="mx-1 h-4 w-px bg-border" aria-hidden="true" />

          <Button
            variant="outline"
            size="sm"
            className="gap-2 border-primary/30 bg-primary/5 hover:bg-primary/10 hover:border-primary/50 text-foreground font-medium"
            onClick={onOpenAssistant}
            aria-haspopup="dialog"
            aria-label={ctaAssistantLabel}
          >
            <MessageCircle className="h-4 w-4" aria-hidden="true" />
            {ctaAssistantLabel}
          </Button>
        </>
      ) : null}
    </div>
  );
}
