"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTranslations } from "next-intl";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  itemsPerPage?: number;
  totalItems?: number;
  showInfo?: boolean;
  className?: string;
}

export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  itemsPerPage = 15,
  totalItems,
  showInfo = true,
  className,
}: PaginationProps) {
  const t = useTranslations("exercises.list.pagination");
  // Calculer les pages à afficher
  const getPageNumbers = () => {
    const pages: (number | "ellipsis")[] = [];
    const maxVisible = 7; // Nombre maximum de pages visibles

    if (totalPages <= maxVisible) {
      // Afficher toutes les pages si moins de maxVisible
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Logique pour afficher les pages avec ellipses
      if (currentPage <= 3) {
        // Début : afficher les premières pages
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push("ellipsis");
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        // Fin : afficher les dernières pages
        pages.push(1);
        pages.push("ellipsis");
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        // Milieu : afficher autour de la page courante
        pages.push(1);
        pages.push("ellipsis");
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push("ellipsis");
        pages.push(totalPages);
      }
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();
  const startItem = totalItems ? (currentPage - 1) * itemsPerPage + 1 : undefined;
  const endItem = totalItems ? Math.min(currentPage * itemsPerPage, totalItems) : undefined;

  if (totalPages <= 1) {
    return null; // Ne pas afficher la pagination s'il n'y a qu'une page
  }

  return (
    <div className={cn("flex flex-col sm:flex-row items-center justify-between gap-4", className)}>
      {showInfo && totalItems && (
        <div className="text-sm text-muted-foreground">
          {startItem && endItem && (
            <>{t("showing", { start: startItem, end: endItem, total: totalItems })}</>
          )}
        </div>
      )}
      <nav aria-label="Pagination" className="flex items-center gap-1">
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          aria-label={t("previous")}
        >
          <ChevronLeft className="h-4 w-4" aria-hidden="true" />
          <span className="sr-only">{t("previous")}</span>
        </Button>

        {pageNumbers.map((page, index) => {
          if (page === "ellipsis") {
            return (
              <div
                key={`ellipsis-${index}`}
                className="flex h-9 w-9 items-center justify-center"
                aria-hidden="true"
              >
                <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
              </div>
            );
          }

          return (
            <Button
              key={page}
              variant={currentPage === page ? "default" : "outline"}
              size="sm"
              onClick={() => onPageChange(page)}
              aria-label={t("page", { page })}
              aria-current={currentPage === page ? "page" : undefined}
              className={cn(
                "min-w-9",
                currentPage === page && "bg-primary text-primary-foreground"
              )}
            >
              {page}
            </Button>
          );
        })}

        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          aria-label={t("next")}
        >
          <span className="sr-only">{t("next")}</span>
          <ChevronRight className="h-4 w-4" aria-hidden="true" />
        </Button>
      </nav>
    </div>
  );
}
