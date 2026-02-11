import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ExerciseCard } from '@/components/exercises/ExerciseCard';
import type { Exercise } from '@/types/api';
import { NextIntlClientProvider } from 'next-intl';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import fr from '@/messages/fr.json';

// Mock dynamic import (ExerciseModal)
vi.mock('next/dynamic', () => ({
  default: vi.fn(() => () => null),
}));

// Mock useCompletedExercises pour éviter les appels API
vi.mock('@/hooks/useCompletedItems', () => ({
  useCompletedExercises: () => ({ isCompleted: () => false }),
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

function TestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <NextIntlClientProvider locale="fr" messages={fr}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </NextIntlClientProvider>
  );
}

describe('ExerciseCard', () => {
  const mockExercise: Exercise = {
    id: 1,
    title: 'Test Exercise',
    question: 'What is 2 + 2?',
    exercise_type: 'addition',
    difficulty: 'initie',
    correct_answer: '4',
    choices: ['3', '4', '5', '6'],
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    ai_generated: false,
    view_count: 0,
  };

  it('affiche le titre de l\'exercice', () => {
    render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
    expect(screen.getByText('Test Exercise')).toBeInTheDocument();
  });

  it('affiche la question de l\'exercice', () => {
    render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
    expect(screen.getByText('What is 2 + 2?')).toBeInTheDocument();
  });

  it('affiche le badge de type d\'exercice', () => {
    render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
    expect(screen.getByText(/addition/i)).toBeInTheDocument();
  });

  it('affiche le badge IA si l\'exercice est généré par IA', () => {
    const aiExercise = { ...mockExercise, ai_generated: true };
    render(<ExerciseCard exercise={aiExercise} />, { wrapper: TestWrapper });
    expect(screen.getByText('IA')).toBeInTheDocument();
  });

  it('affiche le bouton Résoudre', () => {
    render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
    expect(screen.getByRole('button', { name: /résoudre/i })).toBeInTheDocument();
  });

  it('a des attributs ARIA corrects', () => {
    render(<ExerciseCard exercise={mockExercise} />, { wrapper: TestWrapper });
    const card = screen.getByRole('article');
    expect(card).toHaveAttribute('aria-labelledby', `exercise-title-${mockExercise.id}`);
    expect(card).toHaveAttribute('aria-describedby', `exercise-description-${mockExercise.id}`);
  });
});

