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
        // Baseline autoritative CI (GitHub Actions ubuntu-latest, Node 20, 2026-04-12,
        // `npx vitest --coverage --reporter=junit --outputFile=./junit.xml --run`) :
        //   statements 44.57% | branches 37.22% | functions 41.47% | lines 45.68%
        // Les runs locaux Windows/Node 20 observés sur ce dépôt montent plus haut (~47.9/39.93/43.3/49.14),
        // donc les gates doivent être ancrés sur la CI, pas sur la machine locale.
        // Seuils : floor(mesure CI) − 1 pour chaque axe, tout en restant au-dessus des anciens 39/33/37/40.
        // À remonter de nouveau uniquement après nouvelle mesure défendable en CI.
        statements: 43,
        branches: 36,
        functions: 40,
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
