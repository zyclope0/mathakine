n
# 🚀 PLAN DE REFONTE FRONTEND MATHAKINE

**Date de création** : Janvier 2025  
**Objectif** : Refonte complète du frontend avec stack moderne  
**Cible** : Enfants 5-20 ans avec TSA/TDAH

---

## 📋 **VALIDATION DES RÉPONSES**

### ✅ **Architecture et Stack**
- ✅ **Architecture** : Hybride SSR + hydratation (Next.js App Router)
- ✅ **Framework** : React 18+ avec TypeScript strict
- ✅ **Design System** : Radix UI + shadcn/ui + Tailwind CSS
- ✅ **Build** : Next.js natif (Turbopack + SWC)
- ✅ **Styling** : Tailwind CSS (utility-first)

### ✅ **Fonctionnalités Clés**
- ✅ **Thème spatial** : Inspiration Star Wars modifiée (sans droits d'auteur)
- ✅ **Accessibilité** : WCAG 2.1 AAA + Mode Focus TSA/TDAH
- ✅ **Performance** : Mobile-first, < 2s FCP, < 100ms TTI
- ✅ **PWA** : Phase 2 (mode offline)
- ✅ **i18n** : next-intl (FR + autres langues)

### ✅ **Gestion d'État et API**
- ✅ **State** : TanStack Query (server) + Zustand (client léger)
- ✅ **API** : REST + SSE (temps réel) + WebSockets (interactif)
- ✅ **Auth** : Cookies HTTP-only (sécurisé)
- ✅ **Erreurs** : Multi-niveaux (serveur + client + UX)

### ✅ **Tests et Qualité**
- ✅ **Tests** : Suite complète (pyramide) - Vitest + RTL + Playwright
- ✅ **TypeScript** : Mode strict complet
- ✅ **CI/CD** : Intégration avec système existant

---

## 🎯 **STACK TECHNIQUE FINALE**

```yaml
Framework:
  - Next.js 14+ (App Router)
  - React 18+
  - TypeScript (strict mode)

Styling:
  - Tailwind CSS 3.4+
  - Radix UI (primitives accessibles)
  - shadcn/ui (composants)
  - CSS Modules (pour composants spécifiques)

State Management:
  - TanStack Query v5 (server state)
  - Zustand (client state léger)

Animations:
  - Framer Motion (animations avancées)
  - CSS Animations (simples, performantes)

Charts:
  - Recharts (graphiques)

i18n:
  - next-intl (App Router)

Testing:
  - Vitest (unit/integration)
  - React Testing Library (composants)
  - Playwright (E2E)
  - Chromatic (visual regression)

Build:
  - Next.js Turbopack (dev)
  - Next.js SWC (prod)
  - Turborepo (si monorepo)

Accessibility:
  - Radix UI (ARIA natif)
  - @axe-core/react (audit)
  - WCAG 2.1 AAA compliance
```

---

## 📁 **STRUCTURE DU PROJET**

```
mathakine-frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Routes groupe authentification
│   │   ├── login/
│   │   ├── register/
│   │   └── forgot-password/
│   ├── (dashboard)/              # Routes groupe dashboard
│   │   ├── dashboard/
│   │   ├── exercises/
│   │   ├── challenges/
│   │   └── badges/
│   ├── (public)/                 # Routes publiques
│   │   ├── page.tsx              # Home
│   │   └── about/
│   ├── api/                      # API Routes Next.js (proxy si nécessaire)
│   ├── layout.tsx                # Layout racine
│   ├── loading.tsx               # Loading global
│   ├── error.tsx                 # Error boundary global
│   └── not-found.tsx             # 404
│
├── components/                    # Composants React
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── modal.tsx
│   │   └── ...
│   ├── exercises/                # Composants exercices
│   │   ├── ExerciseCard.tsx
│   │   ├── ExerciseGenerator.tsx
│   │   ├── ExerciseSolver.tsx
│   │   └── AIGenerator.tsx
│   ├── challenges/               # Composants défis logiques
│   │   ├── ChallengeCard.tsx
│   │   ├── ChallengeSolver.tsx
│   │   └── HintSystem.tsx
│   ├── badges/                   # Composants badges
│   │   ├── BadgeCard.tsx
│   │   └── BadgeGrid.tsx
│   ├── dashboard/                # Composants dashboard
│   │   ├── StatsCard.tsx
│   │   ├── ProgressChart.tsx
│   │   └── Recommendations.tsx
│   ├── accessibility/            # Composants accessibilité
│   │   ├── AccessibilityToolbar.tsx
│   │   ├── FocusMode.tsx
│   │   └── ReducedMotion.tsx
│   ├── layout/                   # Composants layout
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   ├── Footer.tsx
│   │   └── Breadcrumbs.tsx
│   └── shared/                   # Composants partagés
│       ├── LoadingSpinner.tsx
│       ├── ErrorBoundary.tsx
│       ├── Toast.tsx
│       └── OfflineIndicator.tsx
│
├── lib/                          # Utilitaires et configs
│   ├── api/                      # Clients API
│   │   ├── client.ts              # Fetch wrapper
│   │   ├── exercises.ts
│   │   ├── challenges.ts
│   │   ├── badges.ts
│   │   └── auth.ts
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useExercises.ts
│   │   ├── useChallenges.ts
│   │   └── useAccessibility.ts
│   ├── stores/                   # Zustand stores
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── accessibilityStore.ts
│   ├── utils/                    # Utilitaires
│   │   ├── cn.ts                 # clsx + tailwind-merge
│   │   ├── format.ts
│   │   └── validation.ts
│   └── constants/                # Constantes
│       ├── exercises.ts
│       ├── challenges.ts
│       └── accessibility.ts
│
├── styles/                        # Styles globaux
│   ├── globals.css               # Tailwind + variables CSS
│   ├── space-theme.css           # Thème spatial
│   └── accessibility.css         # Styles accessibilité
│
├── public/                        # Assets statiques
│   ├── images/
│   ├── sounds/
│   └── icons/
│
├── messages/                     # Traductions next-intl
│   ├── fr.json
│   ├── en.json
│   └── ...
│
├── types/                         # Types TypeScript
│   ├── api.ts                    # Types API
│   ├── exercises.ts
│   ├── challenges.ts
│   └── user.ts
│
├── __tests__/                     # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── .env.local                    # Variables d'environnement
├── next.config.js                # Config Next.js
├── tailwind.config.js            # Config Tailwind
├── tsconfig.json                 # Config TypeScript strict
└── package.json
```

---

## 🎨 **DESIGN SYSTEM**

### **Palette de Couleurs (Thème Spatial)**

```css
/* Variables CSS - Thème Spatial */
:root {
  /* Couleurs principales */
  --primary: #8b5cf6;        /* Violet spatial */
  --primary-dark: #7c3aed;
  --primary-light: #a78bfa;
  
  --secondary: #6366f1;      /* Indigo */
  --accent: #ec4899;        /* Rose */
  
  /* Backgrounds */
  --background: #0a0a0f;    /* Espace profond */
  --surface: #12121a;       /* Surface spatiale */
  --surface-elevated: #1a1a24;
  
  /* Text */
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  --text-muted: #6b7280;
  
  /* États */
  --success: #22c55e;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  
  /* Accessibilité */
  --focus-ring: #8b5cf6;
  --focus-ring-offset: 2px;
}
```

### **Composants shadcn/ui à Installer**

```bash
# Composants essentiels
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add form
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add progress
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add tooltip
```

---

## 🔐 **AUTHENTIFICATION**

### **Stratégie**

```typescript
// lib/hooks/useAuth.ts
import { useQuery, useMutation } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';

export function useAuth() {
  const router = useRouter();
  
  const { data: user, isLoading } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: () => fetch('/api/auth/me', { credentials: 'include' }).then(r => r.json()),
    retry: false,
  });
  
  const loginMutation = useMutation({
    mutationFn: async (credentials: { username: string; password: string }) => {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(credentials),
      });
      if (!res.ok) throw new Error('Login failed');
      return res.json();
    },
    onSuccess: () => {
      router.push('/dashboard');
    },
  });
  
  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login: loginMutation.mutate,
    logout: async () => {
      await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' });
      router.push('/login');
    },
  };
}
```

### **Middleware de Protection**

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const isAuthPage = request.nextUrl.pathname.startsWith('/login') || 
                     request.nextUrl.pathname.startsWith('/register');
  
  // Rediriger vers login si non authentifié sur page protégée
  if (!token && !isAuthPage && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  // Rediriger vers dashboard si déjà authentifié sur page auth
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/register'],
};
```

---

## 🧮 **GÉNÉRATION D'EXERCICES**

### **État Actuel Backend**

**Analyse du code existant** :
- ✅ Génération "pseudo-IA" avec prompts pré-écrits Star Wars
- ✅ Tag `[TEST-ZAXXON]` pour identification
- ⚠️ Pas d'appel réel à OpenAI actuellement
- ✅ Package `openai==1.12.0` dans requirements.txt
- ✅ Variable `OPENAI_API_KEY` prévue dans config

**Recommandation** : Implémenter vraie génération OpenAI avec streaming SSE pour expérience premium.

### **Composant Générateur Standard**

```typescript
// components/exercises/ExerciseGenerator.tsx
'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';

export function ExerciseGenerator() {
  const [type, setType] = useState<string>('addition');
  const [difficulty, setDifficulty] = useState<string>('initie');
  
  const generateMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/exercises/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ exercise_type: type, difficulty }),
      });
      return res.json();
    },
  });
  
  return (
    <div className="space-y-4">
      <Select value={type} onValueChange={setType}>
        {/* Options */}
      </Select>
      <Select value={difficulty} onValueChange={setDifficulty}>
        {/* Options */}
      </Select>
      <Button onClick={() => generateMutation.mutate()}>
        Générer un exercice
      </Button>
    </div>
  );
}
```

### **Composant Générateur IA avec Streaming SSE**

```typescript
// components/exercises/AIGenerator.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2, Sparkles } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export function AIGenerator() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [exercise, setExercise] = useState<any>(null);
  const { toast } = useToast();
  
  const handleAIGenerate = async () => {
    setIsGenerating(true);
    setStreamedText('');
    setExercise(null);
    
    try {
      // Connexion SSE pour streaming
      const eventSource = new EventSource(
        `/api/exercises/generate-ai-stream?prompt=${encodeURIComponent(prompt)}`,
        { withCredentials: true }
      );
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
          // Affichage progressif du texte généré
          setStreamedText(prev => prev + data.content);
        } else if (data.type === 'exercise') {
          // Exercice complet reçu
          setExercise(data.exercise);
          eventSource.close();
          setIsGenerating(false);
          toast({
            title: 'Exercice généré !',
            description: 'L\'exercice a été créé avec succès.',
          });
        } else if (data.type === 'error') {
          eventSource.close();
          setIsGenerating(false);
          toast({
            title: 'Erreur',
            description: data.message,
            variant: 'destructive',
          });
        }
      };
      
      eventSource.onerror = () => {
        eventSource.close();
        setIsGenerating(false);
        toast({
          title: 'Erreur de connexion',
          description: 'La génération a été interrompue.',
          variant: 'destructive',
        });
      };
    } catch (error) {
      setIsGenerating(false);
      toast({
        title: 'Erreur',
        description: 'Impossible de démarrer la génération.',
        variant: 'destructive',
      });
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Décris le type d'exercice que tu veux... (ex: 'Un problème de multiplication avec des vaisseaux spatiaux')"
          className="w-full p-3 rounded-lg bg-surface text-text-primary min-h-[100px]"
          disabled={isGenerating}
        />
        {isGenerating && (
          <div className="absolute top-2 right-2">
            <Sparkles className="h-5 w-5 text-primary animate-pulse" />
          </div>
        )}
      </div>
      
      {streamedText && (
        <div className="p-4 rounded-lg bg-surface-elevated border border-primary/20">
          <p className="text-sm text-text-secondary mb-2">Génération en cours...</p>
          <p className="text-text-primary whitespace-pre-wrap">{streamedText}</p>
        </div>
      )}
      
      {exercise && (
        <div className="p-4 rounded-lg bg-success/10 border border-success/20">
          <p className="font-semibold text-success mb-2">✅ Exercice généré !</p>
          <p className="text-text-primary">{exercise.question}</p>
        </div>
      )}
      
      <Button 
        onClick={handleAIGenerate}
        disabled={isGenerating || !prompt.trim()}
        className="w-full"
      >
        {isGenerating ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Génération en cours...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            Générer avec l'IA
          </>
        )}
      </Button>
    </div>
  );
}
```

### **Backend SSE à Implémenter**

```python
# app/api/endpoints/exercises.py (à ajouter)
from fastapi.responses import StreamingResponse
import json
import openai
from app.core.config import settings

