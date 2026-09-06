import React, { useEffect, useRef } from 'react';

interface SignalWaveformProps {
  amplitudes: number[];
  title?: string;
  subcarrierCount?: number;
  height?: number;
  color?: string;
}

export const SignalWaveform: React.FC<SignalWaveformProps> = ({
  amplitudes,
  title = 'CSI Subcarrier Amplitude Spectrum',
  subcarrierCount = 64,
  height = 180,
  color = '#0ea5e9',
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const h = canvas.height;

    // Clear background
    ctx.fillStyle = '#090e17';
    ctx.fillRect(0, 0, width, h);

    // Draw grid lines
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let x = 0; x <= width; x += width / 8) {
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
    }
    for (let y = 0; y <= h; y += h / 4) {
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
    }
    ctx.stroke();

    if (!amplitudes || amplitudes.length === 0) {
      ctx.fillStyle = '#64748b';
      ctx.font = '12px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Awaiting CSI Stream...', width / 2, h / 2);
      return;
    }

    // Determine scale
    const maxVal = Math.max(...amplitudes, 30);
    const minVal = Math.min(...amplitudes, 0);
    const range = maxVal - minVal || 1;

    // Draw glow curve
    ctx.shadowBlur = 10;
    ctx.shadowColor = color;
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.beginPath();

    const step = width / (amplitudes.length - 1 || 1);
    amplitudes.forEach((val, i) => {
      const normalizedY = h - ((val - minVal) / range) * (h - 24) - 12;
      if (i === 0) {
        ctx.moveTo(0, normalizedY);
      } else {
        ctx.lineTo(i * step, normalizedY);
      }
    });
    ctx.stroke();

    // Fill gradient under waveform
    ctx.shadowBlur = 0;
    ctx.lineTo(width, h);
    ctx.lineTo(0, h);
    ctx.closePath();

    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, `${color}33`);
    gradient.addColorStop(1, `${color}00`);
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw points on active subcarriers
    ctx.fillStyle = '#38bdf8';
    amplitudes.forEach((val, i) => {
      if (i % 4 === 0) {
        const x = i * step;
        const y = h - ((val - minVal) / range) * (h - 24) - 12;
        ctx.beginPath();
        ctx.arc(x, y, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    });
  }, [amplitudes, color]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-md flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-brand-400"></span>
          {title}
        </h4>
        <span className="text-[11px] font-mono text-slate-400">
          {amplitudes.length || subcarrierCount} Subcarriers | 20 MHz
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
