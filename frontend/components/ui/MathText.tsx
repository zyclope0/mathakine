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

  const sanitized = sanitizeLatexFractions(children);

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
        // Taille
        sizeClasses[size],
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
        {sanitized}
      </ReactMarkdown>
    </div>
  );
}
