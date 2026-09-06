import React, { useEffect, useRef } from 'react';
import { User, Activity, AlertTriangle, ShieldCheck } from 'lucide-react';

interface SpatialPresenceHeatmapProps {
  activity: string;
  confidence: number;
  presence: string;
  isAnomaly: boolean;
  anomalyScore: number;
  subcarrierAmplitudes?: number[];
  environmentType?: string;
  sourceMode?: string;
  height?: number;
}

export const SpatialPresenceHeatmap: React.FC<SpatialPresenceHeatmapProps> = ({
  activity = 'Walking',
  confidence = 0.92,
  presence = 'Present',
  isAnomaly = false,
  anomalyScore = 0.05,
  subcarrierAmplitudes = [],
  environmentType = 'Living Room',
  sourceMode = 'Simulated CSI',
  height = 360,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);
  
  // Track continuous person position and history
  const stateRef = useRef({
    personX: 0.5,
    personY: 0.5,
    targetX: 0.5,
    targetY: 0.5,
    trail: [] as Array<{ x: number; y: number; alpha: number; radius: number }>,
    phase: 0,
    shockwaveRadius: 0,
    shockwaveAlpha: 0,
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let isAbsent = presence.toLowerCase() === 'absent' || activity.toLowerCase() === 'empty';

    // Update target coordinate depending on activity dynamics
    const state = stateRef.current;

    const render = () => {
      const w = canvas.width;
      const h = canvas.height;
      state.phase += 0.05;

      // 1. Calculate dynamic motion physics based on activity
      if (isAbsent) {
        state.targetX = 0.5;
        state.targetY = 0.5;
      } else {
        switch (activity.toLowerCase()) {
          case 'walking':
            // Smooth pacing ellipse
            state.targetX = 0.5 + 0.32 * Math.cos(state.phase * 0.7);
            state.targetY = 0.5 + 0.18 * Math.sin(state.phase * 1.4);
            break;
          case 'running':
            // Rapid wide figure-eight trajectory
            state.targetX = 0.5 + 0.38 * Math.sin(state.phase * 1.8);
            state.targetY = 0.5 + 0.28 * Math.sin(state.phase * 3.6);
            break;
          case 'falling':
            // Sudden drop to floor and stationary shockwave
            state.targetX = 0.62;
            state.targetY = 0.68;
            if (state.shockwaveRadius === 0 || state.shockwaveAlpha <= 0.05) {
              state.shockwaveRadius = 10;
              state.shockwaveAlpha = 1.0;
            }
            break;
          case 'waving':
            state.targetX = 0.45 + 0.05 * Math.sin(state.phase * 3.5);
            state.targetY = 0.45;
            break;
          case 'sitting':
            state.targetX = 0.7;
            state.targetY = 0.55 + 0.01 * Math.sin(state.phase * 0.5);
            break;
          case 'standing':
            state.targetX = 0.35;
            state.targetY = 0.42 + 0.012 * Math.sin(state.phase * 0.8);
            break;
          default:
            state.targetX = 0.5 + 0.1 * Math.cos(state.phase * 0.6);
            state.targetY = 0.5 + 0.1 * Math.sin(state.phase * 0.6);
        }
      }

      // Smooth interpolation (lerp)
      state.personX += (state.targetX - state.personX) * 0.08;
      state.personY += (state.targetY - state.personY) * 0.08;

      const px = state.personX * w;
      const py = state.personY * h;

      // Add to movement trail
      if (!isAbsent) {
        state.trail.push({ x: px, y: py, alpha: 1.0, radius: activity.toLowerCase() === 'running' ? 24 : 18 });
        if (state.trail.length > 25) state.trail.shift();
      } else {
        state.trail = [];
      }

      // --- CLEAR CANVAS & DRAW GRID ---
      ctx.fillStyle = '#060a12';
      ctx.fillRect(0, 0, w, h);

      // Draw Room Grid Layout
      ctx.strokeStyle = 'rgba(30, 41, 59, 0.45)';
      ctx.lineWidth = 1;
      const gridSize = 32;
      for (let x = 0; x < w; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // --- DRAW WI-FI ROUTER (Tx) & RECEIVER (Rx) ---
      const txX = 60;
      const txY = h / 2;
      const rxX = w - 60;
      const rxY = h / 2;

      // Concentric RF Wave emission from Tx
      ctx.strokeStyle = 'rgba(6, 182, 212, 0.25)';
      ctx.lineWidth = 1.5;
      for (let r = 15; r <= 90; r += 25) {
        const pulseR = (r + (state.phase * 20) % 25);
        ctx.beginPath();
        ctx.arc(txX, txY, pulseR, -Math.PI / 2.5, Math.PI / 2.5);
        ctx.stroke();
      }

      // Fresnel Reflection Ellipses between Tx and Rx
      for (let e = 1; e <= 3; e++) {
        ctx.strokeStyle = `rgba(14, 165, 233, ${0.12 - e * 0.03})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse((txX + rxX) / 2, (txY + rxY) / 2, (rxX - txX) / 2 + e * 20, 45 + e * 35, 0, 0, 2 * Math.PI);
        ctx.stroke();
      }

      // Transmitter Node (Tx)
      ctx.fillStyle = '#06b6d4';
      ctx.beginPath();
      ctx.arc(txX, txY, 8, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px Inter, sans-serif';
      ctx.fillText('Wi-Fi AP (Tx)', txX - 30, txY - 14);

      // Receiver Antenna Node (Rx)
      ctx.fillStyle = '#818cf8';
      ctx.beginPath();
      ctx.arc(rxX, rxY, 8, 0, 2 * Math.PI);
      ctx.fill();
      ctx.fillText('CSI Array (Rx)', rxX - 30, rxY - 14);

      // Direct Line-of-Sight (LoS) Carrier Beam
      ctx.strokeStyle = 'rgba(99, 102, 241, 0.35)';
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(txX, txY);
      ctx.lineTo(rxX, rxY);
      ctx.stroke();
      ctx.setLineDash([]);

      // --- DRAW MULTIPATH SCATTER BEAMS TO PERSON ---
      if (!isAbsent) {
        // Beam Tx -> Person
        const gradTx = ctx.createLinearGradient(txX, txY, px, py);
        gradTx.addColorStop(0, 'rgba(6, 182, 212, 0.4)');
        gradTx.addColorStop(1, 'rgba(244, 63, 94, 0.6)');
        ctx.strokeStyle = gradTx;
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(txX, txY);
        ctx.lineTo(px, py);
        ctx.stroke();

        // Beam Person -> Rx
        const gradRx = ctx.createLinearGradient(px, py, rxX, rxY);
        gradRx.addColorStop(0, 'rgba(244, 63, 94, 0.6)');
        gradRx.addColorStop(1, 'rgba(129, 140, 248, 0.4)');
        ctx.strokeStyle = gradRx;
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(rxX, rxY);
        ctx.stroke();

        // --- DRAW MOVEMENT HEATMAP TRAILS ---
        state.trail.forEach((p, idx) => {
          p.alpha *= 0.94;
          const ratio = idx / state.trail.length;
          const trailGrad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * (1 + (1 - ratio)));
          trailGrad.addColorStop(0, `rgba(245, 158, 11, ${p.alpha * 0.45})`);
          trailGrad.addColorStop(0.6, `rgba(239, 68, 68, ${p.alpha * 0.2})`);
          trailGrad.addColorStop(1, 'rgba(239, 68, 68, 0)');

          ctx.fillStyle = trailGrad;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius * (1 + (1 - ratio)), 0, 2 * Math.PI);
          ctx.fill();
        });

        // --- DRAW EXPANDING SHOCKWAVE IF FALL DETECTED ---
        if (activity.toLowerCase() === 'falling' || isAnomaly) {
          if (state.shockwaveAlpha > 0) {
            ctx.strokeStyle = `rgba(239, 68, 68, ${state.shockwaveAlpha})`;
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(px, py, state.shockwaveRadius, 0, 2 * Math.PI);
            ctx.stroke();

            state.shockwaveRadius += 3.5;
            state.shockwaveAlpha -= 0.018;
          }
        }

        // --- DRAW CORE HUMAN HEATMAP BLOBS (ISOCONTOURS) ---
        const blobRadius = activity.toLowerCase() === 'running' ? 42 : activity.toLowerCase() === 'falling' ? 55 : 34;

        // Outer glow
        const glowGrad = ctx.createRadialGradient(px, py, 0, px, py, blobRadius * 1.8);
        glowGrad.addColorStop(0, isAnomaly ? 'rgba(239, 68, 68, 0.65)' : 'rgba(249, 115, 22, 0.45)');
        glowGrad.addColorStop(0.4, isAnomaly ? 'rgba(225, 29, 72, 0.3)' : 'rgba(234, 88, 12, 0.25)');
        glowGrad.addColorStop(0.8, 'rgba(16, 185, 129, 0.08)');
        glowGrad.addColorStop(1, 'rgba(16, 185, 129, 0)');
        ctx.fillStyle = glowGrad;
        ctx.beginPath();
        ctx.arc(px, py, blobRadius * 1.8, 0, 2 * Math.PI);
        ctx.fill();

        // Inner intense thermal core
        const coreGrad = ctx.createRadialGradient(px, py, 0, px, py, blobRadius * 0.7);
        coreGrad.addColorStop(0, '#ffffff');
        coreGrad.addColorStop(0.3, isAnomaly ? '#ef4444' : '#f59e0b');
        coreGrad.addColorStop(0.8, '#dc2626');
        coreGrad.addColorStop(1, 'rgba(220, 38, 38, 0)');
        ctx.fillStyle = coreGrad;
        ctx.beginPath();
        ctx.arc(px, py, blobRadius * 0.7, 0, 2 * Math.PI);
        ctx.fill();

        // Target Reticle & Activity Pulse Ring
        ctx.strokeStyle = isAnomaly ? '#ef4444' : '#10b981';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(px, py, blobRadius * (0.8 + 0.1 * Math.sin(state.phase * 3)), 0, 2 * Math.PI);
        ctx.stroke();

        // Human Indicator Label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`👤 ${activity.toUpperCase()}`, px, py - blobRadius - 8);
        ctx.fillStyle = 'rgba(148, 163, 184, 0.9)';
        ctx.font = '10px font-mono';
        ctx.fillText(`${(confidence * 100).toFixed(1)}% | (${(state.personX * 8).toFixed(1)}m, ${(state.personY * 6).toFixed(1)}m)`, px, py - blobRadius + 6);
      } else {
        // Room is Vacant / Absent
        ctx.fillStyle = 'rgba(100, 116, 139, 0.5)';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('📡 Room Vacant (Static Ambient CSI Baseline)', w / 2, h / 2 - 10);
        ctx.font = '11px font-mono';
        ctx.fillText('No Kinetic Perturbations Detected in Multipath Zone', w / 2, h / 2 + 12);
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [activity, confidence, presence, isAnomaly, environmentType]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col relative overflow-hidden">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">
              REAL-TIME RF KINETIC RADAR
            </span>
          </div>
          <h3 className="text-lg font-black text-white tracking-tight mt-0.5 flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand-400" />
            2D Spatial Multipath & Human Presence Heatmap
          </h3>
        </div>

        {/* Status Indicators */}
        <div className="flex items-center gap-2">
          <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 text-xs font-bold ${
            presence.toLowerCase() === 'present'
              ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
              : 'bg-slate-800/80 text-slate-400 border-slate-700'
          }`}>
            <User className="w-3.5 h-3.5" />
            {presence.toUpperCase()}
          </div>

          <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 text-xs font-bold ${
            isAnomaly
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-bounce'
              : 'bg-slate-800/80 text-slate-300 border-slate-700'
          }`}>
            {isAnomaly ? <AlertTriangle className="w-3.5 h-3.5 text-rose-400" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />}
            {isAnomaly ? `ANOMALY: ${(anomalyScore * 100).toFixed(0)}%` : 'NORMAL'}
          </div>
        </div>
      </div>

      {/* Canvas Radar Container */}
      <div className="relative w-full rounded-xl overflow-hidden border border-slate-800 shadow-inner bg-slate-950">
        <canvas
          ref={canvasRef}
          width={800}
          height={height}
          className="w-full h-auto block"
        />

        {/* Legend Overlay at Bottom */}
        <div className="absolute bottom-2 left-3 right-3 bg-slate-950/85 backdrop-blur-md border border-slate-800/80 px-3 py-2 rounded-lg flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
          <div className="flex items-center space-x-4">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
              Wi-Fi AP (Tx)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
              CSI Receiver (Rx)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
              Human Kinetic Disturbance
            </span>
          </div>
          <div className="font-mono text-slate-300">
            Zone: <span className="text-white font-bold">{environmentType} (8.0m × 6.0m)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
