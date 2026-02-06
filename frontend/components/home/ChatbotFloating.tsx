'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { MessageCircle, X, Send, Loader2, Minimize2 } from 'lucide-react';
import { cn } from '@/lib/utils/cn';
import { useChat } from '@/hooks/useChat';
import { useTranslations } from 'next-intl';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

/**
 * Chatbot Flottant - Version compacte
 * 
 * Bouton flottant en bas à droite de l'écran.
 * Au clic, ouvre une fenêtre de chat compacte.
 */
export function ChatbotFloating() {
  const t = useTranslations('home.chatbot');
  const [isOpen, setIsOpen] = useState(false);
  
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

  // Auto-scroll vers le bas
  useEffect(() => {
    if (isOpen && messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  // Focus input à l'ouverture
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 200);
    }
  }, [isOpen]);

  return (
    <>
      {/* Fenêtre de chat */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 z-50 w-[350px] max-w-[calc(100vw-2rem)] animate-in slide-in-from-bottom-4 fade-in duration-200">
          <Card className="flex flex-col h-[450px] shadow-2xl border-primary/20">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b bg-primary/5 rounded-t-lg">
              <div className="flex items-center gap-2">
                <MessageCircle className="h-5 w-5 text-primary" />
                <span className="font-semibold text-sm">{t('title')}</span>
              </div>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-8 w-8"
                onClick={() => setIsOpen(false)}
                aria-label="Fermer le chat"
              >
                <Minimize2 className="h-4 w-4" />
              </Button>
            </div>

            {/* Messages */}
            <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-3 space-y-3">
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={cn(
                    'flex gap-2',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <MessageCircle className="h-5 w-5 text-primary flex-shrink-0 mt-1" />
                  )}
                  <div 
                    className={cn(
                      'prose prose-sm max-w-[80%] rounded-lg px-3 py-2 text-sm',
                      message.role === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted'
                    )}
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>
              ))}
              {isLoading && messages[messages.length - 1]?.role === 'user' && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-lg px-3 py-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}
            </div>

            {/* Suggestions (seulement au début) */}
            {messages.length <= 1 && suggestions.length > 0 && (
              <div className="px-3 pb-2 border-t pt-2">
                <div className="flex flex-wrap gap-1">
                  {suggestions.map((s, i) => (
                    <Button 
                      key={i} 
                      variant="outline" 
                      size="sm" 
                      onClick={() => handleSend(s)} 
                      className="text-xs h-7 px-2"
                    >
                      {s}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-3 border-t bg-background rounded-b-lg">
              <div className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={t('inputPlaceholder')}
                  disabled={isLoading}
                  className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
                  aria-label="Message"
                />
                <Button 
                  onClick={sendInputMessage} 
                  disabled={!input.trim() || isLoading} 
                  size="icon"
                  className="h-9 w-9"
                  aria-label="Envoyer"
                >
                  {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Bouton flottant */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "fixed bottom-4 right-4 z-50 h-14 w-14 rounded-full shadow-lg",
          "bg-primary hover:bg-primary/90 text-primary-foreground",
          "transition-transform hover:scale-105",
          isOpen && "bg-muted hover:bg-muted/90 text-muted-foreground"
        )}
        aria-label={isOpen ? "Fermer l'assistant" : "Ouvrir l'assistant mathématique"}
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </Button>
    </>
  );
}
