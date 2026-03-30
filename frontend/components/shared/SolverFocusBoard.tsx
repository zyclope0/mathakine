"use client";

import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/** Glass shell for exercise vs challenge solvers — class strings frozen per domain (FFI-L8 seam for L9/L10). */
const VARIANT_ROOT: Record<"exercise" | "challenge", string> = {
  exercise:
    "bg-card/90 backdrop-blur-xl border border-border shadow-[0_0_40px_rgba(0,0,0,0.15)] rounded-3xl p-8 md:p-12 w-full max-w-4xl mx-auto mt-8 md:mt-12",
  challenge:
    "bg-card/90 backdrop-blur-xl border border-border shadow-2xl rounded-t-3xl p-6 md:p-10 w-full max-w-5xl mx-auto mt-6",
};

export function SolverFocusBoard({
  variant,
  children,
  className,
}: {
  variant: "exercise" | "challenge";
  children: ReactNode;
  className?: string;
}) {
  return <div className={cn(VARIANT_ROOT[variant], className)}>{children}</div>;
}
