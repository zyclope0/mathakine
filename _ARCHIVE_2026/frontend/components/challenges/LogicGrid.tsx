'use client';

import { useState, useCallback } from 'react';
import {
  DndContext,
  DragEndEvent,
  DragStartEvent,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  rectSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';
import { cn } from '@/lib/utils/cn';

// Mapping statique pour les classes grid-cols (Tailwind ne supporte pas les classes dynamiques)
const GRID_COLS_CLASSES: Record<number, string> = {
  1: 'grid-cols-1',
  2: 'grid-cols-2',
  3: 'grid-cols-3',
  4: 'grid-cols-4',
  5: 'grid-cols-5',
  6: 'grid-cols-6',
  7: 'grid-cols-7',
  8: 'grid-cols-8',
  9: 'grid-cols-9',
  10: 'grid-cols-10',
  11: 'grid-cols-11',
  12: 'grid-cols-12',
};

export interface GridCell {
  id: string;
  value: number | string;
  position: { row: number; col: number };
  isLocked?: boolean;
}

interface LogicGridProps {
  grid: GridCell[][];
  onGridChange: (newGrid: GridCell[][]) => void;
  columns?: number;
  disabled?: boolean;
  className?: string;
}

export function LogicGrid({
  grid,
  onGridChange,
  columns = 4,
  disabled = false,
  className,
}: LogicGridProps) {
  const { focusMode, reducedMotion } = useAccessibilityStore();
  const [activeId, setActiveId] = useState<string | null>(null);

  // Flatten grid pour dnd-kit
  const flatGrid = grid.flat();
  const cellIds = flatGrid.map((cell) => cell.id);

  // Capteurs avec support clavier pour accessibilité
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // Évite les drags accidentels
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragStart = useCallback(
    (event: DragStartEvent) => {
      setActiveId(event.active.id as string);
    },
    []
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;

      if (!over || active.id === over.id) {
        setActiveId(null);
        return;
      }

      const activeIndex = flatGrid.findIndex((cell) => cell.id === active.id);
      const overIndex = flatGrid.findIndex((cell) => cell.id === over.id);

      if (activeIndex === -1 || overIndex === -1) {
        setActiveId(null);
        return;
      }

      // Vérifier si les cellules sont verrouillées
      const activeCell = flatGrid[activeIndex];
      const overCell = flatGrid[overIndex];

      if (activeCell?.isLocked || overCell?.isLocked) {
        setActiveId(null);
        return;
      }

      // Réorganiser la grille plate
      const newFlatGrid = arrayMove(flatGrid, activeIndex, overIndex);

      // Reconstruire la grille 2D
      const newGrid: GridCell[][] = [];
      for (let i = 0; i < grid.length; i++) {
        newGrid.push([]);
        for (let j = 0; j < columns; j++) {
          const index = i * columns + j;
          if (index < newFlatGrid.length) {
            newGrid[i]!.push({
              ...newFlatGrid[index]!,
              position: { row: i, col: j },
            });
          }
        }
      }

      onGridChange(newGrid);
      setActiveId(null);
    },
    [flatGrid, grid, columns, onGridChange]
  );

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <SortableContext items={cellIds} strategy={rectSortingStrategy}>
        <div
          className={cn(
            'grid gap-2 p-4',
            GRID_COLS_CLASSES[columns] || 'grid-cols-4',
            focusMode && 'gap-4',
            className
          )}
          role="grid"
          aria-label="Grille logique interactive"
        >
          {flatGrid.map((cell) => (
            <SortableCell
              key={cell.id}
              cell={cell}
              isActive={activeId === cell.id}
              disabled={disabled || !!cell.isLocked}
              reducedMotion={reducedMotion}
            />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}

interface SortableCellProps {
  cell: GridCell;
  isActive: boolean;
  disabled: boolean;
  reducedMotion: boolean;
}

function SortableCell({ cell, isActive, disabled, reducedMotion }: SortableCellProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: cell.id,
    disabled: disabled,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition: reducedMotion ? 'none' : transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 50 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...(disabled ? {} : listeners)}
      className={cn(
        'bg-surface-elevated border-2 rounded-lg p-4 flex items-center justify-center text-xl font-bold',
        'touch-none',
        cell.isLocked
          ? 'border-muted-foreground/30 bg-muted/20 cursor-not-allowed'
          : disabled
            ? 'cursor-default'
            : 'border-primary/30 cursor-grab active:cursor-grabbing hover:border-primary/50 hover:bg-primary/5',
        isActive && 'ring-2 ring-primary ring-offset-2',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2'
      )}
      role="gridcell"
      aria-label={`Cellule ${cell.value} à la position ${cell.position.row}, ${cell.position.col}`}
      aria-readonly={cell.isLocked}
      tabIndex={disabled ? -1 : 0}
    >
      {cell.value}
    </div>
  );
}

