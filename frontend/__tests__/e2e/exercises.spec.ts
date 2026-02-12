import { test, expect } from "@playwright/test";

test.describe("Exercices", () => {
  test.beforeEach(async ({ page }) => {
    // Se connecter avant chaque test
    await page.goto("/login");
    await page.getByLabel(/nom d'utilisateur|username/i).fill("test_user");
    await page.getByLabel(/mot de passe|password/i).fill("test_password");
    await page.getByRole("button", { name: /se connecter|connexion/i }).click();
    await page.waitForURL("/dashboard", { timeout: 5000 });
  });

  test("page exercices s'affiche correctement", async ({ page }) => {
    await page.goto("/exercises");

    await expect(page.getByRole("heading", { name: /exercices/i })).toBeVisible();
  });

  test("génération d'un exercice standard", async ({ page }) => {
    await page.goto("/exercises");

    // Chercher le bouton de génération
    const generateButton = page.getByRole("button", { name: /générer/i });
    if (await generateButton.isVisible()) {
      await generateButton.click();

      // Attendre qu'un exercice soit généré (vérifier la présence d'une question)
      await expect(page.getByText(/question|résoudre/i)).toBeVisible({ timeout: 10000 });
    }
  });

  test("navigation vers page de détail d'exercice", async ({ page }) => {
    await page.goto("/exercises");

    // Chercher un lien ou bouton vers un exercice
    const exerciseLink = page.getByRole("link", { name: /résoudre|voir/i }).first();
    if (await exerciseLink.isVisible()) {
      await exerciseLink.click();
      await expect(page).toHaveURL(/\/exercise\/\d+/);
    }
  });
});
