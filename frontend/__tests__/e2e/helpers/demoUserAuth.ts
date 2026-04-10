import { expect, type Page } from "@playwright/test";
import { DEMO_LOGIN_PASSWORD, DEMO_LOGIN_USERNAME } from "../../../lib/constants/demoLogin";

const LOGIN_NAV_TIMEOUT_MS = 45_000;
const PAGE_READY_TIMEOUT_MS = 25_000;

/**
 * Fills the login form and waits until navigation leaves `/login`.
 * Uses the same seed credentials as `lib/constants/demoLogin` (backend seed / démo).
 */
export async function loginAsDemoUser(page: Page): Promise<void> {
  await page.goto("/login", { waitUntil: "load" });

  const usernameInput = page.locator("#username");
  await usernameInput.waitFor({ state: "visible", timeout: PAGE_READY_TIMEOUT_MS });
  await expect(usernameInput).toBeEditable({ timeout: PAGE_READY_TIMEOUT_MS });
  await usernameInput.fill(DEMO_LOGIN_USERNAME);
  await expect(usernameInput).toHaveValue(DEMO_LOGIN_USERNAME);

  const passwordInput = page.locator("#password");
  await expect(passwordInput).toBeEditable({ timeout: PAGE_READY_TIMEOUT_MS });
  await passwordInput.fill(DEMO_LOGIN_PASSWORD);
  await expect(passwordInput).toHaveValue(DEMO_LOGIN_PASSWORD);

  const loginForm = page.locator("form").filter({ has: page.locator("#username") });
  const submitLogin = loginForm.getByRole("button", {
    name: /sign in|se connecter/i,
  });
  await expect(submitLogin).toBeEnabled();

  await Promise.all([
    page.waitForURL((url) => !url.pathname.endsWith("/login"), {
      timeout: LOGIN_NAV_TIMEOUT_MS,
    }),
    submitLogin.click(),
  ]);
}

/**
 * If the seed user still has no `onboarding_completed_at`, login sends them to `/onboarding`.
 * Minimal path: pick first grade, submit; product then routes to `/diagnostic` (not automated here).
 */
export async function completeOnboardingIfNeeded(page: Page): Promise<void> {
  if (!page.url().includes("/onboarding")) {
    return;
  }

  await page
    .getByRole("heading", {
      level: 1,
      name: /Personnalise ton apprentissage|Personalize your learning/i,
    })
    .waitFor({ state: "visible", timeout: PAGE_READY_TIMEOUT_MS });

  await page.locator("#grade_level").click();
  await page.getByRole("option").first().click();

  const onboardingForm = page.locator("form").filter({ has: page.locator("#grade_level") });
  await Promise.all([
    page.waitForURL((url) => url.pathname.includes("/diagnostic"), {
      timeout: LOGIN_NAV_TIMEOUT_MS,
    }),
    onboardingForm.locator('button[type="submit"]').click(),
  ]);
}

/**
 * Login + optional onboarding. Caller should `goto` the target protected route
 * (diagnostic is skipped intentionally — see QF-05 scope).
 */
export async function authenticateDemoUserForProtectedPages(page: Page): Promise<void> {
  await loginAsDemoUser(page);
  await completeOnboardingIfNeeded(page);
}
