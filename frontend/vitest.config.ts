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
      exclude: [
        "node_modules/",
        "**/*.config.{ts,tsx}",
        "**/types/**",
        "**/*.d.ts",
        "**/__tests__/**",
        "**/*.test.{ts,tsx}",
        "**/*.spec.{ts,tsx}",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
});
