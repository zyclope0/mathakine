"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Network } from "lucide-react";
import { useRef, useState, useLayoutEffect } from "react";
import { motion } from "framer-motion";
import { useAccessibleAnimation } from "@/lib/hooks/useAccessibleAnimation";

interface GraphRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
}

// Constantes de layout
const NODE_RADIUS = 20;
const PADDING = NODE_RADIUS + 8; // marge minimale pour que les nœuds ne soient pas coupés

type GraphNode = Record<string, unknown> | string | number;
type GraphEdge = Record<string, unknown> | unknown[];

function getNodeLabel(node: GraphNode, fallbackIndex: number): string {
  if (typeof node === "object" && node !== null) {
    const record = node as Record<string, unknown>;
    return String(record.label ?? record.value ?? record.id ?? fallbackIndex);
  }

  return String(node);
}

function formatGraphCount(count: number, singular: string, plural: string): string {
  return `${count} ${count > 1 ? plural : singular}`;
}

/**
 * Renderer pour les défis de type GRAPH.
 *
 * Approche : layout en coordonnées logiques (viewBox dynamique) — le SVG est
 * responsive via viewBox + preserveAspectRatio. Plus de dimensions fixes.
 * Le ResizeObserver observe le conteneur div, pas le SVG, ce qui évite le
 * cycle infini de dimensionnement.
 */
