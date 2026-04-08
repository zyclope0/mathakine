import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

import {
  ALLOWED_DENSE_EXCEPTIONS,
  CHATBOT_FLOATING_GLOBAL_FORBIDDEN_HOME,
  collectChatbotGlobalOwnershipViolations,
  collectDenseExceptionViolations,
  collectMissingCanonicalLibFiles,
  collectMissingSeams,
  collectProtectedBudgetViolations,
  FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS,
  OWNERSHIP_RULE_GROUPS,
  PROTECTED_FRONTEND_SURFACES,
  REQUIRED_ARCHITECTURE_SEAMS,
  REQUIRED_CANONICAL_LIB_FILES,
} from "@/lib/architecture/frontendGuardrails";

/**
 * Vitest cwd is the frontend package root (see package.json "test" script usage).
 */
const frontendRoot = process.cwd();

function resolveFrontendPath(relativePath: string): string {
  return join(frontendRoot, relativePath);
}

function fileExists(relativePath: string): boolean {
  return existsSync(resolveFrontendPath(relativePath));
}

/** wc -l style: newline-terminated file yields line count including trailing newline split. */
function countPhysicalLines(relativePath: string): number {
  const abs = resolveFrontendPath(relativePath);
  if (!existsSync(abs)) {
    throw new Error(`Guardrail: file not found at ${relativePath} (cwd=${frontendRoot})`);
  }
  const raw = readFileSync(abs, "utf8");
  return raw.split(/\r?\n/).length;
}

describe("FFI-L17A frontend architecture guardrails", () => {
  it("lists explicit paths only (no glob magic)", () => {
    const protectedPaths = PROTECTED_FRONTEND_SURFACES.map((s) => s.relativePath);
    const seamPaths = REQUIRED_ARCHITECTURE_SEAMS.map((s) => s.relativePath);
    const densePaths = ALLOWED_DENSE_EXCEPTIONS.map((s) => s.relativePath);
    const canonicalLibPaths = REQUIRED_CANONICAL_LIB_FILES.map((s) => s.relativePath);
    const forbiddenChatPaths = [...FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS];

    for (const p of protectedPaths) {
      expect(p).not.toMatch(/[*?\[]/);
      expect(p).not.toContain("**");
    }
    for (const p of seamPaths) {
      expect(p).not.toMatch(/[*?\[]/);
    }
    for (const p of densePaths) {
      expect(p).not.toMatch(/[*?\[]/);
    }
    for (const p of canonicalLibPaths) {
      expect(p).not.toMatch(/[*?\[]/);
    }
    for (const p of forbiddenChatPaths) {
      expect(p).not.toMatch(/[*?\[]/);
    }
  });

  it("required architecture seams exist on disk", () => {
    const issues = collectMissingSeams(fileExists);
    expect(issues, issues.join("\n")).toEqual([]);
  });

  it("protected facades and page containers stay within LOC budgets", () => {
    const lineCounts: Record<string, number> = {};
    for (const s of PROTECTED_FRONTEND_SURFACES) {
      lineCounts[s.relativePath] = countPhysicalLines(s.relativePath);
    }
    const issues = collectProtectedBudgetViolations(lineCounts);
    expect(issues, issues.join("\n")).toEqual([]);
  });

  it("documented dense exceptions exist and stay within provisional budgets", () => {
    const lineCounts: Record<string, number> = {};
    for (const ex of ALLOWED_DENSE_EXCEPTIONS) {
      lineCounts[ex.relativePath] = countPhysicalLines(ex.relativePath);
    }
    const issues = collectDenseExceptionViolations(lineCounts, fileExists);
    expect(issues, issues.join("\n")).toEqual([]);
  });

  it("global chatbot shell stays under components/chat/ and not under components/home/", () => {
    const issues = collectChatbotGlobalOwnershipViolations(fileExists);
    expect(issues, issues.join("\n")).toEqual([]);
    expect(
      fileExists(CHATBOT_FLOATING_GLOBAL_FORBIDDEN_HOME),
      `must not create ${CHATBOT_FLOATING_GLOBAL_FORBIDDEN_HOME}`
    ).toBe(false);
  });
});

describe("FFI-L17B ownership + canonical lib guardrails", () => {
  it("required canonical lib anchors exist on disk", () => {
    const issues = collectMissingCanonicalLibFiles(fileExists);
    expect(issues, issues.join("\n")).toEqual([]);
  });

  it("ownership rule groups stay documented (non-empty contract)", () => {
    expect(OWNERSHIP_RULE_GROUPS.length).toBeGreaterThanOrEqual(4);
    for (const g of OWNERSHIP_RULE_GROUPS) {
      expect(g.id.length).toBeGreaterThan(0);
      expect(g.summary.length).toBeGreaterThan(0);
      expect(g.bullets.length).toBeGreaterThan(0);
    }
  });

  it("forbidden ChatbotFloatingGlobal paths are not present on disk", () => {
    for (const p of FORBIDDEN_CHATBOT_FLOATING_GLOBAL_PATHS) {
      expect(fileExists(p), `must not create ${p}`).toBe(false);
    }
  });
});
