/**
 * ChallengeSolverHint — onboarding première visite (U3, lot neuro-inclusion).
 *
 * Cas couverts :
 * 1. S'affiche si localStorage ne contient pas la clé (première visite).
 * 2. Ne s'affiche pas si localStorage contient déjà la clé (retour).
 * 3. Fermer écrit la clé et masque le composant.
 * 4. Contenu step1 contextuel : single_choice / text / interactive_visual.
 * 5. Ligne indice conditionnelle (hasHints).
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";
import { ChallengeSolverHint } from "./ChallengeSolverHint";
import type { ChallengeResponseMode } from "./ChallengeSolverHint";
import { STORAGE_KEYS } from "@/lib/storage/keys";

function Wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

function renderHint(props: { responseMode?: ChallengeResponseMode; hasHints?: boolean } = {}) {
  return render(
    <Wrapper>
      <ChallengeSolverHint
        responseMode={props.responseMode ?? "single_choice"}
        hasHints={props.hasHints ?? true}
      />
    </Wrapper>
  );
}

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

describe("ChallengeSolverHint", () => {
  it("s'affiche lors de la première visite (clé absente de localStorage)", () => {
    renderHint();
    expect(screen.getByRole("region", { name: /comment/i })).toBeInTheDocument();
  });

  it("ne s'affiche pas si la clé est déjà présente dans localStorage", async () => {
    localStorage.setItem(STORAGE_KEYS.challengeSolverHintSeen, "1");
    renderHint();
    await waitFor(() => {
      expect(screen.queryByRole("region", { name: /comment/i })).not.toBeInTheDocument();
    });
  });

  it("masque le hint et écrit la clé au clic sur le bouton dismiss", async () => {
    const user = userEvent.setup();
    renderHint();

    await screen.findByRole("region", { name: /comment/i });

    const dismissBtn = screen.getByRole("button", { name: /OK, je commence/i });
    await user.click(dismissBtn);

    expect(screen.queryByRole("region", { name: /comment/i })).not.toBeInTheDocument();
    expect(localStorage.getItem(STORAGE_KEYS.challengeSolverHintSeen)).toBe("1");
  });

  it("affiche l'étape QCM si responseMode=single_choice", async () => {
    renderHint({ responseMode: "single_choice" });
    await screen.findByText(/Clique sur la bonne réponse/i);
  });

  it("affiche l'étape texte si responseMode=text", async () => {
    renderHint({ responseMode: "text" });
    await screen.findByText(/Écris ta réponse dans le champ/i);
  });

  it("affiche l'étape visuelle si responseMode=interactive_visual", async () => {
    renderHint({ responseMode: "interactive_visual" });
    await screen.findByText(/Complète le schéma/i);
  });

  it("n'affiche pas la ligne indice si hasHints=false", async () => {
    renderHint({ hasHints: false });
    await screen.findByRole("region", { name: /comment/i });
    expect(screen.queryByText(/Demande un indice/i)).not.toBeInTheDocument();
  });

  it("affiche la ligne indice si hasHints=true", async () => {
    renderHint({ hasHints: true });
    await screen.findByText(/Demande un indice/i);
  });
});
