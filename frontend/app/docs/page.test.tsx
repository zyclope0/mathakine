import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { createTranslator } from "use-intl/core";

import fr from "@/messages/fr.json";
import DocsPage from "./page";

vi.mock("next-intl/server", () => ({
  getTranslations: (namespace: "docs") =>
    Promise.resolve(
      createTranslator({
        locale: "fr",
        messages: fr,
        namespace,
      })
    ),
}));

const frontendRoot = process.cwd();

describe("DocsPage", () => {
  it("reste un Server Component", () => {
    const src = readFileSync(join(frontendRoot, "app/docs/page.tsx"), "utf8").trimStart();
    expect(src.startsWith('"use client"')).toBe(false);
    expect(src.startsWith("'use client'")).toBe(false);
  });

  it("affiche le parcours beta rapide et la FAQ", async () => {
    const jsx = await DocsPage();
    render(jsx);

    expect(
      screen.getByRole("heading", { level: 1, name: fr.docs.betaHero.title })
    ).toBeInTheDocument();
    expect(screen.getByText(fr.docs.quickstart.title)).toBeInTheDocument();
    expect(screen.getByText(fr.docs.howToReport.title)).toBeInTheDocument();
    expect(screen.getByText(fr.docs.betaGuideNoteTitle)).toBeInTheDocument();
    expect(screen.getByText(fr.docs.faq.q11)).toBeInTheDocument();
  });

  it("propose les CTA principaux vers inscription et exercices", async () => {
    const jsx = await DocsPage();
    render(jsx);

    const registerLinks = screen.getAllByRole("link", {
      name: new RegExp(fr.docs.betaHero.ctaRegister, "i"),
    });
    const exerciseLinks = screen.getAllByRole("link", {
      name: new RegExp(fr.docs.betaHero.ctaExercises, "i"),
    });

    expect(registerLinks.some((link) => link.getAttribute("href") === "/register")).toBe(true);
    expect(exerciseLinks.some((link) => link.getAttribute("href") === "/exercises")).toBe(true);
  });
});
