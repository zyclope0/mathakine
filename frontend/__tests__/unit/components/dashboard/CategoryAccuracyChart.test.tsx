import type { HTMLAttributes, ReactNode } from "react";

import { render, screen } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import { describe, expect, it, vi } from "vitest";

import { CategoryAccuracyChart } from "@/components/dashboard/CategoryAccuracyChart";
import en from "@/messages/en.json";
import fr from "@/messages/fr.json";

vi.mock("@/lib/hooks/useAccessibleAnimation", () => ({
  useAccessibleAnimation: () => ({
    shouldReduceMotion: true,
    createVariants: (variants: unknown) => variants,
    createTransition: (transition: unknown) => transition,
  }),
}));

vi.mock("framer-motion", () => ({
  motion: {
    div: (
      props: HTMLAttributes<HTMLDivElement> & {
        whileHover?: unknown;
        variants?: unknown;
        initial?: unknown;
        animate?: unknown;
        transition?: unknown;
      }
    ) => {
      const sanitizedProps = { ...props };
      delete sanitizedProps.whileHover;
      delete sanitizedProps.variants;
      delete sanitizedProps.initial;
      delete sanitizedProps.animate;
      delete sanitizedProps.transition;
      return <div {...sanitizedProps}>{props.children}</div>;
    },
  },
}));

vi.mock("recharts", () => {
  const Passthrough = ({ children }: { children?: ReactNode }) => <div>{children}</div>;

  return {
    ResponsiveContainer: Passthrough,
    Radar: Passthrough,
    PolarGrid: Passthrough,
    PolarRadiusAxis: Passthrough,
    Tooltip: Passthrough,
    PolarAngleAxis: Passthrough,
    RadarChart: ({
      data,
      children,
    }: {
      data?: Array<{ category: string }>;
      children?: ReactNode;
    }) => (
      <div>
        {data?.map((entry) => (
          <span key={entry.category}>{entry.category}</span>
        ))}
        {children}
      </div>
    ),
  };
});

function renderWithLocale(locale: "fr" | "en") {
  return render(
    <NextIntlClientProvider locale={locale} messages={locale === "fr" ? fr : en}>
      <CategoryAccuracyChart categoryData={{ geometry: { completed: 4, accuracy: 0.82 } }} />
    </NextIntlClientProvider>
  );
}

describe("CategoryAccuracyChart", () => {
  it("retraduit les libelles radar quand la locale change", () => {
    const view = renderWithLocale("fr");

    expect(screen.getByText("Géométrie")).toBeInTheDocument();

    view.rerender(
      <NextIntlClientProvider locale="en" messages={en}>
        <CategoryAccuracyChart categoryData={{ geometry: { completed: 4, accuracy: 0.82 } }} />
      </NextIntlClientProvider>
    );

    expect(screen.getByText("Geometry")).toBeInTheDocument();
  });
});
