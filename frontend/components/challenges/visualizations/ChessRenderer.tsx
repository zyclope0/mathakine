'use client';

import { useEffect, useState } from 'react';
import { Crown, Target } from 'lucide-react';

interface ChessRendererProps {
  visualData: any;
  className?: string;
}

/**
 * Renderer pour les défis d'échecs.
 * Affiche un échiquier visuel avec les pièces et les positions atteignables.
 */
export function ChessRenderer({ visualData, className = '' }: ChessRendererProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || !visualData) {
    return null;
  }

  // Fonction pour convertir notation échecs (ex: "E4") en coordonnées [row, col]
  const chessNotationToCoords = (notation: string): [number, number] | null => {
    if (!notation || typeof notation !== 'string' || notation.length < 2) return null;
    const file = notation.charAt(0).toLowerCase();
    const rank = notation.charAt(1);
    const col = file.charCodeAt(0) - 'a'.charCodeAt(0);  // a=0, b=1, ..., h=7
    const row = 8 - parseInt(rank);  // 8=0, 7=1, ..., 1=7
    if (col < 0 || col > 7 || row < 0 || row > 7 || isNaN(row)) return null;
    return [row, col];
  };

  // Extraire les données
  const board = visualData.board || [];
  let knightPosition = visualData.knight_position || visualData.position || null;
  let reachablePositions = visualData.reachable_positions || visualData.targets || [];
  const currentPiece = visualData.piece || visualData.current_piece || 'knight';
  const question = visualData.question || '';
  const turn = visualData.turn || '';
  const objective = visualData.objective || '';

  // Convertir knight_position si c'est une string (ex: "E4" → [3, 4])
  if (typeof knightPosition === 'string') {
    knightPosition = chessNotationToCoords(knightPosition);
  }

  // Convertir reachable_positions si c'est un tableau de strings
  if (Array.isArray(reachablePositions) && reachablePositions.length > 0 && typeof reachablePositions[0] === 'string') {
    reachablePositions = reachablePositions
      .map((notation: string) => chessNotationToCoords(notation))
      .filter((coords): coords is [number, number] => coords !== null);
  }

  // Convertir highlight_positions si c'est un tableau de strings (ex: ["b7", "d2"])
  let normalizedHighlights = Array.isArray(visualData.highlight_positions) ? visualData.highlight_positions : [];
  if (normalizedHighlights.length > 0) {
    const first = normalizedHighlights[0];
    if (typeof first === 'string') {
      normalizedHighlights = normalizedHighlights
        .map((n: unknown) => (typeof n === 'string' ? chessNotationToCoords(n) : null))
        .filter((c: [number, number] | null): c is [number, number] => c !== null);
    } else if (Array.isArray(first) && first.length >= 2) {
      // Déjà [row, col] - s'assurer que ce sont des nombres
      normalizedHighlights = normalizedHighlights
        .filter((p: unknown) => Array.isArray(p) && p.length >= 2)
        .map((p: unknown[]) => [Number(p[0]), Number(p[1])]);
    }
  }

  // Dimensions de l'échiquier (standard 8x8 ou custom)
  const boardSize = board.length > 0 ? board.length : 8;

  // Si on a un échiquier 2D
  const hasBoard = board.length > 0;

  // Filtrer les highlights : n'afficher que sur les cases qui contiennent une pièce (cohérence visuelle)
  const squareHasPiece = (r: number, c: number): boolean => {
    if (!hasBoard || !board[r]?.[c]) return false;
    const raw = board[r][c];
    if (typeof raw === 'object' && raw !== null && 'piece' in raw) {
      const p = String((raw as { piece?: string }).piece ?? '');
      return !!p && !p.match(/^[a-h][1-8]$/i);
    }
    const p = String(raw ?? '');
    return !!p && p !== ' ' && p !== '.' && !p.match(/^[a-h][1-8]$/i);
  };
  if (hasBoard && normalizedHighlights.length > 0) {
    normalizedHighlights = normalizedHighlights.filter(([r, c]) => squareHasPiece(r, c));
  }

  // Symboles des pièces d'échecs
  // Pièces blanches (outline) - majuscules en notation FEN
  const whitePieceSymbols: Record<string, string> = {
    'K': '♔',
    'Q': '♕',
    'R': '♖',
    'B': '♗',
    'N': '♘',
    'P': '♙',
    'king': '♔',
    'queen': '♕',
    'rook': '♖',
    'bishop': '♗',
    'knight': '♘',
    'pawn': '♙',
  };

  // Pièces noires (pleines) - minuscules en notation FEN
  const blackPieceSymbols: Record<string, string> = {
    'k': '♚',
    'q': '♛',
    'r': '♜',
    'b': '♝',
    'n': '♞',
    'p': '♟',
  };

  // Détecter si une pièce est blanche (majuscule ou mot-clé)
  const isWhitePiece = (piece: string): boolean => {
    if (!piece || piece.length === 0) return false;
    // Majuscule = blanc en notation FEN
    if (piece.length === 1) return piece === piece.toUpperCase();
    // Mot-clé avec préfixe white
    return piece.toLowerCase().startsWith('white') || 
           ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn'].includes(piece.toLowerCase());
  };

  // Obtenir le symbole et la couleur d'une pièce
  const getPieceInfo = (piece: string): { symbol: string; isWhite: boolean } | null => {
    if (!piece || piece === '' || piece === ' ' || piece === '.') return null;
    
    const isWhite = isWhitePiece(piece);
    const key = piece.length === 1 ? piece : piece.toLowerCase().replace('white', '').replace('black', '').trim();
    
    if (isWhite) {
      const symbol = whitePieceSymbols[piece] || whitePieceSymbols[key.toUpperCase()] || whitePieceSymbols[key];
      if (symbol) return { symbol, isWhite: true };
    } else {
      const symbol = blackPieceSymbols[piece] || blackPieceSymbols[key.toLowerCase()];
      if (symbol) return { symbol, isWhite: false };
    }
    return null;
  };

  // Couleurs pour l'échiquier
  const lightSquare = 'bg-amber-100 dark:bg-amber-200';
  const darkSquare = 'bg-amber-800 dark:bg-amber-900';
  const highlightSquare = 'bg-blue-400 dark:bg-blue-600';
  const reachableSquare = 'bg-green-400 dark:bg-green-600';
  const currentSquare = 'bg-red-400 dark:bg-red-600';

  // Vérifier si une position est la position actuelle
  const isCurrentPosition = (row: number, col: number): boolean => {
    if (!knightPosition) return false;
    return knightPosition[0] === row && knightPosition[1] === col;
  };

  // Vérifier si une position est atteignable
  const isReachablePosition = (row: number, col: number): boolean => {
    return reachablePositions.some((pos: number[]) => pos[0] === row && pos[1] === col);
  };

  // Vérifier si une position est mise en évidence
  const isHighlightPosition = (row: number, col: number): boolean => {
    return normalizedHighlights.some((pos: number[]) => pos[0] === row && pos[1] === col);
  };

  // Obtenir la couleur de fond d'une case
  const getSquareColor = (row: number, col: number): string => {
    if (isCurrentPosition(row, col)) return currentSquare;
    if (isReachablePosition(row, col)) return reachableSquare;
    if (isHighlightPosition(row, col)) return highlightSquare;
    
    // Alternance standard échiquier
    return (row + col) % 2 === 0 ? lightSquare : darkSquare;
  };

  // Obtenir le contenu d'une case avec info couleur
  const getSquareContentInfo = (row: number, col: number): { symbol: string; isWhite: boolean } | null => {
    // Si on a un board 2D avec des vraies pièces (pas des labels comme "A1", "B2")
    if (hasBoard && board[row] && board[row][col] !== undefined) {
      const raw = board[row][col];
      const piece = typeof raw === 'object' && raw !== null && 'piece' in raw
        ? String((raw as { piece?: string }).piece)
        : String(raw ?? '');
      // Exclure les labels de cases (a1-h8) et les chaînes vides
      if (piece && piece !== ' ' && piece !== '.' && !piece.match(/^[a-h][1-8]$/i)) {
        const info = getPieceInfo(piece);
        if (info) return info;
      }
    }

    // Afficher la pièce actuelle si c'est sa position
    if (isCurrentPosition(row, col)) {
      const info = getPieceInfo(currentPiece);
      if (info) return info;
      // Fallback pour le cavalier par défaut (blanc)
      return { symbol: '♘', isWhite: true };
    }

    return null;
  };

  // Obtenir le label d'une position (notation échecs : a1, b2, etc.)
  const getPositionLabel = (row: number, col: number): string => {
    const files = 'abcdefgh';
    return `${files[col]}${boardSize - row}`;
  };

  // Labels d'objectif lisibles
  const objectiveLabels: Record<string, string> = {
    mat_en_1: 'Mat en 1 coup',
    mat_en_2: 'Mat en 2 coups',
    mat_en_3: 'Mat en 3 coups',
    meilleur_coup: 'Meilleur coup',
    gain_materiel: 'Gain de matériel',
  };
  const objectiveLabel = objective ? (objectiveLabels[objective] || objective) : '';
  const turnLabel = turn === 'white' ? 'Les blancs jouent' : turn === 'black' ? 'Les noirs jouent' : '';

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Tour + objectif (puzzles mat) */}
      {(turnLabel || objectiveLabel) && (
        <div className="flex flex-wrap gap-3 items-center text-sm">
          {turnLabel && (
            <span className="bg-primary/20 text-primary px-3 py-1.5 rounded-lg font-medium">
              {turnLabel}
            </span>
          )}
          {objectiveLabel && (
            <span className="bg-amber-500/20 text-amber-600 dark:text-amber-400 px-3 py-1.5 rounded-lg font-medium">
              {objectiveLabel}
            </span>
          )}
        </div>
      )}

      {/* Question ou contexte */}
      {question && (
        <div className="bg-card/50 border border-border rounded-lg p-3">
          <p className="text-sm text-muted-foreground italic">{question}</p>
        </div>
      )}

      {/* Légende */}
      <div className="flex flex-wrap gap-3 justify-center text-xs">
        {knightPosition && (
          <div className="flex items-center gap-1">
            <div className={`w-4 h-4 ${currentSquare} rounded border border-border`} />
            <span className="text-muted-foreground">Position actuelle</span>
          </div>
        )}
        {reachablePositions.length > 0 && (
          <div className="flex items-center gap-1">
            <div className={`w-4 h-4 ${reachableSquare} rounded border border-border`} />
            <span className="text-muted-foreground">Positions atteignables</span>
          </div>
        )}
        {normalizedHighlights.length > 0 && (
          <div className="flex items-center gap-1">
            <div className={`w-4 h-4 ${highlightSquare} rounded border border-border`} />
            <span className="text-muted-foreground">
              {hasBoard ? 'Pièces clés / cases importantes' : 'Positions spéciales'}
            </span>
          </div>
        )}
      </div>

      {/* Échiquier */}
      <div className="bg-card/50 border border-border rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Crown className="h-5 w-5 text-primary" />
          <h4 className="font-semibold text-foreground">Échiquier</h4>
        </div>

        <div className="flex justify-center">
          <div className="inline-block">
            {/* Labels des colonnes (a-h) */}
            <div className="flex mb-1">
              <div className="w-6" /> {/* Espace pour les labels de lignes */}
              {Array.from({ length: boardSize }, (_, i) => (
                <div
                  key={i}
                  className="w-10 h-6 flex items-center justify-center text-xs font-semibold text-muted-foreground"
                >
                  {String.fromCharCode(97 + i)}
                </div>
              ))}
            </div>

            {/* Échiquier avec labels de lignes */}
            <div className="flex">
              {/* Labels des lignes (8-1) */}
              <div className="flex flex-col">
                {Array.from({ length: boardSize }, (_, i) => (
                  <div
                    key={i}
                    className="w-6 h-10 flex items-center justify-center text-xs font-semibold text-muted-foreground"
                  >
                    {boardSize - i}
                  </div>
                ))}
              </div>

              {/* Grille de l'échiquier */}
              <div className="border-2 border-border rounded overflow-hidden">
                {Array.from({ length: boardSize }, (_, row) => (
                  <div key={row} className="flex">
                    {Array.from({ length: boardSize }, (_, col) => {
                      const pieceInfo = getSquareContentInfo(row, col);
                      const bgColor = getSquareColor(row, col);
                      const posLabel = getPositionLabel(row, col);

                      return (
                        <div
                          key={col}
                          className={`w-10 h-10 flex items-center justify-center relative group ${bgColor} transition-all duration-200`}
                          title={posLabel}
                        >
                          {/* Contenu de la case (pièce ou marqueur) */}
                          {pieceInfo ? (
                            <span 
                              className="text-2xl select-none"
                              style={{
                                // Pièces blanches : texte clair avec contour sombre
                                // Pièces noires : texte sombre avec contour clair
                                color: pieceInfo.isWhite ? '#FFFFFF' : '#1a1a1a',
                                textShadow: pieceInfo.isWhite 
                                  ? '0 0 3px #000, 0 0 3px #000, 1px 1px 1px #000, -1px -1px 1px #000, 1px -1px 1px #000, -1px 1px 1px #000'
                                  : '0 0 3px #fff, 0 0 3px #fff, 1px 1px 1px #fff, -1px -1px 1px #fff, 1px -1px 1px #fff, -1px 1px 1px #fff',
                                WebkitTextStroke: pieceInfo.isWhite ? '0.5px #333' : '0.5px #ccc',
                              }}
                            >
                              {pieceInfo.symbol}
                            </span>
                          ) : isReachablePosition(row, col) ? (
                            <Target className="h-4 w-4 text-white/80" />
                          ) : null}

                          {/* Coordonnées au hover (coin bas-droit, discret) */}
                          <div className="absolute bottom-0.5 right-0.5 opacity-0 group-hover:opacity-90 transition-opacity pointer-events-none">
                            <span className="text-[9px] font-mono text-muted-foreground/80 bg-background/60 px-1 rounded">
                              {posLabel}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Informations supplémentaires */}
      {(knightPosition || reachablePositions.length > 0) && (
        <div className="bg-card/50 border border-border rounded-lg p-4">
          <div className="space-y-2 text-sm">
            {knightPosition && Array.isArray(knightPosition) && knightPosition.length >= 2 && (
              <div className="flex items-center gap-2">
                <span className="font-semibold text-primary">Position actuelle :</span>
                <code className="bg-muted px-2 py-1 rounded text-foreground">
                  {getPositionLabel(knightPosition[0], knightPosition[1])} ({knightPosition[0]}, {knightPosition[1]})
                </code>
              </div>
            )}

            {reachablePositions.length > 0 && (
              <div>
                <span className="font-semibold text-primary">Positions atteignables :</span>
                <div className="flex flex-wrap gap-2 mt-2">
                  {reachablePositions.map((pos: any, index: number) => {
                    // Vérifier que pos est un tableau valide avec 2 éléments
                    if (!Array.isArray(pos) || pos.length < 2 || typeof pos[0] !== 'number' || typeof pos[1] !== 'number') {
                      return null;
                    }
                    return (
                      <code
                        key={index}
                        className="bg-green-500/20 border border-green-500/30 px-2 py-1 rounded text-foreground text-xs"
                      >
                        {getPositionLabel(pos[0], pos[1])}
                      </code>
                    );
                  })}
                </div>
                <div className="mt-2 text-muted-foreground">
                  Total : <span className="font-semibold">{reachablePositions.length}</span> positions
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

