"use client";

import "katex/dist/katex.min.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { cn } from "@/lib/utils";

/**
 * Corrige le bug classique : \frac{1}{8}81 → \frac{1}{8} 81
 * Quand une fraction LaTeX est immédiatement suivie de chiffres (sans espace),
 * le parseur les fusionne et casse le rendu. On injecte un espace.
 */
function sanitizeLatexFractions(text: string): string {
  return text.replace(/(\\frac\{\d+\}\{\d+\})(\d+)/g, "$1 $2");
}

function restoreJsonEscapedLatexCommands(text: string): string {
  return text
    .replace(/\u000crac/g, "\\frac")
    .replace(/\u0009ext/g, "\\text")
    .replace(/(^|[\s(])rac\{/g, "$1\\frac{")
    .replace(/(^|[\s(])text\{/g, "$1\\text{");
}

/**
 * Normalise les délimiteurs LaTeX que l'IA produit parfois (`\(...\)`, `\[...\]`).
 * `remark-math` parse de façon fiable `$...$` et `$$...$$`, mais pas ces variantes.
 */
function normalizeLatexDelimiters(text: string): string {
  return text
    .replace(/\\\[([\s\S]*?)\\\]/g, (_match, inner: string) => `\n\n$$\n${inner.trim()}\n$$\n\n`)
    .replace(/\\\(([^\n]*?)\\\)/g, (_match, inner: string) => `$${inner}$`);
}

/**
 * Dégrade proprement certains blocs LaTeX manifestement cassés générés par l'IA.
 * Exemple fréquent : `$$ ... \end{cases}$$` sans `\begin{cases}`.
 * Au lieu de laisser KaTeX afficher une erreur rouge, on repasse le contenu en texte lisible.
 */
function sanitizeBrokenLatexBlocks(text: string): string {
  return text.replace(/\$\$([\s\S]*?)\$\$/g, (full, rawInner) => {
    const inner = String(rawInner ?? "");
    const hasBrokenCases = inner.includes("\\end{cases}") && !inner.includes("\\begin{cases}");

    if (!hasBrokenCases) {
      return full;
    }

    return inner
      .replace(/\\text\{([^}]*)\}/g, "$1")
      .replace(/\\boxed\{([^}]*)\}/g, "$1")
      .replace(/\\times/g, "×")
      .replace(/\\div/g, "÷")
      .replace(/\\end\{cases\}/g, "")
      .replace(/\\\\(\[[^\]]*\])?/g, "\n")
      .replace(/\s*&\s*/g, " ")
      .replace(/[ \t]+\n/g, "\n")
      .trim();
  });
}

function transformOutsideMath(text: string, transform: (part: string) => string): string {
  return text
    .split(/(\$\$[\s\S]*?\$\$|\$[^$\n]*?\$)/g)
    .map((part) => (part.startsWith("$") ? part : transform(part)))
    .join("");
}

function renderLooseLatexAsReadableText(text: string): string {
  return transformOutsideMath(text, (part) =>
    part
      .replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "$1/$2")
      .replace(/\\sqrt\{([^{}]+)\}/g, "√($1)")
      .replace(/\\text\{([^{}]*)\}/g, "$1")
      .replace(/\\boxed\{([^{}]*)\}/g, "$1")
      .replace(/\\times/g, "×")
      .replace(/\\div/g, "÷")
      .replace(/\\approx/g, "≈")
      .replace(/\\pi/g, "π")
      .replace(/\\quad/g, " ")
      .replace(/\\,/g, " ")
      .replace(/[ \t]{2,}/g, " ")
  );
}

interface MathTextProps {
  /** Texte à rendre — supporte Markdown et LaTeX ($...$ inline, $$...$$ bloc) */
  children: string;
  className?: string;
  /** Taille du texte — héritée par défaut */
  size?: "sm" | "base" | "lg" | "xl";
}

const sizeClasses = {
  sm: "text-sm",
  base: "text-base",
  lg: "text-lg",
  xl: "text-xl",
};

/**
 * Composant MathText — Rendu Markdown + LaTeX/KaTeX
 *
 * Supporte :
 * - Texte brut (rendu tel quel)
 * - Markdown (gras, italique, listes, code inline)
 * - LaTeX inline : $a^2 + b^2 = c^2$
 * - LaTeX bloc  : $$\frac{a}{b}$$
 *
 * Stylé pour s'intégrer dans le design glassmorphism actuel.
 * Utilisé dans ExerciseSolver et ChallengeSolver.
 */
export function MathText({ children, className, size = "base" }: MathTextProps) {
  if (!children) return null;

  const sanitized = renderLooseLatexAsReadableText(
    sanitizeBrokenLatexBlocks(
      sanitizeLatexFractions(normalizeLatexDelimiters(restoreJsonEscapedLatexCommands(children)))
    )
  );

  return (
    <div
      className={cn(
        "math-text prose prose-neutral dark:prose-invert max-w-none",
        // Hérite la couleur du contexte (text-foreground du parent)
        "text-inherit [&_p]:m-0 [&_p]:leading-relaxed",
        "[&_strong]:text-inherit [&_strong]:font-semibold",
        "[&_em]:opacity-80",
        "[&_code]:bg-foreground/10 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:rounded [&_code]:text-primary [&_code]:text-sm [&_code]:font-mono",
        // KaTeX display math centré
        "[&_.katex-display]:my-4 [&_.katex-display]:overflow-x-auto",
        // Erreurs KaTeX : rester neutres et lisibles, jamais rouges agressives
        "[&_.katex-error]:!text-inherit [&_.katex-error]:whitespace-pre-wrap [&_.katex-error]:break-words",
        // Taille
        sizeClasses[size],
        className
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[[rehypeKatex, { strict: "ignore", throwOnError: false }]]}
      >
        {sanitized}
      </ReactMarkdown>
    </div>
  );
}
