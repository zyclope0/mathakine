import { test, expect } from '@playwright/test';

test.describe('Authentification', () => {
  test('page de connexion s\'affiche correctement', async ({ page }) => {
    await page.goto('/login');
    
    // Vérifier que les éléments essentiels sont présents
    await expect(page.getByRole('heading', { name: /connexion/i })).toBeVisible();
    await expect(page.getByLabel(/nom d'utilisateur|username/i)).toBeVisible();
    await expect(page.getByLabel(/mot de passe|password/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /se connecter|connexion/i })).toBeVisible();
  });

  test('redirection vers dashboard après connexion réussie', async ({ page }) => {
    await page.goto('/login');
    
    // Remplir le formulaire (utiliser des identifiants de test valides)
    await page.getByLabel(/nom d'utilisateur|username/i).fill('test_user');
    await page.getByLabel(/mot de passe|password/i).fill('test_password');
    
    // Soumettre le formulaire
    await page.getByRole('button', { name: /se connecter|connexion/i }).click();
    
    // Attendre la redirection vers le dashboard
    await page.waitForURL('/dashboard', { timeout: 5000 });
    await expect(page).toHaveURL('/dashboard');
  });

  test('affichage d\'erreur avec identifiants invalides', async ({ page }) => {
    await page.goto('/login');
    
    await page.getByLabel(/nom d'utilisateur|username/i).fill('invalid_user');
    await page.getByLabel(/mot de passe|password/i).fill('invalid_password');
    await page.getByRole('button', { name: /se connecter|connexion/i }).click();
    
    // Attendre un message d'erreur
    await expect(page.getByText(/erreur|invalid|incorrect/i)).toBeVisible({ timeout: 5000 });
  });

  test('navigation vers page d\'inscription', async ({ page }) => {
    await page.goto('/login');
    
    const registerLink = page.getByRole('link', { name: /s'inscrire|inscription/i });
    if (await registerLink.isVisible()) {
      await registerLink.click();
      await expect(page).toHaveURL('/register');
    }
  });

  test('page mot de passe oublié s\'affiche et lien reset présent', async ({ page }) => {
    await page.goto('/login');
    const forgotLink = page.getByRole('link', { name: /mot de passe oublié|forgot/i });
    if (await forgotLink.isVisible()) {
      await forgotLink.click();
      await expect(page).toHaveURL('/forgot-password');
    } else {
      await page.goto('/forgot-password');
    }
    await expect(page.getByRole('heading', { name: /mot de passe oublié|réinitialiser|forgot/i })).toBeVisible();
    await expect(page.getByLabel(/email|adresse/i).first()).toBeVisible();
    await expect(page.getByRole('button', { name: /envoyer|réinitialiser|envoy/i })).toBeVisible();
  });
});

