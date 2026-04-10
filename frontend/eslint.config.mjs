import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";
import eslintConfigPrettier from "eslint-config-prettier";

const tsconfigRootDir = path.dirname(fileURLToPath(import.meta.url));

/** Paths excluded from type-aware lint (no tsconfig program or non-app code). */
const TYPE_AWARE_IGNORES = [
  ".next/**",
  "out/**",
  "build/**",
  "coverage/**",
  "scripts/**",
  "node_modules/**",
];

const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,
  eslintConfigPrettier, // Désactive les règles ESLint qui entrent en conflit avec Prettier
  // QF-04C: React Compiler hook rules at error (signal clean; rare intentional cases use local disable)
  {
    rules: {
      "react-hooks/set-state-in-effect": "error",
      "react-hooks/preserve-manual-memoization": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-require-imports": "error",
      "@typescript-eslint/no-unused-vars": "error",
      "@typescript-eslint/consistent-type-imports": [
        "error",
        {
          prefer: "type-imports",
          fixStyle: "inline-type-imports",
          // Vitest `vi.importActual<typeof import("...")>` needs `import()` type args; value imports stay enforced
          disallowTypeAnnotations: false,
        },
      ],
      "react-hooks/exhaustive-deps": "error",
    },
  },
  // QF-04B: minimal type-aware setup for @typescript-eslint rules that need parser services (no full recommendedTypeChecked)
  {
    files: ["**/*.{ts,mts,tsx}"],
    ignores: TYPE_AWARE_IGNORES,
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir,
      },
    },
  },
  {
    files: ["**/*.{ts,mts,tsx}"],
    ignores: TYPE_AWARE_IGNORES,
    rules: {
      "@typescript-eslint/no-floating-promises": "error",
    },
  },
  // Override default ignores of eslint-config-next.
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts", "scripts/**", "coverage/**"]),
]);

export default eslintConfig;
