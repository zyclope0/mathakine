# Correction: Erreur "Non authentifié" lors de la génération IA

## 🐛 Problème identifié

**Symptôme**: Erreur "Non authentifié" lors de la tentative de génération de défis logiques avec l'IA.

**Date**: 18 novembre 2025  
**Contexte**: Génération IA de défis logiques via EventSource (SSE)  
**Impact**: Impossible de générer des défis avec l'IA, même pour les utilisateurs connectés

---

## 🔍 Analyse de la cause

### Problème 1: Cookies d'authentification non transmis

Le composant `AIGenerator` utilisait `EventSource` pour se connecter au backend via un proxy Next.js. Cependant:

1. **EventSource** ne supporte pas nativement l'envoi de credentials (cookies) avec certaines configurations
2. Le proxy Next.js récupérait les cookies avec `request.headers.get('cookie')` qui peut ne pas capturer tous les cookies
3. Aucune vérification préalable de l'authentification côté frontend

### Problème 2: Absence de feedback utilisateur

- Aucun message d'avertissement si l'utilisateur n'était pas connecté
- Erreur générique "Non authentifié" sans indication de la marche à suivre
- Bouton de génération actif même sans authentification

---

## ✅ Solution appliquée

### 1. Amélioration de la récupération des cookies dans le proxy

**Fichier**: `frontend/app/api/challenges/generate-ai-stream/route.ts`

#### Avant ❌
```typescript
// Récupérer les cookies de la requête
const cookies = request.headers.get('cookie') || '';
```

#### Après ✅
```typescript
// Récupérer les cookies de la requête (tous les cookies disponibles)
const cookies = request.cookies.getAll()
  .map(cookie => `${cookie.name}=${cookie.value}`)
  .join('; ');

// Debug: Vérifier si les cookies d'authentification sont présents
const hasAuthCookie = request.cookies.get('access_token');
if (process.env.NODE_ENV === 'development') {
  console.log('[AI Stream Proxy] Auth cookie present:', !!hasAuthCookie);
}

// Si pas de cookie d'authentification, retourner une erreur immédiatement
if (!hasAuthCookie) {
  return new Response(
    `data: ${JSON.stringify({ type: 'error', message: 'Non authentifié' })}\n\n`,
    {
      status: 200, // 200 pour que EventSource reçoive le message
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    }
  );
}
```

**Avantages**:
- ✅ Utilise `request.cookies.getAll()` plus fiable que `headers.get('cookie')`
- ✅ Vérification précoce de la présence du cookie d'authentification
- ✅ Retour immédiat d'erreur si non authentifié (évite appel backend inutile)
- ✅ Logging en développement pour faciliter le débogage

### 2. Vérification d'authentification côté frontend

**Fichier**: `frontend/components/challenges/AIGenerator.tsx`

#### Ajout du hook d'authentification

```typescript
import { useAuth } from '@/hooks/useAuth';

export function AIGenerator({ onChallengeGenerated }: AIGeneratorProps) {
  // ... autres states
  const { user, isLoading: isAuthLoading } = useAuth();
```

#### Vérification avant génération

```typescript
const handleAIGenerate = async () => {
  if (isGenerating) return;

  // Vérifier l'authentification
  if (!user) {
    toast.error(t('aiGenerator.authRequired'), {
      description: t('aiGenerator.authRequiredDescription'),
      action: {
        label: t('aiGenerator.login'),
        onClick: () => router.push('/login'),
      },
    });
    return;
  }

  // ... suite de la génération
};
```

**Avantages**:
- ✅ Empêche la génération si l'utilisateur n'est pas connecté
- ✅ Message d'erreur clair avec action (bouton "Se connecter")
- ✅ Redirection vers la page de connexion

#### Message d'avertissement visuel

```typescript
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
```

**Avantages**:
- ✅ Avertissement proactif avant que l'utilisateur ne tente de générer
- ✅ Style visuel cohérent avec le thème de l'application
- ✅ Message clair et explicite

#### Désactivation du bouton si non authentifié

```typescript
<Button
  onClick={handleAIGenerate}
  disabled={isGenerating || !user || isAuthLoading}
  className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
  size="sm"
  title={!user ? t('aiGenerator.authRequired') : undefined}
>
```

**Avantages**:
- ✅ Bouton désactivé si non authentifié
- ✅ Tooltip explicatif au survol
- ✅ Indicateur visuel clair pour l'utilisateur

### 3. Ajout des traductions

**Fichiers**: `frontend/messages/fr.json` et `frontend/messages/en.json`

```json
{
  "challenges": {
    "aiGenerator": {
      // ... traductions existantes
      "authRequired": "Connexion requise",
      "authRequiredDescription": "Vous devez être connecté pour générer des défis avec l'IA",
      "login": "Se connecter"
    }
  }
}
```

**Avantages**:
- ✅ Messages en français et anglais
- ✅ Cohérence avec le système i18n
- ✅ Messages clairs et actionnables

---

## 🧪 Tests recommandés

### Test 1: Génération sans authentification

1. Se déconnecter
2. Naviguer vers `/challenges`
3. Vérifier que:
   - ✅ Message d'avertissement affiché
   - ✅ Bouton "Générer" désactivé
   - ✅ Tooltip "Connexion requise" au survol du bouton

### Test 2: Tentative de génération sans authentification

1. Se déconnecter
2. Forcer l'activation du bouton (via console dev)
3. Cliquer sur "Générer"
4. Vérifier que:
   - ✅ Toast d'erreur avec message clair
   - ✅ Action "Se connecter" dans le toast
   - ✅ Clic sur l'action redirige vers `/login`

