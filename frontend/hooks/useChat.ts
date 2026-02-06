'use client';

import { useState } from 'react';
import { nanoid } from 'nanoid';
import { streamChat } from '@/lib/api/chat';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  error?: boolean;
}

export interface UseChatOptions {
  initialMessages?: Message[];
  initialSuggestions?: string[];
}

type ChatStatus = 'idle' | 'awaiting_response' | 'streaming';

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>(options.initialMessages || []);
  const [suggestions, setSuggestions] = useState<string[]>(options.initialSuggestions || []);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState<ChatStatus>('idle');
  const [error, setError] = useState<Error | null>(null);

  const handleSend = async (messageContent: string) => {
    if (status !== 'idle') return;

    if (suggestions.length > 0) {
      setSuggestions([]);
    }

    setError(null);
    setStatus('awaiting_response');

    const userMessage: Message = {
      id: nanoid(),
      role: 'user',
      content: messageContent.trim(),
    };
    setMessages((prev) => [...prev, userMessage]);

    const assistantMessageId = nanoid();
    setMessages((prev) => [
      ...prev,
      { id: assistantMessageId, role: 'assistant', content: '' },
    ]);

    let firstChunk = true;
    await streamChat(
      {
        message: messageContent.trim(),
        conversation_history: messages.slice(-5).map((m) => ({
          role: m.role,
          content: m.content,
        })),
        stream: true,
      },
      {
        onChunk: (chunk) => {
          if (firstChunk) {
            firstChunk = false;
            setStatus('streaming');
          }
          if (chunk.type === 'chunk') {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + chunk.content }
                  : msg
              )
            );
          }
        },
        onFinish: () => {
          setStatus('idle');
        },
        onError: (err) => {
          setError(err);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
                    error: true,
                  }
                : msg
            )
          );
          setStatus('idle');
        },
      }
    );
  };
  
  const sendInputMessage = () => {
    const currentInput = input.trim();
    if (currentInput) {
      setInput('');
      handleSend(currentInput);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendInputMessage();
    }
  };

  return {
    messages,
    suggestions,
    input,
    setInput,
    status,
    isLoading: status !== 'idle',
    error,
    handleSend,
    sendInputMessage,
    handleKeyPress,
  };
}
