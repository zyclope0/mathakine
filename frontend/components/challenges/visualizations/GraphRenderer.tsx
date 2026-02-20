"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Network } from "lucide-react";
import { useState, useEffect, useRef } from "react";

interface GraphRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string | undefined;
}

/**
 * Renderer pour les défis de type GRAPH.
 * Visualisation simple de graphe avec canvas SVG.
 */
export function GraphRenderer({ visualData, className }: GraphRendererProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });

  // Parser les données de graphe
  const nodes = Array.isArray(visualData?.nodes) ? visualData.nodes : Array.isArray(visualData?.vertices) ? visualData.vertices : [];
  const edges = Array.isArray(visualData?.edges) ? visualData.edges : Array.isArray(visualData?.links) ? visualData.links : [];

  useEffect(() => {
    if (svgRef.current) {
      const rect = svgRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width || 400, height: rect.height || 300 });
    }
  }, []);

  if (!nodes || nodes.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ""}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun graphe disponible
        </CardContent>
      </Card>
    );
  }

  // Créer un mapping des noms de nœuds vers leurs indices
  const nodeMap = new Map<string, number>();
  nodes.forEach((node: Record<string, unknown>, index: number) => {
    const nodeKey = String(
      typeof node === "object" && node !== null
        ? node.label ?? node.value ?? node.id ?? index
        : node
    );
    nodeMap.set(nodeKey.toUpperCase(), index);
  });

  // Positions : explicites (visual_data.positions) ou layout circulaire par défaut
  const centerX = dimensions.width / 2;
  const centerY = dimensions.height / 2;
  const radius = Math.min(dimensions.width, dimensions.height) / 3;
  const explicitPositions = (visualData?.positions ?? visualData?.layout) as Record<string, unknown> | null | undefined;

  const nodePositions = nodes.map((node: Record<string, unknown>, index: number) => {
    if (explicitPositions && typeof explicitPositions === "object" && !Array.isArray(explicitPositions)) {
      const nodeKey = String(
        typeof node === "object" && node !== null
          ? node.label ?? node.value ?? node.id ?? index
          : node
      );
      const pos = (explicitPositions as Record<string, unknown>)[nodeKey.toUpperCase()] ?? (explicitPositions as Record<string, unknown>)[nodeKey];
      if (Array.isArray(pos) && pos.length >= 2 && typeof pos[0] === "number" && typeof pos[1] === "number") {
        const padding = 40;
        const maxCoord = 200;
        const scale = Math.min(
          (dimensions.width - 2 * padding) / maxCoord,
          (dimensions.height - 2 * padding) / maxCoord
        );
        return {
          x: padding + pos[0] * scale,
          y: padding + pos[1] * scale,
        };
      }
    }
    const angle = (2 * Math.PI * index) / nodes.length;
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  return (
    <Card className={`bg-card border-primary/20 ${className || ""}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Network className="h-5 w-5 text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Graphe</h4>
          </div>

          <div className="flex justify-center bg-muted/30 rounded-lg p-4 overflow-auto">
            <svg
              ref={svgRef}
              width={dimensions.width}
              height={dimensions.height}
              className="border border-primary/20 rounded"
            >
              {/* Dessiner les arêtes */}
              {edges.map((edge: Record<string, unknown>, index: number) => {
                let fromIndex: number | undefined;
                let toIndex: number | undefined;
                let weight: number | string | undefined;

                // Gérer différents formats d'edges
                if (typeof edge === "object" && edge !== null && "from" in edge && "to" in edge) {
                  const e = edge as Record<string, unknown>;
                  // Format {from: "A", to: "B", weight: 5} ou {from: 0, to: 1}
                  if (typeof e.from === "number") {
                    fromIndex = e.from;
                  } else {
                    fromIndex = nodeMap.get(String(e.from ?? "").toUpperCase());
                  }

                  if (typeof e.to === "number") {
                    toIndex = e.to;
                  } else {
                    toIndex = nodeMap.get(String(e.to ?? "").toUpperCase());
                  }

                  // Extraire le poids (weight, cost, time, distance, label)
                  const w = e.weight ?? e.cost ?? e.time ?? e.distance ?? e.label ?? e.value;
                  weight = w !== undefined && w !== null ? (typeof w === "number" || typeof w === "string" ? w : String(w)) : undefined;
                } else if (Array.isArray(edge)) {
                  // Format ["A", "B"] ou ["A", "B", 5] ou [0, 1, 5]
                  if (typeof edge[0] === "number") {
                    fromIndex = edge[0];
                  } else {
                    fromIndex = nodeMap.get(String(edge[0] ?? "").toUpperCase());
                  }

                  if (typeof edge[1] === "number") {
                    toIndex = edge[1];
                  } else {
                    toIndex = nodeMap.get(String(edge[1] ?? "").toUpperCase());
                  }

                  // Le poids peut être le 3ème élément
                  if (edge.length >= 3) {
                    const w2 = edge[2];
                    weight = w2 !== undefined && w2 !== null ? (typeof w2 === "number" || typeof w2 === "string" ? w2 : String(w2)) : undefined;
                  }
                }

                if (fromIndex === undefined || toIndex === undefined) {
                  if (process.env.NODE_ENV === "development") {
                    console.warn(`Edge invalide ignorée:`, edge);
                  }
                  return null;
                }

                const from = nodePositions[fromIndex];
                const to = nodePositions[toIndex];

                if (!from || !to) return null;

                // Calculer le point milieu pour le label du poids
                const midX = (from.x + to.x) / 2;
                const midY = (from.y + to.y) / 2;

                // Décaler légèrement le label perpendiculairement à la ligne pour éviter le chevauchement
                const dx = to.x - from.x;
                const dy = to.y - from.y;
                const len = Math.sqrt(dx * dx + dy * dy);
                const offsetX = len > 0 ? (-dy / len) * 12 : 0;
                const offsetY = len > 0 ? (dx / len) * 12 : 0;

                return (
                  <g key={index}>
                    <line
                      x1={from.x}
                      y1={from.y}
                      x2={to.x}
                      y2={to.y}
                      stroke="currentColor"
                      strokeWidth="2"
                      className="text-primary/50"
                    />
                    {/* Afficher le poids de l'arête */}
                    {weight !== undefined && (
                      <>
                        {/* Fond jaune/orange pour contraste optimal */}
                        <rect
                          x={midX + offsetX - 14}
                          y={midY + offsetY - 11}
                          width="28"
                          height="22"
                          rx="4"
                          fill="#fbbf24"
                          stroke="#f59e0b"
                          strokeWidth="2"
                        />
                        <text
                          x={midX + offsetX}
                          y={midY + offsetY}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          fill="#1e293b"
                          fontSize="12"
                          fontWeight="bold"
                        >
                          {String(weight ?? "")}
                        </text>
                      </>
                    )}
                  </g>
                );
              })}

              {/* Dessiner les nœuds */}
              {nodes.map((node: Record<string, unknown>, index: number) => {
                const pos = nodePositions[index];
                if (!pos) return null;

                const label = String(
                  typeof node === "object" && node !== null
                    ? node.label ?? node.value ?? node.id ?? index
                    : node
                );

                return (
                  <g key={index}>
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r="20"
                      fill="currentColor"
                      className="text-primary"
                    />
                    <text
                      x={pos.x}
                      y={pos.y}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="white"
                      fontSize="12"
                      fontWeight="bold"
                    >
                      {label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          <div className="text-xs text-center text-muted-foreground">
            {nodes.length} nœud{nodes.length > 1 ? "s" : ""} • {edges.length} arête
            {edges.length > 1 ? "s" : ""}
            {/* Indiquer si c'est un graphe pondéré */}
            {edges.some((edge: Record<string, unknown>) => {
              if (typeof edge === "object" && !Array.isArray(edge)) {
                return (
                  edge.weight !== undefined ||
                  edge.cost !== undefined ||
                  edge.time !== undefined ||
                  edge.distance !== undefined
                );
              }
              if (Array.isArray(edge) && edge.length >= 3) {
                return true;
              }
              return false;
            }) && <span className="ml-2 text-primary">• pondéré</span>}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
