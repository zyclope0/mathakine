"use client";

import { useEffect, useState, useMemo } from "react";
import { Users, ArrowRight, Calendar, CheckSquare, Grid3x3 } from "lucide-react";
import { useTranslations } from "next-intl";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DeductionRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string;
  onAnswerChange?: (answer: string) => void;
}

/**
 * Renderer pour les défis de déduction logique.
 * Affiche les entités, leurs attributs et une interface de réponse interactive.
 */
export function DeductionRenderer({
  visualData,
  className = "",
  onAnswerChange,
}: DeductionRendererProps) {
  const t = useTranslations("challenges.visualizations.deduction");
  const [mounted, setMounted] = useState(false);
  const [selections, setSelections] = useState<Record<string, Record<string, string>>>({});

  useEffect(() => {
    setMounted(true);
  }, []);

  // Extraire les données structurées
  const friends = Array.isArray(visualData?.friends) ? visualData.friends : [];
  const ages = Array.isArray(visualData?.ages) ? visualData.ages : [];
  const relationships = Array.isArray(visualData?.relationships) ? visualData.relationships : [];
  const entities = (visualData?.entities != null && typeof visualData.entities === "object" && !Array.isArray(visualData.entities) ? visualData.entities : {}) as Record<string, unknown>;
  const attributes = (visualData?.attributes != null && typeof visualData.attributes === "object" && !Array.isArray(visualData.attributes) ? visualData.attributes : {}) as Record<string, unknown>;
  const rules = Array.isArray(visualData?.rules) ? visualData.rules : relationships;
  const clues = Array.isArray(visualData?.clues) ? visualData.clues : [];
  const description: string = String(visualData?.description ?? "");
  const type: string = String(visualData?.type ?? "");

  // Détecter le format "logic_grid" avec entities comme objet
  const isLogicGrid =
    type === "logic_grid" ||
    (typeof entities === "object" && !Array.isArray(entities) && Object.keys(entities).length > 0);

  // Extraire les catégories et valeurs pour la grille logique
  const gridCategories = useMemo(() => {
    if (!isLogicGrid || typeof entities !== "object") return null;

    // entities est un objet comme { eleves: [...], matieres: [...], scores: [...] }
    const categories = Object.entries(entities).map(([key, values]) => ({
      name: key,
      displayName: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " "),
      values: Array.isArray(values)
        ? values.map((v) => (typeof v === "string" ? v : String(v)))
        : String(values)
            .split(",")
            .map((v) => v.trim()),
    }));

    return categories;
  }, [entities, isLogicGrid]);

  // Catégorie principale (première) et catégories à associer (reste)
  const primaryCategory = gridCategories?.[0];
  const secondaryCategories = gridCategories?.slice(1) || [];

  // Initialiser les sélections
  useEffect(() => {
    if (primaryCategory && secondaryCategories.length > 0 && Object.keys(selections).length === 0) {
      const initialSelections: Record<string, Record<string, string>> = {};
      primaryCategory.values.forEach((entity) => {
        initialSelections[entity] = {};
        secondaryCategories.forEach((cat) => {
          initialSelections[entity]![cat.name] = "";
        });
      });
      setSelections(initialSelections);
    }
  }, [primaryCategory, secondaryCategories, selections]);

  // Mettre à jour la réponse formatée quand les sélections changent
  useEffect(() => {
    if (onAnswerChange && primaryCategory && Object.keys(selections).length > 0) {
      // Vérifier si toutes les sélections sont faites
      const allFilled = primaryCategory.values.every((entity) =>
        secondaryCategories.every((cat) => selections[entity]?.[cat.name])
      );

      if (allFilled) {
        // Formater la réponse : "Emma:Chimie:700,Lucas:Informatique:600,..."
        const answerParts = primaryCategory.values.map((entity) => {
          const entitySelections = secondaryCategories.map(
            (cat) => selections[entity]?.[cat.name] || ""
          );
          return `${entity}:${entitySelections.join(":")}`;
        });
        onAnswerChange(answerParts.join(","));
      }
    }
  }, [selections, onAnswerChange, primaryCategory, secondaryCategories]);

  // Handler pour les changements de sélection
  const handleSelectionChange = (entity: string, category: string, value: string) => {
    setSelections((prev) => ({
      ...prev,
      [entity]: {
        ...prev[entity],
        [category]: value,
      },
    }));
  };

  // Obtenir les valeurs déjà utilisées pour une catégorie (éviter les doublons)
  const getUsedValues = (category: string, excludeEntity: string): string[] => {
    return Object.entries(selections)
      .filter(([entity]) => entity !== excludeEntity)
      .map(([, cats]) => cats[category])
      .filter((v): v is string => Boolean(v));
  };

  if (!mounted || !visualData) {
    return null;
  }

  // Cas 1 : Logic Grid (grille de déduction)
  if (isLogicGrid && primaryCategory && secondaryCategories.length > 0) {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Description */}
        {description && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
        )}

        {/* Entités et leurs valeurs possibles */}
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Grid3x3 className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("elements")}</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {gridCategories?.map((category) => (
              <div
                key={category.name}
                className="bg-background/50 border border-border rounded-md p-3"
              >
                <p className="text-sm font-semibold text-primary capitalize mb-2">
                  {category.displayName}
                </p>
                <div className="flex flex-wrap gap-1">
                  {category.values.map((value, i) => (
                    <span
                      key={i}
                      className="bg-primary/10 border border-primary/30 px-2 py-0.5 rounded text-xs text-foreground"
                    >
                      {value}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Indices */}
        {clues.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ArrowRight className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">{t("hints")}</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {clues.map((clue: string, index: number) => (
                <span
                  key={index}
                  className="bg-background/50 border border-border rounded-md px-3 py-2 text-sm text-foreground hover:border-primary/50 transition-colors"
                >
                  {clue}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Interface de réponse interactive */}
        {onAnswerChange && (
          <div className="bg-gradient-to-br from-primary/5 to-primary/10 border-2 border-primary/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-4">
              <CheckSquare className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">{t("yourAssociations")}</h4>
            </div>
            <p className="text-xs text-muted-foreground mb-4">
              {t("associateEach", { category: primaryCategory.displayName.toLowerCase() })}
            </p>

            <div className="space-y-3">
              {primaryCategory.values.map((entity) => (
                <div key={entity} className="bg-card/80 border border-border rounded-lg p-3">
                  <div className="flex flex-wrap items-center gap-3">
                    {/* Nom de l'entité principale */}
                    <div className="min-w-[100px] font-medium text-foreground">{entity}</div>

                    {/* Sélecteurs pour chaque catégorie secondaire */}
                    {secondaryCategories.map((category) => {
                      const usedValues = getUsedValues(category.name, entity);
                      const currentValue = selections[entity]?.[category.name] || "";

                      return (
                        <div key={category.name} className="flex-1 min-w-[120px]">
                          <Select
                            value={currentValue}
                            onValueChange={(value) =>
                              handleSelectionChange(entity, category.name, value)
                            }
                          >
                            <SelectTrigger className="w-full bg-background border-primary/20 hover:border-primary/50">
                              <SelectValue placeholder={category.displayName} />
                            </SelectTrigger>
                            <SelectContent>
                              {category.values.map((value) => {
                                const isUsed = usedValues.includes(value) && value !== currentValue;
                                return (
                                  <SelectItem
                                    key={value}
                                    value={value}
                                    disabled={isUsed}
                                    className={isUsed ? "opacity-50" : ""}
                                  >
                                    {value} {isUsed && t("alreadyUsed")}
                                  </SelectItem>
                                );
                              })}
                            </SelectContent>
                          </Select>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>

            {/* Indicateur de progression */}
            <div className="mt-4 text-xs text-muted-foreground text-center">
              {(() => {
                const totalSelections = primaryCategory.values.length * secondaryCategories.length;
                const madeSelections = Object.values(selections).reduce(
                  (acc, cats) => acc + Object.values(cats).filter(Boolean).length,
                  0
                );
                return t("associationsCompleted", {
                  made: String(madeSelections),
                  total: String(totalSelections),
                });
              })()}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Cas 2 : Données de type "friends + ages + relationships"
  if (friends.length > 0 && ages.length > 0) {
    return (
      <div className={`space-y-6 ${className}`}>
        {/* Liste des personnes */}
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("peopleAndAges")}</h4>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {friends.map((friend: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                <div className="font-medium text-foreground">{friend}</div>
                {ages[index] && (
                  <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                    <Calendar className="h-3 w-3" />
                    <span>
                      {ages[index]} {t("years")}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Relations logiques */}
        {relationships.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ArrowRight className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">{t("relationships")}</h4>
            </div>
            <div className="space-y-2">
              {relationships.map((rel: Record<string, unknown>, index: number) => (
                <div
                  key={index}
                  className="bg-background/50 border border-border rounded-md p-3 flex items-center gap-2 hover:border-primary/50 transition-colors"
                >
                  <span className="font-medium text-primary">{String(rel.name ?? rel.subject ?? "")}</span>
                  <span className="text-muted-foreground text-sm">{String(rel.relation ?? "est")}</span>
                  <span className="font-medium text-foreground">{String(rel.target ?? rel.object ?? "")}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Cas 3 : Données génériques avec entités en tableau
  if (Array.isArray(entities) && entities.length > 0) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">{t("entities")}</h4>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {entities.map((entity: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
              >
                <div className="font-medium text-foreground">{entity}</div>
                {Boolean(attributes[entity]) && (
                  <div className="text-sm text-muted-foreground mt-1">
                    {typeof attributes[entity] === "object" && attributes[entity] !== null
                      ? Object.entries(attributes[entity] as Record<string, unknown>).map(([key, value]) => (
                          <div key={key}>
                            {key}: {String(value)}
                          </div>
                        ))
                      : String(attributes[entity])}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Règles logiques */}
        {rules.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <ArrowRight className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">{t("rules")}</h4>
            </div>
            <div className="space-y-2">
              {rules.map((rule: string | Record<string, unknown>, index: number) => (
                <div
                  key={index}
                  className="bg-background/50 border border-border rounded-md p-3 hover:border-primary/50 transition-colors"
                >
                  {typeof rule === "string" ? (
                    <span className="text-foreground">{rule}</span>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-primary">{String(rule.name ?? rule.subject ?? "")}</span>
                      <span className="text-muted-foreground text-sm">
                        {String(rule.relation ?? "est")}
                      </span>
                      <span className="font-medium text-foreground">
                        {String(rule.target ?? rule.object ?? "")}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Fallback : afficher les données structurées de manière plus claire
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Afficher les props disponibles de manière structurée */}
      <div className="bg-card/50 border border-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Users className="h-5 w-5 text-primary" />
          <h4 className="font-semibold text-foreground">{t("challengeData")}</h4>
        </div>
        <div className="space-y-3">
          {Object.entries(visualData).map(([key, value]) => {
            // Arrays
            if (Array.isArray(value) && value.length > 0) {
              return (
                <div key={key} className="bg-background/50 border border-border rounded-md p-3">
                  <p className="text-sm font-semibold text-primary capitalize mb-2">
                    {key.replace(/_/g, " ")}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {value.map((item: unknown, i: number) => (
                      <span
                        key={i}
                        className="bg-primary/10 border border-primary/30 px-2 py-1 rounded text-sm text-foreground"
                      >
                        {typeof item === "object" && item !== null
                          ? String((item as Record<string, unknown>).name ?? (item as Record<string, unknown>).value ?? JSON.stringify(item))
                          : String(item)}
                      </span>
                    ))}
                  </div>
                </div>
              );
            }
            // Objects
            if (value && typeof value === "object" && !Array.isArray(value)) {
              return (
                <div key={key} className="bg-background/50 border border-border rounded-md p-3">
                  <p className="text-sm font-semibold text-primary capitalize mb-2">
                    {key.replace(/_/g, " ")}
                  </p>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {Object.entries(value).map(([subKey, subValue]) => (
                      <div key={subKey} className="flex gap-2">
                        <span className="text-muted-foreground">{subKey}:</span>
                        <span className="text-foreground font-medium">{String(subValue)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
            // Primitives
            return (
              <div key={key} className="flex items-center gap-2 text-sm">
                <span className="font-semibold text-primary capitalize">
                  {key.replace(/_/g, " ")}:
                </span>
                <span className="text-foreground">{String(value)}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
