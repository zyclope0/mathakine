import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MathText } from "@/components/ui/MathText";

describe("MathText", () => {
  it("rend les délimiteurs LaTeX IA \\[...\\] au lieu d'afficher les crochets bruts", () => {
    const explanation = String.raw`1. Surface latérale du cylindre :
\[A_1 = 2\pi r h = 2\pi \times 250 \times 600 = 300000\pi \approx 942478 \text{cm}^2\]`;

    const { container } = render(<MathText>{explanation}</MathText>);

    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.querySelector(".katex-display")).not.toBeNull();
    expect(container.innerHTML).not.toContain("\\[");
    expect(container.innerHTML).not.toContain("\\]");
  });

  it("rend les délimiteurs LaTeX IA \\(...\\) en inline math", () => {
    const { container } = render(
      <MathText>{String.raw`La génératrice vaut \(l = \sqrt{250^2 + 400^2}\).`}</MathText>
    );

    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.innerHTML).not.toContain("\\(");
    expect(container.innerHTML).not.toContain("\\)");
  });

  it("dégrade un bloc cases cassé sans afficher d'erreur KaTeX rouge", () => {
    const malformed = String.raw`Plus formellement :

$$\text{Étape } 2n-1 &: a_{k}=a_{k-1}+n^{2},\\[4pt]\text{Étape } 2n &: a_{k}=a_{k-1}\times (n+1). \end{cases}$$

Ainsi le terme suivant vaut \boxed{980}.`;

    const { container } = render(<MathText>{malformed}</MathText>);

    expect(screen.getByText(/Étape 2n-1/i)).toBeInTheDocument();
    expect(screen.getByText(/980/)).toBeInTheDocument();
    expect(container.querySelector(".katex-error")).not.toBeInTheDocument();
  });
});
