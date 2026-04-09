import { test, expect } from "@playwright/test";

test.describe("Admin — accès (invité)", () => {
  test("invité est redirigé vers /login", async ({ page }) => {
    await page.goto("/admin", { waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => window.location.pathname === "/login", undefined, {
      timeout: 15_000,
    });
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
  });
});

test.describe.skip("Admin — authentifié (hors E2E-CORE-06 minimal)", () => {
  test("surfaces read-heavy avec session admin — nécessite lot E2E auth stable séparé", async () => {
    // Pas de globalSetup / storageState dans ce lot ; réactiver avec infra dédiée.
  });
});