@router.get("/generate-ai-stream")
async def generate_ai_exercise_stream(
    prompt: str,
    exercise_type: Optional[str] = None,
    difficulty: Optional[str] = None,
):
    """Génère un exercice avec OpenAI en streaming SSE"""
    
    async def generate():
        try:
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            system_prompt = """Tu es un assistant pédagogique spécialisé dans la création d'exercices mathématiques pour enfants.
            Crée des exercices adaptés au niveau demandé avec un contexte spatial/galactique (sans références Star Wars identifiables).
            Retourne uniquement l'exercice au format JSON: {"question": "...", "correct_answer": "...", "choices": [...], "explanation": "..."}"""
            
            user_prompt = f"Crée un exercice de type {exercise_type} niveau {difficulty}. {prompt}"
            
            stream = await client.chat.completions.create(
                model="gpt-4o-mini",  # ou gpt-3.5-turbo pour coût réduit
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
                temperature=0.7,
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Envoyer chaque chunk au client
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content})}\n\n"
            
            # Parser la réponse JSON et envoyer l'exercice complet
            exercise = json.loads(full_response)
            yield f"data: {json.dumps({'type': 'exercise', 'exercise': exercise})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

---

## 🧩 **DÉFIS MATHÉLOGIQUE**

### **Spécificités UI : Grilles et Drag & Drop**

