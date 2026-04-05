"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles, X, AlertCircle } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AIGeneratorStreamingRow,
  AIGeneratorSuccessRowCompact,
} from "@/components/shared/aiGeneratorSharedUi";

export interface AISelectOption {
  value: string;
  label: string;
}

export interface AIGeneratedItem {
  id?: number;
  title: string;
  subtitle?: string;
}

/** Suggestions d'inspiration par défaut pour le textarea (si aucune prop fournie). */
const DEFAULT_PROMPT_SUGGESTIONS = [
  "Un voyage sur Mars 🚀",
  "Boutique de potions 🧪",
  "Mission secrète 🕵️",
  "Course de dragons 🐉",
] as const;

export interface AIGeneratorBaseProps {
  /** Mode toolbar compact (une ligne sur desktop) */
  compact?: boolean;
  // UI strings (pre-resolved by the domain variant)
  title: string;
  description: string;
  typeLabel: string;
  typeSelectId: string;
  /** ID HTML du select groupe d'âge (doit être unique sur la page si plusieurs instances). */
  ageSelectId?: string;
  ageLabel: string;
  promptLabel: string;
  promptPlaceholder: string;
  generateLabel: string;
  generatingLabel: string;
  cancelLabel: string;
  viewItemLabel: string;
  successLabel: string;
  closeAriaLabel: string;

  // Select options
  typeOptions: AISelectOption[];
  defaultType: string;
  ageOptions: AISelectOption[];
  defaultAge: string;
  /** Mode compact uniquement : classes du trigger « groupe d'âge » (défaut h-9 w-[95px]). */
  compactAgeSelectTriggerClassName?: string;

  /** Pilules de suggestions cliquables sous le textarea (optionnel). */
  promptSuggestions?: string[];

  // Streaming state (owned by the domain variant)
  isGenerating: boolean;
  streamedText: string;
  generatedItem: AIGeneratedItem | null;

  // Callbacks
  onGenerate: (type: string, ageGroup: string, prompt: string) => void;
  onCancel: () => void;
  onViewItem: () => void;
  onDismissResult: () => void;

  // Auth
  isAuthenticated: boolean;
  isAuthLoading?: boolean;
  /** Affiche un bandeau inline si non-authentifié (challenges). Exercises utilise un toast. */
  showAuthBanner?: boolean;
  authBannerTitle?: string;
  authBannerDescription?: string;
}

/**
 * Composant UI partagé pour les générateurs IA exercices et défis.
 * La logique de streaming (EventSource vs fetch+ReadableStream) reste dans chaque variante.
 */