export function GraphRenderer({ visualData, className }: GraphRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(560);
  const { shouldReduceMotion } = useAccessibleAnimation();

  // Observer la largeur réelle du conteneur div (pas du SVG)
  useLayoutEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const update = () => {
      const w = el.getBoundingClientRect().width;
      if (w > 0) setContainerWidth(w);
    };

    update();

    if (typeof ResizeObserver === "undefined") return;
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Parser les données de graphe
  const nodes = Array.isArray(visualData?.nodes)
    ? (visualData!.nodes as GraphNode[])
    : Array.isArray(visualData?.vertices)
      ? (visualData!.vertices as GraphNode[])
      : [];
  const edges = Array.isArray(visualData?.edges)
    ? (visualData!.edges as GraphEdge[])
    : Array.isArray(visualData?.links)
      ? (visualData!.links as GraphEdge[])
      : [];

  if (nodes.length === 0) {
    return (
      <Card flat className={`bg-card border-border/50 ${className ?? ""}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun graphe disponible
        </CardContent>
      </Card>
    );
  }

  // Mapping label → index
  const nodeMap = new Map<string, number>();
  nodes.forEach((node, index) => {
    const key = getNodeLabel(node, index);
    nodeMap.set(key.toUpperCase(), index);
  });

  const nodeCountLabel = formatGraphCount(nodes.length, "nœud", "nœuds");
  const edgeCountLabel = formatGraphCount(edges.length, "arête", "arêtes");

  // ─── Layout en coordonnées logiques ───────────────────────────────────────
  // On travaille dans un espace logique indépendant de la taille d'affichage.
  // Le SVG s'adapte via viewBox.

  const logicalW = Math.max(containerWidth, 300);
  const logicalH = Math.round(logicalW * 0.6); // ratio 5:3

  const centerX = logicalW / 2;
  const centerY = logicalH / 2;
  // Rayon suffisant pour que les nœuds ne débordent pas
  const radius = Math.min(centerX, centerY) - PADDING;

  const explicitPositions = (visualData?.positions ?? visualData?.layout) as
    | Record<string, unknown>
    | null
    | undefined;

  const nodePositions = nodes.map((node, index) => {
    const key = getNodeLabel(node, index);

    if (
      explicitPositions &&
      typeof explicitPositions === "object" &&
      !Array.isArray(explicitPositions)
    ) {
      const pos =
        (explicitPositions as Record<string, unknown>)[key.toUpperCase()] ??
        (explicitPositions as Record<string, unknown>)[key];

      if (
        Array.isArray(pos) &&
        pos.length >= 2 &&
        typeof pos[0] === "number" &&
        typeof pos[1] === "number"
      ) {
        // Normaliser les positions explicites dans l'espace logique
        const rawMaxCoord = 200;
        const availW = logicalW - 2 * PADDING;
        const availH = logicalH - 2 * PADDING;
        const scale = Math.min(availW / rawMaxCoord, availH / rawMaxCoord);
        return {
          x: PADDING + (pos[0] as number) * scale,
          y: PADDING + (pos[1] as number) * scale,
        };
      }
    }

    // Layout circulaire — commence à -π/2 pour avoir le premier nœud en haut
    const angle = -Math.PI / 2 + (2 * Math.PI * index) / nodes.length;
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  // ─── Résoudre une arête en indices from/to + poids ────────────────────────
  function resolveEdge(edge: GraphEdge): {
    fromIndex: number | undefined;
    toIndex: number | undefined;
    weight: string | number | undefined;
  } {
    let fromIndex: number | undefined;
    let toIndex: number | undefined;
    let weight: string | number | undefined;

    if (
      !Array.isArray(edge) &&
      typeof edge === "object" &&
      edge !== null &&
      "from" in edge &&
      "to" in edge
    ) {
      const e = edge as Record<string, unknown>;
      fromIndex =
        typeof e.from === "number" ? e.from : nodeMap.get(String(e.from ?? "").toUpperCase());
      toIndex = typeof e.to === "number" ? e.to : nodeMap.get(String(e.to ?? "").toUpperCase());
      const w = e.weight ?? e.cost ?? e.time ?? e.distance ?? e.label ?? e.value;
      weight =
        w != null && (typeof w === "number" || typeof w === "string")
          ? w
          : w != null
            ? String(w)
            : undefined;
    } else if (Array.isArray(edge)) {
      fromIndex =
        typeof edge[0] === "number" ? edge[0] : nodeMap.get(String(edge[0] ?? "").toUpperCase());
      toIndex =
        typeof edge[1] === "number" ? edge[1] : nodeMap.get(String(edge[1] ?? "").toUpperCase());
      if (edge.length >= 3 && edge[2] != null) {
        const w2 = edge[2];
        weight = typeof w2 === "number" || typeof w2 === "string" ? w2 : String(w2);
      }
    }

    return { fromIndex, toIndex, weight };
  }

  const isWeighted = edges.some((edge) => {
    const { weight } = resolveEdge(edge);
    return weight !== undefined;
  });

  return (
    <Card flat className={`bg-card border-border/50 ${className ?? ""}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Network className="h-5 w-5 text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Graphe</h4>
          </div>

          {/* Conteneur observé — pas de overflow-auto, le SVG s'adapte */}
          <div ref={containerRef} className="w-full bg-muted/30 rounded-lg p-2">
            <svg
              viewBox={`0 0 ${logicalW} ${logicalH}`}
              preserveAspectRatio="xMidYMid meet"
              width="100%"
              aria-label={`Graphe avec ${nodeCountLabel} et ${edgeCountLabel}`}
              role="img"
              className="border border-border/50 rounded"
              style={{ display: "block", maxHeight: "420px" }}
            >
              {/* Arêtes */}
              {edges.map((edge, index) => {
                const { fromIndex, toIndex, weight } = resolveEdge(edge);

                if (fromIndex === undefined || toIndex === undefined) return null;

                const from = nodePositions[fromIndex];
                const to = nodePositions[toIndex];
                if (!from || !to) return null;

                const midX = (from.x + to.x) / 2;
                const midY = (from.y + to.y) / 2;

                // Offset perpendiculaire pour le label de poids
                const dx = to.x - from.x;
                const dy = to.y - from.y;
                const len = Math.sqrt(dx * dx + dy * dy);
                const offsetX = len > 0 ? (-dy / len) * 14 : 0;
                const offsetY = len > 0 ? (dx / len) * 14 : 0;
                const edgeKey = `${fromIndex}-${toIndex}-${String(weight ?? "edge")}-${index}`;

                return (
                  <motion.g
                    key={edgeKey}
                    initial={shouldReduceMotion ? false : { opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <line
                      x1={from.x}
                      y1={from.y}
                      x2={to.x}
                      y2={to.y}
                      stroke="var(--color-primary)"
                      strokeOpacity={0.5}
                      strokeWidth="2"
                    />
                    {weight !== undefined && (
                      <>
                        <rect
                          x={midX + offsetX - 14}
                          y={midY + offsetY - 11}
                          width="28"
                          height="22"
                          rx="4"
                          fill="var(--color-card)"
                          stroke="var(--color-primary)"
                          strokeOpacity={0.6}
                          strokeWidth="1.5"
                        />
                        <text
                          x={midX + offsetX}
                          y={midY + offsetY}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="var(--color-foreground)"
                          fontSize="11"
                          fontWeight="bold"
                        >
                          {String(weight)}
                        </text>
                      </>
                    )}
                  </motion.g>
                );
              })}

              {/* Nœuds */}
              {nodes.map((node, index) => {
                const pos = nodePositions[index];
                if (!pos) return null;

                const label = getNodeLabel(node, index);

                return (
                  <motion.g
                    key={`${label}-${index}`}
                    initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.06, duration: 0.3, ease: "easeOut" }}
                    style={{ transformOrigin: `${pos.x}px ${pos.y}px` }}
                  >
                    <circle cx={pos.x} cy={pos.y} r={NODE_RADIUS} fill="var(--color-primary)" />
                    <text
                      x={pos.x}
                      y={pos.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="var(--color-primary-foreground)"
                      fontSize="12"
                      fontWeight="bold"
                    >
                      {label}
                    </text>
                  </motion.g>
                );
              })}
            </svg>
          </div>

          <div className="text-xs text-center text-muted-foreground">
            <span>{nodeCountLabel}</span>
            <span aria-hidden="true" className="mx-2">
              •
            </span>
            <span>{edgeCountLabel}</span>
            {isWeighted && (
              <>
                <span aria-hidden="true" className="mx-2">
                  •
                </span>
                <span className="text-primary">pondéré</span>
              </>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