Les défis mathélogique nécessitent des interactions spécifiques pour une meilleure compréhension visuelle.

### **Composant Grille Interactive**

```typescript
// components/challenges/LogicGrid.tsx
'use client';

import { useState, useCallback } from 'react';
import { DndContext, DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { SortableContext, arrayMove } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

interface GridCell {
  id: string;
  value: number | string;
  position: { row: number; col: number };
}

export function LogicGrid({ 
  grid, 
  onGridChange 
}: { 
  grid: GridCell[][]; 
  onGridChange: (newGrid: GridCell[][]) => void;
}) {
  const [activeId, setActiveId] = useState<string | null>(null);
  
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };
  
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;
    
    // Logique de réorganisation de la grille
    // ...
    
    setActiveId(null);
  };
  
  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-4 gap-2 p-4">
        {grid.flat().map((cell) => (
          <SortableCell key={cell.id} cell={cell} />
        ))}
      </div>
    </DndContext>
  );
}

function SortableCell({ cell }: { cell: GridCell }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: cell.id });
  
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };
  
  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-surface-elevated border-2 border-primary/30 rounded-lg p-4 cursor-grab active:cursor-grabbing touch-none"
      role="button"
      aria-label={`Cellule ${cell.value} à la position ${cell.position.row}, ${cell.position.col}`}
    >
      {cell.value}
    </div>
  );
}
```

