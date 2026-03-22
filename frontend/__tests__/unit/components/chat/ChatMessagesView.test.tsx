import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatMessagesView } from "@/components/chat/ChatMessagesView";

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

    expect(screen.getByAltText("Illustration générée par l'assistant")).toBeInTheDocument();
  });
});
