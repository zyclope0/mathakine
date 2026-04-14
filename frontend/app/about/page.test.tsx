/**
 * Characterization tests for app/about/page.tsx (Server Component + getTranslations).
 * FFI-L20G
 */

import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { createTranslator } from "use-intl/core";

import fr from "@/messages/fr.json";
import AboutPage from "./page";

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

describe("AboutPage", () => {
  it("n’expose pas de directive use client en tête de fichier", () => {
    const src = readFileSync(join(frontendRoot, "app/about/page.tsx"), "utf8").trimStart();
    expect(src.startsWith('"use client"')).toBe(false);
    expect(src.startsWith("'use client'")).toBe(false);
  });

  it("affiche le titre traduit (namespace about)", async () => {
    const jsx = await AboutPage();
    render(jsx);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(fr.about.title);
  });

  it("affiche un extrait du paragraphe riche story.p2 (balise bold)", async () => {
    const jsx = await AboutPage();
    const { container } = render(jsx);
    expect(container.textContent).toContain("surcharge sensorielle et cognitive");
  });

  it("conserve le lien contact avec libellé traduit", async () => {
    const jsx = await AboutPage();
    render(jsx);
    const link = screen.getByRole("link", { name: fr.about.contactCta });
    expect(link).toHaveAttribute("href", "/contact");
  });
});
