# Chat discussionnel (frontend)

Architecture cible (lot **IA13b**, alignée sur l’esprit **IA13a** sans abstraction « super-IA » partagée avec les widgets de génération).  
**FFI-L16** précise l’ownership shell : assistant **global** sous `components/chat/` ; carte embarquée home sous `components/home/Chatbot.tsx`.

## Couches

| Couche                          | Emplacement                                          | Rôle                                                                                                                                           |
| ------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Client HTTP + SSE**           | `lib/api/chat.ts`                                    | `POST` vers `/api/chat/stream`, parsing des événements `data: {...}`                                                                           |
| **Types / helpers métier chat** | `lib/chat/`                                          | Messages UI, historique API (`conversationHistory.ts`)                                                                                         |
| **Hook de flux**                | `hooks/chat/useChat.ts` (réexport `@/hooks/useChat`) | État messages, suggestions, phase transport, envoi, erreurs                                                                                    |
| **Quota invité session**        | `hooks/chat/useGuestChatAccess.ts`                   | Plafond **5 messages** par session navigateur (`sessionStorage`) ; état compatible SSR/hydratation ; **ne remplace pas** le rate-limit serveur |
| **Présentation**                | `components/chat/`                                   | Drawer global, FAB, liste messages, composer, suggestions                                                                                      |
| **Shell marketing home**        | `components/home/Chatbot.tsx`                        | Carte / bloc assistant sur la page d’accueil (non confondue avec le drawer global)                                                             |

## Décisions produit (documentées, FFI-L16)

- **Invités (public)** : l’assistant reste accessible ; **pas** de CTA « Assistant » dans le **header** ; entrée via le **FAB global** (`ChatbotFloatingGlobal`).
- **Quota invité** : **5 messages** max par session navigateur côté client (`useGuestChatAccess`). Le **backend** conserve le **rate-limit** existant sur le chat : c’est l’**autorité** serveur ; le plafond client est une couche UX complémentaire.
- **Authentifiés** : comportement inchangé ; CTA Assistant dans le header conservé.
- **Reliquat explicite** : durcissement optionnel futur (quota invité aligné serveur via cookie / IP / clé dédiée) — hors périmètre de clôture **FFI-L16** frontend.

## Ce qui reste volontairement hors partage

- Les **dispatchers SSE** des exercices/défis (`lib/ai/generation/…`) : autre schéma d’événements et auth.
- Une **abstraction unique « toute IA »** : le chat est public, rate-limité, transport SSE simple ; forcer une API commune obscurcirait les deux mondes.

## Imports

Les consommateurs peuvent continuer à importer depuis `@/hooks/useChat` (réexport).
