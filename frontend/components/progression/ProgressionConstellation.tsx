"use client";

import { useLayoutEffect, useRef } from "react";
import { cn } from "@/lib/utils";

/** État d’un palier dans l’arc de progression persistant (≠ streak temporel). */
export type ProgressionConstellationNodeState = "completed" | "current" | "upcoming";

export interface ProgressionConstellationNode {
  id: string;
  state: ProgressionConstellationNodeState;
  label: string;
}

export interface ProgressionConstellationProps {
  nodes: ProgressionConstellationNode[];
  /** Résumé pour lecteurs d’écran (ex. « Progression : palier 2 sur 4 »). */
  ariaLabel: string;
  className?: string;
}

const GAP = 100;
const PAD_X = 48;
/** Rayon nœud SVG — lisibilité renforcée (l’arc reste décoratif ; pas d’interaction). */
const NODE_R = 12;
/** Nœud « current » : anneau extérieur = NODE_R + 3 ; garder la marge dans le viewBox. */
const NODE_OUTER_PAD = 3;
const NODE_CY = 28;
/** Hauteur viewBox serrée sur la ligne de paliers : éviter un vide SVG énorme au-dessus des libellés HTML. */
const VB_H = NODE_CY + NODE_R + NODE_OUTER_PAD + 4;

function stateAriaFragment(state: ProgressionConstellationNodeState): string {
  switch (state) {
    case "completed":
      return "completed";
    case "current":
      return "current step";
    case "upcoming":
      return "upcoming";
    default: {
      const _exhaustive: never = state;
      return _exhaustive;
    }
  }
}

/**
 * Constellation géométrique calme : arc de progression persistant (niveaux / paliers).
 * Défilement horizontal si la ligne dépasse la largeur utile — pas de réduction du GAP / des nœuds.
 * Scrollbar masquée (classe `no-scrollbar`) : swipe / molette / trackpad conservés.
 * Pas de particules ni d’animation : rien à désactiver pour `prefers-reduced-motion`.
 */
export function ProgressionConstellation({
  nodes,
  ariaLabel,
  className,
}: ProgressionConstellationProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const count = nodes.length;
  const currentIndex = nodes.findIndex((n) => n.state === "current");

  useLayoutEffect(() => {
    const el = scrollRef.current;
    if (!el || count === 0 || currentIndex < 0) {
      return;
    }
    const nodeCenterPx = PAD_X + currentIndex * GAP;
    const targetScroll = nodeCenterPx - el.clientWidth / 2;
    const maxScroll = Math.max(0, el.scrollWidth - el.clientWidth);
    el.scrollLeft = Math.max(0, Math.min(targetScroll, maxScroll));
  }, [currentIndex, count]);

  if (count === 0) {
    return null;
  }

  const vbW = PAD_X * 2 + Math.max(0, count - 1) * GAP;
  const listId = `progression-constellation-detail-${nodes.map((n) => n.id).join("-")}`;

  const xs = nodes.map((_, i) => PAD_X + i * GAP);

  return (
    <div className={cn("w-full max-w-lg min-w-0", className)}>
      <div
        ref={scrollRef}
        role="region"
        aria-label={ariaLabel}
        aria-describedby={listId}
        className={cn(
          "no-scrollbar touch-pan-x",
          "overflow-x-auto overflow-y-hidden overscroll-x-contain",
          "scroll-smooth pt-0.5 pb-2"
        )}
      >
        <div className="inline-block min-w-full text-start pb-1" style={{ width: vbW }}>
          <svg
            viewBox={`0 0 ${vbW} ${VB_H}`}
            className="block h-auto w-full max-w-none text-border"
            aria-hidden
          >
            {nodes.slice(0, -1).map((node, i) => {
              const next = nodes[i + 1];
              if (!next) {
                return null;
              }
              const x1 = xs[i];
              const x2 = xs[i + 1];
              return (
                <line
                  key={`edge-${node.id}-${next.id}`}
                  x1={x1}
                  y1={NODE_CY}
                  x2={x2}
                  y2={NODE_CY}
                  stroke="currentColor"
                  strokeWidth={2}
                  strokeLinecap="round"
                  className="text-border"
                />
              );
            })}

            {nodes.map((node, i) => {
              const cx = xs[i];
              const r = NODE_R;
              if (node.state === "completed") {
                return (
                  <circle
                    key={node.id}
                    cx={cx}
                    cy={NODE_CY}
                    r={r}
                    className="fill-success stroke-0"
                  />
                );
              }
              if (node.state === "current") {
                return (
                  <g key={node.id}>
                    <circle
                      cx={cx}
                      cy={NODE_CY}
                      r={r + 3}
                      className="fill-none stroke-primary"
                      strokeWidth={2}
                    />
                    <circle
                      cx={cx}
                      cy={NODE_CY}
                      r={r}
                      className="fill-background stroke-primary"
                      strokeWidth={2}
                    />
                  </g>
                );
              }
              return (
                <circle
                  key={node.id}
                  cx={cx}
                  cy={NODE_CY}
                  r={r}
                  stroke="currentColor"
                  strokeWidth={2}
                  className="fill-transparent text-muted-foreground"
                />
              );
            })}
          </svg>

          <div
            className="relative mt-2 min-h-[3.25rem] pb-1 sm:min-h-[2.75rem]"
            style={{ width: vbW }}
            aria-hidden
          >
            {nodes.map((node, i) => (
              <span
                key={node.id}
                className="absolute left-0 top-0 max-w-[min(6.5rem,calc(100vw-3rem))] -translate-x-1/2 text-center text-xs leading-snug text-muted-foreground break-words"
                style={{ left: PAD_X + i * GAP }}
              >
                {node.label}
              </span>
            ))}
          </div>
        </div>
      </div>

      <ul id={listId} className="sr-only">
        {nodes.map((node) => (
          <li key={node.id}>
            {node.label}: {stateAriaFragment(node.state)}
          </li>
        ))}
      </ul>
    </div>
  );
}
