import { renderHook } from "@testing-library/react";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";
import fr from "@/messages/fr.json";
import { useChallengeTypeDisplay, useExerciseTypeDisplay } from "@/hooks/useChallengeTranslations";

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("useChallengeTypeDisplay", () => {
  it("returns the dedicated filter label for the all sentinel", () => {
    const { result } = renderHook(() => useChallengeTypeDisplay(), { wrapper });

    expect(result.current("all")).toBe(fr.challenges.filters.allTypes);
  });

  it("keeps translating known challenge types", () => {
    const { result } = renderHook(() => useChallengeTypeDisplay(), { wrapper });

    expect(result.current("sequence")).toBe(fr.challenges.types.sequence);
  });
});

describe("useExerciseTypeDisplay", () => {
  it("returns the dedicated filter label for the all sentinel", () => {
    const { result } = renderHook(() => useExerciseTypeDisplay(), { wrapper });

    expect(result.current("all")).toBe(fr.exercises.filters.allTypes);
  });
});
