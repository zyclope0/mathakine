import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessagesView } from "@/components/chat/ChatMessagesView";

const ASSISTANT_IMG_NAME = /Illustration générée par l'assistant/i;

describe("ChatMessagesView", () => {
  it("shows the loader while hiding empty assistant placeholders", () => {
    const { container } = render(
      <ChatMessagesView
        messages={[
          { id: "u1", role: "user", content: "Bonjour" },
          { id: "a1", role: "assistant", content: "" },
        ]}
        variant="embedded"
        isAwaitingAssistant={true}
      />
    );

    expect(screen.getByLabelText("loading")).toBeInTheDocument();
    expect(screen.getByText("Bonjour")).toBeInTheDocument();
    expect(container.querySelectorAll(".prose")).toHaveLength(1);
  });

  it("renders assistant image messages even before text arrives", () => {
    render(
      <ChatMessagesView
        messages={[
          {
            id: "a1",
            role: "assistant",
            content: "",
            imageUrl: "https://cdn.example.com/math-image.png",
          },
        ]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );

    const img = screen.getByRole("img", { name: ASSISTANT_IMG_NAME });
    expect(img).toHaveAttribute("src", "https://cdn.example.com/math-image.png");
    expect(img).toHaveClass("max-h-64", "w-full", "rounded-lg", "object-cover");
  });

  it("renders assistant text and image together with spacing wrapper", () => {
    render(
      <ChatMessagesView
        messages={[
          {
            id: "a1",
            role: "assistant",
            content: "Voir la figure ci-dessus.",
            imageUrl: "https://cdn.example.com/fig.png",
          },
        ]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );

    expect(screen.getByText(/Voir la figure ci-dessus/)).toBeInTheDocument();
    const img = screen.getByRole("img", { name: ASSISTANT_IMG_NAME });
    expect(img.parentElement).toHaveClass("mb-3");
  });

  it("uses native img for HTTPS URL outside next remotePatterns (arbitrary SSE host)", () => {
    const src = "https://unknown-cdn.example.org/chat-out.png";
    render(
      <ChatMessagesView
        messages={[{ id: "a1", role: "assistant", content: "", imageUrl: src }]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );
    const img = screen.getByRole("img", { name: ASSISTANT_IMG_NAME });
    expect(img.tagName).toBe("IMG");
    expect(img).toHaveAttribute("src", src);
  });

  it("uses native img for blob: URLs", () => {
    const src = "blob:http://localhost/uuid-test";
    render(
      <ChatMessagesView
        messages={[{ id: "a1", role: "assistant", content: "", imageUrl: src }]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );
    expect(screen.getByRole("img", { name: ASSISTANT_IMG_NAME })).toHaveAttribute("src", src);
  });

  it("uses native img for data: URLs", () => {
    const src = "data:image/png;base64,iVBORw0KGgo=";
    render(
      <ChatMessagesView
        messages={[{ id: "a1", role: "assistant", content: "", imageUrl: src }]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );
    expect(screen.getByRole("img", { name: ASSISTANT_IMG_NAME })).toHaveAttribute("src", src);
  });

  it("renders assistant inline LaTeX with KaTeX", () => {
    const { container } = render(
      <ChatMessagesView
        messages={[
          {
            id: "a1",
            role: "assistant",
            content: "Droïde A : $12\\ \\text{u/s}$",
          },
        ]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );

    expect(container.querySelector(".katex")).not.toBeNull();
    expect(container.textContent).toContain("Droïde A");
  });

  it("exposes error messages with role alert", () => {
    render(
      <ChatMessagesView
        messages={[
          {
            id: "a1",
            role: "assistant",
            content: "Impossible de joindre le service.",
            error: true,
          },
        ]}
        variant="embedded"
        isAwaitingAssistant={false}
      />
    );
    expect(screen.getByRole("alert")).toHaveTextContent(/Impossible de joindre/);
  });

  describe("layout variant parity for assistant image", () => {
    it("embedded: image row uses items-end gap-2", () => {
      const { container } = render(
        <ChatMessagesView
          messages={[
            {
              id: "a1",
              role: "assistant",
              content: "",
              imageUrl: "https://cdn.example.com/e.png",
            },
          ]}
          variant="embedded"
          isAwaitingAssistant={false}
        />
      );
      const row = screen.getByRole("img", { name: ASSISTANT_IMG_NAME }).closest(".flex");
      expect(row).toHaveClass("items-end", "gap-2");
      expect(container.querySelector(".flex.gap-3")).toBeNull();
    });

    it("drawer: image row uses gap-3 (drawer shell)", () => {
      const { container } = render(
        <ChatMessagesView
          messages={[
            {
              id: "a1",
              role: "assistant",
              content: "",
              imageUrl: "https://cdn.example.com/d.png",
            },
          ]}
          variant="drawer"
          isAwaitingAssistant={false}
        />
      );
      const row = screen.getByRole("img", { name: ASSISTANT_IMG_NAME }).closest(".flex");
      expect(row).toHaveClass("gap-3");
      expect(row).not.toHaveClass("items-end");
      expect(container.querySelector(".flex.h-8.w-8.shrink-0")).toBeTruthy();
    });
  });
});
