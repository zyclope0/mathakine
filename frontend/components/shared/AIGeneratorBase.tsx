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

  return (
    <Card className="h-full border-white/10 bg-card/40 backdrop-blur-md shadow-lg">
      <CardHeader className="pb-3">
        {/* En-tête avec icône dans conteneur stylisé */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10 flex-shrink-0">
            <Sparkles className="h-5 w-5 text-primary" aria-hidden="true" />
          </div>
          <div>
            <CardTitle className="text-primary-on-dark text-sm md:text-base">{title}</CardTitle>
            <CardDescription className="text-xs hidden sm:block">{description}</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3 pt-0">
        <div className="max-w-4xl mx-auto space-y-3">
          {/* Sélecteurs type + groupe d'âge — côte à côte */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label
                htmlFor={typeSelectId}
                className="block text-xs font-medium text-muted-foreground"
              >
                {typeLabel}
              </label>
              <Select value={selectedType} onValueChange={setSelectedType} disabled={isGenerating}>
                <SelectTrigger
                  id={typeSelectId}
                  className="w-full h-8 text-xs bg-background text-foreground border-primary/30"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-primary/30">
                  {typeOptions.map((opt) => (
                    <SelectItem
                      key={opt.value}
                      value={opt.value}
                      className="text-foreground hover:bg-primary/10"
                    >
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
                <SelectTrigger
                  id={ageSelectId}
                  className="w-full h-8 text-xs bg-background text-foreground border-primary/30"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-card border-primary/30">
                  {ageOptions.map((opt) => (
                    <SelectItem
                      key={opt.value}
                      value={opt.value}
                      className="text-foreground hover:bg-primary/10"
                    >
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Prompt personnalisé — pleine largeur */}
          <div className="space-y-1">
            <label htmlFor="ai-prompt" className="block text-xs font-medium text-muted-foreground">
              {promptLabel}
            </label>
            <Textarea
              id="ai-prompt"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder={promptPlaceholder}
              className="text-xs bg-background text-foreground border-primary/30 min-h-[60px] resize-none transition-all focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:border-primary"
              disabled={isGenerating}
              rows={3}
            />

            {/* Suggestions d'inspiration */}
            {promptSuggestions.length > 0 && (
              <div className="pt-2">
                <p className="text-xs text-muted-foreground/70 mb-1.5">
                  Manque d&apos;inspiration ?
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {promptSuggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => setCustomPrompt(suggestion)}
                      disabled={isGenerating}
                      className="text-xs bg-white/5 hover:bg-white/10 text-muted-foreground px-3 py-1 rounded-full cursor-pointer transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Indicateur de streaming + bouton annuler inline */}
          {isGenerating && (
            <div className="p-3 rounded-lg bg-card border border-primary/20 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
              <p className="flex-1 text-xs text-muted-foreground">
                {streamedText || generatingLabel}
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={onCancel}
                className="h-6 w-6 p-0 flex-shrink-0"
                aria-label={cancelLabel}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          )}

          {/* Résultat généré */}
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

          {/* Bandeau auth (variante challenges) */}
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

          {/* Bouton générer — centré, taille auto */}
          <div className="flex justify-center">
            <Button
              onClick={handleGenerate}
              disabled={isDisabled}
              className="btn-cta-primary h-8 text-xs px-8 shadow-[0_0_14px_hsl(var(--primary)/0.35)] hover:shadow-[0_0_20px_hsl(var(--primary)/0.45)]"
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
