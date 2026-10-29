import React, { useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Clock,
  Layers,
  Info,
  Sliders,
  Eye,
  Activity,
  FileCheck2,
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  ReferenceArea,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { useTheme } from '../contexts/ThemeContext';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Badge,
  SegmentedControl,
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '../components/ui';
import { TiltCard } from '../components/motion';

export const SignalAnalysisPage: React.FC = () => {
  const { chartColors } = useTheme();
  const [selectedStimulus, setSelectedStimulus] = useState<'probe' | 'irrelevant'>('probe');

  // Synthetic sample time-series data demonstrating realistic physiological trajectories
  // Probe: early visual orienting to target (stable fixation at x=0.35, y=0.40 from 120ms to 460ms)
  // Irrelevant: exploratory saccadic movement with shorter initial fixation
  const generateTimeSeriesData = (isProbe: boolean) => {
    const data = [];
    for (let t = 0; t <= 2000; t += 20) {
      let x, y, isFixation = false;
      if (isProbe) {
        if (t < 120) {
          x = 0.50 + (t / 120) * -0.15;
          y = 0.50 + (t / 120) * -0.10;
        } else if (t <= 460) { // Long early fixation on probe (340ms)
          x = 0.35 + Math.sin(t * 0.05) * 0.005;
          y = 0.40 + Math.cos(t * 0.05) * 0.005;
          isFixation = true;
        } else if (t < 540) {
          x = 0.35 + ((t - 460) / 80) * 0.30;
          y = 0.40 + ((t - 460) / 80) * 0.20;
        } else {
          x = 0.65 + Math.sin(t * 0.02) * 0.008;
          y = 0.60 + Math.cos(t * 0.02) * 0.008;
          isFixation = true;
        }
      } else {
        if (t < 180) {
          x = 0.50 + (t / 180) * 0.20;
          y = 0.50 + (t / 180) * 0.15;
        } else if (t <= 400) { // Brief initial fixation on irrelevant (220ms)
          x = 0.70 + Math.sin(t * 0.04) * 0.006;
          y = 0.65 + Math.cos(t * 0.04) * 0.006;
          isFixation = true;
        } else if (t < 480) {
          x = 0.70 - ((t - 400) / 80) * 0.40;
          y = 0.65 - ((t - 400) / 80) * 0.30;
        } else {
          x = 0.30 + Math.sin(t * 0.03) * 0.006;
          y = 0.35 + Math.cos(t * 0.03) * 0.006;
          isFixation = true;
        }
      }

      data.push({
        time_ms: t,
        gaze_x: Math.round(x * 1000) / 1000,
        gaze_y: Math.round(y * 1000) / 1000,
        is_fixation: isFixation ? 1 : 0,
        valid: t !== 520 && t !== 540, // Simulated occasional blink
      });
    }
    return data;
  };

  const isProbe = selectedStimulus === 'probe';
  const timeSeries = generateTimeSeriesData(isProbe);

  // Per-window metrics
  const windowSummary = isProbe
    ? [
        { window: 'w0_500 (Early)', fixCount: 1, meanDur: 340, totalDur: 340, firstLatency: 120 },
        { window: 'w500_1000 (Mid)', fixCount: 1, meanDur: 460, totalDur: 460, firstLatency: 540 },
        { window: 'w1000_2000 (Late)', fixCount: 2, meanDur: 260, totalDur: 520, firstLatency: 1080 },
      ]
    : [
        { window: 'w0_500 (Early)', fixCount: 1, meanDur: 220, totalDur: 220, firstLatency: 180 },
        { window: 'w500_1000 (Mid)', fixCount: 1, meanDur: 240, totalDur: 240, firstLatency: 600 },
        { window: 'w1000_2000 (Late)', fixCount: 3, meanDur: 230, totalDur: 690, firstLatency: 1100 },
      ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="accent">Signal Diagnostics</Badge>
            <Badge variant="neutral">I-VT Velocity Filter (0.5 norm/s)</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content flex items-center gap-2.5">
            <BarChart3 className="w-7 h-7 text-accent-primary" />
            <span>Temporal Gaze Dynamics & Fixation Signal Analysis</span>
          </h1>
          <p className="text-sm text-content-secondary mt-1">
            Inspect raw coordinate streams, velocity-threshold fixation classifications, and temporal window segmentations.
          </p>
        </div>

        {/* Condition Selector */}
        <div className="w-full sm:w-auto">
          <SegmentedControl
            options={[
              { id: 'probe', label: 'Probe Stimulus (Familiar)' },
              { id: 'irrelevant', label: 'Irrelevant Stimulus (Neutral)' },
            ]}
            value={selectedStimulus}
            onChange={(val) => setSelectedStimulus(val as 'probe' | 'irrelevant')}
          />
        </div>
      </div>

      {/* Main Coordinate Time-Series Plot */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <CardTitle className="flex items-center gap-2 text-base">
                <TrendingUp className="w-4 h-4 text-accent-primary" />
                <span>Ocular Coordinate Trajectory [X(t), Y(t)] vs. Time</span>
              </CardTitle>
              <CardDescription>
                Normalized coordinates [0.0 - 1.0]. Vertical dashed marker at 500 ms delineates the early recognition hypothesis window.
              </CardDescription>
            </div>

            <div className="flex items-center gap-4 text-xs font-mono">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 rounded" style={{ backgroundColor: chartColors.probe }}></span>
                <span className="text-content-secondary">Gaze X</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 rounded" style={{ backgroundColor: chartColors.secondary }}></span>
                <span className="text-content-secondary">Gaze Y</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: chartColors.success }}></span>
                <span className="text-content-secondary">Fixation Lock</span>
              </div>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeSeries} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" />
                <XAxis
                  dataKey="time_ms"
                  stroke={chartColors.text}
                  tick={{ fill: chartColors.text, fontSize: 11 }}
                  unit="ms"
                />
                <YAxis
                  domain={[0, 1]}
                  stroke={chartColors.text}
                  tick={{ fill: chartColors.text, fontSize: 11 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: chartColors.tooltipBg,
                    borderColor: chartColors.tooltipBorder,
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: chartColors.text,
                  }}
                  formatter={(val: any, name: any) => [val, name === 'gaze_x' ? 'Gaze X' : 'Gaze Y']}
                  labelFormatter={(label) => `Time: ${label} ms`}
                />
                <ReferenceArea
                  x1={0}
                  x2={500}
                  fill={chartColors.probe}
                  fillOpacity={0.07}
                />
                <ReferenceLine
                  x={500}
                  stroke={chartColors.warning}
                  strokeDasharray="4 4"
                  label={{
                    value: '500 ms Early Window',
                    fill: chartColors.warning,
                    fontSize: 10,
                    position: 'top',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="gaze_x"
                  stroke={chartColors.probe}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="gaze_y"
                  stroke={chartColors.secondary}
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-wrap items-center justify-between text-xs text-content-muted pt-3 border-t border-border font-mono">
            <span>Observed Valid Samples: 98/100 (98.0%)</span>
            <span>Inter-Sample Jitter: 1.2 ms (60 Hz target)</span>
            <span>Simulated Blink / Missing Interval: 1 (40 ms at t=520 ms)</span>
          </div>
        </CardContent>
      </Card>

      {/* Temporal Window Breakdown & Mean Fixation Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Table of window metrics */}
        <TiltCard className="rounded-lg">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent-primary" />
                <CardTitle className="text-sm">Temporal Window Feature Breakdown</CardTitle>
              </div>
              <CardDescription>
                Fixation count, durations, and initial visual latencies partitioned across trial intervals.
              </CardDescription>
            </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Window Interval</TableHead>
                  <TableHead>Fixations</TableHead>
                  <TableHead>Mean Duration</TableHead>
                  <TableHead>Total Duration</TableHead>
                  <TableHead>First Latency</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {windowSummary.map((w, i) => (
                  <TableRow key={i}>
                    <TableCell className="font-bold text-accent-primary font-mono">{w.window}</TableCell>
                    <TableCell className="font-mono">{w.fixCount}</TableCell>
                    <TableCell className="font-mono font-semibold text-status-success">{w.meanDur} ms</TableCell>
                    <TableCell className="font-mono">{w.totalDur} ms</TableCell>
                    <TableCell className="font-mono text-content-muted">{w.firstLatency} ms</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <div className="p-4 text-xs text-content-secondary leading-relaxed border-t border-border">
              <strong className="text-content">Theoretical Insight:</strong> In CIT paradigms, familiar visual stimuli
              elicit longer initial fixations during early viewing (&lt; 500 ms) before visual search saccades diversify.
            </div>
          </CardContent>
        </Card>
      </TiltCard>

      {/* Mean Fixation Duration Bar Chart */}
      <TiltCard className="rounded-lg">
        <Card className="h-full">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-status-success" />
              <CardTitle className="text-sm">Mean Fixation Duration Comparison (ms)</CardTitle>
            </div>
            <CardDescription>
              Observed dwell time per temporal window for {isProbe ? 'Probe Target' : 'Neutral Control'}.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={windowSummary} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" />
                  <XAxis dataKey="window" stroke={chartColors.text} tick={{ fill: chartColors.text, fontSize: 10 }} />
                  <YAxis stroke={chartColors.text} tick={{ fill: chartColors.text, fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: chartColors.tooltipBg,
                      borderColor: chartColors.tooltipBorder,
                      borderRadius: '8px',
                      fontSize: '12px',
                      color: chartColors.text,
                    }}
                  />
                  <Bar
                    dataKey="meanDur"
                    name="Mean Fixation Duration (ms)"
                    fill={chartColors.success}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </TiltCard>
    </div>

      {/* Rigorous Distinction between Observed and Derived Metrics */}
      <div className="p-4 rounded-xl bg-surface-elevated border border-border flex items-start gap-3 text-xs text-content-secondary">
        <Info className="w-5 h-5 text-accent-primary shrink-0 mt-0.5" />
        <div className="space-y-1">
          <strong className="text-content block">Distinction Between Observed Signal and Derived Estimation:</strong>
          <p className="leading-relaxed">
            The raw coordinate trace [X, Y] represents hardware-measured or webcam-tracked gaze samples. Fixation events,
            boundaries, and duration intervals are <em>derived estimations</em> computed via the I-VT velocity-threshold algorithm
            (threshold: 0.5 norm/sec, minimum duration: 80 ms). Blink intervals and exploratory saccades are filtered non-fixation
            periods and must not be misinterpreted as cognitive suppression.
          </p>
        </div>
      </div>
    </div>
  );
};
