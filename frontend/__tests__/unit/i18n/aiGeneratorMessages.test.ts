import { describe, expect, it } from "vitest";
import fr from "@/messages/fr.json";
import en from "@/messages/en.json";

describe("AI generator messages", () => {
  it("expose la clé close pour le générateur IA des défis en français et en anglais", () => {
    expect(fr.challenges.aiGenerator.close).toBe("Fermer");
    expect(en.challenges.aiGenerator.close).toBe("Close");
  });

  it("expose les clés IA13a (persisted / warnings) exercices et défis", () => {
    expect(fr.exercises.aiGenerator.exerciseNotPersisted).toBeTruthy();
    expect(en.exercises.aiGenerator.exerciseNotPersisted).toBeTruthy();
    expect(fr.challenges.aiGenerator.challengeNotPersisted).toBeTruthy();
    expect(en.challenges.aiGenerator.challengeNotPersisted).toBeTruthy();
  });
});