### Test 3: Génération avec authentification

1. Se connecter
2. Naviguer vers `/challenges`
3. Configurer un défi (type, âge)
4. Cliquer sur "Générer"
5. Vérifier que:
   - ✅ Génération démarre sans erreur
   - ✅ Messages de statut s'affichent
   - ✅ Défi généré s'affiche à la fin
   - ✅ Pas d'erreur "Non authentifié"

### Test 4: Cookie expiré pendant la génération

1. Se connecter
2. Attendre expiration du cookie (30 min)
3. Tenter une génération
4. Vérifier que:
   - ✅ Erreur claire "Non authentifié"
   - ✅ Suggestion de se reconnecter

### Test 5: Logs en développement

1. Mode développement
2. Ouvrir console dev
3. Tenter une génération (connecté ou non)
4. Vérifier que:
   - ✅ Log `[AI Stream Proxy] Auth cookie present: true/false`
   - ✅ Pas d'erreurs de console

---

## 📊 Impact

### Avant
- ❌ Erreur "Non authentifié" sans explication
- ❌ Bouton actif même sans authentification
- ❌ Aucun feedback proactif
- ❌ Cookies potentiellement non transmis

### Après
- ✅ Message d'avertissement proactif si non connecté
- ✅ Bouton désactivé automatiquement
- ✅ Toast avec action "Se connecter"
- ✅ Cookies correctement récupérés et transmis
- ✅ Vérification précoce côté proxy
- ✅ Logging pour faciliter le débogage

---

## 🔗 Fichiers modifiés

1. **frontend/app/api/challenges/generate-ai-stream/route.ts**
   - Amélioration récupération cookies avec `request.cookies.getAll()`
   - Vérification préalable de la présence du cookie `access_token`
   - Retour immédiat d'erreur si non authentifié
   - Logging en développement

2. **frontend/components/challenges/AIGenerator.tsx**
   - Import et utilisation du hook `useAuth`
   - Vérification d'authentification avant génération
   - Message d'avertissement visuel
   - Désactivation du bouton si non authentifié
   - Toast avec action de redirection

3. **frontend/messages/fr.json**
   - Ajout traductions `authRequired`, `authRequiredDescription`, `login`

4. **frontend/messages/en.json**
   - Ajout traductions `authRequired`, `authRequiredDescription`, `login`

---

## 🎯 Commits

**Commit 1**: `5f2c292` - "fix: normalisation des types de challenges pour affichage"  
**Commit 2**: `0eb4ce0` - "docs: documentation de la correction pour affichage types challenges"  
**Commit 3**: `680595c` - "fix: gestion authentification pour generation IA challenges - Verification cookies et message utilisateur clair"

---

## 📝 Notes importantes

### Architecture d'authentification

L'authentification Mathakine utilise des **cookies HTTP-only** pour stocker les tokens:

- `access_token` : Token d'accès (expire après 30 minutes)
- `refresh_token` : Token de rafraîchissement (expire après 30 jours)

**Configuration des cookies** (définie dans `server/views.py`):
```python
response.set_cookie(
    key="access_token",
    value=tokens["access_token"],
    httponly=True,
    secure=True,      # Requis pour samesite="none"
    samesite="none",  # Permet cross-domain (frontend ≠ backend en prod)
    max_age=access_token_max_age
)
```

### EventSource et cookies

`EventSource` (API SSE) a des limitations avec les cookies cross-origin:
1. Ne supporte pas nativement `withCredentials: true`
2. Les cookies sont envoyés automatiquement **seulement** si même domaine
3. En production (frontend Next.js ≠ backend FastAPI), nécessite `samesite="none"`

**Solution adoptée**: Proxy Next.js (`/api/challenges/generate-ai-stream`) qui:
- Reçoit la requête EventSource (même domaine → cookies inclus automatiquement)
- Récupère les cookies
- Les transmet au backend dans l'en-tête `Cookie`

### Vérifications multiples (défense en profondeur)

1. **Frontend (composant)** : Vérifie `user` avant d'appeler le proxy
2. **Proxy Next.js** : Vérifie présence `access_token` avant d'appeler backend
3. **Backend** : Vérifie et décode le token avant génération

Cette approche en couches garantit:
- ✅ Meilleure UX (feedback immédiat frontend)
- ✅ Économie de ressources (pas d'appel backend inutile)
- ✅ Sécurité (vérification finale backend)

### Cas limites

**Cas 1: Token expire pendant la génération**
- Génération démarre avec token valide
- Token expire pendant les 30-60s de génération
- **Solution actuelle**: Génération continue (token vérifié au début)
- **Amélioration future**: Rafraîchissement automatique si nécessaire

**Cas 2: Utilisateur ouvre plusieurs onglets**
- Se déconnecte dans un onglet
- Tente génération dans l'autre onglet
- **Solution actuelle**: Erreur "Non authentifié"
- **Amélioration future**: Synchronisation d'état entre onglets

---

## ✅ Résultat

Le problème "Non authentifié" lors de la génération de défis logiques avec l'IA est **résolu**. Les utilisateurs reçoivent maintenant:

1. **Feedback proactif** : Avertissement si non connectés
2. **UI adaptée** : Bouton désactivé sans authentification
3. **Guidance claire** : Action "Se connecter" dans les messages d'erreur
4. **Meilleure fiabilité** : Cookies correctement transmis au backend

**Status**: ✅ **Déployé en production**

