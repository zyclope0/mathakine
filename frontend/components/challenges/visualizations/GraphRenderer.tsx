'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Network } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';

interface GraphRendererProps {
  visualData: any;
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
  const nodes = visualData?.nodes || visualData?.vertices || [];
  const edges = visualData?.edges || visualData?.links || [];

  useEffect(() => {
    if (svgRef.current) {
      const rect = svgRef.current.getBoundingClientRect();
      setDimensions({ width: rect.width || 400, height: rect.height || 300 });
    }
  }, []);

  if (!nodes || nodes.length === 0) {
    return (
      <Card className={`bg-card border-primary/20 ${className || ''}`}>
        <CardContent className="p-4 text-center text-muted-foreground">
          Aucun graphe disponible
        </CardContent>
      </Card>
    );
  }

  // Créer un mapping des noms de nœuds vers leurs indices
  const nodeMap = new Map<string, number>();
  nodes.forEach((node: any, index: number) => {
    const nodeKey = typeof node === 'object' ? (node.label || node.value || node.id || String(index)) : String(node);
    nodeMap.set(nodeKey.toUpperCase(), index);
  });

  // Calculer les positions des nœuds (layout simple en cercle)
  const centerX = dimensions.width / 2;
  const centerY = dimensions.height / 2;
  const radius = Math.min(dimensions.width, dimensions.height) / 3;
  
  const nodePositions = nodes.map((_: any, index: number) => {
    const angle = (2 * Math.PI * index) / nodes.length;
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
  });

  return (
    <Card className={`bg-card border-primary/20 ${className || ''}`}>
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
              {edges.map((edge: any, index: number) => {
                let fromIndex: number | undefined;
                let toIndex: number | undefined;
                
                // Gérer différents formats d'edges
                if (typeof edge === 'object' && 'from' in edge && 'to' in edge) {
                  // Format {from: "A", to: "B"} ou {from: 0, to: 1}
                  if (typeof edge.from === 'number') {
                    fromIndex = edge.from;
                  } else {
                    fromIndex = nodeMap.get(String(edge.from).toUpperCase());
                  }
                  
                  if (typeof edge.to === 'number') {
                    toIndex = edge.to;
                  } else {
                    toIndex = nodeMap.get(String(edge.to).toUpperCase());
                  }
                } else if (Array.isArray(edge) && edge.length >= 2) {
                  // Format ["A", "B"] ou [0, 1]
                  if (typeof edge[0] === 'number') {
                    fromIndex = edge[0];
                  } else {
                    fromIndex = nodeMap.get(String(edge[0]).toUpperCase());
                  }
                  
                  if (typeof edge[1] === 'number') {
                    toIndex = edge[1];
                  } else {
                    toIndex = nodeMap.get(String(edge[1]).toUpperCase());
                  }
                }
                
                if (fromIndex === undefined || toIndex === undefined) {
                  console.warn(`Edge invalide ignorée:`, edge);
                  return null;
                }
                
                const from = nodePositions[fromIndex];
                const to = nodePositions[toIndex];
                
                if (!from || !to) return null;
                
                return (
                  <line
                    key={index}
                    x1={from.x}
                    y1={from.y}
                    x2={to.x}
                    y2={to.y}
                    stroke="currentColor"
                    strokeWidth="2"
                    className="text-primary/50"
                  />
                );
              })}
              
              {/* Dessiner les nœuds */}
              {nodes.map((node: any, index: number) => {
                const pos = nodePositions[index];
                if (!pos) return null;
                
                const label = typeof node === 'object' ? node.label || node.value || node.id || index : String(node);
                
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
            {nodes.length} nœud{nodes.length > 1 ? 's' : ''} • {edges.length} arête{edges.length > 1 ? 's' : ''}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

