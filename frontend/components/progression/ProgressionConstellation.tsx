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

function labelGridColsClass(count: number): string {
  switch (count) {
    case 1:
      return "grid-cols-1";
    case 2:
      return "grid-cols-2";
    case 3:
      return "grid-cols-3";
    case 4:
      return "grid-cols-4";
    default:
      return "grid-cols-4";
  }
}

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
 * Pas de particules ni d’animation : rien à désactiver pour `prefers-reduced-motion`.
 */
export function ProgressionConstellation({
  nodes,
  ariaLabel,
  className,
}: ProgressionConstellationProps) {
  if (nodes.length === 0) {
    return null;
  }

  const count = nodes.length;
  const vbW = PAD_X * 2 + Math.max(0, count - 1) * GAP;
  const listId = `progression-constellation-detail-${nodes.map((n) => n.id).join("-")}`;

  const xs = nodes.map((_, i) => PAD_X + i * GAP);

  return (
    <div
      role="img"
      aria-label={ariaLabel}
      aria-describedby={listId}
      className={cn("w-full max-w-lg", className)}
    >
      <svg viewBox={`0 0 ${vbW} ${VB_H}`} className="w-full h-auto text-border" aria-hidden>
        {/* Segments — trait discret, pas de couleur « arcade » */}
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
              <circle key={node.id} cx={cx} cy={NODE_CY} r={r} className="fill-success stroke-0" />
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

      <ul id={listId} className="sr-only">
        {nodes.map((node) => (
          <li key={node.id}>
            {node.label}: {stateAriaFragment(node.state)}
          </li>
        ))}
      </ul>

      <div
        className={cn(
          "grid mt-2 gap-x-1 gap-y-1 text-center sm:gap-x-2",
          "text-xs text-muted-foreground",
          labelGridColsClass(count)
        )}
        aria-hidden
      >
        {nodes.map((node) => (
          <span
            key={node.id}
            className="flex min-h-[2.75rem] min-w-0 items-center justify-center px-0.5 text-center leading-snug break-words sm:min-h-0"
          >
            {node.label}
          </span>
        ))}
      </div>
    </div>
  );
}
