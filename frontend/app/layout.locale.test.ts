import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const __dirname = dirname(fileURLToPath(import.meta.url));

describe("RootLayout html lang", () => {
  it('does not hardcode lang="fr" on the html element', () => {
    const src = readFileSync(join(__dirname, "layout.tsx"), "utf8");
    expect(src).not.toMatch(/<html[^>]*\s+lang="fr"/);
  });

  it("binds lang from resolved server locale", () => {
    const src = readFileSync(join(__dirname, "layout.tsx"), "utf8");
    expect(src).toContain("lang={htmlLang}");
  });
});