### **Composant Pattern Recognition**

```typescript
// components/challenges/PatternSolver.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface PatternChallenge {
  sequence: number[];
  pattern: 'arithmetic' | 'geometric' | 'fibonacci' | 'custom';
  nextValue?: number;
}

export function PatternSolver({ challenge }: { challenge: PatternChallenge }) {
  const [selectedValue, setSelectedValue] = useState<number | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  
  const handleSubmit = () => {
    if (selectedValue === challenge.nextValue) {
      setIsCorrect(true);
    } else {
      setIsCorrect(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex gap-4 items-center justify-center">
        {challenge.sequence.map((value, index) => (
          <div
            key={index}
            className="w-16 h-16 bg-primary/20 border-2 border-primary rounded-lg flex items-center justify-center text-2xl font-bold"
          >
            {value}
          </div>
        ))}
        <div className="w-16 h-16 bg-surface-elevated border-2 border-dashed border-primary/50 rounded-lg flex items-center justify-center text-2xl font-bold">
          ?
        </div>
      </div>
      
      <div className="grid grid-cols-4 gap-2">
        {[challenge.nextValue! - 2, challenge.nextValue! - 1, challenge.nextValue!, challenge.nextValue! + 1].map((value) => (
          <Button
            key={value}
            variant={selectedValue === value ? 'default' : 'outline'}
            onClick={() => setSelectedValue(value)}
            className="h-16 text-lg"
          >
            {value}
          </Button>
        ))}
      </div>
      
      <Button onClick={handleSubmit} disabled={selectedValue === null}>
        Valider
      </Button>
      
      {isCorrect !== null && (
        <div className={`p-4 rounded-lg ${isCorrect ? 'bg-success/20 text-success' : 'bg-error/20 text-error'}`}>
          {isCorrect ? '✅ Correct !' : '❌ Incorrect, essaie encore !'}
        </div>
      )}
    </div>
  );
}
```

### **Accessibilité Drag & Drop**

```typescript
// lib/hooks/useAccessibleDragDrop.ts
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';

export function useAccessibleDragDrop() {
  const { focusMode, reducedMotion } = useAccessibilityStore();
  
  // Alternative clavier pour drag & drop
  const handleKeyDown = (event: React.KeyboardEvent, onMove: (direction: 'up' | 'down' | 'left' | 'right') => void) => {
    if (focusMode || !event.shiftKey) return;
    
    switch (event.key) {
      case 'ArrowUp':
        event.preventDefault();
        onMove('up');
        break;
      case 'ArrowDown':
        event.preventDefault();
        onMove('down');
        break;
      case 'ArrowLeft':
        event.preventDefault();
        onMove('left');
        break;
      case 'ArrowRight':
        event.preventDefault();
        onMove('right');
        break;
    }
  };
  
  return { handleKeyDown };
}
```

### **Installation Dépendances**

```bash
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
```

---

## ♿ **ACCESSIBILITÉ WCAG 2.1 AAA**

### **Composant Barre d'Accessibilité**

```typescript
// components/accessibility/AccessibilityToolbar.tsx
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useAccessibilityStore } from '@/lib/stores/accessibilityStore';

export function AccessibilityToolbar() {
  const {
    highContrast,
    largeText,
    reducedMotion,
    dyslexiaMode,
    focusMode,
    toggleHighContrast,
    toggleLargeText,
    toggleReducedMotion,
    toggleDyslexiaMode,
    toggleFocusMode,
  } = useAccessibilityStore();
  
  useEffect(() => {
    // Appliquer les styles selon les préférences
    document.documentElement.classList.toggle('high-contrast', highContrast);
    document.documentElement.classList.toggle('large-text', largeText);
    document.documentElement.classList.toggle('reduced-motion', reducedMotion);
    document.documentElement.classList.toggle('dyslexia-mode', dyslexiaMode);
    document.documentElement.classList.toggle('focus-mode', focusMode);
  }, [highContrast, largeText, reducedMotion, dyslexiaMode, focusMode]);
  
  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      <Button
        onClick={toggleHighContrast}
        variant={highContrast ? 'default' : 'outline'}
        aria-label="Mode contraste élevé (Alt+C)"
      >
        <span aria-hidden="true">🔍</span>
      </Button>
      {/* Autres boutons */}
    </div>
  );
}
```

### **Mode Focus TSA/TDAH (Phase 1 - Mode Unique)**

**Phase 1** : Mode unique avec fonctionnalités essentielles. Améliorations multi-niveaux prévues pour Phase 2.

