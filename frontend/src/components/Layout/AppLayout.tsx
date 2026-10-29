import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Activity,
  FileCheck2,
  Crosshair,
  PlayCircle,
  BarChart3,
  GitCompare,
  FileText,
  FlaskConical,
  Settings,
  Eye,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Database,
  Sun,
  Moon,
  Sparkles,
  Palette,
  Check,
  ShieldAlert,
} from 'lucide-react';
import { useTheme, ThemeName } from '../../contexts/ThemeContext';
import { SessionState } from '../../types';
import { ProvenanceBanner } from '../ProvenanceBanner';
import { AmbientBackground, PageTransition } from '../motion';

interface AppLayoutProps {
  children: React.ReactNode;
  activeSession?: SessionState;
  isBackendOnline: boolean;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  activeSession,
  isBackendOnline,
}) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [themeMenuOpen, setThemeMenuOpen] = useState<boolean>(false);
  const { theme, setTheme } = useTheme();
  const location = useLocation();

  const navGroups = [
    {
      group: 'Overview',
      items: [{ to: '/', label: 'Research Dashboard', icon: Activity, short: 'Overview' }],
    },
    {
      group: 'Testing Protocol',
      items: [
        { to: '/consent', label: '1. Consent & Setup', icon: FileCheck2, short: 'Consent' },
        { to: '/calibration', label: '2. Spatial Calibration', icon: Crosshair, short: 'Calibration' },
        { to: '/experiment', label: '3. Stimulus Experiment', icon: PlayCircle, short: 'Experiment' },
      ],
    },
    {
      group: 'Scientific Analytics',
      items: [
        { to: '/signal', label: 'Signal Analysis', icon: BarChart3, short: 'Signals' },
        { to: '/models', label: 'Model Benchmark', icon: GitCompare, short: 'Models' },
        { to: '/research', label: 'Research Ablations', icon: FlaskConical, short: 'Research' },
        { to: '/report', label: 'Scientific Report', icon: FileText, short: 'Report' },
      ],
    },
    {
      group: 'System & Protocol',
      items: [{ to: '/settings', label: 'Settings & Citations', icon: Settings, short: 'Settings' }],
    },
  ];

  const themeOptions: { id: ThemeName; name: string; icon: any; colorDot: string }[] = [
    { id: 'midnight', name: 'Midnight Research', icon: Moon, colorDot: 'bg-[#38BDF8]' },
    { id: 'clinical', name: 'Clinical Light', icon: Sun, colorDot: 'bg-[#2563EB]' },
    { id: 'graphite', name: 'Graphite & Emerald', icon: Sparkles, colorDot: 'bg-[#34D399]' },
    { id: 'indigo', name: 'Indigo Intelligence', icon: Palette, colorDot: 'bg-[#A78BFA]' },
  ];

  // Dynamic breadcrumb label
  const currentNav = navGroups
    .flatMap((g) => g.items)
    .find((i) => i.to === location.pathname);

  const breadcrumbTitle = currentNav ? currentNav.label : 'Dashboard';

  return (
    <div className="min-h-screen flex flex-col bg-app text-content-primary relative">
      {/* Ambient 3D scientific background layer */}
      <AmbientBackground />

      {/* 1. Global Provenance Watermark Banner */}
      <div className="no-print relative z-10">
        <ProvenanceBanner mode={activeSession?.cameraPermitted ? 'live' : 'real'} />
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* 2. Desktop Sidebar */}
        <aside
          className={`no-print hidden md:flex flex-col border-r border-border bg-surface transition-all duration-200 shrink-0 z-30 ${
            sidebarCollapsed ? 'w-16' : 'w-64'
          }`}
        >
          {/* Logo & Platform Name */}
          <div className="h-16 px-4 border-b border-border flex items-center justify-between">
            <NavLink to="/" className="flex items-center gap-3 overflow-hidden">
              <div className="w-9 h-9 rounded-lg bg-accent-primary flex items-center justify-center shrink-0 shadow-sm text-white font-bold">
                <Eye className="w-5 h-5 text-white" />
              </div>
              {!sidebarCollapsed && (
                <div className="leading-tight truncate">
                  <span className="text-sm font-bold tracking-tight text-content-primary block">
                    GazeGuard AI
                  </span>
                  <span className="text-[10px] font-mono uppercase text-content-muted block tracking-wider">
                    QPTC Research Platform
                  </span>
                </div>
              )}
            </NavLink>
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-1 rounded-md text-content-muted hover:text-content-primary hover:bg-surface-elevated cursor-pointer transition-colors"
              title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
              aria-label={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {sidebarCollapsed ? (
                <ChevronRight className="w-4 h-4" />
              ) : (
                <ChevronLeft className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Navigation Links Grouped */}
          <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
            {navGroups.map((group) => (
              <div key={group.group} className="space-y-1">
                {!sidebarCollapsed && (
                  <div className="px-3 pb-1 text-[11px] font-mono uppercase tracking-wider text-content-muted font-medium">
                    {group.group}
                  </div>
                )}
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      title={sidebarCollapsed ? item.label : undefined}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-all duration-150 ${
                          isActive
                            ? 'bg-accent-primary/15 text-accent-primary border border-accent-primary/30 font-semibold shadow-xs'
                            : 'text-content-secondary hover:text-content-primary hover:bg-surface-elevated/70 border border-transparent'
                        }`
                      }
                    >
                      <Icon className="w-4 h-4 shrink-0" />
                      {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </nav>

          {/* Sidebar Footer: Participant & Ethics Note */}
          {!sidebarCollapsed && (
            <div className="p-3.5 border-t border-border bg-surface-elevated/40 text-[11px] font-mono text-content-muted">
              <div className="flex items-center gap-1.5 text-accent-primary mb-1">
                <Database className="w-3.5 h-3.5 shrink-0" />
                <span className="font-semibold truncate">Zenodo CIT 120Hz</span>
              </div>
              <p className="text-[10px] text-content-muted truncate">
                38 Cohorts | 819 Physical Trials
              </p>
            </div>
          )}
        </aside>

        {/* 3. Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 md:hidden flex">
            <div
              className="fixed inset-0 bg-black/50 backdrop-blur-xs"
              onClick={() => setMobileMenuOpen(false)}
            />
            <div className="relative w-72 max-w-[80vw] bg-surface border-r border-border flex flex-col z-50">
              <div className="h-16 px-4 border-b border-border flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-accent-primary flex items-center justify-center text-white font-bold">
                    <Eye className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-bold text-content-primary">GazeGuard AI</span>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 rounded-md text-content-muted hover:text-content-primary hover:bg-surface-elevated"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <nav className="flex-1 overflow-y-auto p-4 space-y-6">
                {navGroups.map((group) => (
                  <div key={group.group} className="space-y-1">
                    <div className="px-2 pb-1 text-[11px] font-mono uppercase tracking-wider text-content-muted">
                      {group.group}
                    </div>
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      return (
                        <NavLink
                          key={item.to}
                          to={item.to}
                          onClick={() => setMobileMenuOpen(false)}
                          className={({ isActive }) =>
                            `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${
                              isActive
                                ? 'bg-accent-primary/15 text-accent-primary border border-accent-primary/30'
                                : 'text-content-secondary hover:bg-surface-elevated'
                            }`
                          }
                        >
                          <Icon className="w-4 h-4 shrink-0" />
                          <span>{item.label}</span>
                        </NavLink>
                      );
                    })}
                  </div>
                ))}
              </nav>
            </div>
          </div>
        )}

        {/* 4. Main Body Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          {/* Top Application Bar */}
          <header className="no-print h-16 border-b border-border bg-surface/90 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between gap-4 sticky top-0 z-20">
            {/* Left: Mobile trigger & Breadcrumbs */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="md:hidden p-1.5 rounded-md text-content-secondary hover:text-content-primary hover:bg-surface-elevated cursor-pointer"
                aria-label="Open navigation menu"
              >
                <Menu className="w-5 h-5" />
              </button>

              <div className="hidden sm:flex items-center gap-2 text-xs font-mono text-content-muted">
                <NavLink to="/" className="hover:text-content-primary transition-colors">
                  GazeGuard
                </NavLink>
                <span>/</span>
                <span className="text-content-primary font-medium">{breadcrumbTitle}</span>
              </div>
            </div>

            {/* Right Controls: Session ID, Theme Switcher, API status */}
            <div className="flex items-center gap-2.5 sm:gap-3">
              {/* Active Session Pill */}
              {activeSession?.sessionId ? (
                <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-surface-elevated border border-border text-xs font-mono text-accent-primary">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse" />
                  <span className="font-semibold truncate max-w-[120px] sm:max-w-none">
                    {activeSession.participantPseudonym || activeSession.sessionId}
                  </span>
                </div>
              ) : (
                <span className="hidden lg:inline-block text-xs font-mono text-content-muted">
                  No Active Session
                </span>
              )}

              {/* Theme Dropdown Toggle */}
              <div className="relative">
                <button
                  onClick={() => setThemeMenuOpen(!themeMenuOpen)}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md bg-surface-elevated border border-border text-xs text-content-secondary hover:text-content-primary hover:border-border-strong cursor-pointer transition-colors"
                  title="Select theme palette"
                  aria-label="Select theme palette"
                >
                  <Palette className="w-3.5 h-3.5 text-accent-primary" />
                  <span className="hidden sm:inline capitalize font-medium">{theme}</span>
                </button>

                {themeMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setThemeMenuOpen(false)}
                    />
                    <div className="absolute right-0 mt-1.5 w-52 rounded-lg bg-surface border border-border shadow-dropdown p-1.5 z-50">
                      <div className="px-2.5 py-1.5 text-[11px] font-mono uppercase tracking-wider text-content-muted border-b border-border-subtle mb-1">
                        Theme Palette
                      </div>
                      {themeOptions.map((opt) => (
                        <button
                          key={opt.id}
                          onClick={() => {
                            setTheme(opt.id);
                            setThemeMenuOpen(false);
                          }}
                          className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors cursor-pointer ${
                            theme === opt.id
                              ? 'bg-accent-primary/10 text-accent-primary font-medium'
                              : 'text-content-secondary hover:text-content-primary hover:bg-surface-elevated'
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <span className={`w-2.5 h-2.5 rounded-full ${opt.colorDot}`} />
                            <span>{opt.name}</span>
                          </div>
                          {theme === opt.id && <Check className="w-3.5 h-3.5 text-accent-primary" />}
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </div>

              {/* API Backend Health Status */}
              <div
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono border ${
                  isBackendOnline
                    ? 'bg-emerald-500/10 text-status-success border-emerald-500/20'
                    : 'bg-rose-500/10 text-status-error border-rose-500/20'
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isBackendOnline ? 'bg-status-success' : 'bg-status-error'
                  }`}
                />
                <span className="hidden sm:inline font-medium">
                  {isBackendOnline ? 'API 8000' : 'OFFLINE'}
                </span>
              </div>
            </div>
          </header>

          {/* Content Viewport with 3D Depth & Route Transition */}
          <main className="relative z-10 flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            <PageTransition key={location.pathname}>
              {children}
            </PageTransition>
          </main>

          {/* Global Research Disclaimer Footer */}
          <footer className="no-print relative z-10 border-t border-border bg-surface/90 backdrop-blur-md py-5 text-xs text-content-muted">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left font-mono text-[11px]">
              <div>
                <span className="font-semibold text-content-primary">
                  GazeGuard AI — Quality-Aware Personalized Temporal Calibration (QPTC)
                </span>
                <p className="text-content-muted text-[10px] mt-0.5">
                  Research Prototype | Forensic Non-Accusatory Protocol | Zero Raw Video Retention
                </p>
              </div>
              <div className="text-content-muted">
                Zenodo DOI: 10.5281/zenodo.18525952 | CC-BY-4.0 | Tobii Pro 120Hz
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
};