export function AIGeneratorBase({
  compact = false,
  title,
  description,
  typeLabel,
  typeSelectId,
  ageSelectId = "ai-age-group",
  ageLabel,
  promptLabel,
  promptPlaceholder,
  generateLabel,
  generatingLabel,
  cancelLabel,
  viewItemLabel,
  successLabel,
  closeAriaLabel,
  typeOptions,
  defaultType,
  ageOptions,
  defaultAge,
  compactAgeSelectTriggerClassName,
  promptSuggestions = [...DEFAULT_PROMPT_SUGGESTIONS],
  isGenerating,
  streamedText,
  generatedItem,
  onGenerate,
  onCancel,
  onViewItem,
  onDismissResult,
  isAuthenticated,
  isAuthLoading = false,
  showAuthBanner = false,
  authBannerTitle,
  authBannerDescription,
}: AIGeneratorBaseProps) {
  const [selectedType, setSelectedType] = useState(defaultType);
  const [selectedAge, setSelectedAge] = useState(defaultAge);
  const [customPrompt, setCustomPrompt] = useState("");

  const handleGenerate = () => {
    onGenerate(selectedType, selectedAge, customPrompt);
  };

  const isDisabled = isGenerating || (showAuthBanner && (!isAuthenticated || isAuthLoading));

  const baseClasses = "rounded-xl border border-border/50 bg-card/40 backdrop-blur-md";

  if (compact) {
    return (
      <div className="rounded-xl border border-border/30 bg-muted/40 px-4 py-3 animate-fade-in-up-delay-1">
        {/* Ligne 1 — Contrôles */}
        <div className="flex flex-row flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-shrink-0">
            <Sparkles className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" aria-hidden="true" />
            <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
          </div>

          <div className="flex items-center gap-3 flex-shrink-0">
            {showAuthBanner && !isAuthenticated && !isAuthLoading && authBannerTitle && (
              <div className="flex items-center gap-2 text-xs text-warning">
                <AlertCircle className="h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
                <span>{authBannerTitle}</span>
              </div>
            )}
            <Select value={selectedType} onValueChange={setSelectedType} disabled={isGenerating}>
              <SelectTrigger id={typeSelectId} className="h-9 w-[115px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {typeOptions.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={selectedAge} onValueChange={setSelectedAge} disabled={isGenerating}>
              <SelectTrigger
                id={ageSelectId}
                className={compactAgeSelectTriggerClassName ?? "h-9 w-[95px]"}
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ageOptions.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleGenerate} disabled={isDisabled} size="sm" className="h-9">
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                  {generatingLabel}
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" aria-hidden="true" />
                  {generateLabel}
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Ligne 2 — Prompt (input compact) */}
        <input
          type="text"
          id="ai-prompt"
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder={promptPlaceholder}
          disabled={isGenerating}
          className="mt-3 w-full h-10 bg-background/50 border border-border rounded-lg px-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label={promptLabel}
        />

        {/* Ligne 3 — Suggestions ultra-compactes */}
        {promptSuggestions.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {promptSuggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => setCustomPrompt(suggestion)}
                disabled={isGenerating}
                className="text-xs px-2 py-1 rounded-full bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {isGenerating && (
          <AIGeneratorStreamingRow
            streamedText={streamedText}
            fallbackLabel={generatingLabel}
            cancelLabel={cancelLabel}
            onCancel={onCancel}
            rootClassName="mt-3 p-2.5"
            streamParagraphClassName="truncate"
            cancelButtonClassName="flex-shrink-0"
          />
        )}

        {generatedItem && !isGenerating && (
          <AIGeneratorSuccessRowCompact
            successLabel={successLabel}
            title={generatedItem.title}
            viewItemLabel={viewItemLabel}
            onViewItem={onViewItem}
            showViewButton={!!generatedItem.id}
            onDismiss={onDismissResult}
            closeAriaLabel={closeAriaLabel}
            rootClassName="mt-3 p-2.5"
          />
        )}
      </div>
    );
  }

  return (
    <Card className={`h-full ${baseClasses}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          <div>
            <CardTitle className="text-foreground text-sm md:text-base">{title}</CardTitle>
            <CardDescription className="text-xs hidden sm:block">{description}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 pt-0">
        <div className="max-w-4xl mx-auto space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label
                htmlFor={typeSelectId}
                className="block text-xs font-medium text-muted-foreground"
              >
                {typeLabel}
              </label>
              <Select value={selectedType} onValueChange={setSelectedType} disabled={isGenerating}>
                <SelectTrigger id={typeSelectId} className="w-full h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {typeOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <label
                htmlFor={ageSelectId}
                className="block text-xs font-medium text-muted-foreground"
              >
                {ageLabel}
              </label>
              <Select value={selectedAge} onValueChange={setSelectedAge} disabled={isGenerating}>
                <SelectTrigger id={ageSelectId} className="w-full h-8 text-xs">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {ageOptions.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-1">
            <label htmlFor="ai-prompt" className="block text-xs font-medium text-muted-foreground">
              {promptLabel}
            </label>
            <Textarea
              id="ai-prompt"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder={promptPlaceholder}
              className="text-xs min-h-[60px] resize-none border-border/50"
              disabled={isGenerating}
              rows={3}
            />
            {promptSuggestions.length > 0 && (
              <div className="pt-2">
                <div className="flex flex-wrap gap-1.5">
                  {promptSuggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => setCustomPrompt(suggestion)}
                      disabled={isGenerating}
                      className="text-xs bg-muted/50 hover:bg-muted text-muted-foreground px-3 py-1 rounded-full transition-colors disabled:opacity-40"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {isGenerating && (
            <AIGeneratorStreamingRow
              streamedText={streamedText}
              fallbackLabel={generatingLabel}
              cancelLabel={cancelLabel}
              onCancel={onCancel}
              rootClassName="p-3"
            />
          )}

          {generatedItem && !isGenerating && (
            <div className="p-2 rounded-lg bg-success/10 border border-success/20">
              <div className="flex items-start justify-between mb-1">
                <p className="font-semibold text-success text-xs">{successLabel}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDismissResult}
                  className="h-6 w-6 p-0"
                  aria-label={closeAriaLabel}
                >
                  <X className="h-3 w-3" />
                </Button>
              </div>
              <p className="text-foreground font-medium text-xs mb-0.5">{generatedItem.title}</p>
              {generatedItem.subtitle && (
                <p className="text-muted-foreground text-xs mb-1.5 line-clamp-2">
                  {generatedItem.subtitle}
                </p>
              )}
              {generatedItem.id && (
                <Button onClick={onViewItem} size="sm" className="w-full h-7 text-xs">
                  {viewItemLabel}
                </Button>
              )}
            </div>
          )}

          {showAuthBanner && !isAuthenticated && !isAuthLoading && authBannerTitle && (
            <div className="p-3 rounded-lg bg-warning/10 border border-warning/30 flex items-start gap-2">
              <AlertCircle
                className="h-4 w-4 text-warning mt-0.5 flex-shrink-0"
                aria-hidden="true"
              />
              <div className="text-xs text-warning">
                <p className="font-medium mb-1">{authBannerTitle}</p>
                {authBannerDescription && <p className="opacity-80">{authBannerDescription}</p>}
              </div>
            </div>
          )}

          <div className="flex justify-center">
            <Button
              onClick={handleGenerate}
              disabled={isDisabled}
              className="btn-cta-primary h-8 text-xs px-8"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                  {generatingLabel}
                </>
              ) : (
                <>
                  <Sparkles className="mr-1.5 h-3.5 w-3.5" aria-hidden="true" />
                  {generateLabel}
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
