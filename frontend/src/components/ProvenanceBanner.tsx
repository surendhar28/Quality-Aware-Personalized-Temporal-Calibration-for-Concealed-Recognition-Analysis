import React from 'react';
import { AlertTriangle, Database, Info, ShieldAlert } from 'lucide-react';

interface ProvenanceBannerProps {
  mode: 'real' | 'synthetic' | 'live';
  customMessage?: string;
}

export const ProvenanceBanner: React.FC<ProvenanceBannerProps> = ({ mode, customMessage }) => {
  if (mode === 'real') {
    return (
      <div className="bg-emerald-950/40 border-b border-emerald-500/20 px-4 py-2 text-xs font-mono text-emerald-300 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
          <Database className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>
            <strong>DATA PROVENANCE: REAL HARDWARE CIT DATASET</strong> — Tobii Pro Fusion Desktop Eye Tracker (Zenodo DOI: 10.5281/zenodo.18525952 | CC-BY-4.0).
          </span>
        </div>
      </div>
    );
  }

  if (mode === 'synthetic') {
    return (
      <div className="bg-amber-950/40 border-b border-amber-500/20 px-4 py-2 text-xs font-mono text-amber-300 flex items-center justify-between">
        <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            <strong>DATA PROVENANCE: SYNTHETIC TEST BENCHMARK</strong> — Results generated via mathematical test fixtures for software verification and algorithmic ablation. 
            <em className="text-amber-200 ml-1">Must NOT be interpreted or cited as empirical scientific findings.</em>
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-blue-950/40 border-b border-blue-500/20 px-4 py-2 text-xs font-mono text-cyan-300 flex items-center justify-between">
      <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
        <Info className="w-4 h-4 text-cyan-400 shrink-0" />
        <span>
          <strong>DATA PROVENANCE: LIVE WEBCAM SESSION</strong> — Real-time browser gaze estimation. Pseudonymous session. Raw video is never stored.
        </span>
      </div>
    </div>
  );
};
