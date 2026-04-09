# Chat discussionnel (frontend)

Architecture cible (lot **IA13b**, alignée sur l’esprit **IA13a** sans abstraction « super-IA » partagée avec les widgets de génération).  
**FFI-L16** précise l’ownership shell : assistant **global** sous `components/chat/` ; carte embarquée home sous `components/home/Chatbot.tsx`.

## Couches

| Couche                          | Emplacement                                          | Rôle                                                                                                                                           |
| ------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Client HTTP + SSE**           | `lib/api/chat.ts`                                    | `POST` vers `/api/chat/stream` (même origine), `credentials: "include"`, en-tête `X-CSRF-Token` si cookie présent                               |
| **Proxy Next → backend**        | `lib/api/chatProxyRequest.ts` + `app/api/chat/*`     | Garde `access_token` ; relais cookies + CSRF ; 401 aligné sur le backend (`UNAUTHORIZED`) — **CHAT-AUTH-01** ; libellés proxy utilisateur depuis `messages/*` (`apiChat.proxy`) + `lib/api/chatProxyLocale.ts` — **CHAT-I18N-03** |
| **Types / helpers métier chat** | `lib/chat/`                                          | Messages UI, historique API (`conversationHistory.ts`)                                                                                         |
| **Hook de flux**                | `hooks/chat/useChat.ts` (réexport `@/hooks/useChat`) | État messages, suggestions, phase transport, envoi, erreurs                                                                                    |
| **Quota invité (legacy)**       | `hooks/chat/useGuestChatAccess.ts`                   | Ancien plafond **5 messages** session (`sessionStorage`) ; **non branché** sur les surfaces chat produit après **CHAT-AUTH-01** ; tests conservés |
| **Présentation**                | `components/chat/`                                   | Drawer global, FAB, liste messages, composer, suggestions                                                                                        |
| **Shell marketing home**        | `components/home/Chatbot.tsx`                        | Carte / bloc assistant sur la page d’accueil ; même politique d’envoi que le drawer (auth requise)                                            |

## Décisions produit (à jour)

- **Invités** : le shell assistant reste visible (FAB global, bloc home) ; **l’envoi** exige connexion — message **`guestLimitCta`** (clé i18n existante) + liens login / inscription. Pas d’appel réseau chat tant que la session est absente (garde UI + refus Next + JWT backend).
- **Authentifiés** : flux inchangé pour l’utilisateur connecté (cookies session + CSRF).
- **Autorité** : le **backend** impose le JWT ; le proxy Next évite le trafic inutile et propage les en-têtes attendus.

## Ce qui reste volontairement hors partage

- Les **dispatchers SSE** des exercices/défis (`lib/ai/generation/…`) : autre schéma d’événements et politique d’accès.
- Une **abstraction unique « toute IA »** : le chat et la génération pédagogique restent des flux distincts.

## Imports

Les consommateurs peuvent continuer à importer depuis `@/hooks/useChat` (réexport).
