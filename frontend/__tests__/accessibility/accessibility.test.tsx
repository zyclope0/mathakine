import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AccessibilityToolbar } from '@/components/accessibility/AccessibilityToolbar';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';
import { vi } from 'vitest';

// Mock store
vi.mock('@/lib/stores/accessibilityStore', () => ({
  useAccessibilityStore: vi.fn(),
}));

describe('AccessibilityToolbar', () => {
  it('affiche tous les boutons d\'accessibilité', () => {
    (useAccessibilityStore as any).mockReturnValue({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      dyslexiaMode: false,
      focusMode: false,
      toggleHighContrast: vi.fn(),
      toggleLargeText: vi.fn(),
      toggleReducedMotion: vi.fn(),
      toggleDyslexiaMode: vi.fn(),
      toggleFocusMode: vi.fn(),
    });

    render(<AccessibilityToolbar />);
    
    expect(screen.getByRole('button', { name: /contraste/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /texte/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /animations/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /dyslexie/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /focus/i })).toBeInTheDocument();
  });

  it('a des labels ARIA corrects', () => {
    (useAccessibilityStore as any).mockReturnValue({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      dyslexiaMode: false,
      focusMode: false,
      toggleHighContrast: vi.fn(),
      toggleLargeText: vi.fn(),
      toggleReducedMotion: vi.fn(),
      toggleDyslexiaMode: vi.fn(),
      toggleFocusMode: vi.fn(),
    });

    render(<AccessibilityToolbar />);
    
    const buttons = screen.getAllByRole('button');
    buttons.forEach((button) => {
      expect(button).toHaveAttribute('aria-label');
    });
  });
});

