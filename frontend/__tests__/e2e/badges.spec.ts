import { test, expect } from "@playwright/test";

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
