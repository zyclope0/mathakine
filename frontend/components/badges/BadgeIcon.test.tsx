import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { BadgeIcon } from "@/components/badges/BadgeIcon";

vi.mock("next/image", () => ({
  default: ({
    onError,
    src,
    alt,
    width,
    height,
    className,
  }: {
    onError?: React.ReactEventHandler<HTMLImageElement>;
    src: string;
    alt?: string;
    width?: number;
    height?: number;
    className?: string;
  }) => (
    // Test double for next/image — not product markup.
    // eslint-disable-next-line @next/next/no-img-element -- mock renders as img for onError tests
    <img
      data-testid="next-image"
      src={src}
      alt={alt ?? ""}
      width={width}
      height={height}
      className={className}
      onError={onError}
    />
  ),
}));

describe("BadgeIcon", () => {
  it("renders local SVG mask when code maps to a local path", () => {
    const { container } = render(<BadgeIcon code="premiers_pas" category="special" isEarned />);
    const masked = container.querySelector("[style*='mask']");
    expect(masked).toBeTruthy();
    expect(masked).toHaveClass("bg-current");
  });

  it("renders next/image for allowed remote URL when there is no local SVG (no code)", () => {
    render(
      <BadgeIcon
        code={null}
        iconUrl="https://my-service.onrender.com/badge.png"
        category="mastery"
      />
    );
    const img = screen.getByTestId("next-image");
    expect(img).toHaveAttribute("src", "https://my-service.onrender.com/badge.png");
  });

  it("renders plain img for CDN URL outside remotePatterns", () => {
    render(
      <BadgeIcon code={undefined} iconUrl="https://cdn.example.com/b.png" category="progression" />
    );
    expect(screen.queryByTestId("next-image")).toBeNull();
    const img = document.querySelector('img[src="https://cdn.example.com/b.png"]');
    expect(img).toBeTruthy();
  });

  it("shows category emoji after image load error on remote branch (React state, no DOM append)", () => {
    render(<BadgeIcon code="" iconUrl="https://cdn.example.com/missing.png" category="mastery" />);
    const img = document.querySelector("img");
    expect(img).toBeTruthy();
    fireEvent.error(img!);
    expect(screen.getByText("⭐")).toBeInTheDocument();
  });

  it("shows emoji when no local path and no http iconUrl", () => {
    render(<BadgeIcon code="" category="special" />);
    expect(screen.getByText("✨")).toBeInTheDocument();
  });
});
