'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useAccessibleAnimation } from '@/lib/hooks/useAccessibleAnimation';
import { useTranslations } from 'next-intl';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  imageUrl?: string; // URL de l'image générée (si présente)
}

/**
 * Chatbot - Assistant virtuel pour répondre aux questions sur Mathakine
 * 
 * Utilise OpenAI via le backend pour répondre aux questions
 * Design discret et sobre, accessible
 */
export function Chatbot() {
  const t = useTranslations('home.chatbot');
  const [isOpen, setIsOpen] = useState(true); // Ouvert par défaut
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: t('initialMessage'),
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Fonction pour nettoyer les placeholders d'images Markdown
  const cleanMarkdownPlaceholders = (text: string): string => {
    // Supprimer les images Markdown avec placeholders (via.placeholder, example.com, etc.)
    let cleaned = text.replace(
      /!\[([^\]]*)\]\([^)]*(?:placeholder|via\.placeholder|example\.com|example\.org)[^)]*\)/gi,
      '$1' // Remplacer par juste le texte alternatif
    );
    // Supprimer aussi les images Markdown sans URL valide
    cleaned = cleaned.replace(
      /!\[([^\]]*)\]\([^)]*\)/g,
      (match, altText) => {
        // Si l'URL ne contient pas http/https, c'est probablement un placeholder
        return match.toLowerCase().includes('http') ? match : altText;
      }
    );
    return cleaned;
  };

  // Scroll vers le bas quand de nouveaux messages arrivent (dans le conteneur, pas la page)
  useEffect(() => {
    if (isOpen && messagesContainerRef.current) {
      // Utiliser scrollTop au lieu de scrollIntoView pour éviter de scroller la page entière
      const container = messagesContainerRef.current;
      const scrollToBottom = () => {
        container.scrollTop = container.scrollHeight;
      };
      
      // Petit délai pour laisser le DOM se mettre à jour
      setTimeout(scrollToBottom, 100);
    }
  }, [messages, isOpen]);

  // Focus sur l'input seulement si l'utilisateur ouvre explicitement le chat
  // Ne pas prendre le focus au chargement initial de la page
  const [hasUserInteracted, setHasUserInteracted] = useState(false);
  
  useEffect(() => {
    // Ne prendre le focus que si l'utilisateur a déjà interagi avec le chat
    if (isOpen && inputRef.current && hasUserInteracted) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen, hasUserInteracted]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    // Marquer que l'utilisateur a interagi avec le chat
    if (!hasUserInteracted) {
      setHasUserInteracted(true);
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsLoading(true);

    // Créer un message assistant vide pour le streaming
    const assistantMessageId = (Date.now() + 1).toString();
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      // Utiliser fetch avec POST pour le streaming SSE (EventSource ne supporte que GET)
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message: currentInput,
          conversation_history: messages.slice(-5).map((m) => ({
            role: m.role,
            content: m.content,
          })),
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la communication avec l\'assistant');
      }

      // Lire le stream SSE
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('Impossible de lire le stream');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Garder la dernière ligne incomplète dans le buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'chunk') {
                // Nettoyer le contenu avant de l'ajouter (supprimer placeholders Markdown)
                const cleanedContent = cleanMarkdownPlaceholders(data.content);
                // Ajouter le chunk au message assistant
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: msg.content + cleanedContent }
                      : msg
                  )
                );
              } else if (data.type === 'status') {
                // Message de statut (optionnel, peut être affiché)
                console.log('Status:', data.message);
              } else if (data.type === 'image') {
                // Image générée
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? { ...msg, imageUrl: data.url }
                      : msg
                  )
                );
              } else if (data.type === 'done') {
                // Stream terminé
                setIsLoading(false);
                return;
              } else if (data.type === 'error') {
                throw new Error(data.message || 'Erreur lors de la génération');
              }
            } catch (parseError) {
              console.error('Erreur parsing SSE:', parseError);
            }
          }
        }
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: assistantMessageId,
        role: 'assistant',
        content: 'Désolé, une erreur est survenue. Veuillez réessayer plus tard.',
        timestamp: new Date(),
      };
      setMessages((prev) =>
        prev.map((msg) => (msg.id === assistantMessageId ? errorMessage : msg))
      );
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
      <div className="w-full max-w-4xl mx-auto space-y-3 md:space-y-4">
        <div className="text-center space-y-1 md:space-y-2">
          <h2 id="chatbot-title" className="text-2xl sm:text-3xl md:text-4xl font-bold">
            {t('title')}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto px-4 text-sm md:text-base">
            {t('description')}
          </p>
        </div>
      
      {/* Fenêtre de chat intégrée */}
      <Card
        className={cn(
          'w-full flex flex-col shadow-lg transition-all',
          isOpen ? 'h-[450px] md:h-[500px]' : 'h-14 md:h-16'
        )}
      >
          {/* En-tête */}
          <div className="flex items-center justify-between p-4 border-b bg-primary/5">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-primary" aria-hidden="true" />
              <h3 className="font-semibold">{t('title')}</h3>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setIsOpen(!isOpen);
                // Marquer l'interaction si l'utilisateur ouvre le chat
                if (!isOpen && !hasUserInteracted) {
                  setHasUserInteracted(true);
                }
              }}
              aria-label={isOpen ? t('collapseLabel') : t('expandLabel')}
              className="h-8 w-8"
            >
              {isOpen ? (
                <X className="h-4 w-4" aria-hidden="true" />
              ) : (
                <MessageCircle className="h-4 w-4" aria-hidden="true" />
              )}
            </Button>
          </div>

          {/* Messages */}
          {isOpen && (
            <>
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4"
          >
            {messages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[80%] rounded-lg px-4 py-2',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{cleanMarkdownPlaceholders(message.content)}</p>
                  {/* Afficher l'image si présente */}
                  {message.imageUrl && (
                    <div className="mt-3 rounded-lg overflow-hidden">
                      <img
                        src={message.imageUrl}
                        alt="Visualisation mathématique"
                        className="w-full h-auto rounded-lg"
                        loading="lazy"
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted rounded-lg px-4 py-2">
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  // Marquer l'interaction quand l'utilisateur commence à taper
                  if (!hasUserInteracted) {
                    setHasUserInteracted(true);
                  }
                }}
                onKeyPress={handleKeyPress}
                onFocus={() => {
                  // Marquer l'interaction quand l'utilisateur clique sur l'input
                  if (!hasUserInteracted) {
                    setHasUserInteracted(true);
                  }
                }}
                placeholder={t('inputPlaceholder')}
                disabled={isLoading}
                className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
                aria-label={t('inputLabel')}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
                aria-label={t('sendButton')}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                ) : (
                  <Send className="h-4 w-4" aria-hidden="true" />
                )}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              {t('info')}
            </p>
          </div>
          </>
          )}
        </Card>
    </div>
  );
}

