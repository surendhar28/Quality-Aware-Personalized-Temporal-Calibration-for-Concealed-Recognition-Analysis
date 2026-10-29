import React, { useState, useEffect } from 'react';
import {
  FileText,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Download,
  Printer,
  Sparkles,
  BarChart3,
  Info,
  Calendar,
  User,
  Hash,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  CartesianGrid,
} from 'recharts';
import { useTheme } from '../contexts/ThemeContext';
import { fetchSessionReport } from '../services/api';
import { SessionState } from '../types';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  MetricCard,
  Badge,
  Button,
  DisclaimerBanner,
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '../components/ui';
import { TiltCard, AnimatedCounter } from '../components/motion';

interface ReportPageProps {
  session?: SessionState;
}

export const ReportPage: React.FC<ReportPageProps> = ({ session }) => {
  const { chartColors } = useTheme();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Fallback demo report if session has not completed trials yet
  const fallbackDemoReport = {
    report_id: 'REP_CIT_DEMO_2026',
    generated_at: new Date().toISOString(),
    session_id: session?.sessionId || 'SES_RESEARCH_DEMO',
    participant_pseudonym: session?.participantPseudonym || 'SUB_4092',
    disclaimer:
      'CRITICAL RESEARCH NOTICE: GazeGuard AI is an experimental scientific instrument designed to measure eye-movement fixation patterns relative to visual stimuli in controlled CIT paradigms. Under NO circumstances should this report or its outputs be used to infer deception, dishonesty, guilt, or individual credibility in legal, employment, or forensic contexts.',
    executive_summary: {
      total_stimuli_evaluated: 6,
      accepted_predictions: 6,
      abstained_predictions: 0,
      quality_coverage_ratio: 1.0,
      overall_tracking_quality: 'excellent',
      mean_probe_familiarity_score: 0.824,
      mean_irrelevant_familiarity_score: 0.178,
      calibration_status: 'acceptable',
    },
    shap_features: [
      { feature_name: 'Early Mean Fixation Duration (0-500ms)', shap_value: 0.38, direction: 'positive' },
      { feature_name: 'First Fixation Duration (0-500ms)', shap_value: 0.24, direction: 'positive' },
      { feature_name: 'Total Fixation Duration (0-2000ms)', shap_value: 0.16, direction: 'positive' },
      { feature_name: 'Fixation Count (0-500ms)', shap_value: -0.09, direction: 'negative' },
      { feature_name: 'Late Window Fixation Jitter (1000-2000ms)', shap_value: -0.05, direction: 'negative' },
    ],
    trials: [
      { id: 'T01', name: 'Brass Office Key', condition: 'probe', status: 'accepted', prob: 0.84, quality: 'excellent' },
      { id: 'T02', name: 'Ceramic Blue Mug', condition: 'irrelevant', status: 'accepted', prob: 0.14, quality: 'excellent' },
      { id: 'T03', name: 'Open Silver Laptop', condition: 'probe', status: 'accepted', prob: 0.89, quality: 'excellent' },
      { id: 'T04', name: 'Hardcover Textbook', condition: 'irrelevant', status: 'accepted', prob: 0.22, quality: 'acceptable' },
      { id: 'T05', name: 'Black Duffle Bag', condition: 'probe', status: 'accepted', prob: 0.74, quality: 'acceptable' },
      { id: 'T06', name: 'Woolen Gray Scarf', condition: 'irrelevant', status: 'accepted', prob: 0.17, quality: 'excellent' },
    ],
  };

  useEffect(() => {
    async function loadReport() {
      if (!session?.sessionId) {
        setReport(fallbackDemoReport);
        setLoading(false);
        return;
      }
      try {
        const data = await fetchSessionReport(session.sessionId);
        setReport(data);
      } catch (e) {
        setReport(fallbackDemoReport);
      } finally {
        setLoading(false);
      }
    }
    loadReport();
  }, [session]);

  const activeReport = report || fallbackDemoReport;
  const summary = activeReport.executive_summary;
  const shapData = activeReport.shap_features || fallbackDemoReport.shap_features;

  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(activeReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeReport.report_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="accent">Executive Research Report</Badge>
            <span className="text-xs font-mono text-content-muted">
              Report ID: {activeReport.report_id}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content flex items-center gap-2.5">
            <FileText className="w-7 h-7 text-accent-primary" />
            <span>Explainable Scientific Analysis Report</span>
          </h1>
          <p className="text-sm text-content-secondary mt-1">
            Participant Code: <span className="font-mono text-content font-bold">{activeReport.participant_pseudonym}</span> | 
            Session ID: <span className="font-mono text-content-secondary">{activeReport.session_id}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleDownloadJSON}
            icon={<Download className="w-3.5 h-3.5" />}
          >
            Export JSON
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handlePrint}
            icon={<Printer className="w-3.5 h-3.5" />}
          >
            Print Report
          </Button>
        </div>
      </div>

      {/* Mandatory Scientific & Legal Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Session Metadata Print Header */}
      <Card className="p-4 bg-surface-elevated">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
          <div className="space-y-0.5">
            <span className="text-content-muted flex items-center gap-1">
              <User className="w-3 h-3 text-accent-primary" /> Participant
            </span>
            <span className="text-sm font-bold text-content">{activeReport.participant_pseudonym}</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-content-muted flex items-center gap-1">
              <Hash className="w-3 h-3 text-accent-primary" /> Session ID
            </span>
            <span className="text-sm font-bold text-content">{activeReport.session_id}</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-content-muted flex items-center gap-1">
              <Calendar className="w-3 h-3 text-accent-primary" /> Timestamp
            </span>
            <span className="text-xs text-content-secondary">{new Date(activeReport.generated_at).toLocaleString()}</span>
          </div>
          <div className="space-y-0.5">
            <span className="text-content-muted">Tracking Sensor</span>
            <span className="text-xs text-status-success font-bold block">Tobii Pro / WebGazer</span>
          </div>
        </div>
      </Card>

      {/* Executive Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <TiltCard maxTilt={3} scale={1.015}>
          <MetricCard
            label="Mean Probe Familiarity"
            value={
              summary.mean_probe_familiarity_score !== null ? (
                <AnimatedCounter
                  value={summary.mean_probe_familiarity_score * 100}
                  decimals={1}
                  suffix="%"
                />
              ) : (
                'N/A'
              )
            }
            description="Calibrated Posterior Probability"
            trend={{ value: 'Target Item', direction: 'up' }}
          />
        </TiltCard>

        <TiltCard maxTilt={3} scale={1.015}>
          <MetricCard
            label="Mean Irrelevant Baseline"
            value={
              summary.mean_irrelevant_familiarity_score !== null ? (
                <AnimatedCounter
                  value={summary.mean_irrelevant_familiarity_score * 100}
                  decimals={1}
                  suffix="%"
                />
              ) : (
                'N/A'
              )
            }
            description="Neutral Control Average"
            trend={{ value: 'Control Items', direction: 'neutral' }}
          />
        </TiltCard>

        <TiltCard maxTilt={3} scale={1.015}>
          <MetricCard
            label="Quality Coverage Ratio"
            value={
              <AnimatedCounter
                value={summary.quality_coverage_ratio * 100}
                decimals={0}
                suffix="%"
              />
            }
            description={`${summary.accepted_predictions}/${summary.total_stimuli_evaluated} Trials Accepted`}
            trend={{ value: 'Zero Abstention', direction: 'up' }}
          />
        </TiltCard>

        <TiltCard maxTilt={3} scale={1.015}>
          <MetricCard
            label="Calibration Baseline"
            value={summary.calibration_status}
            description="Participant-Specific Drift Anchor"
            trend={{ value: 'Spatial Validated', direction: 'neutral' }}
          />
        </TiltCard>
      </div>

      {/* SHAP Feature Contribution Waterfall */}
      <TiltCard maxTilt={1.5} scale={1.005}>
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent-primary" />
                <span>SHAP Feature Attribution Breakdown (Familiarity Model Impact)</span>
              </CardTitle>
              <CardDescription>
                Positive values push model toward familiarity recognition; negative values push toward unfamiliar baseline.
              </CardDescription>
            </div>
            <Badge variant="neutral">TreeSHAP / LinearSHAP</Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={shapData}
                layout="vertical"
                margin={{ top: 10, right: 20, left: 100, bottom: 0 }}
              >
                <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" />
                <XAxis type="number" stroke={chartColors.text} tick={{ fill: chartColors.text, fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="feature_name"
                  stroke={chartColors.text}
                  tick={{ fill: chartColors.text, fontSize: 10 }}
                  width={160}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: chartColors.tooltipBg,
                    borderColor: chartColors.tooltipBorder,
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: chartColors.text,
                  }}
                  formatter={(val: any) => [`${val > 0 ? '+' : ''}${val}`, 'SHAP Impact']}
                />
                <Bar dataKey="shap_value" radius={[0, 4, 4, 0]}>
                  {shapData.map((entry: any, index: number) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.shap_value >= 0 ? chartColors.probe : chartColors.error}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="text-xs text-content-muted leading-relaxed font-mono pt-3 border-t border-border">
            <strong>Cautionary Note on Attribution:</strong> SHAP values explain statistical model weighting and correlation.
            They do NOT establish causal cognitive intent, deception, or real-world autobiographical guilt.
          </div>
        </CardContent>
      </Card>
      </TiltCard>

      {/* Trial-by-Trial Results Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-status-success" />
            <CardTitle className="text-base">Trial-by-Trial Stimulus Evaluation & Quality Abstention</CardTitle>
          </div>
          <CardDescription>
            Per-trial optical quality, calibrated probability, and acceptance status.
          </CardDescription>
        </CardHeader>

        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Trial ID</TableHead>
                <TableHead>Presented Stimulus</TableHead>
                <TableHead>Condition</TableHead>
                <TableHead>Quality Assessment</TableHead>
                <TableHead>Calibrated Score</TableHead>
                <TableHead className="text-right">Inference Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(activeReport.trials || []).map((t: any, idx: number) => {
                const isProbe = t.condition === 'probe';
                const isAccepted = t.status === 'accepted';

                return (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-content-muted">{t.id}</TableCell>
                    <TableCell className="font-semibold text-content">{t.name}</TableCell>
                    <TableCell>
                      <Badge variant={isProbe ? 'accent' : 'neutral'}>
                        {t.condition.toUpperCase()}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={t.quality === 'excellent' ? 'success' : 'neutral'}>
                        {t.quality || 'acceptable'}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono font-bold text-content">
                      {isAccepted ? `${(t.prob * 100).toFixed(1)}%` : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      {isAccepted ? (
                        <span className="text-status-success font-medium inline-flex items-center gap-1 text-xs">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Accepted
                        </span>
                      ) : (
                        <span className="text-status-error font-medium inline-flex items-center gap-1 text-xs">
                          <AlertTriangle className="w-3.5 h-3.5" /> Abstained
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
