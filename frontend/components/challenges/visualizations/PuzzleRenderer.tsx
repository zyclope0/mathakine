"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Puzzle, GripVertical } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  DndContext,
  closestCenter,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  pointerWithin,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import {
  itemDisplayLabel,
  itemLabel,
  itemOrderKey,
} from "@/components/challenges/visualizations/_itemLabel";

interface PuzzleRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
  onOrderChange?: ((order: string[]) => void) | undefined;
}

interface SortableItemProps {
  id: string;
  value: string;
  index: number;
}

/**
 * ``orderKey`` : clé courte envoyée dans ``correct_answer`` (ex. "P1", "P2").
 *     Priorité stricte à ``id`` / ``piece_id`` pour rester matchable côté
 *     backend, même si la pièce expose aussi ``name`` / ``label`` éditorial.
 * ``displayLabel`` : libellé affiché à l'élève, enrichi avec les champs
 *     descriptifs (``left`` / ``right`` / ``pattern`` …) pour rester solvable.
 * Les deux DOIVENT être séparés — sinon l'élève voit ``P1 P2 …`` sans
 * contenu pédagogique et le puzzle devient insoluble (cf. défi #4071).
 */
interface PuzzleItem {
  id: string;
  value: string;
  displayLabel: string;
  original: Record<string, unknown>;
}

/**
 * Pure function — construction d'un PuzzleItem. Déclarée hors du composant
 * pour éviter sa re-création à chaque render (cf. review P1 : dnd-kit
 * déclenche plusieurs renders par geste).
 */
function buildPuzzleItem(p: unknown, i: number): PuzzleItem {
  const orderKey = itemOrderKey(p, { fallback: `#${i + 1}` });
  const display = itemDisplayLabel(p, { fallback: orderKey });
  return {
    id: `item-${i}`,
    value: orderKey,
    displayLabel: display || orderKey,
    original: p && typeof p === "object" && !Array.isArray(p) ? (p as Record<string, unknown>) : {},
  };
}

/** Collision : pointer d'abord (où on relâche = cible), sinon plus proche centre */
function pointerWithinOrClosestCenter(
  args: Parameters<typeof pointerWithin>[0]
): ReturnType<typeof pointerWithin> {
  const pointerResult = pointerWithin(args);
  if (pointerResult.length > 0) return pointerResult;
  return closestCenter(args);
}

/** Composant présentatif pour le DragOverlay (n'utilise pas useSortable) */
function PuzzleItemPreview({ value, index }: { value: string; index: number }) {
  return (
    <div className="flex items-center gap-3 p-3 bg-card border-2 border-primary rounded-lg shadow-lg cursor-grabbing min-w-[200px]">
      <GripVertical className="h-5 w-5 text-muted-foreground flex-shrink-0" />
      <span className="flex-1 text-foreground font-medium">{value}</span>
      <span className="text-xs text-muted-foreground">#{index + 1}</span>
    </div>
  );
}

