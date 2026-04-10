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
        statements: 43,
        branches: 36,
        functions: 39,
        lines: 44,
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
