/**
 * Characterization tests for app/privacy/page.tsx (Server Component + getTranslations).
 * FFI-L20G
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { createTranslator } from "use-intl/core";

import fr from "@/messages/fr.json";
import PrivacyPage from "@/app/privacy/page";

vi.mock("next-intl/server", () => ({
  getTranslations: (namespace: "about" | "privacy") =>
    Promise.resolve(
      createTranslator({
        locale: "fr",
        messages: fr,
        namespace,
      })
    ),
}));

const frontendRoot = process.cwd();

describe("PrivacyPage", () => {
  it("n’expose pas de directive use client en tête de fichier", () => {
    const src = readFileSync(join(frontendRoot, "app/privacy/page.tsx"), "utf8").trimStart();
    expect(src.startsWith('"use client"')).toBe(false);
    expect(src.startsWith("'use client'")).toBe(false);
  });

  it("affiche le titre et la date de mise à jour traduits", async () => {
    const jsx = await PrivacyPage();
    render(jsx);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(fr.privacy.title);
    expect(screen.getByText(fr.privacy.lastUpdate)).toBeInTheDocument();
  });

  it("liste les droits RGPD attendus", async () => {
    const jsx = await PrivacyPage();
    render(jsx);
    expect(screen.getByText(fr.privacy.rights.access)).toBeInTheDocument();
    expect(screen.getByText(fr.privacy.rights.complaint)).toBeInTheDocument();
  });
});
