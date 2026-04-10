import { test, expect } from "@playwright/test";
import { authenticateDemoUserForProtectedPages } from "./helpers/demoUserAuth";

test.describe("Badges (invité)", () => {
  test("invité est redirigé vers /login", async ({ page }) => {
    await page.goto("/badges", { waitUntil: "domcontentloaded" });

    await page.waitForFunction(() => window.location.pathname === "/login", undefined, {
      timeout: 20_000,
    });
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
  });
});

test.describe("Badges (utilisateur authentifié)", () => {
  test.skip(
    ({ browserName }) => browserName !== "chromium",
    "QF-05: parcours auth réel stabilisé sur Chromium"
  );
  test.describe.configure({ timeout: 120_000 });

  test("affiche la page badges authentifiée (titre et action principale)", async ({ page }) => {
    await authenticateDemoUserForProtectedPages(page);
    await page.goto("/badges", { waitUntil: "domcontentloaded" });

    await expect(
      page.getByRole("heading", { level: 1, name: /Badges et Récompenses|Badges and Rewards/i })
    ).toBeVisible({ timeout: 25_000 });
    await expect(
      page.getByRole("button", { name: /Vérifier les badges|Check badges/i })
    ).toBeVisible();
  });
});