function SortableItem({ id, value, index }: SortableItemProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-3 p-3 bg-card border-2 rounded-lg transition-colors cursor-grab active:cursor-grabbing ${
        isDragging
          ? "border-primary/50 border-dashed bg-primary/5"
          : "border-primary/30 hover:border-primary/50"
      }`}
      whileHover={{ scale: isDragging ? 1 : 1.01 }}
      whileTap={{ scale: isDragging ? 1 : 0.99 }}
      {...attributes}
      {...listeners}
    >
      <GripVertical className="h-5 w-5 text-muted-foreground flex-shrink-0" />
      <span className="flex-1 text-foreground font-medium">{value}</span>
      <span className="text-xs text-muted-foreground">#{index + 1}</span>
    </motion.div>
  );
}

/**
 * Renderer pour les défis de type PUZZLE.
 * Interface drag & drop pour réorganiser les pièces avec @dnd-kit.
 */
export function PuzzleRenderer({ visualData, className, onOrderChange }: PuzzleRendererProps) {
  const t = useTranslations("challenges.visualizations.puzzle");

  // Parser les données de puzzle
  const pieces = Array.isArray(visualData?.pieces)
    ? visualData.pieces
    : Array.isArray(visualData?.items)
      ? visualData.items
      : Array.isArray(visualData?.parts)
        ? visualData.parts
        : [];

  // Parser les indices pour aider à résoudre le puzzle
  const hints = Array.isArray(visualData?.hints)
    ? visualData.hints
    : Array.isArray(visualData?.rules)
      ? visualData.rules
      : Array.isArray(visualData?.clues)
        ? visualData.clues
        : Array.isArray(visualData?.indices)
          ? visualData.indices
          : [];
  // Description via ``itemLabel`` : évite un leak ``[object Object]`` si le
  // LLM renvoie ``description`` comme objet ``{ text: "..." }`` au lieu d'une
  // chaîne plate — cohérent avec ADR-006.
  const description: string = itemLabel(visualData?.description);

  // Ref sur onOrderChange : **déclarée avant** les useEffect qui la
  // consomment, pour éviter le couplage temporel fragile (review P1).
  const onOrderChangeRef = useRef(onOrderChange);
  useEffect(() => {
    onOrderChangeRef.current = onOrderChange;
  }, [onOrderChange]);

  const [items, setItems] = useState<PuzzleItem[]>(() => pieces.map(buildPuzzleItem));
  const [activeId, setActiveId] = useState<string | null>(null);

  // Réinitialiser l'ordre quand visualData change
  useEffect(() => {
    const newItems: PuzzleItem[] = pieces.map(buildPuzzleItem);
    setItems(newItems);
    // Notifier le parent en différé pour éviter "Cannot update while rendering"
    const order = newItems.map((item: PuzzleItem) => item.value);
    queueMicrotask(() => {
      onOrderChangeRef.current?.(order);
    });
    // exhaustive-deps: onOrderChange via ref ; pieces dérivé de visualData — éviter reset sur identité du tableau seule.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pieces.length, visualData]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(String(event.active.id));
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        const newItems = arrayMove(items, oldIndex, newIndex);
        const order = newItems.map((item) => item.value);
        queueMicrotask(() => onOrderChangeRef.current?.(order));
        return newItems;
      });
    }
    setActiveId(null);
  };

  // Notifier le parent de l'ordre initial uniquement au montage (différé).
  // Passe par la ref pour rester cohérent avec les autres callsites et
  // absorber un remplacement de ``onOrderChange`` entre mount et microtask.
  useEffect(() => {
    const initialOrder = items.map((item) => item.value);
    queueMicrotask(() => onOrderChangeRef.current?.(initialOrder));
    // exhaustive-deps: intentionnel au montage seulement — inclure items/onOrderChange recréerait des boucles avec le parent.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!pieces || pieces.length === 0) {
    return (
      <Card flat className={`bg-card border-primary/20 ${className || ""}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          {t("emptyState")}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card flat className={`bg-card border-primary/20 ${className || ""}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Puzzle className="h-5 w-5 text-primary" aria-hidden="true" />
            <h4 className="section-title-sm min-w-0">{t("title")}</h4>
            <span className="text-xs text-muted-foreground ml-auto text-right">
              {t("dragHint")}
            </span>
          </div>

          {/* Afficher la description si disponible */}
          {description && (
            <div className="bg-muted/30 rounded-lg p-3 text-sm text-foreground">{description}</div>
          )}

          {/* Afficher les indices pour aider à résoudre */}
          {hints && hints.length > 0 && (
            <div className="bg-primary/5 border border-primary/20 rounded-lg p-3 space-y-2">
              <h5 className="section-label-primary">{t("hintsHeading")}</h5>
              <ul className="space-y-1">
                {hints.map((hint: unknown, idx: number) => (
                  <li key={idx} className="text-sm text-foreground flex items-start gap-2">
                    <span className="text-primary font-bold">{idx + 1}.</span>
                    <span>{itemLabel(hint)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <DndContext
            sensors={sensors}
            collisionDetection={pointerWithinOrClosestCenter}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <SortableContext
              items={items.map((item) => item.id)}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-2">
                {items.map((item, index) => (
                  <SortableItem
                    key={item.id}
                    id={item.id}
                    value={item.displayLabel}
                    index={index}
                  />
                ))}
              </div>
            </SortableContext>
            <DragOverlay
              dropAnimation={{
                duration: 150,
                easing: "cubic-bezier(0.22, 1, 0.36, 1)",
              }}
            >
              {activeId
                ? (() => {
                    const item = items.find((i) => i.id === activeId);
                    const idx = items.findIndex((i) => i.id === activeId);
                    return item ? (
                      <PuzzleItemPreview value={item.displayLabel} index={idx >= 0 ? idx : 0} />
                    ) : null;
                  })()
                : null}
            </DragOverlay>
          </DndContext>

          <div className="text-xs text-center text-muted-foreground">
            Réorganisez les éléments dans le bon ordre
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
