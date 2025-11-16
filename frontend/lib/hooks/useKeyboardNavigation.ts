import { useEffect, useCallback } from 'react';

/**
 * Hook pour améliorer la navigation clavier
 * Gère les raccourcis et la navigation par flèches dans les listes
 */
export function useKeyboardNavigation() {
  const handleArrowNavigation = useCallback((
    event: React.KeyboardEvent,
    items: HTMLElement[],
    currentIndex: number,
    onSelect: (index: number) => void
  ) => {
    let newIndex = currentIndex;

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        newIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
        break;
      case 'ArrowUp':
        event.preventDefault();
        newIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
        break;
      case 'Home':
        event.preventDefault();
        newIndex = 0;
        break;
      case 'End':
        event.preventDefault();
        newIndex = items.length - 1;
        break;
      default:
        return;
    }

    onSelect(newIndex);
    items[newIndex]?.focus();
  }, []);

  return { handleArrowNavigation };
}

/**
 * Hook pour gérer la navigation clavier dans une grille 2D
 */
export function useGridNavigation() {
  const handleGridNavigation = useCallback((
    event: React.KeyboardEvent,
    grid: HTMLElement[][],
    currentRow: number,
    currentCol: number,
    onSelect: (row: number, col: number) => void
  ) => {
    let newRow = currentRow;
    let newCol = currentCol;

    switch (event.key) {
      case 'ArrowRight':
        event.preventDefault();
        if (grid[currentRow] && currentCol < grid[currentRow]!.length - 1) {
          newCol = currentCol + 1;
        } else if (currentRow < grid.length - 1) {
          newRow = currentRow + 1;
          newCol = 0;
        }
        break;
      case 'ArrowLeft':
        event.preventDefault();
        if (currentCol > 0) {
          newCol = currentCol - 1;
        } else if (currentRow > 0 && grid[currentRow - 1]) {
          newRow = currentRow - 1;
          newCol = grid[newRow]!.length - 1;
        }
        break;
      case 'ArrowDown':
        event.preventDefault();
        if (currentRow < grid.length - 1 && grid[currentRow + 1]) {
          newRow = currentRow + 1;
          if (newCol >= grid[newRow]!.length) {
            newCol = grid[newRow]!.length - 1;
          }
        }
        break;
      case 'ArrowUp':
        event.preventDefault();
        if (currentRow > 0 && grid[currentRow - 1]) {
          newRow = currentRow - 1;
          if (newCol >= grid[newRow]!.length) {
            newCol = grid[newRow]!.length - 1;
          }
        }
        break;
      case 'Home':
        event.preventDefault();
        newCol = 0;
        break;
      case 'End':
        event.preventDefault();
        if (grid[currentRow]) {
          newCol = grid[currentRow]!.length - 1;
        }
        break;
      default:
        return;
    }

    onSelect(newRow, newCol);
    const targetElement = grid[newRow]?.[newCol];
    if (targetElement) {
      targetElement.focus();
    }
  }, []);

  return { handleGridNavigation };
}

