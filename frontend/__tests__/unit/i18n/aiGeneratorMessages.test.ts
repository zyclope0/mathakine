import { describe, expect, it } from "vitest";
import fr from "@/messages/fr.json";
import en from "@/messages/en.json";

describe("AI generator messages", () => {
  it("expose la clé close pour le générateur IA des défis en français et en anglais", () => {
    expect(fr.challenges.aiGenerator.close).toBe("Fermer");
    expect(en.challenges.aiGenerator.close).toBe("Close");
  });
});
