import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Eye,
  Activity,
  FileCheck2,
  Crosshair,
  PlayCircle,
  BarChart3,
  GitCompare,
  FileText,
  FlaskConical,
  Settings,
  ShieldCheck,
} from 'lucide-react';

interface NavbarProps {
  sessionId?: string;
  isBackendOnline: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ sessionId, isBackendOnline }) => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: Activity },
    { to: '/consent', label: 'Consent', icon: FileCheck2 },
    { to: '/calibration', label: 'Calibration', icon: Crosshair },
    { to: '/experiment', label: 'Experiment', icon: PlayCircle },
    { to: '/signal', label: 'Signal Analysis', icon: BarChart3 },
    { to: '/models', label: 'Models', icon: GitCompare },
    { to: '/report', label: 'Report', icon: FileText },
    { to: '/research', label: 'Experiments', icon: FlaskConical },
    { to: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 bg-navy-950/80 backdrop-blur-md border-b border-navy-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 p-0.5 shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-shadow">
              <div className="w-full h-full bg-navy-950 rounded-[10px] flex items-center justify-center">
                <Eye className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-cyan-400 bg-clip-text text-transparent">
                GazeGuard AI
              </span>
              <span className="block text-[10px] font-mono uppercase tracking-wider text-slate-400">
                QPTC CIT Platform
              </span>
            </div>
          </NavLink>

          {/* Navigation links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-blue-600/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                    }`
                  }
                >
                  <Icon className="w-3.5 h-3.5" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>

          {/* Right Status Badges */}
          <div className="flex items-center gap-3">
            {/* Session Pill */}
            {sessionId ? (
              <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-navy-800/80 border border-navy-700 text-xs font-mono text-cyan-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                <span>{sessionId}</span>
              </div>
            ) : (
              <span className="hidden sm:inline-block text-xs font-mono text-slate-500">
                No Active Session
              </span>
            )}

            {/* Backend Health Status */}
            <div
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-mono border ${
                isBackendOnline
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
              }`}
            >
              <span
                className={`w-1.5 h-1.5 rounded-full ${
                  isBackendOnline ? 'bg-emerald-400' : 'bg-rose-400'
                }`}
              ></span>
              <span>{isBackendOnline ? 'API READY' : 'OFFLINE'}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
