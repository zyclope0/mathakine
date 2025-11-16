'use client';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CalendarDays } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { type TimeRange } from '@/hooks/useUserStats';

interface TimeRangeSelectorProps {
  value: TimeRange;
  onValueChange: (value: TimeRange) => void;
  className?: string;
}

export function TimeRangeSelector({ value, onValueChange, className }: TimeRangeSelectorProps) {
  const t = useTranslations('dashboard.timeRange');
  
  return (
    <div className={className}>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="w-[180px] flex items-center gap-2">
          <CalendarDays className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <SelectValue placeholder={t('30days')} />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="7">
            {t('7days', { default: '7 derniers jours' })}
          </SelectItem>
          <SelectItem value="30">
            {t('30days', { default: '30 derniers jours' })}
          </SelectItem>
          <SelectItem value="90">
            {t('90days', { default: '3 derniers mois' })}
          </SelectItem>
          <SelectItem value="all">
            {t('all', { default: 'Tout' })}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}

