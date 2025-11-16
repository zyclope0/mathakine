'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Puzzle, GripVertical } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface PuzzleRendererProps {
  visualData: any;
  className?: string | undefined;
  onOrderChange?: ((order: string[]) => void) | undefined;
}

interface SortableItemProps {
  id: string;
  value: string;
  index: number;
}

interface PuzzleItem {
  id: string;
  value: string;
  original: any;
}

function SortableItem({ id, value, index }: SortableItemProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-3 p-3 bg-card border-2 border-primary/30 rounded-lg hover:border-primary/50 transition-colors cursor-grab active:cursor-grabbing"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
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
  // Parser les données de puzzle
  const pieces = visualData?.pieces || visualData?.items || visualData?.parts || [];
  
  // Initialiser les items avec un ordre mélangé pour rendre le puzzle intéressant
  const initialItems: PuzzleItem[] = pieces.map((p: any, i: number) => ({
    id: `item-${i}`,
    value: typeof p === 'object' ? p.value || p.label || JSON.stringify(p) : String(p),
    original: p,
  }));
  
  const [items, setItems] = useState<PuzzleItem[]>(initialItems);
  
  // Réinitialiser l'ordre quand visualData change
  useEffect(() => {
    const newItems: PuzzleItem[] = pieces.map((p: any, i: number) => ({
      id: `item-${i}`,
      value: typeof p === 'object' ? p.value || p.label || JSON.stringify(p) : String(p),
      original: p,
    }));
    setItems(newItems);
    // Notifier le parent du nouvel ordre initial
    if (onOrderChangeRef.current) {
      const order = newItems.map((item: PuzzleItem) => item.value);
      onOrderChangeRef.current(order);
    }
  }, [pieces.length, visualData]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setItems((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        const newItems = arrayMove(items, oldIndex, newIndex);
        
        // Notifier le parent du nouvel ordre via la ref pour éviter les re-renders infinis
        if (onOrderChangeRef.current) {
          const order = newItems.map(item => item.value);
          onOrderChangeRef.current(order);
        }
        
        return newItems;
      });
    }
  };

  // Notifier le parent de l'ordre initial uniquement au montage
  useEffect(() => {
    if (onOrderChange) {
      const initialOrder = items.map(item => item.value);
      onOrderChange(initialOrder);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Seulement au montage, pas à chaque changement de items

  // Utiliser une ref pour éviter les re-renders infinis
  const onOrderChangeRef = useRef(onOrderChange);
  useEffect(() => {
    onOrderChangeRef.current = onOrderChange;
  }, [onOrderChange]);

  if (!pieces || pieces.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ''}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun puzzle disponible
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`bg-card border-primary/20 ${className || ''}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Puzzle className="h-5 w-5 text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Puzzle interactif</h4>
            <span className="text-xs text-muted-foreground ml-auto">
              Glissez-déposez pour réorganiser
            </span>
          </div>
          
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext items={items.map((item) => item.id)} strategy={verticalListSortingStrategy}>
              <div className="space-y-2">
                {items.map((item, index) => (
                  <SortableItem
                    key={item.id}
                    id={item.id}
                    value={item.value}
                    index={index + 1}
                  />
                ))}
              </div>
            </SortableContext>
          </DndContext>

          <div className="text-xs text-center text-muted-foreground">
            Réorganisez les éléments dans le bon ordre
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

