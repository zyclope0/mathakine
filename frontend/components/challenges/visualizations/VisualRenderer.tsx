'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Eye, RotateCw, ZoomIn, ZoomOut } from 'lucide-react';
import { useState } from 'react';
import { motion } from 'framer-motion';

interface VisualRendererProps {
  visualData: any;
  className?: string | undefined;
}

/**
 * Fonction helper pour obtenir l'icône d'une forme
 */
function getShapeIcon(shape: string): string {
  const shapeMap: Record<string, string> = {
    'triangle': '▲',
    'rectangle': '■',
    'cercle': '●',
    'circle': '●',
    'carré': '■',
    'square': '■',
    'losange': '◆',
    'diamond': '◆',
    'étoile': '★',
    'star': '★',
  };
  return shapeMap[shape.toLowerCase()] || shape.charAt(0).toUpperCase();
}

/**
 * Renderer pour les défis de type VISUAL/SPATIAL.
 * Affiche des formes, rotations et manipulations spatiales.
 */
export function VisualRenderer({ visualData, className }: VisualRendererProps) {
  const [rotation, setRotation] = useState(0);
  const [scale, setScale] = useState(1);
  const [flipped, setFlipped] = useState(false);

  // Parser les données visuelles
  const shapes = visualData?.shapes || visualData?.items || [];
  const asciiArt = visualData?.ascii || visualData?.art || visualData?.content;
  const layout = visualData?.layout || [];
  const symmetryType = visualData?.type;
  const symmetryLine = visualData?.symmetry_line;

  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
  };

  const handleZoomIn = () => {
    setScale((prev) => Math.min(prev + 0.1, 2));
  };

  const handleZoomOut = () => {
    setScale((prev) => Math.max(prev - 0.1, 0.5));
  };

  const handleFlip = () => {
    setFlipped((prev) => !prev);
  };

  return (
    <Card className={`bg-card border-primary/20 ${className || ''}`}>
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Eye className="h-5 w-5 text-primary" />
              <h4 className="text-sm font-semibold text-foreground">Visualisation spatiale</h4>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleRotate}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Rotation"
                aria-label="Rotation"
              >
                <RotateCw className="h-4 w-4" />
              </button>
              <button
                onClick={handleZoomIn}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Zoom avant"
                aria-label="Zoom avant"
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Zoom arrière"
                aria-label="Zoom arrière"
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              <button
                onClick={handleFlip}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Retourner"
                aria-label="Retourner"
              >
                <span className="text-xs">↔</span>
              </button>
            </div>
          </div>

          <div className="flex justify-center items-center min-h-[200px] bg-muted/30 rounded-lg p-6">
            {symmetryType === 'symmetry' && layout.length > 0 ? (
              // Rendu spécialisé pour la symétrie
              <motion.div
                className="w-full"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? 'scaleX(-1)' : ''}`,
                  transformOrigin: 'center',
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                <div className="relative flex items-center justify-center gap-4">
                  {/* Côté gauche */}
                  <div className="flex gap-3 items-center">
                    {layout
                      .filter((item: any) => item.side === 'left')
                      .sort((a: any, b: any) => a.position - b.position)
                      .map((item: any, idx: number) => (
                        <motion.div
                          key={`left-${item.position}`}
                          className="w-20 h-20 border-2 border-primary rounded-lg flex items-center justify-center font-semibold bg-primary/10"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                        >
                          <span className="text-lg">{getShapeIcon(item.shape)}</span>
                        </motion.div>
                      ))}
                  </div>
                  
                  {/* Ligne de symétrie */}
                  <div className={`w-1 h-32 bg-primary/50 ${symmetryLine === 'vertical' ? '' : 'rotate-90'}`} />
                  
                  {/* Côté droit */}
                  <div className="flex gap-3 items-center">
                    {layout
                      .filter((item: any) => item.side === 'right')
                      .sort((a: any, b: any) => a.position - b.position)
                      .map((item: any, idx: number) => (
                        <motion.div
                          key={`right-${item.position}`}
                          className={`w-20 h-20 border-2 rounded-lg flex items-center justify-center font-semibold ${
                            item.question 
                              ? 'border-dashed border-primary/70 bg-primary/5 animate-pulse' 
                              : 'border-primary bg-primary/10'
                          }`}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                        >
                          {item.question ? (
                            <span className="text-2xl font-bold text-primary">?</span>
                          ) : (
                            <span className="text-lg">{getShapeIcon(item.shape)}</span>
                          )}
                        </motion.div>
                      ))}
                  </div>
                </div>
                {visualData?.description && (
                  <p className="text-xs text-muted-foreground text-center mt-4">
                    {visualData.description}
                  </p>
                )}
              </motion.div>
            ) : asciiArt ? (
              <motion.pre
                className="text-foreground font-mono text-sm whitespace-pre"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? 'scaleX(-1)' : ''}`,
                  transformOrigin: 'center',
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                {asciiArt}
              </motion.pre>
            ) : shapes.length > 0 ? (
              <motion.div
                className="flex flex-wrap gap-4 justify-center"
                style={{
                  transform: `rotate(${rotation}deg) scale(${scale}) ${flipped ? 'scaleX(-1)' : ''}`,
                  transformOrigin: 'center',
                }}
                animate={{ rotate: rotation }}
                transition={{ duration: 0.3 }}
              >
                {shapes.map((shape: any, index: number) => (
                  <motion.div
                    key={index}
                    className="w-16 h-16 border-2 border-primary rounded-lg flex items-center justify-center font-semibold"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    {typeof shape === 'string' ? getShapeIcon(shape) : (shape.label || shape.value || index + 1)}
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <div className="text-muted-foreground text-center">
                <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Aucune donnée visuelle disponible</p>
              </div>
            )}
          </div>

          <div className="text-xs text-center text-muted-foreground">
            Utilisez les contrôles pour manipuler la visualisation
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

