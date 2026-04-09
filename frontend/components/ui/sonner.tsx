"use client";

import { useEffect, useState } from "react";
import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react";
import { Toaster as Sonner, type ToasterProps } from "sonner";
import { readStoredDarkMode } from "@/lib/theme/themeDom";

const Toaster = ({ ...props }: ToasterProps) => {
  // Sync with actual .dark class on <html> instead of guessing from theme name.
  // This correctly handles all theme x dark-mode combinations.
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof document === "undefined") return false;
    return document.documentElement.classList.contains("dark");
  });

  useEffect(() => {
    const root = document.documentElement;

    // Initial sync after hydration - deferred to avoid SSR mismatch
    const initial = root.classList.contains("dark") || readStoredDarkMode();
    if (initial !== isDark) {
      // Intentional setState in effect - post-hydration DOM sync, runs once
      setIsDark(initial);
    }

    const observer = new MutationObserver(() => {
      setIsDark(root.classList.contains("dark"));
    });
    observer.observe(root, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
    // Register once; MutationObserver handles subsequent theme class changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sonnerTheme: ToasterProps["theme"] = isDark ? "dark" : "light";

  return (
    <Sonner
      theme={sonnerTheme}
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
          "--border-radius": "var(--radius)",
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
