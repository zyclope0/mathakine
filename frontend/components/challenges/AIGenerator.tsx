'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Sparkles, X, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CHALLENGE_TYPES, AGE_GROUPS, type ChallengeType, type AgeGroup } from '@/lib/constants/challenges';
import { useChallengeTranslations } from '@/hooks/useChallengeTranslations';
import type { Challenge } from '@/types/api';
import { useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/hooks/useAuth';

interface AIGeneratorProps {
  onChallengeGenerated?: (challenge: Challenge) => void;
}

export function AIGenerator({ onChallengeGenerated }: AIGeneratorProps) {
  const [challengeType, setChallengeType] = useState<ChallengeType>(CHALLENGE_TYPES.SEQUENCE);
  const [ageGroup, setAgeGroup] = useState<AgeGroup>(AGE_GROUPS.GROUP_9_11);
  const [customPrompt, setCustomPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [streamedText, setStreamedText] = useState('');
  const [generatedChallenge, setGeneratedChallenge] = useState<Challenge | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();
  const t = useTranslations('challenges');
  const { getTypeDisplay, getAgeDisplay } = useChallengeTranslations();
  const { user, isLoading: isAuthLoading } = useAuth();

  // Nettoyer l'AbortController lors du démontage
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleAIGenerate = async () => {
    if (isGenerating) return;

    // Vérifier l'authentification
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      console.log('[AIGenerator] User auth state:', { 
        hasUser: !!user, 
        userId: user?.id, 
        username: user?.username 
      });
    }
    
    if (!user) {
      if (isDev) console.error('[AIGenerator] User not authenticated');
      toast.error(t('aiGenerator.authRequired'), {
        description: t('aiGenerator.authRequiredDescription'),
        action: {
          label: t('aiGenerator.login'),
          onClick: () => router.push('/login'),
        },
      });
      return;
    }

    if (isDev) console.log('[AIGenerator] User authenticated, starting generation');
    setIsGenerating(true);
    setStreamedText('');
    setGeneratedChallenge(null);

    try {
      // Construire l'URL avec les paramètres
      const params = new URLSearchParams({
        challenge_type: challengeType,
        age_group: ageGroup,
      });
      if (customPrompt.trim()) {
        params.append('prompt', customPrompt.trim());
      }

      // Créer un AbortController pour pouvoir annuler la requête
      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      // Appeler directement le backend (pas d'API route proxy)
      // C'est la même approche que tous les autres endpoints (login, exercices, etc.)
      const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL;
      
      if (!backendUrl) {
        // En développement, utiliser localhost par défaut
        // En production, les variables d'environnement DOIVENT être définies
        const isDev = process.env.NODE_ENV === 'development';
        if (!isDev) {
          throw new Error('Configuration manquante: NEXT_PUBLIC_API_BASE_URL non défini');
        }
      }
      
      const finalUrl = backendUrl || 'http://localhost:10000';
      const url = `${finalUrl}/api/challenges/generate-ai-stream?${params.toString()}`;
      
      if (process.env.NODE_ENV === 'development') {
        console.log('[AIGenerator] Calling backend:', url);
      }
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'text/event-stream',
        },
        credentials: 'include', // Important : envoie les cookies HTTP-only
        signal: abortController.signal, // Permet l'annulation
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      // Buffer pour accumuler les données incomplètes
      let buffer = '';

      // Lire le stream
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          setIsGenerating(false);
          break;
        }

        // Décoder le chunk et l'ajouter au buffer
        const newChunk = decoder.decode(value, { stream: true });
        buffer += newChunk;
        
        if (newChunk && isDev) {
          console.log('[AIGenerator] Received chunk:', newChunk.substring(0, 100), '...');
        }
        
        // Traiter toutes les lignes complètes dans le buffer
        const lines = buffer.split('\n');
        
        // Garder la dernière ligne (potentiellement incomplète) dans le buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          
          if (trimmedLine.startsWith('data: ')) {
            try {
              const jsonStr = trimmedLine.slice(6);
              const data = JSON.parse(jsonStr);

              if (isDev) console.log('[AIGenerator] Received SSE message:', data.type);

              if (data.type === 'status') {
                // Message de statut uniquement
                setStreamedText(data.message);
              } else if (data.type === 'challenge') {
                // Challenge complet reçu
                const challenge = data.challenge as Challenge;
                
                // Vérifier que le challenge est valide
                if (!challenge || !challenge.title) {
                  if (isDev) console.error('Challenge invalide reçu:', challenge);
                  toast.error(t('aiGenerator.error'), {
                    description: t('aiGenerator.errorDescription'),
                  });
                  setStreamedText('');
                  setIsGenerating(false);
                  return;
                }
                
                setGeneratedChallenge(challenge);
                setStreamedText(''); // Nettoyer le message de statut
                setIsGenerating(false);

                // Invalider le cache pour recharger la liste
                queryClient.invalidateQueries({ queryKey: ['challenges'] });
                queryClient.invalidateQueries({ queryKey: ['completed-challenges'] });

                toast.success(t('aiGenerator.success'), {
                  description: t('aiGenerator.successDescription', { title: challenge.title }),
                });

                // Appeler le callback si fourni
                if (onChallengeGenerated) {
                  onChallengeGenerated(challenge);
                }
                return;
              } else if (data.type === 'error') {
                setStreamedText(''); // Nettoyer le message de statut
                setIsGenerating(false);
                toast.error(t('aiGenerator.error'), {
                  description: data.message || t('aiGenerator.errorDescription'),
                });
                return;
              } else if (data.type === 'done') {
                // Génération terminée
                setStreamedText('');
                setIsGenerating(false);
                return;
              }
            } catch (parseError) {
              if (isDev) console.error('[AIGenerator] Erreur de parsing SSE:', parseError, 'Line:', trimmedLine);
            }
          }
        }
      }
    } catch (error) {
      // Ne pas afficher d'erreur si la requête a été annulée par l'utilisateur
      if (error instanceof Error && error.name === 'AbortError') {
        if (isDev) console.log('[AIGenerator] Génération annulée par l\'utilisateur');
        setIsGenerating(false);
        return;
      }
      
      if (isDev) console.error('Erreur lors de la génération:', error);
      setIsGenerating(false);
      toast.error(t('aiGenerator.connectionError'), {
        description: t('aiGenerator.connectionErrorDescription'),
      });
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsGenerating(false);
    setStreamedText('');
  };

  const handleViewChallenge = () => {
    if (generatedChallenge?.id) {
      router.push(`/challenge/${generatedChallenge.id}`);
    }
  };

  return (
    <Card className="h-full bg-card border-primary/20 shadow-lg">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center text-primary-on-dark text-sm md:text-base">
          <Sparkles className="mr-2 h-4 w-4 text-primary" />
          {t('aiGenerator.title')}
        </CardTitle>
        <CardDescription className="text-xs hidden sm:block">
          {t('aiGenerator.description')}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2 pt-0">
        {/* Sélecteurs de type et groupe d'âge */}
        <div className="grid grid-cols-2 gap-2">
          <div className="space-y-1">
            <label htmlFor="ai-challenge-type" className="block text-xs font-medium text-muted-foreground">
              {t('aiGenerator.challengeType')}
            </label>
            <Select
              value={challengeType}
              onValueChange={(value: ChallengeType) => setChallengeType(value)}
              disabled={isGenerating}
            >
              <SelectTrigger id="ai-challenge-type" className="w-full h-8 text-xs bg-background text-foreground border-primary/30">
                <SelectValue placeholder={t('aiGenerator.selectType')} />
              </SelectTrigger>
              <SelectContent className="bg-card border-primary/30">
                {Object.values(CHALLENGE_TYPES).map((type) => (
                  <SelectItem key={type} value={type} className="text-foreground hover:bg-primary/10">
                    {getTypeDisplay(type)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <label htmlFor="ai-age-group" className="block text-xs font-medium text-muted-foreground">
              {t('aiGenerator.ageGroup')}
            </label>
            <Select
              value={ageGroup}
              onValueChange={(value: AgeGroup) => setAgeGroup(value)}
              disabled={isGenerating}
            >
              <SelectTrigger id="ai-age-group" className="w-full h-8 text-xs bg-background text-foreground border-primary/30">
                <SelectValue placeholder={t('aiGenerator.selectAgeGroup')} />
              </SelectTrigger>
              <SelectContent className="bg-card border-primary/30">
                {Object.values(AGE_GROUPS).map((group) => (
                  <SelectItem key={group} value={group} className="text-foreground hover:bg-primary/10">
                    {getAgeDisplay(group)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Prompt personnalisé (optionnel) */}
        <div className="space-y-1">
          <label htmlFor="ai-prompt" className="block text-xs font-medium text-muted-foreground">
            {t('aiGenerator.customPrompt')}
          </label>
          <textarea
            id="ai-prompt"
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder={t('aiGenerator.customPromptPlaceholder')}
            className="w-full p-2 text-xs rounded-lg bg-background text-foreground border border-primary/30 min-h-[60px] resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            disabled={isGenerating}
          />
        </div>

        {/* Affichage du streaming - Indicateur simple */}
        {isGenerating && (
          <div className="p-3 rounded-lg bg-card border border-primary/20 relative flex items-center gap-2">
            <div className="flex-shrink-0">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
            </div>
            <div className="flex-1">
              <p className="text-xs text-muted-foreground">
                {streamedText || t('aiGenerator.generating')}
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="h-6 w-6 p-0"
              aria-label={t('aiGenerator.cancel')}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}

        {/* Challenge généré */}
        {generatedChallenge && !isGenerating && (
          <div className="p-3 rounded-lg bg-success/10 border border-success/30">
            <p className="text-xs font-medium text-success mb-1">
              {t('aiGenerator.success')}
            </p>
            <p className="text-xs text-muted-foreground mb-2">
              {generatedChallenge.title}
            </p>
            <Button
              onClick={handleViewChallenge}
              size="sm"
              variant="outline"
              className="w-full text-xs"
            >
              {t('aiGenerator.viewChallenge')}
            </Button>
          </div>
        )}

        {/* Message si non authentifié */}
        {!user && !isAuthLoading && (
          <div className="p-3 rounded-lg bg-warning/10 border border-warning/30 flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-warning mt-0.5 flex-shrink-0" />
            <div className="text-xs text-warning">
              <p className="font-medium mb-1">{t('aiGenerator.authRequired')}</p>
              <p className="text-xs opacity-80">{t('aiGenerator.authRequiredDescription')}</p>
            </div>
          </div>
        )}

        {/* Bouton de génération */}
        <Button
          onClick={handleAIGenerate}
          disabled={isGenerating || !user || isAuthLoading}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
          size="sm"
          title={!user ? t('aiGenerator.authRequired') : undefined}
        >
          {isGenerating ? (
            <>
              <Loader2 className="mr-2 h-3 w-3 animate-spin" />
              {t('aiGenerator.generating')}
            </>
          ) : (
            <>
              <Sparkles className="mr-2 h-3 w-3" />
              {t('aiGenerator.generate')}
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

