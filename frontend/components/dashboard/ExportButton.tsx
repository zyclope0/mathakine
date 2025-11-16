'use client';

import { Button } from '@/components/ui/button';
import { FileText, FileSpreadsheet } from 'lucide-react';
import { exportStatsToPDF } from '@/lib/utils/exportPDF';
import { exportStatsToExcel } from '@/lib/utils/exportExcel';
import { useUserStats } from '@/hooks/useUserStats';
import { toast } from 'sonner';
import { useTranslations } from 'next-intl';

interface ExportButtonProps {
  timeRange?: '7' | '30' | '90' | 'all';
}

export function ExportButton({ timeRange = '30' }: ExportButtonProps) {
  const { stats } = useUserStats(timeRange);
  const t = useTranslations('dashboard.export');
  
  const handleExportPDF = async () => {
    if (!stats) {
      toast.error(t('noData', { default: 'Aucune donnée disponible' }), {
        description: t('noDataDescription', { default: 'Veuillez attendre le chargement des statistiques.' }),
      });
      return;
    }
    
    try {
      await exportStatsToPDF(stats);
      toast.success(t('pdfSuccess', { default: 'Export PDF réussi !' }), {
        description: t('pdfSuccessDescription', { default: 'Votre rapport a été téléchargé.' }),
      });
    } catch (error) {
      // En production, les erreurs sont gérées par le toast
      // Ne pas logger en console pour éviter les fuites d'information
      toast.error(t('pdfError', { default: "Erreur lors de l'export PDF" }), {
        description: t('pdfErrorDescription', { default: 'Une erreur est survenue lors de la génération du PDF.' }),
      });
    }
  };
  
  const handleExportExcel = async () => {
    if (!stats) {
      toast.error(t('noData', { default: 'Aucune donnée disponible' }), {
        description: t('noDataDescription', { default: 'Veuillez attendre le chargement des statistiques.' }),
      });
      return;
    }
    
    try {
      exportStatsToExcel(stats);
      toast.success(t('excelSuccess', { default: 'Export Excel réussi !' }), {
        description: t('excelSuccessDescription', { default: 'Votre fichier Excel a été téléchargé.' }),
      });
    } catch (error) {
      // En production, les erreurs sont gérées par le toast
      // Ne pas logger en console pour éviter les fuites d'information
      toast.error(t('excelError', { default: "Erreur lors de l'export Excel" }), {
        description: t('excelErrorDescription', { default: 'Une erreur est survenue lors de la génération du fichier Excel.' }),
      });
    }
  };
  
  return (
    <div className="flex gap-2">
      <Button 
        onClick={handleExportPDF} 
        variant="outline"
        disabled={!stats}
        className="flex items-center gap-2"
        aria-label={t('pdfLabel', { default: 'Exporter en PDF' })}
      >
        <FileText className="h-4 w-4" aria-hidden="true" />
        {t('pdf', { default: 'Exporter PDF' })}
      </Button>
      <Button 
        onClick={handleExportExcel} 
        variant="outline"
        disabled={!stats}
        className="flex items-center gap-2"
        aria-label={t('excelLabel', { default: 'Exporter en Excel' })}
      >
        <FileSpreadsheet className="h-4 w-4" aria-hidden="true" />
        {t('excel', { default: 'Exporter Excel' })}
      </Button>
    </div>
  );
}

