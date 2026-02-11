import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AccessibilityToolbar } from '@/components/accessibility/AccessibilityToolbar';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';
import { vi } from 'vitest';

// Mock store
vi.mock('@/lib/stores/accessibilityStore', () => ({
  useAccessibilityStore: vi.fn(),
}));

describe('AccessibilityToolbar', () => {
  it('affiche tous les boutons d\'accessibilité', async () => {
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
    
    // Attendre le montage (portal) puis ouvrir le menu
    const mainButton = await screen.findByRole('button', { name: /options d'accessibilité/i });
    await userEvent.click(mainButton);
    
    // Les options sont des role="switch" avec les labels du menu
    expect(screen.getByRole('switch', { name: /contraste élevé/i })).toBeInTheDocument();
    expect(screen.getByRole('switch', { name: /texte agrandi/i })).toBeInTheDocument();
    expect(screen.getByRole('switch', { name: /réduire animations/i })).toBeInTheDocument();
    expect(screen.getByRole('switch', { name: /mode dyslexie/i })).toBeInTheDocument();
    expect(screen.getByRole('switch', { name: /mode focus/i })).toBeInTheDocument();
  });

  it('a des labels ARIA corrects', async () => {
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
    
    // Attendre le montage puis vérifier le bouton principal
    const mainButton = await screen.findByRole('button', { name: /options d'accessibilité/i });
    expect(mainButton).toHaveAttribute('aria-label');
    
    // Ouvrir le menu pour vérifier les options (role="switch")
    await userEvent.click(mainButton);
    const switches = screen.getAllByRole('switch');
    switches.forEach((switchEl) => {
      expect(switchEl).toHaveAttribute('aria-label');
    });
  });
});

