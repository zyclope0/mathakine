'use client';

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useTranslations } from 'next-intl';

interface ProgressChartProps {
  data: {
    labels: string[];
    datasets: Array<{
      label: string;
      data: number[];
    }>;
  };
}

export function ProgressChart({ data }: ProgressChartProps) {
  const t = useTranslations('dashboard.charts.progressByType');
  
  // Memoization de la transformation des données pour éviter les recalculs
  const chartData = useMemo(() => {
    return data.labels.map((label, index) => ({
      name: label,
      [data.datasets[0]?.label || 'Exercices résolus']: data.datasets[0]?.data[index] || 0,
    }));
  }, [data.labels, data.datasets]);

  // Memoization de la description textuelle pour l'accessibilité
  const chartDescription = useMemo(() => {
    return data.labels.map((label, index) => 
      `${label}: ${data.datasets[0]?.data[index] || 0} ${data.datasets[0]?.label || 'exercices'}`
    ).join(', ');
  }, [data.labels, data.datasets]);

  return (
    <Card className="bg-card border-primary/20">
      <CardHeader>
        <CardTitle className="text-xl text-foreground">
          {t('title', { default: "Progression par type d'exercice" })}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div 
          className="h-[300px] w-full"
          role="img"
          aria-label={t('ariaLabel', { default: "Graphique de progression montrant le nombre d'exercices résolus par type" })}
          aria-describedby="progress-chart-description"
        >
          <div id="progress-chart-description" className="sr-only">
            {chartDescription}
          </div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
              <XAxis
                dataKey="name"
                stroke="#a0a0a0"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#a0a0a0"
                style={{ fontSize: '12px' }}
                allowDecimals={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(18, 18, 26, 0.95)',
                  border: '1px solid rgba(124, 58, 237, 0.3)',
                  borderRadius: '8px',
                  color: '#ffffff',
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={data.datasets[0]?.label || 'Exercices résolus'}
                stroke="#7c3aed"
                strokeWidth={2}
                fill="rgba(124, 58, 237, 0.2)"
                dot={{ fill: '#7c3aed', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

