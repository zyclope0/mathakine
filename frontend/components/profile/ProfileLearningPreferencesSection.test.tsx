import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NextIntlClientProvider } from "next-intl";
import type { ReactNode } from "react";
import fr from "@/messages/fr.json";
import { ProfileLearningPreferencesSection } from "./ProfileLearningPreferencesSection";
import type { LearningPrefsState } from "@/hooks/useProfilePageController";

const baseLearningPrefs: LearningPrefsState = {
  grade_system: "unifie",
  grade_level: "5",
  age_group: "9-11",
  learning_style: "visuel",
  preferred_difficulty: "9-11",
  learning_goal: "progresser",
  practice_rhythm: "20min_jour",
};

const baseUser = {
  grade_system: "unifie",
  grade_level: 5,
  age_group: "9-11",
  learning_style: "visuel",
  preferred_difficulty: "9-11",
  learning_goal: "progresser",
  practice_rhythm: "20min_jour",
};

function wrapper({ children }: { children: ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      {children}
    </NextIntlClientProvider>
  );
}

describe("ProfileLearningPreferencesSection", () => {
  it("renders section title and read-only rows", () => {
    render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing={false}
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => `Âge ${g}`}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />,
      { wrapper }
    );

    expect(screen.getByText(fr.profile.learningPreferences.title)).toBeInTheDocument();
    expect(screen.getAllByText(fr.profile.learningPreferences.gradeLevel).length).toBeGreaterThan(
      0
    );
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("calls onStartEditing when Modifier is clicked", async () => {
    const user = userEvent.setup();
    const onStartEditing = vi.fn();
    render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing={false}
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => g}
        onStartEditing={onStartEditing}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />,
      { wrapper }
    );

    await user.click(screen.getByRole("button", { name: fr.profile.actions.edit }));
    expect(onStartEditing).toHaveBeenCalledTimes(1);
  });

  it("shows save/cancel actions in edit mode", () => {
    render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => g}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />,
      { wrapper }
    );

    expect(screen.getByRole("button", { name: fr.profile.actions.save })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: fr.profile.actions.cancel })).toBeInTheDocument();
  });

  it("shows saving state on save button when isUpdatingProfile", () => {
    render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile
        getAgeDisplay={(g) => g}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />,
      { wrapper }
    );

    expect(screen.getByText(fr.profile.actions.saving)).toBeInTheDocument();
  });

  it("calls onSave and onCancel from edit actions", async () => {
    const user = userEvent.setup();
    const onSave = vi.fn();
    const onCancel = vi.fn();
    render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => g}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={onSave}
        onCancel={onCancel}
      />,
      { wrapper }
    );

    await user.click(screen.getByRole("button", { name: fr.profile.actions.save }));
    await user.click(screen.getByRole("button", { name: fr.profile.actions.cancel }));
    expect(onSave).toHaveBeenCalledTimes(1);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("shows age group band block only for unifie in edit mode", () => {
    const { rerender } = render(
      <ProfileLearningPreferencesSection
        user={baseUser}
        isEditing
        learningPrefs={baseLearningPrefs}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => g}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />,
      { wrapper }
    );

    expect(screen.getByText(fr.profile.learningPreferences.ageGroupBand)).toBeInTheDocument();

    rerender(
      <ProfileLearningPreferencesSection
        user={{ ...baseUser, grade_system: "suisse" }}
        isEditing
        learningPrefs={{ ...baseLearningPrefs, grade_system: "suisse", age_group: "" }}
        isUpdatingProfile={false}
        getAgeDisplay={(g) => g}
        onStartEditing={vi.fn()}
        onLearningPrefsChange={vi.fn()}
        onSave={vi.fn()}
        onCancel={vi.fn()}
      />
    );

    expect(screen.queryByText(fr.profile.learningPreferences.ageGroupBand)).toBeNull();
  });
});
