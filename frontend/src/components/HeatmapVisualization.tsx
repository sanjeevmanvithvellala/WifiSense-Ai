import React, { useEffect, useRef } from 'react';

interface HeatmapVisualizationProps {
  matrix: number[][]; // (time_steps, subcarriers)
  title?: string;
  height?: number;
}

export const HeatmapVisualization: React.FC<HeatmapVisualizationProps> = ({
  matrix,
  title = 'CSI Amplitude Spectrogram Heatmap',
  height = 180,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = '#090e17';
    ctx.fillRect(0, 0, width, h);

    if (!matrix || matrix.length === 0 || matrix[0].length === 0) {
      ctx.fillStyle = '#64748b';
      ctx.font = '12px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Accumulating Spectrogram Windows...', width / 2, h / 2);
      return;
    }

    const timeSteps = matrix.length;
    const subcarriers = matrix[0].length;

    // Find min and max
    let min = Infinity;
    let max = -Infinity;
    for (let t = 0; t < timeSteps; t++) {
      for (let s = 0; s < subcarriers; s++) {
        const v = matrix[t][s];
        if (v < min) min = v;
        if (v > max) max = v;
      }
    }
    const range = max - min || 1;

    const cellWidth = width / timeSteps;
    const cellHeight = h / subcarriers;

    // Render cells with colormap: deep navy -> cyan -> amber -> rose
    for (let t = 0; t < timeSteps; t++) {
      for (let s = 0; s < subcarriers; s++) {
        const norm = Math.max(0, Math.min(1, (matrix[t][s] - min) / range));
        
        // Colormap calculation (Turbo / Viridis inspired)
        let r = 0, g = 0, b = 0;
        if (norm < 0.25) {
          const ratio = norm / 0.25;
          r = Math.floor(10 + 15 * ratio);
          g = Math.floor(25 + 90 * ratio);
          b = Math.floor(60 + 140 * ratio);
        } else if (norm < 0.5) {
          const ratio = (norm - 0.25) / 0.25;
          r = Math.floor(25 + 10 * ratio);
          g = Math.floor(115 + 100 * ratio);
          b = Math.floor(200 - 40 * ratio);
        } else if (norm < 0.75) {
          const ratio = (norm - 0.5) / 0.25;
          r = Math.floor(35 + 210 * ratio);
          g = Math.floor(215 - 50 * ratio);
          b = Math.floor(160 - 130 * ratio);
        } else {
          const ratio = (norm - 0.75) / 0.25;
          r = Math.floor(245 + 10 * ratio);
          g = Math.floor(165 - 120 * ratio);
          b = Math.floor(30 + 40 * ratio);
        }

        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.fillRect(t * cellWidth, h - (s + 1) * cellHeight, cellWidth + 0.5, cellHeight + 0.5);
      }
    }
  }, [matrix]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent-amber"></span>
          {title}
        </h4>
        <span className="text-[11px] font-mono text-slate-400">
          Time vs Subcarrier Doppler Energy
        </span>
      </div>
      <div className="relative w-full rounded-lg overflow-hidden border border-slate-800/80">
        <canvas
          ref={canvasRef}
          width={700}
          height={height}
          className="w-full h-auto block"
        />
      </div>
    </div>
  );
};
