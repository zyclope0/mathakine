# Chat discussionnel (frontend)

Architecture cible (lot **IA13b**, alignée sur l’esprit **IA13a** sans abstraction « super-IA » partagée avec les widgets de génération).

## Couches

| Couche                          | Emplacement                                          | Rôle                                                                   |
| ------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| **Client HTTP + SSE**           | `lib/api/chat.ts`                                    | `POST` vers `/api/chat/stream`, parsing des événements `data: {...}`   |
| **Types / helpers métier chat** | `lib/chat/`                                          | Messages UI, historique API (`conversationHistory.ts`)                 |
| **Hook de flux**                | `hooks/chat/useChat.ts`                              | État messages, suggestions, phase transport, envoi, erreurs            |
| **Présentation**                | `components/chat/`                                   | Liste de messages, suggestions, composer (variantes embedded / drawer) |
| **Shells produit**              | `components/home/Chatbot.tsx`, `components/chat/ChatbotFloating.tsx` | Carte home vs drawer global (shell), quota invité côté client          |

## Ce qui reste volontairement hors partage

- Les **dispatchers SSE** des exercices/défis (`lib/ai/generation/…`) : autre schéma d’événements et auth.
- Une **abstraction unique « toute IA »** : le chat est public, rate-limité, transport SSE simple ; forcer une API commune obscurcirait les deux mondes.

## Imports

Les consommateurs peuvent continuer à importer depuis `@/hooks/useChat` (réexport).
