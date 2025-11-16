# 📄 Template Page Liste

**Usage** : Copier ce template pour créer une nouvelle page de liste

---

## 📋 **Structure**

```tsx
'use client';

import { useState } from 'react';
import { PageLayout } from '@/components/layout/PageLayout';
import { PageHeader } from '@/components/layout/PageHeader';
import { PageSection } from '@/components/layout/PageSection';
import { PageGrid } from '@/components/layout/PageGrid';
import { EmptyState } from '@/components/layout/EmptyState';
import { LoadingState } from '@/components/layout/LoadingState';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Filter, X } from 'lucide-react';
import { useTranslations } from 'next-intl';
// Importez votre hook de données
// import { useMyData } from '@/hooks/useMyData';
// Importez votre composant Card
// import { MyCard } from '@/components/my/MyCard';

export default function MyListPage() {
  const t = useTranslations('myPage');
  
  // État des filtres
  const [filter1, setFilter1] = useState<string>('all');
  const [filter2, setFilter2] = useState<string>('all');
  
  // Construire les filtres pour l'API
  const filters = {
    limit: 20,
    // Ajoutez vos filtres ici
    // ...(filter1 !== 'all' && { filter1 }),
    // ...(filter2 !== 'all' && { filter2 }),
  };

  // Récupérer les données
  // const { data, isLoading } = useMyData(filters);

  // Pour le template, on simule
  const data: any[] = [];
  const isLoading = false;

  const hasActiveFilters = filter1 !== 'all' || filter2 !== 'all';

  const clearFilters = () => {
    setFilter1('all');
    setFilter2('all');
  };

  return (
    <ProtectedRoute>
      <PageLayout>
        {/* En-tête */}
        <PageHeader
          title={t('title')}
          description={t('pageDescription')}
          // icon={MyIcon} // Optionnel
          actions={
            // Actions optionnelles (boutons dans l'en-tête)
            // <Button variant="outline">Action</Button>
          }
        />

        {/* Filtres */}
        <PageSection>
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-5 w-5" />
            <h2 className="text-xl font-semibold">{t('filters.title')}</h2>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="ml-auto"
              >
                <X className="h-4 w-4 mr-1" />
                {t('filters.reset')}
              </Button>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {/* Filtre 1 */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('filters.filter1')}</label>
              <Select value={filter1} onValueChange={setFilter1}>
                <SelectTrigger>
                  <SelectValue placeholder={t('filters.all')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.all')}</SelectItem>
                  {/* Ajoutez vos options ici */}
                </SelectContent>
              </Select>
            </div>

            {/* Filtre 2 */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('filters.filter2')}</label>
              <Select value={filter2} onValueChange={setFilter2}>
                <SelectTrigger>
                  <SelectValue placeholder={t('filters.all')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('filters.all')}</SelectItem>
                  {/* Ajoutez vos options ici */}
                </SelectContent>
              </Select>
            </div>
          </div>
        </PageSection>

        {/* Liste */}
        <PageSection>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              {isLoading 
                ? t('list.loading')
                : data.length === 1
                  ? t('list.count', { count: data.length })
                  : t('list.countPlural', { count: data.length })
              }
            </h2>
          </div>

          {isLoading ? (
            <LoadingState message={t('list.loading')} />
          ) : data.length === 0 ? (
            <EmptyState
              title={t('list.empty')}
              description={t('list.emptyHint')}
              // icon={MyIcon} // Optionnel
              // action={<Button>Action</Button>} // Optionnel
            />
          ) : (
            <PageGrid columns={{ mobile: 1, tablet: 2, desktop: 3 }} gap="md">
              {data.map((item) => (
                <MyCard key={item.id} item={item} />
              ))}
            </PageGrid>
          )}
        </PageSection>
      </PageLayout>
    </ProtectedRoute>
  );
}
```

---

## 🔧 **Étapes de Personnalisation**

1. **Remplacer les imports** :
   - `useMyData` → Votre hook
   - `MyCard` → Votre composant Card
   - `MyIcon` → Votre icône

2. **Ajouter les filtres** :
   - Ajoutez les états de filtres
   - Construisez l'objet `filters`
   - Ajoutez les `Select` dans la section filtres

3. **Ajouter les traductions** :
   - Créez les clés dans `messages/fr.json` et `messages/en.json`

4. **Personnaliser** :
   - Ajustez les colonnes de la grille
   - Ajoutez des actions dans l'en-tête
   - Personnalisez l'état vide

---

## ✅ **Checklist**

- [ ] Imports personnalisés ajoutés
- [ ] Hook de données intégré
- [ ] Composant Card créé
- [ ] Filtres configurés
- [ ] Traductions ajoutées
- [ ] Testé sur mobile, tablet, desktop
- [ ] Accessibilité vérifiée

---

**Temps estimé** : ~15 minutes

