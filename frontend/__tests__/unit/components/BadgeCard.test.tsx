import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BadgeCard } from '@/components/badges/BadgeCard';
import type { Badge, UserBadge } from '@/types/api';

describe('BadgeCard', () => {
  const mockBadge: Badge = {
    id: 1,
    code: 'first_steps',
    name: 'Premiers Pas',
    description: 'Compléter votre premier exercice',
    category: 'progression',
    difficulty: 'bronze',
    points_reward: 10,
    requirements: {},
    star_wars_title: 'Éveil de la Force',
    is_active: true,
    created_at: '2025-01-01T00:00:00Z',
  };

  it('affiche le nom du badge', () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />);
    expect(screen.getByText('Premiers Pas')).toBeInTheDocument();
  });

  it('affiche le titre Star Wars si disponible', () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />);
    expect(screen.getByText('Éveil de la Force')).toBeInTheDocument();
  });

  it('affiche l\'icône de verrouillage si le badge n\'est pas obtenu', () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />);
    // L'icône Lock devrait être présente (vérification via aria-hidden car c'est décoratif)
    const lockIcon = document.querySelector('[aria-hidden="true"]');
    expect(lockIcon).toBeInTheDocument();
  });

  it('affiche l\'icône de succès si le badge est obtenu', () => {
    const userBadge: UserBadge = {
      id: 1,
      achievement_id: 1,
      user_id: 1,
      earned_at: '2025-01-01T00:00:00Z',
      progress_data: {},
      is_displayed: true,
    };
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />);
    // L'icône CheckCircle devrait être présente
    const checkIcon = document.querySelector('[class*="text-green-500"]');
    expect(checkIcon).toBeInTheDocument();
  });

  it('affiche les points de récompense', () => {
    render(<BadgeCard badge={mockBadge} isEarned={false} />);
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('pts')).toBeInTheDocument();
  });

  it('affiche la date d\'obtention si le badge est obtenu', () => {
    const userBadge: UserBadge = {
      id: 1,
      achievement_id: 1,
      user_id: 1,
      earned_at: '2025-01-15T00:00:00Z',
      progress_data: {},
      is_displayed: true,
    };
    render(<BadgeCard badge={mockBadge} userBadge={userBadge} isEarned={true} />);
    expect(screen.getByText(/obtenu le/i)).toBeInTheDocument();
  });
});

