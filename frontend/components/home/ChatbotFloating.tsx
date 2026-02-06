'use client';

import { useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useChat } from '@/hooks/useChat';
import { useTranslations } from 'next-intl';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatbotFloatingProps {
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/**
 * Chatbot Flottant - Version améliorée
 * 
 * - Bouton flottant positionné à gauche des boutons d'accessibilité
 * - Chat en drawer slide-in depuis la droite (plus grand et mieux positionné)
 */
export function ChatbotFloating({ isOpen = false, onOpenChange }: ChatbotFloatingProps) {
  const t = useTranslations('home.chatbot');
  
  const { messages, input, setInput, handleSend, sendInputMessage, handleKeyPress, isLoading, suggestions } = useChat({
    initialMessages: [
      {
        id: '1',
        role: 'assistant',
        content: t('initialMessage'),
      },
    ],
    initialSuggestions: [
      "Qu'est-ce que Mathakine ?",
      "Comment progresser ?",
      "Créer un exercice"
    ]
  });

  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleOpenChange = (open: boolean) => {
    onOpenChange?.(open);
  };

  // Auto-scroll vers le bas
  useEffect(() => {
    if (isOpen && messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  // Focus input à l'ouverture
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  return (
    <>
      {/* Overlay sombre quand ouvert */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 animate-in fade-in duration-200"
          onClick={() => handleOpenChange(false)}
          aria-hidden="true"
        />
      )}

      {/* Panel de chat - Drawer depuis la droite */}
      <div 
        className={cn(
          "fixed top-0 right-0 h-full w-full sm:w-[400px] z-50",
          "bg-background border-l shadow-2xl",
          "transition-transform duration-300 ease-out",
          isOpen ? "translate-x-0" : "translate-x-full"
        )}
      >
        <Card className="flex flex-col h-full rounded-none border-0">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b bg-primary/5">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                <MessageCircle className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h2 className="font-semibold">{t('title')}</h2>
                <p className="text-xs text-muted-foreground">Pose-moi tes questions !</p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-10 w-10"
              onClick={() => handleOpenChange(false)}
              aria-label="Fermer l'assistant"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Messages */}
          <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <MessageCircle className="h-4 w-4 text-primary" />
                  </div>
                )}
                <div 
                  className={cn(
                    'prose prose-sm max-w-[85%] rounded-2xl px-4 py-3',
                    message.role === 'user' 
                      ? 'bg-primary text-primary-foreground rounded-br-md' 
                      : 'bg-muted rounded-bl-md'
                  )}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
            {isLoading && messages[messages.length - 1]?.role === 'user' && (
              <div className="flex justify-start gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
                  <MessageCircle className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              </div>
            )}
          </div>

          {/* Suggestions (seulement au début) */}
          {messages.length <= 1 && suggestions.length > 0 && (
            <div className="px-4 pb-3 border-t pt-3">
              <p className="text-xs text-muted-foreground mb-2">Suggestions :</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((s, i) => (
                  <Button 
                    key={i} 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleSend(s)} 
                    className="text-xs h-8 rounded-full"
                  >
                    {s}
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t bg-background">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={t('inputPlaceholder')}
                disabled={isLoading}
                className="flex-1 rounded-full border border-input bg-muted/50 px-4 py-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
                aria-label="Message"
              />
              <Button 
                onClick={sendInputMessage} 
                disabled={!input.trim() || isLoading} 
                size="icon"
                className="h-11 w-11 rounded-full"
                aria-label="Envoyer"
              >
                {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Bouton flottant - Positionné à gauche des boutons d'accessibilité */}
      <Button
        onClick={() => handleOpenChange(!isOpen)}
        className={cn(
          "fixed bottom-4 right-20 z-30 h-12 w-12 rounded-full shadow-lg",
          "transition-all duration-200 hover:scale-110",
          isOpen 
            ? "opacity-0 pointer-events-none" 
            : "bg-primary hover:bg-primary/90 text-primary-foreground"
        )}
        aria-label="Ouvrir l'assistant mathématique"
      >
        <MessageCircle className="h-5 w-5" />
      </Button>
    </>
  );
}
