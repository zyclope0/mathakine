import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MathText } from "@/components/ui/MathText";

describe("MathText", () => {
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
