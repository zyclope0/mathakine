/**
 * ExerciseSolverHint — onboarding première visite (U2, lot neuro-inclusion).
 *
 * Trois cas :
 * 1. S'affiche si localStorage ne contient pas la clé (première visite).
 * 2. Ne s'affiche pas si localStorage contient déjà la clé (retour).
 * 3. Fermer écrit la clé et masque le composant.
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";
import { ExerciseSolverHint } from "./ExerciseSolverHint";
import { STORAGE_KEYS } from "@/lib/storage/keys";

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function renderHint(props: { isOpenAnswer?: boolean; hasHint?: boolean } = {}) {
  return render(
    <Wrapper>
      <ExerciseSolverHint
        isOpenAnswer={props.isOpenAnswer ?? false}
        hasHint={props.hasHint ?? true}
      />
    </Wrapper>
  );
}

/**
 * vitest.setup.ts remplace localStorage par un vi.fn() mock sans store en mémoire.
 * On réinitialise le mock avant chaque test avec un vrai store en mémoire pour
 * permettre de tester la logique de persistance réelle.
 */
beforeEach(() => {
  const store: Record<string, string> = {};
  vi.mocked(localStorage.getItem).mockImplementation((key: string) => store[key] ?? null);
  vi.mocked(localStorage.setItem).mockImplementation((key: string, value: string) => {
    store[key] = value;
  });
  vi.mocked(localStorage.removeItem).mockImplementation((key: string) => {
    delete store[key];
  });
  vi.mocked(localStorage.clear).mockImplementation(() => {
    Object.keys(store).forEach((k) => delete store[k]);
  });
});

describe("ExerciseSolverHint", () => {
  it("s'affiche lors de la première visite (clé absente de localStorage)", () => {
    renderHint();
    expect(screen.getByRole("region", { name: /comment/i })).toBeInTheDocument();
  });

  it("ne s'affiche pas si la clé est déjà présente dans localStorage", async () => {
    localStorage.setItem(STORAGE_KEYS.exerciseSolverHintSeen, "1");
    renderHint();
    // useEffect is async — wait for potential state update then assert absent
    await waitFor(() => {
      expect(screen.queryByRole("region", { name: /comment/i })).not.toBeInTheDocument();
    });
  });

  it("masque le hint et écrit la clé au clic sur le bouton dismiss", async () => {
    const user = userEvent.setup();
    renderHint();

    // Wait for hint to appear (useEffect)
    await screen.findByRole("region", { name: /comment/i });

    const dismissBtn = screen.getByRole("button", { name: /OK, je commence/i });
    await user.click(dismissBtn);

    expect(screen.queryByRole("region", { name: /comment/i })).not.toBeInTheDocument();
    expect(localStorage.getItem(STORAGE_KEYS.exerciseSolverHintSeen)).toBe("1");
  });

  it("affiche l'étape QCM si isOpenAnswer=false", async () => {
    renderHint({ isOpenAnswer: false });
    await screen.findByText(/Clique sur la bonne réponse/i);
  });

  it("affiche l'étape open-answer si isOpenAnswer=true", async () => {
    renderHint({ isOpenAnswer: true });
    await screen.findByText(/Écris ta réponse/i);
  });

  it("n'affiche pas la ligne indice si hasHint=false", async () => {
    renderHint({ hasHint: false });
    await screen.findByRole("region", { name: /comment/i });
    expect(screen.queryByText(/Voir un indice/i)).not.toBeInTheDocument();
  });

  it("affiche la ligne indice si hasHint=true", async () => {
    renderHint({ hasHint: true });
    await screen.findByText(/Voir un indice/i);
  });
});