```typescript
// lib/stores/accessibilityStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AccessibilityState {
  highContrast: boolean;
  largeText: boolean;
  reducedMotion: boolean;
  dyslexiaMode: boolean;
  focusMode: boolean; // Mode unique Phase 1
  toggleHighContrast: () => void;
  toggleLargeText: () => void;
  toggleReducedMotion: () => void;
  toggleDyslexiaMode: () => void;
  toggleFocusMode: () => void;
}

export const useAccessibilityStore = create<AccessibilityState>()(
  persist(
    (set) => ({
      highContrast: false,
      largeText: false,
      reducedMotion: false,
      dyslexiaMode: false,
      focusMode: false,
      toggleHighContrast: () => set((state) => ({ highContrast: !state.highContrast })),
      toggleLargeText: () => set((state) => ({ largeText: !state.largeText })),
      toggleReducedMotion: () => set((state) => ({ reducedMotion: !state.reducedMotion })),
      toggleDyslexiaMode: () => set((state) => ({ dyslexiaMode: !state.dyslexiaMode })),
      toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),
    }),
    { name: 'accessibility-preferences' }
  )
);
```

```css
/* styles/accessibility.css */
.focus-mode {
  /* Réduire les distractions visuelles */
  --background: #000000;
  --surface: #0a0a0a;
  --text-primary: #ffffff;
  --text-secondary: #cccccc;
  
  /* Masquer éléments non essentiels */
  .navigation-secondary,
  .footer,
  .recommendations,
  .sidebar,
  .badges-preview {
    display: none !important;
  }
  
  /* Agrandir zone de focus */
  .exercise-solver,
  .challenge-solver {
    max-width: 100%;
    padding: 2rem;
    margin: 0 auto;
  }
  
  /* Réduire animations (respect prefers-reduced-motion) */
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
  }
  
  /* Focus visible renforcé pour TSA/TDAH */
  *:focus-visible {
    outline: 4px solid var(--focus-ring);
    outline-offset: 4px;
    box-shadow: 0 0 0 8px rgba(139, 92, 246, 0.2);
  }
  
  /* Masquer étoiles et particules */
  .stars,
  .particles,
  .planets {
    display: none !important;
  }
  
  /* Simplifier les cartes */
  .card {
    border: 2px solid var(--primary);
    box-shadow: none;
  }
  
  /* Agrandir les boutons pour meilleure accessibilité */
  button {
    min-height: 48px;
    min-width: 48px;
    padding: 0.75rem 1.5rem;
  }
  
  /* Espacement augmenté pour lisibilité */
  p, li {
    line-height: 1.8;
    margin-bottom: 1rem;
  }
}
```

**Note Phase 2** : Ajouter niveaux 2 et 3 avec options supplémentaires (mode ultra-minimaliste, personnalisation avancée).

---

## 🎨 **SYSTÈME DE THÈMES**

### **Priorités d'Implémentation**

1. **Spatial** (Priorité 1) - Thème actuel avec modifications
2. **Minimaliste** (Priorité 2) - Design épuré, noir et blanc
3. **Océan** (Priorité 3) - Tons bleus apaisants
4. **Neutre** (Priorité 4) - Gris et blancs neutres

### **Store de Thèmes**

```typescript
// lib/stores/themeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'spatial' | 'minimalist' | 'ocean' | 'neutral';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'spatial',
      setTheme: (theme) => {
        set({ theme });
        // Appliquer le thème au document
        document.documentElement.setAttribute('data-theme', theme);
      },
    }),
    { name: 'theme-preferences' }
  )
);
```

### **Thème Spatial (Modifié)**

```css
/* styles/themes/spatial.css */
[data-theme='spatial'] {
  --primary: #8b5cf6;
  --primary-dark: #7c3aed;
  --primary-light: #a78bfa;
  --secondary: #6366f1;
  --accent: #ec4899;
  --background: #0a0a0f;
  --surface: #12121a;
  --text-primary: #ffffff;
  --text-secondary: #a0a0a0;
  
  /* Éléments spatiaux */
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
}
```

### **Thème Minimaliste**

```css
/* styles/themes/minimalist.css */
[data-theme='minimalist'] {
  --primary: #000000;
  --primary-dark: #000000;
  --primary-light: #333333;
  --secondary: #666666;
  --accent: #000000;
  --background: #ffffff;
  --surface: #f5f5f5;
  --text-primary: #000000;
  --text-secondary: #666666;
  
  /* Pas d'éléments décoratifs */
  background-image: none;
  
  /* Bordures nettes */
  --border-radius: 0px;
  --border-width: 2px;
}
```

### **Thème Océan**

```css
/* styles/themes/ocean.css */
[data-theme='ocean'] {
  --primary: #0ea5e9;
  --primary-dark: #0284c7;
  --primary-light: #38bdf8;
  --secondary: #06b6d4;
  --accent: #14b8a6;
  --background: #0c1220;
  --surface: #1e293b;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  
  /* Dégradés océaniques */
  background-image: 
    linear-gradient(180deg, rgba(14, 165, 233, 0.1) 0%, transparent 100%);
}
```

### **Thème Neutre**

