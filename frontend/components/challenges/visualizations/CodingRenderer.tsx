"use client";

import { useEffect, useState } from "react";
import {
  Code,
  Terminal,
  FileCode,
  CheckCircle2,
  XCircle,
  Lock,
  Key,
  Binary,
  Hash,
  ArrowRight,
  Lightbulb,
} from "lucide-react";
import { motion } from "framer-motion";

interface CodingRendererProps {
  visualData: Record<string, unknown> | null;
  className?: string;
}

/**
 * Renderer pour les défis de codage/cryptographie.
 * Gère : code César, substitution, binaire, symboles, algorithmes.
 */
export function CodingRenderer({ visualData, className = "" }: CodingRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Détecter le type de défi de codage
  const codingType = String(visualData.type ?? "").toLowerCase();
  const isCryptography = ["caesar", "substitution", "binary", "symbols", "algorithm"].includes(
    codingType
  );

  // Détecter le format "maze" (labyrinthe avec robot)
  const maze = visualData.maze || visualData.grid || visualData.labyrinth || null;
  const start = visualData.start || visualData.start_position || null;
  const end = visualData.end || visualData.end_position || visualData.goal || null;
  const isMaze = maze && Array.isArray(maze) && maze.length > 0;

  // Données de cryptographie
  const encodedMessage: string = String(visualData.encoded_message ?? visualData.message ?? "");
  const shift: number | undefined =
    typeof visualData.shift === "number"
      ? visualData.shift
      : visualData.shift != null
        ? Number(visualData.shift)
        : undefined;
  const alphabet: string = String(visualData.alphabet ?? "ABCDEFGHIJKLMNOPQRSTUVWXYZ");
  const cryptoKey = (visualData.key ?? visualData.partial_key ?? {}) as Record<string, unknown>;
  const steps = Array.isArray(visualData.steps) ? visualData.steps : [];
  const cryptoInput = visualData.input;
  const description: string = String(visualData.description ?? "");
  const hint: string = String(visualData.hint ?? "");

  // Extraire les données structurées (legacy/programmation)
  const code: string = String(visualData.code ?? visualData.snippet ?? "");
  const language: string = String(visualData.language ?? visualData.lang ?? "python");
  const examples = Array.isArray(visualData.examples) ? visualData.examples : (Array.isArray(visualData.test_cases) ? visualData.test_cases : []);
  const input: string = String(visualData.input ?? "");
  const output: string = String(visualData.output ?? "");
  const expectedOutput: string = String(visualData.expected_output ?? visualData.expected ?? "");
  const constraints = Array.isArray(visualData.constraints) ? visualData.constraints : [];
  const hints = Array.isArray(visualData.hints) ? visualData.hints : [];
  const question: string = String(visualData.question ?? "");

  // ==================== RENDU CRYPTOGRAPHIE ====================
  if (isCryptography) {
    return (
      <div className={`space-y-4 ${className}`}>
        {/* Description */}
        {description && (
          <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Lock className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Mission secrète</span>
            </div>
            <p className="text-foreground">{description}</p>
          </div>
        )}

        {/* Message encodé */}
        {encodedMessage && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Hash className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Message codé</span>
            </div>
            <motion.div
              className="bg-slate-900 border-2 border-primary/50 rounded-lg p-4 font-mono text-center"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <span className="text-2xl md:text-3xl tracking-widest text-amber-400 font-bold">
                {encodedMessage}
              </span>
            </motion.div>
          </div>
        )}

        {/* Code César - Afficher le décalage OU la clé partielle */}
        {codingType === "caesar" && shift !== undefined && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Key className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Clé César</span>
            </div>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <div className="bg-primary/20 border border-primary/40 rounded-lg px-4 py-2">
                <span className="text-sm text-muted-foreground">Décalage :</span>
                <span className="ml-2 text-2xl font-bold text-primary">{shift}</span>
              </div>
              <div className="text-muted-foreground text-sm">
                A → {alphabet[shift % 26]}, B → {alphabet[(1 + shift) % 26]}, C →{" "}
                {alphabet[(2 + shift) % 26]}...
              </div>
            </div>
          </div>
        )}

        {/* Code César avec partial_key : exemples pour déduire le décalage */}
        {codingType === "caesar" &&
          shift === undefined &&
          Object.keys(cryptoKey).length > 0 && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <Key className="h-5 w-5 text-primary" />
                <span className="font-semibold text-foreground">Exemples codés → clair</span>
              </div>
              <p className="text-xs text-muted-foreground italic mb-3">
                Ces exemples te permettent de déduire le décalage César.
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {Object.entries(cryptoKey).map(([encoded, decoded], index) => (
                  <motion.div
                    key={encoded}
                    className="bg-slate-800 border border-primary/30 rounded-lg px-3 py-2 flex items-center gap-2"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <span className="text-amber-400 font-mono font-bold">{encoded}</span>
                    <ArrowRight className="h-3 w-3 text-muted-foreground" />
                    <span className="text-green-400 font-mono font-bold">{String(decoded)}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

        {/* Substitution - Table de correspondance */}
        {codingType === "substitution" && Object.keys(cryptoKey).length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Key className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Table de correspondance</span>
            </div>
            {Boolean(visualData.rule_type || visualData.deducible_rule) && (
              <p className="text-xs text-muted-foreground italic mb-3">
                Ces exemples te permettent de déduire la règle de codage.
              </p>
            )}
            <div className="flex flex-wrap justify-center gap-2">
              {Object.entries(cryptoKey).map(([encoded, decoded], index) => (
                <motion.div
                  key={encoded}
                  className="bg-slate-800 border border-primary/30 rounded-lg px-3 py-2 flex items-center gap-2"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <span className="text-amber-400 font-mono font-bold">{encoded}</span>
                  <ArrowRight className="h-3 w-3 text-muted-foreground" />
                  <span className="text-green-400 font-mono font-bold">{String(decoded)}</span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Binaire - Affichage stylisé */}
        {codingType === "binary" && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Binary className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Code binaire</span>
            </div>
            <div className="flex flex-wrap justify-center gap-3">
              {encodedMessage.split(" ").map((byte: string, index: number) => (
                <motion.div
                  key={index}
                  className="bg-slate-900 border border-green-500/50 rounded px-3 py-2 font-mono"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span className="text-green-400 text-lg tracking-wider">{byte}</span>
                </motion.div>
              ))}
            </div>
            <p className="text-xs text-center text-muted-foreground mt-3">
              Chaque groupe = 1 caractère ASCII
            </p>
          </div>
        )}

        {/* Symboles - Légende */}
        {codingType === "symbols" && Object.keys(cryptoKey).length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Key className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Légende des symboles</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(cryptoKey).map(([symbol, letter], index) => (
                <motion.div
                  key={symbol}
                  className="bg-slate-800 border border-primary/30 rounded-lg p-3 flex items-center justify-center gap-3"
                  initial={{ opacity: 0, rotateY: 90 }}
                  animate={{ opacity: 1, rotateY: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span className="text-2xl">{symbol}</span>
                  <span className="text-muted-foreground">=</span>
                  <span className="text-xl font-bold text-primary">{String(letter)}</span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Algorithme - Étapes */}
        {codingType === "algorithm" && steps.length > 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Terminal className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Algorithme à suivre</span>
              {cryptoInput !== undefined && (
                <span className="ml-auto bg-primary/20 text-primary px-3 py-1 rounded-full text-sm font-bold">
                  Départ : {String(cryptoInput ?? "")}
                </span>
              )}
            </div>
            <div className="space-y-2">
              {steps.map((step: string, index: number) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3 bg-background/50 border border-border rounded-md p-3"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span className="flex-shrink-0 w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold">
                    {index + 1}
                  </span>
                  <span className="text-foreground">{step}</span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Indice */}
        {hint && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              <span className="text-sm text-amber-200">{hint}</span>
            </div>
          </div>
        )}
      </div>
    );
  }

  // ==================== RENDU LABYRINTHE (maze/robot) ====================
  if (isMaze) {
    const startObj = start != null && typeof start === "object" && !Array.isArray(start) ? (start as { row?: number; col?: number }) : null;
    const endObj = end != null && typeof end === "object" && !Array.isArray(end) ? (end as { row?: number; col?: number }) : null;
    const startRow = Array.isArray(start) ? Number(start[0]) : (startObj?.row ?? 1);
    const startCol = Array.isArray(start) ? Number(start[1]) : (startObj?.col ?? 1);
    const endRow = Array.isArray(end) ? Number(end[0]) : (endObj?.row ?? 0);
    const endCol = Array.isArray(end) ? Number(end[1]) : (endObj?.col ?? 0);

    return (
      <div className={`space-y-4 ${className}`}>
        {/* Description */}
        {description && (
          <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Terminal className="h-5 w-5 text-primary" />
              <span className="font-semibold text-foreground">Mission</span>
            </div>
            <p className="text-foreground text-sm">{description}</p>
          </div>
        )}

        {/* Labyrinthe visuel */}
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Code className="h-5 w-5 text-primary" />
            <span className="font-semibold text-foreground">Labyrinthe</span>
            <div className="ml-auto flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1">
                <span className="w-4 h-4 bg-green-500 rounded-sm flex items-center justify-center text-white text-[10px] font-bold">
                  S
                </span>
                <span className="text-muted-foreground">Départ</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-4 h-4 bg-red-500 rounded-sm flex items-center justify-center text-white text-[10px] font-bold">
                  F
                </span>
                <span className="text-muted-foreground">Arrivée</span>
              </span>
            </div>
          </div>

          <div className="flex justify-center">
            <div className="inline-block bg-slate-900 p-3 rounded-lg border border-primary/30">
              {maze.map((row: string | string[], rowIndex: number) => {
                // Gérer les formats: string[] ou string
                const cells = Array.isArray(row) ? row : row.split("");

                return (
                  <div key={rowIndex} className="flex">
                    {cells.map((cell: string, colIndex: number) => {
                      const isStart = rowIndex === startRow && colIndex === startCol;
                      const isEnd = rowIndex === endRow && colIndex === endCol;
                      const isWall = cell === "#" || cell === "█" || cell === "1";
                      const isPath = cell === " " || cell === "." || cell === "0";

                      return (
                        <motion.div
                          key={`${rowIndex}-${colIndex}`}
                          className={`
                            w-7 h-7 flex items-center justify-center text-xs font-bold
                            ${isStart ? "bg-green-500 text-white" : ""}
                            ${isEnd ? "bg-red-500 text-white" : ""}
                            ${!isStart && !isEnd && isWall ? "bg-slate-700" : ""}
                            ${!isStart && !isEnd && isPath ? "bg-slate-800/50" : ""}
                          `}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: (rowIndex * cells.length + colIndex) * 0.01 }}
                        >
                          {isStart && "S"}
                          {isEnd && "F"}
                          {!isStart && !isEnd && isWall && ""}
                        </motion.div>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Coordonnées */}
          <div className="mt-3 flex justify-center gap-6 text-xs text-muted-foreground">
            <span>
              Départ : ({startRow}, {startCol})
            </span>
            <span>
              Arrivée : ({endRow}, {endCol})
            </span>
          </div>
        </div>

        {/* Instructions possibles */}
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="h-5 w-5 text-amber-500" />
            <span className="font-semibold text-foreground">Instructions disponibles</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {["↑ HAUT", "↓ BAS", "← GAUCHE", "→ DROITE"].map((instruction, index) => (
              <motion.span
                key={instruction}
                className="bg-slate-800 border border-primary/30 rounded px-3 py-1.5 text-sm font-mono text-primary"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {instruction}
              </motion.span>
            ))}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Exemple de réponse : DROITE, BAS, BAS, DROITE, HAUT
          </p>
        </div>
      </div>
    );
  }

  // ==================== RENDU LEGACY (programmation) ====================

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Question */}
      {question && (
        <div className="bg-primary/10 border border-primary/30 rounded-lg p-3">
          <p className="text-foreground font-medium">{question}</p>
        </div>
      )}

      {/* Code snippet */}
      {code && (
        <div className="bg-card/50 border border-border rounded-lg overflow-hidden">
          <div className="flex items-center gap-2 bg-muted px-4 py-2 border-b border-border">
            <FileCode className="h-4 w-4 text-primary" />
            <span className="text-sm font-semibold text-foreground">Code</span>
            {language && (
              <span className="ml-auto text-xs bg-primary/20 text-primary px-2 py-1 rounded">
                {language}
              </span>
            )}
          </div>
          <pre className="p-4 overflow-x-auto text-sm">
            <code className="text-foreground font-mono">{code}</code>
          </pre>
        </div>
      )}

      {/* Exemples d'entrée/sortie */}
      {examples.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Terminal className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Exemples</h4>
          </div>
          <div className="space-y-3">
            {examples.map((example: Record<string, unknown>, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md overflow-hidden"
              >
                <div className="bg-muted/50 px-3 py-1 border-b border-border">
                  <span className="text-xs font-semibold text-muted-foreground">
                    Exemple {index + 1}
                  </span>
                </div>
                <div className="p-3 space-y-2">
                  {example.input !== undefined && (
                    <div>
                      <span className="text-xs font-semibold text-muted-foreground">Entrée :</span>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                        {typeof example.input === "object"
                          ? JSON.stringify(example.input, null, 2)
                          : String(example.input)}
                      </pre>
                    </div>
                  )}
                  {example.output !== undefined && (
                    <div>
                      <span className="text-xs font-semibold text-muted-foreground">Sortie :</span>
                      <pre className="mt-1 p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                        {typeof example.output === "object"
                          ? JSON.stringify(example.output, null, 2)
                          : String(example.output)}
                      </pre>
                    </div>
                  )}
                  {example.explanation != null && example.explanation !== "" && (
                    <div className="text-xs text-muted-foreground italic pt-1 border-t border-border">
                      {String(example.explanation)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Entrée/Sortie simple */}
      {(input || output || expectedOutput) && examples.length === 0 && (
        <div className="grid gap-3 md:grid-cols-2">
          {input && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Terminal className="h-4 w-4 text-primary" />
                <h5 className="text-sm font-semibold text-foreground">Entrée</h5>
              </div>
              <pre className="p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                {typeof input === "object" ? JSON.stringify(input, null, 2) : String(input)}
              </pre>
            </div>
          )}
          {(output || expectedOutput) && (
            <div className="bg-card/50 border border-border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="h-4 w-4 text-green-500" />
                <h5 className="text-sm font-semibold text-foreground">Sortie attendue</h5>
              </div>
              <pre className="p-2 bg-muted rounded text-xs font-mono text-foreground overflow-x-auto">
                {typeof (output || expectedOutput) === "object"
                  ? JSON.stringify(output || expectedOutput, null, 2)
                  : String(output || expectedOutput)}
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Contraintes */}
      {constraints.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <XCircle className="h-5 w-5 text-orange-500" />
            <h4 className="font-semibold text-foreground">Contraintes</h4>
          </div>
          <ul className="space-y-1.5 text-sm">
            {constraints.map((constraint: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-orange-500 mt-0.5">•</span>
                <span className="text-muted-foreground">{constraint}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Indices */}
      {hints.length > 0 && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Code className="h-5 w-5 text-primary" />
            <h4 className="font-semibold text-foreground">Indices</h4>
          </div>
          <div className="space-y-2">
            {hints.map((hint: string, index: number) => (
              <div
                key={index}
                className="bg-background/50 border border-border rounded-md p-3 text-sm text-muted-foreground"
              >
                <span className="font-semibold text-primary">Indice {index + 1} :</span> {hint}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback : afficher toutes les données structurées */}
      {!code &&
        !question &&
        examples.length === 0 &&
        !input &&
        !output &&
        constraints.length === 0 && (
          <div className="bg-card/50 border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-3">
              <Code className="h-5 w-5 text-primary" />
              <h4 className="font-semibold text-foreground">Données du défi</h4>
            </div>
            <div className="space-y-2">
              {Object.entries(visualData).map(([key, value]) => {
                if (Array.isArray(value) && value.length > 0) {
                  return (
                    <div key={key} className="space-y-1">
                      <p className="text-sm font-semibold text-primary capitalize">
                        {key.replace(/_/g, " ")} :
                      </p>
                      <div className="pl-3 space-y-1">
                        {value.map((item: unknown, i: number) => (
                          <p key={i} className="text-sm text-foreground">
                            • {typeof item === "object" ? JSON.stringify(item) : String(item)}
                          </p>
                        ))}
                      </div>
                    </div>
                  );
                }
                return (
                  <div key={key} className="flex gap-2">
                    <span className="text-sm font-semibold text-primary capitalize">
                      {key.replace(/_/g, " ")} :
                    </span>
                    <span className="text-sm text-foreground">
                      {typeof value === "object" ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
    </div>
  );
}
