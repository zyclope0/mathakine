import { test, expect } from "@playwright/test";
import { authenticateDemoUserForProtectedPages } from "./helpers/demoUserAuth";

test.describe("Settings (invité)", () => {
  test("invité est redirigé vers /login", async ({ page }) => {
    await page.goto("/settings", { waitUntil: "domcontentloaded" });

    await page.waitForFunction(() => window.location.pathname === "/login", undefined, {
      timeout: 20_000,
    });
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
  });
});

test.describe("Settings (utilisateur authentifié)", () => {
  test.skip(
    ({ browserName }) => browserName !== "chromium",
    "QF-05: parcours auth réel stabilisé sur Chromium"
  );
  test.describe.configure({ timeout: 120_000 });

  test("affiche les paramètres et la navigation latérale", async ({ page }) => {
    await authenticateDemoUserForProtectedPages(page);
    await page.goto("/settings", { waitUntil: "domcontentloaded" });

    await expect(page.getByRole("heading", { level: 1, name: /Paramètres|Settings/i })).toBeVisible(
      { timeout: 25_000 }
    );
    await expect(page.getByRole("navigation").getByText(/Général|General/i)).toBeVisible();
  });
});