```css
/* styles/themes/neutral.css */
[data-theme='neutral'] {
  --primary: #6b7280;
  --primary-dark: #4b5563;
  --primary-light: #9ca3af;
  --secondary: #9ca3af;
  --accent: #6b7280;
  --background: #ffffff;
  --surface: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  
  /* Design neutre */
  background-image: none;
}
```

### **Sélecteur de Thème**

```typescript
// components/theme/ThemeSelector.tsx
'use client';

import { useThemeStore } from '@/lib/stores/themeStore';
import { Button } from '@/components/ui/button';

const themes = [
  { id: 'spatial', name: 'Spatial', icon: '🚀' },
  { id: 'minimalist', name: 'Minimaliste', icon: '⚪' },
  { id: 'ocean', name: 'Océan', icon: '🌊' },
  { id: 'neutral', name: 'Neutre', icon: '⚫' },
] as const;

export function ThemeSelector() {
  const { theme, setTheme } = useThemeStore();
  
  return (
    <div className="flex gap-2">
      {themes.map((t) => (
        <Button
          key={t.id}
          variant={theme === t.id ? 'default' : 'outline'}
          onClick={() => setTheme(t.id)}
          aria-label={`Changer le thème vers ${t.name}`}
        >
          <span className="mr-2">{t.icon}</span>
          {t.name}
        </Button>
      ))}
    </div>
  );
}
```

---

## 📄 **EXPORT DE DONNÉES**

### **Formats Prioritaires : PDF et Excel**

### **Export PDF**

```typescript
// lib/utils/exportPDF.ts
import jsPDF from 'jspdf';
import 'jspdf-autotable';

export async function exportStatsToPDF(stats: UserStats) {
  const doc = new jsPDF();
  
  // En-tête
  doc.setFontSize(20);
  doc.text('Rapport de Progression Mathakine', 14, 20);
  
  // Statistiques générales
  doc.setFontSize(14);
  doc.text(`Utilisateur: ${stats.username}`, 14, 35);
  doc.text(`Période: ${stats.period}`, 14, 42);
  
  // Tableau de statistiques
  const tableData = stats.exercises.map(ex => [
    ex.type,
    ex.totalAttempts.toString(),
    ex.correctAttempts.toString(),
    `${ex.successRate}%`,
  ]);
  
  doc.autoTable({
    head: [['Type', 'Tentatives', 'Réussites', 'Taux']],
    body: tableData,
    startY: 50,
  });
  
  // Graphique (optionnel avec canvas)
  // ...
  
  doc.save(`mathakine-stats-${Date.now()}.pdf`);
}
```

### **Export Excel**

```typescript
// lib/utils/exportExcel.ts
import * as XLSX from 'xlsx';

export function exportStatsToExcel(stats: UserStats) {
  const workbook = XLSX.utils.book_new();
  
  // Feuille Statistiques Générales
  const generalData = [
    ['Utilisateur', stats.username],
    ['Période', stats.period],
    ['Total Tentatives', stats.totalAttempts],
    ['Total Réussites', stats.totalCorrect],
    ['Taux de Réussite', `${stats.overallSuccessRate}%`],
  ];
  const generalSheet = XLSX.utils.aoa_to_sheet(generalData);
  XLSX.utils.book_append_sheet(workbook, generalSheet, 'Général');
  
  // Feuille Détails par Type
  const detailsData = [
    ['Type', 'Tentatives', 'Réussites', 'Taux', 'Temps Moyen'],
    ...stats.exercises.map(ex => [
      ex.type,
      ex.totalAttempts,
      ex.correctAttempts,
      ex.successRate,
      ex.averageTime,
    ]),
  ];
  const detailsSheet = XLSX.utils.aoa_to_sheet(detailsData);
  XLSX.utils.book_append_sheet(workbook, detailsSheet, 'Détails');
  
  // Feuille Historique
  const historyData = [
    ['Date', 'Type', 'Difficulté', 'Résultat', 'Temps'],
    ...stats.history.map(h => [
      h.date,
      h.type,
      h.difficulty,
      h.isCorrect ? 'Réussi' : 'Échoué',
      h.timeSpent,
    ]),
  ];
  const historySheet = XLSX.utils.aoa_to_sheet(historyData);
  XLSX.utils.book_append_sheet(workbook, historySheet, 'Historique');
  
  XLSX.writeFile(workbook, `mathakine-stats-${Date.now()}.xlsx`);
}
```

### **Composant Export**

```typescript
// components/dashboard/ExportButton.tsx
'use client';

import { Button } from '@/components/ui/button';
import { Download, FileText, FileSpreadsheet } from 'lucide-react';
import { exportStatsToPDF } from '@/lib/utils/exportPDF';
import { exportStatsToExcel } from '@/lib/utils/exportExcel';
import { useQuery } from '@tanstack/react-query';

export function ExportButton() {
  const { data: stats } = useQuery({
    queryKey: ['user', 'stats'],
    queryFn: () => fetch('/api/users/stats', { credentials: 'include' }).then(r => r.json()),
  });
  
  const handleExportPDF = () => {
    if (stats) exportStatsToPDF(stats);
  };
  
  const handleExportExcel = () => {
    if (stats) exportStatsToExcel(stats);
  };
  
  return (
    <div className="flex gap-2">
      <Button onClick={handleExportPDF} variant="outline">
        <FileText className="mr-2 h-4 w-4" />
        Exporter PDF
      </Button>
      <Button onClick={handleExportExcel} variant="outline">
        <FileSpreadsheet className="mr-2 h-4 w-4" />
        Exporter Excel
      </Button>
    </div>
  );
}
```

