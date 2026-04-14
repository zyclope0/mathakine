import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { AlphaBanner } from "./AlphaBanner";

describe("AlphaBanner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("affiche la bannière si elle n'a pas été fermée", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue(null);

    render(<AlphaBanner />);

    expect(await screen.findByText("Version Alpha")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Signaler/i })).toBeInTheDocument();
  });

  it("masque la bannière si elle a déjà été fermée", async () => {
    vi.mocked(localStorage.getItem).mockReturnValue("true");

    render(<AlphaBanner />);

    await waitFor(() => {
      expect(screen.queryByText("Version Alpha")).not.toBeInTheDocument();
    });
  });
});
