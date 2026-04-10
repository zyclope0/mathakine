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
        // Baseline réelle mesurée en CI (2026-04-10) :
        //   statements 39.75% | branches 34.04% | functions 37.85% | lines 40.66%
        // Seuils posés 1 point sous le réel pour absorber la variance inter-runs.
        // À remonter progressivement à chaque lot de tests ajoutés.
        statements: 39,
        branches: 33,
        functions: 37,
        lines: 40,
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