### **Installation Dépendances**

```bash
npm install jspdf jspdf-autotable xlsx
npm install -D @types/jspdf
```

---

## 🌐 **INTERNATIONALISATION (next-intl)**

### **Configuration**

```typescript
// i18n.ts
import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

export const locales = ['fr', 'en'] as const;
export const defaultLocale = 'fr' as const;

export default getRequestConfig(async ({ locale }) => {
  if (!locales.includes(locale as any)) notFound();
  
  return {
    messages: (await import(`./messages/${locale}.json`)).default,
  };
});
```

### **Utilisation dans les Composants**

```typescript
// app/(dashboard)/exercises/page.tsx
import { useTranslations } from 'next-intl';

export default function ExercisesPage() {
  const t = useTranslations('exercises');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### **Messages (exemple)**

```json
// messages/fr.json
{
  "exercises": {
    "title": "Exercices Mathématiques",
    "description": "Choisis ton type d'exercice",
    "types": {
      "addition": "Addition",
      "subtraction": "Soustraction"
    }
  }
}
```

---

## 🧪 **TESTS**

### **Structure Pyramide**

```typescript
// __tests__/unit/components/ExerciseCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ExerciseCard } from '@/components/exercises/ExerciseCard';

describe('ExerciseCard', () => {
  it('affiche le titre de l\'exercice', () => {
    render(<ExerciseCard exercise={{ title: 'Test', id: 1 }} />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});
```

```typescript
// __tests__/e2e/exercises.spec.ts
import { test, expect } from '@playwright/test';

test('parcours complet résolution exercice', async ({ page }) => {
  await page.goto('/exercises');
  await page.click('text=Générer un exercice');
  await page.waitForSelector('.exercise-solver');
  await page.click('text=5'); // Sélectionner réponse
  await page.click('text=Valider');
  await expect(page.locator('.feedback-success')).toBeVisible();
});
```

---

## 📱 **PWA (Phase 2)**

### **Configuration**

```typescript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
});

module.exports = withPWA({
  // Config Next.js
});
```

### **Service Worker pour Mode Offline**

```typescript
// public/sw.js
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Mettre en file d'attente si offline
    event.respondWith(
      fetch(event.request).catch(() => {
        // Retourner réponse en cache ou file d'attente
      })
    );
  }
});
```

---

## 🚀 **PLAN D'IMPLÉMENTATION**

### **Phase 1 : Setup (Semaine 1-2)**

1. **Initialisation projet**
   - [ ] Créer projet Next.js avec TypeScript
   - [ ] Configurer Tailwind CSS + shadcn/ui
   - [ ] Installer dépendances (React Query, Zustand, Framer Motion)
   - [ ] Configurer next-intl
   - [ ] Setup ESLint + Prettier

2. **Design System**
   - [ ] Installer composants shadcn/ui essentiels
   - [ ] Créer palette de couleurs spatiale
   - [ ] Configurer thème Tailwind
   - [ ] Créer composants de base (Button, Card, Modal)

3. **Structure**
   - [ ] Créer structure de dossiers
   - [ ] Configurer App Router
   - [ ] Créer layouts de base
   - [ ] Setup middleware authentification

### **Phase 2 : Authentification (Semaine 3)**

1. **Pages Auth**
   - [ ] Page login
   - [ ] Page register
   - [ ] Page forgot-password
   - [ ] Hook useAuth

2. **Protection Routes**
   - [ ] Middleware Next.js
   - [ ] HOC pour pages protégées
   - [ ] Gestion erreurs 401/403

### **Phase 3 : Exercices (Semaine 4-5)**

1. **Liste Exercices**
   - [ ] Page /exercises
   - [ ] Composant ExerciseCard
   - [ ] Filtres (type, difficulté)
   - [ ] Pagination

2. **Génération**
   - [ ] Composant ExerciseGenerator (standard)
   - [ ] Composant AIGenerator
   - [ ] Intégration API

3. **Résolution**
   - [ ] Page /exercise/[id]
   - [ ] Composant ExerciseSolver
   - [ ] Feedback immédiat
   - [ ] Enregistrement tentative

### **Phase 4 : Défis Logiques (Semaine 6)**

1. **Liste Défis**
   - [ ] Page /challenges
   - [ ] Composant ChallengeCard
   - [ ] Filtres (type, âge)

2. **Résolution**
   - [ ] Page /challenge/[id]
   - [ ] Composant ChallengeSolver
   - [ ] Système d'indices
   - [ ] Affichage données visuelles

### **Phase 5 : Dashboard et Statistiques (Semaine 7)**

1. **Dashboard**
   - [ ] Page /dashboard
   - [ ] Composants StatsCard
   - [ ] Graphiques Recharts
   - [ ] Recommandations

2. **Statistiques**
   - [ ] Intégration React Query
   - [ ] Mise à jour temps réel (SSE)
   - [ ] Export PDF/CSV

### **Phase 6 : Badges et Gamification (Semaine 8)**

1. **Badges**
   - [ ] Page /badges
   - [ ] Composant BadgeGrid
   - [ ] Animations attribution
   - [ ] Progression visuelle

### **Phase 7 : Accessibilité (Semaine 9)**

1. **Barre d'Outils**
   - [ ] Composant AccessibilityToolbar
   - [ ] Mode contraste élevé
   - [ ] Mode dyslexie
   - [ ] Réduction animations
   - [ ] Mode Focus TSA/TDAH

2. **WCAG 2.1 AAA**
   - [ ] Audit avec @axe-core
   - [ ] Navigation clavier complète
   - [ ] Support lecteurs d'écran
   - [ ] Contraste AAA

### **Phase 8 : Polish et Optimisations (Semaine 10)**

1. **Performance**
   - [ ] Optimisation images (next/image)
   - [ ] Code splitting
   - [ ] Lazy loading composants
   - [ ] Optimisation bundle

2. **Animations**
   - [ ] Framer Motion (composants clés)
   - [ ] Garde-fous neuro-inclusifs
   - [ ] Respect prefers-reduced-motion

3. **Tests**
   - [ ] Tests unitaires composants
   - [ ] Tests E2E parcours critiques
   - [ ] Tests accessibilité

### **Phase 9 : i18n et Finalisation (Semaine 11)**

1. **Internationalisation**
   - [ ] Traductions FR
   - [ ] Traductions EN
   - [ ] Sélecteur langue
   - [ ] Pré-cache messages PWA

2. **Documentation**
   - [ ] README frontend
   - [ ] Guide composants
   - [ ] Guide accessibilité

### **Phase 10 : PWA (Phase 2 - Semaine 12+)**

1. **Service Worker**
   - [ ] Configuration next-pwa
   - [ ] Cache stratégies
   - [ ] Mode offline
   - [ ] Sync file d'attente

2. **Notifications Push**
   - [ ] Setup notifications
   - [ ] Permissions utilisateur
   - [ ] Gestion abonnements

---

## 🔧 **CONFIGURATIONS CLÉS**

### **next.config.js**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Images
  images: {
    domains: ['localhost', 'mathakine.onrender.com'],
  },
  
  // i18n
  i18n: {
    locales: ['fr', 'en'],
    defaultLocale: 'fr',
  },
  
  // Headers sécurité
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

### **tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#8b5cf6',
          dark: '#7c3aed',
          light: '#a78bfa',
        },
        background: '#0a0a0f',
        surface: '#12121a',
      },
      animation: {
        'star-twinkle': 'twinkle 3s ease-in-out infinite',
        'planet-rotate': 'rotate 20s linear infinite',
      },
    },
  },
  plugins: [],
};
```

