import { test, expect } from "@playwright/test";
import { authenticateDemoUserForProtectedPages } from "./helpers/demoUserAuth";

test.describe("Dashboard (invité)", () => {
  test("invité est redirigé vers /login", async ({ page }) => {
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    await page.waitForFunction(() => window.location.pathname === "/login", undefined, {
      timeout: 15_000,
    });
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
  });
});

test.describe("Dashboard (utilisateur authentifié)", () => {
  test.skip(
    ({ browserName }) => browserName !== "chromium",
    "QF-05: parcours auth réel stabilisé sur Chromium"
  );
  test.describe.configure({ timeout: 120_000 });

  test("affiche l’en-tête du tableau de bord après session démo", async ({ page }) => {
    await authenticateDemoUserForProtectedPages(page);
    await page.goto("/dashboard", { waitUntil: "domcontentloaded" });

    await expect(
      page.getByRole("heading", {
        level: 1,
        name: /Tableau de bord|Dashboard|Bienvenue|Welcome/i,
      })
    ).toBeVisible({ timeout: 40_000 });
  });
});
