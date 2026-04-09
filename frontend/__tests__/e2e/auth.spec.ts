import { test, expect } from "@playwright/test";

test.describe("Authentification (invite)", () => {
  test("page de connexion affiche le formulaire", async ({ page }) => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });

    await expect(page.locator('[data-slot="card-title"]')).toHaveText(/connexion|login/i);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
    await expect(page.getByRole("button", { name: /se connecter|sign in/i })).toBeVisible();
  });

  test("la carte login expose un lien vers /register", async ({ page }) => {
    await page.goto("/login", { waitUntil: "domcontentloaded" });

    const registerLink = page.locator('[data-slot="card-content"] a[href="/register"]').first();
    await expect(registerLink).toBeVisible();
    await expect(registerLink).toHaveAttribute("href", "/register");
  });

  test("page inscription affiche le formulaire", async ({ page }) => {
    await page.goto("/register", { waitUntil: "domcontentloaded" });

    await expect(page.locator('[data-slot="card-title"]')).toHaveText(/inscription|register/i);
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
    await expect(page.locator("#email")).toBeVisible();
    await expect(page.locator("#password")).toBeVisible();
    await expect(page.getByRole("button", { name: /s'inscrire|register/i })).toBeVisible();
  });

  test("mot de passe oublie: formulaire email et action envoi", async ({ page }) => {
    await page.goto("/forgot-password", { waitUntil: "domcontentloaded" });
    await expect(page.locator('[data-slot="card-title"]')).toHaveText(
      /mot de passe oublie|forgot password/i
    );
    await expect(page.locator("#email")).toBeVisible();
    await expect(
      page.getByRole("button", {
        name: /envoyer le lien|send reset|envoi en cours|sending/i,
      })
    ).toBeVisible();
  });
});