### **tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": true,
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## ✅ **CHECKLIST VALIDATION**

### **Fonctionnalités**
- [ ] Authentification complète (login, register, logout)
- [ ] Génération exercices (standard + IA)
- [ ] Résolution exercices avec feedback
- [ ] Défis logiques avec indices
- [ ] Dashboard avec statistiques
- [ ] Badges et gamification
- [ ] Recommandations personnalisées

### **Accessibilité**
- [ ] WCAG 2.1 AAA compliance
- [ ] Mode contraste élevé
- [ ] Mode dyslexie
- [ ] Réduction animations
- [ ] Mode Focus TSA/TDAH
- [ ] Navigation clavier complète
- [ ] Support lecteurs d'écran

### **Performance**
- [ ] First Contentful Paint < 2s
- [ ] Time to Interactive < 100ms
- [ ] Mobile-first optimisé
- [ ] Bundle size optimisé
- [ ] Images optimisées

### **Tests**
- [ ] Tests unitaires composants
- [ ] Tests E2E parcours critiques
- [ ] Tests accessibilité
- [ ] Tests visual regression

### **i18n**
- [ ] Traductions FR complètes
- [ ] Traductions EN complètes
- [ ] Sélecteur langue fonctionnel
- [ ] Pré-cache messages PWA

---

## 🎯 **PROCHAINES ÉTAPES IMMÉDIATES**

1. **Créer le projet Next.js**
   ```bash
   npx create-next-app@latest mathakine-frontend --typescript --tailwind --app
   cd mathakine-frontend
   ```

2. **Installer dépendances**
   ```bash
   npm install @tanstack/react-query zustand framer-motion recharts next-intl
   npm install -D @types/node vitest @testing-library/react @playwright/test
   ```

3. **Setup shadcn/ui**
   ```bash
   npx shadcn-ui@latest init
   ```

4. **Créer structure de base**
   - Créer dossiers `components/`, `lib/`, `types/`
   - Configurer `tsconfig.json` avec paths
   - Créer `app/layout.tsx` de base

---

**Prêt à démarrer la refonte ! 🚀**

