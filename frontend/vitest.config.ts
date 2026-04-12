import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    css: true,
    exclude: ["**/node_modules/**", "**/__tests__/e2e/**", "**/*.spec.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html", "lcov"],
      include: [
        "*.{ts,tsx}",
        "app/**/*.{ts,tsx}",
        "components/**/*.{ts,tsx}",
        "hooks/**/*.{ts,tsx}",
        "i18n/**/*.{ts,tsx}",
        "lib/**/*.{ts,tsx}",
        "messages/**/*.json",
      ],
      thresholds: {
        // Baseline réelle mesurée localement (2026-04-12, `npx vitest run --coverage`, v8) :
        //   statements 47.8% | branches 39.87% | functions 43.19% | lines 49.03%
        // Seuils : floor(mesure) − 1 pour chaque axe (lot ACTIF-04-COVERAGE-01), uniquement
        // parce que ces valeurs dépassent les anciens seuils (39/33/37/40).
        // À remonter de nouveau après nouvelle mesure quand des tests supplémentaires le justifient.
        statements: 46,
        branches: 38,
        functions: 42,
        lines: 48,
      },
      exclude: [
        "node_modules/",
        "**/*.config.{ts,tsx}",
        "**/types/**",
        "**/*.d.ts",
        "**/__tests__/**",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
        ".next/**",
        "coverage/**",
        "playwright-report/**",
        "scripts/**",
        "test-results/**",
        "vitest.setup.ts",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});
