import React, { useState, useEffect } from 'react';
import {
  Settings,
  Palette,
  Clock,
  Sliders,
  Database,
  BookOpen,
  Copy,
  Check,
  ExternalLink,
  Save,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { fetchSettings, updateSettings } from '../services/api';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
  Button,
} from '../components/ui';
import { TiltCard } from '../components/motion';

export const SettingsPage: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [copiedBib, setCopiedBib] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Original saved values
  const [savedSettings, setSavedSettings] = useState({
    rawPath: './data/raw',
    minQuality: 0.60,
    earlyWinMs: 500,
    stimDurMs: 2000,
  });

  // Current form values
  const [rawPath, setRawPath] = useState<string>('./data/raw');
  const [minQuality, setMinQuality] = useState<number>(0.60);
  const [earlyWinMs, setEarlyWinMs] = useState<number>(500);
  const [stimDurMs, setStimDurMs] = useState<number>(2000);

  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [saveErrorMsg, setSaveErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const s = await fetchSettings();
        if (s) {
          const loaded = {
            rawPath: s.raw_data_dir || './data/raw',
            minQuality: s.tracking?.min_valid_sample_ratio ?? 0.60,
            earlyWinMs: s.tracking?.early_window_ms ?? 500,
            stimDurMs: 2000,
          };
          setSavedSettings(loaded);
          setRawPath(loaded.rawPath);
          setMinQuality(loaded.minQuality);
          setEarlyWinMs(loaded.earlyWinMs);
          setStimDurMs(loaded.stimDurMs);
        }
      } catch (e) {
        // use default state
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const isDirty =
    rawPath !== savedSettings.rawPath ||
    minQuality !== savedSettings.minQuality ||
    earlyWinMs !== savedSettings.earlyWinMs ||
    stimDurMs !== savedSettings.stimDurMs;

  const handleResetForm = () => {
    setRawPath(savedSettings.rawPath);
    setMinQuality(savedSettings.minQuality);
    setEarlyWinMs(savedSettings.earlyWinMs);
    setStimDurMs(savedSettings.stimDurMs);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccessMsg(null);
    setSaveErrorMsg(null);

    const payload = {
      raw_data_dir: rawPath,
      tracking: {
        min_valid_sample_ratio: minQuality,
        early_window_ms: earlyWinMs,
        stimulus_duration_ms: stimDurMs,
      },
    };

    try {
      await updateSettings(payload);
      setSavedSettings({
        rawPath,
        minQuality,
        earlyWinMs,
        stimDurMs,
      });
      setSaveSuccessMsg('Configuration successfully persisted to backend runtime environment.');
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch (err: any) {
      setSaveErrorMsg(err.message || 'Failed to persist settings to backend');
    } finally {
      setSaving(false);
    }
  };

  const bibtex = `@dataset{celniak2026eyetracking,
  author       = {Celniak, Weronika and Słapczyńska, Dominika and Jarszak, Beata and Augustyniak, Piotr},
  title        = {Eye tracking as a Tool for deception detection with CIT},
  month        = feb,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18525952},
  url          = {https://zenodo.org/records/18525952}
}`;

  const handleCopyBib = () => {
    navigator.clipboard.writeText(bibtex);
    setCopiedBib(true);
    setTimeout(() => setCopiedBib(false), 2000);
  };

  const themesList = [
    {
      id: 'midnight' as const,
      name: 'Midnight Research',
      badge: 'Default Enterprise',
      bgHex: '#0B1220',
      surfaceHex: '#111C2E',
      accentHex: '#38BDF8',
      desc: 'Balanced low-glare dark palette tailored for high-density analytics.',
    },
    {
      id: 'clinical' as const,
      name: 'Clinical Light',
      badge: 'Medical / Academic',
      bgHex: '#F4F7FB',
      surfaceHex: '#FFFFFF',
      accentHex: '#2563EB',
      desc: 'High-contrast light interface optimized for clinical review and documentation.',
    },
    {
      id: 'graphite' as const,
      name: 'Graphite & Emerald',
      badge: 'High Contrast',
      bgHex: '#111315',
      surfaceHex: '#1A1F21',
      accentHex: '#34D399',
      desc: 'Minimalist carbon-dark interface accented with emerald signals.',
    },
    {
      id: 'indigo' as const,
      name: 'Indigo Intelligence',
      badge: 'AI Research',
      bgHex: '#0F1020',
      surfaceHex: '#1B1B35',
      accentHex: '#A78BFA',
      desc: 'Deep violet palette designed for machine learning visualizers.',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="accent">Configuration & Provenance</Badge>
            {isDirty && <Badge variant="warning">Unsaved Changes Pending</Badge>}
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content flex items-center gap-2.5">
            <Settings className="w-7 h-7 text-accent-primary" />
            <span>System Settings & Dataset Provenance</span>
          </h1>
          <p className="text-sm text-content-secondary mt-1">
            Configure appearance palettes, experimental timings, quality thresholds, and inspect verified scholarly citations.
          </p>
        </div>
      </div>

      {/* Group 1: Appearance & Theme Palettes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Palette className="w-4 h-4 text-accent-primary" />
              <CardTitle className="text-base">Appearance & Interface Theme</CardTitle>
            </div>
            <span className="text-xs font-mono text-content-muted">
              Active: {themesList.find((t) => t.id === theme)?.name}
            </span>
          </div>
          <CardDescription>
            Select a centralized design system palette. Theme switching dynamically re-indexes CSS tokens, charts, and surfaces.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {themesList.map((t) => {
              const isSelected = theme === t.id;
              return (
                <TiltCard key={t.id} maxTilt={3} scale={1.015} className="h-full">
                  <button
                    type="button"
                    onClick={() => setTheme(t.id)}
                    className={`w-full h-full p-4 rounded-xl text-left border transition-all relative ${
                      isSelected
                        ? 'border-accent-primary bg-surface-elevated shadow-md ring-2 ring-accent-primary'
                        : 'border-border bg-surface hover:bg-surface-elevated hover:border-border-focus'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-accent-primary font-semibold">
                        {t.badge}
                      </span>
                      {isSelected && (
                        <CheckCircle2 className="w-4 h-4 text-accent-primary" />
                      )}
                    </div>

                    <div className="text-sm font-bold text-content">{t.name}</div>
                    <p className="text-[11px] text-content-muted mt-1 leading-snug">{t.desc}</p>

                    {/* Palette Swatch Preview */}
                    <div className="flex items-center gap-1.5 mt-3 pt-3 border-t border-border">
                      <span
                        className="w-5 h-5 rounded-md border border-border shadow-xs"
                        style={{ backgroundColor: t.bgHex }}
                        title={`Background ${t.bgHex}`}
                      />
                      <span
                        className="w-5 h-5 rounded-md border border-border shadow-xs"
                        style={{ backgroundColor: t.surfaceHex }}
                        title={`Surface ${t.surfaceHex}`}
                      />
                      <span
                        className="w-5 h-5 rounded-md border border-border shadow-xs"
                        style={{ backgroundColor: t.accentHex }}
                        title={`Accent ${t.accentHex}`}
                      />
                    </div>
                  </button>
                </TiltCard>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Main Settings Form */}
      <form onSubmit={handleSave} className="space-y-6">
        {/* Group 2: Experimental Timing & Quality Parameters */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-accent-primary" />
              <CardTitle className="text-base">Temporal Windowing & Quality Thresholds</CardTitle>
            </div>
            <CardDescription>
              Configure cognitive fixation hypothesis cutoffs and quality abstention thresholds.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1.5">
                <label className="block text-xs font-mono font-semibold text-content uppercase tracking-wider">
                  Early Window Cutoff (ms):
                </label>
                <input
                  type="number"
                  min="200"
                  max="1000"
                  step="50"
                  value={earlyWinMs}
                  onChange={(e) => setEarlyWinMs(Number(e.target.value))}
                  className="w-full bg-app border border-border rounded-lg px-3 py-2 text-sm font-mono text-content focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                />
                <span className="text-[11px] text-content-muted block">
                  Default: 500 ms (orienting vs visual search).
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-mono font-semibold text-content uppercase tracking-wider">
                  Stimulus Duration (ms):
                </label>
                <input
                  type="number"
                  min="1000"
                  max="5000"
                  step="250"
                  value={stimDurMs}
                  onChange={(e) => setStimDurMs(Number(e.target.value))}
                  className="w-full bg-app border border-border rounded-lg px-3 py-2 text-sm font-mono text-content focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                />
                <span className="text-[11px] text-content-muted block">
                  Default: 2000 ms (standard CIT display interval).
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-mono font-semibold text-content uppercase tracking-wider">
                  Min Valid Sample Ratio:
                </label>
                <input
                  type="number"
                  step="0.05"
                  min="0.30"
                  max="0.95"
                  value={minQuality}
                  onChange={(e) => setMinQuality(Number(e.target.value))}
                  className="w-full bg-app border border-border rounded-lg px-3 py-2 text-sm font-mono text-content focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
                />
                <span className="text-[11px] text-content-muted block">
                  Abstains if valid tracking ratio is below threshold.
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Group 3: Dataset Storage Paths & Governance */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-status-success" />
              <CardTitle className="text-base">Dataset Storage & Privacy Governance</CardTitle>
            </div>
            <CardDescription>
              Local repository directories and participant privacy policies.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-mono font-semibold text-content uppercase tracking-wider">
                Raw Primary Dataset Directory:
              </label>
              <input
                type="text"
                value={rawPath}
                onChange={(e) => setRawPath(e.target.value)}
                className="w-full bg-app border border-border rounded-lg px-3 py-2 text-sm font-mono text-accent-primary focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary transition-colors"
              />
              <span className="text-[11px] text-content-muted block">
                Primary ingestion directory for Zenodo 18525952 recordings and SQLite trial storage.
              </span>
            </div>

            <div className="p-3.5 rounded-lg bg-surface-elevated border border-border text-xs space-y-2">
              <div className="flex items-center justify-between font-mono">
                <span className="text-content-secondary">Raw Webcam Video Frame Storage:</span>
                <span className="text-status-success font-bold">DISABLED (Privacy First)</span>
              </div>
              <div className="flex items-center justify-between font-mono">
                <span className="text-content-secondary">Participant Pseudonymization:</span>
                <span className="text-status-success font-bold">ACTIVE (Zero Identifiers)</span>
              </div>
              <div className="flex items-center justify-between font-mono">
                <span className="text-content-secondary">Data Retention Policy:</span>
                <span className="text-content font-bold">30 Days (Local SQLite Repository)</span>
              </div>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
            <div className="text-xs">
              {saveSuccessMsg && (
                <span className="text-status-success font-mono flex items-center gap-1.5">
                  <Check className="w-4 h-4" /> {saveSuccessMsg}
                </span>
              )}
              {saveErrorMsg && (
                <span className="text-status-error font-mono flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4" /> {saveErrorMsg}
                </span>
              )}
              {!saveSuccessMsg && !saveErrorMsg && (
                <span className="text-content-muted font-mono">
                  {isDirty ? 'Unsaved parameter modifications detected.' : 'Current configuration matches saved backend state.'}
                </span>
              )}
            </div>

            <div className="flex items-center gap-3 w-full sm:w-auto">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleResetForm}
                disabled={!isDirty || saving}
                icon={<RotateCcw className="w-3.5 h-3.5" />}
              >
                Reset
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="sm"
                disabled={!isDirty || saving}
                icon={<Save className="w-3.5 h-3.5" />}
              >
                {saving ? 'Persisting Configuration...' : 'Save Configuration'}
              </Button>
            </div>
          </CardFooter>
        </Card>
      </form>

      {/* Group 4: Dataset Provenance & Scholarly Citation */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-accent-primary" />
              <CardTitle className="text-base">Scholarly Dataset Attribution & Provenance</CardTitle>
            </div>
            <a
              href="https://zenodo.org/records/18525952"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-accent-primary hover:underline flex items-center gap-1 font-mono"
            >
              <span>Zenodo Record DOI 10.5281/zenodo.18525952</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
          <CardDescription>
            Academic citation details and hardware apparatus specification for benchmark validation.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="p-4 rounded-xl bg-surface-elevated border border-border text-xs leading-relaxed space-y-2 text-content-secondary">
            <p>
              <strong className="text-content">Title:</strong> Eye tracking as a Tool for deception detection with CIT
            </p>
            <p>
              <strong className="text-content">Authors:</strong> Weronika Celniak, Dominika Słapczyńska, Beata Jarszak, Piotr Augustyniak
            </p>
            <p>
              <strong className="text-content">Institutions:</strong> AGH University of Krakow; Forensic Laboratory of the Police Headquarters in Katowice
            </p>
            <p>
              <strong className="text-content">DOI:</strong> 10.5281/zenodo.18525952 | <strong className="text-content">License:</strong> Creative Commons Attribution 4.0 International (CC-BY-4.0)
            </p>
            <p>
              <strong className="text-content">Apparatus:</strong> Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz) on 27-inch Full HD Monitor.
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs font-mono text-content-muted">
              <span>BibTeX Scholarly Citation:</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={handleCopyBib}
                icon={copiedBib ? <Check className="w-3.5 h-3.5 text-status-success" /> : <Copy className="w-3.5 h-3.5" />}
              >
                {copiedBib ? 'Copied to Clipboard' : 'Copy BibTeX'}
              </Button>
            </div>
            <pre className="p-3.5 rounded-xl bg-app border border-border text-[11px] font-mono text-content-secondary overflow-x-auto">
              {bibtex}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
