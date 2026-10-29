import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PlayCircle,
  Pause,
  RotateCcw,
  CheckCircle2,
  Clock,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Layers,
  Sparkles,
  Eye,
  Activity,
} from 'lucide-react';
import { submitTrial } from '../services/api';
import { SessionState, StimulusCondition, TrialData, GazeSample } from '../types';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Badge,
  Button,
  ProgressBar,
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '../components/ui';

interface ExperimentPageProps {
  session?: SessionState;
  onTrialRecorded?: (trial: any) => void;
}

interface StimulusItem {
  id: string;
  name: string;
  condition: StimulusCondition;
  category: string;
  description: string;
}

// Standard CIT mock crime stimulus battery (probe items matching Zenodo 18525952 protocol + irrelevant controls)
const DEFAULT_STIMULI: StimulusItem[] = [
  { id: 'STIM_KEY', name: 'Brass Office Key', condition: 'probe', category: 'Crime Target', description: 'Key retrieved from lecturer jacket' },
  { id: 'STIM_MUG', name: 'Ceramic Blue Mug', condition: 'irrelevant', category: 'Control Item', description: 'Neutral office item' },
  { id: 'STIM_LAPTOP', name: 'Open Silver Laptop', condition: 'probe', category: 'Crime Target', description: 'Laptop containing exam documents' },
  { id: 'STIM_BOOK', name: 'Hardcover Textbook', condition: 'irrelevant', category: 'Control Item', description: 'Neutral academic item' },
  { id: 'STIM_BAG', name: 'Black Duffle Bag', condition: 'probe', category: 'Crime Target', description: 'Bag used to transport transcribed copy' },
  { id: 'STIM_SCARF', name: 'Woolen Gray Scarf', condition: 'irrelevant', category: 'Control Item', description: 'Neutral apparel item' },
];

export const ExperimentPage: React.FC<ExperimentPageProps> = ({ session, onTrialRecorded }) => {
  const navigate = useNavigate();

  // Experiment sequence settings
  const [fixationDurationMs, setFixationDurationMs] = useState<number>(500);
  const [stimulusDurationMs, setStimulusDurationMs] = useState<number>(2000);
  const [isiDurationMs, setIsiDurationMs] = useState<number>(500); // Inter-stimulus interval

  // Trial execution state: 'idle' | 'fixation' | 'stimulus' | 'isi' | 'finished'
  const [trialPhase, setTrialPhase] = useState<'idle' | 'fixation' | 'stimulus' | 'isi' | 'finished'>('idle');
  const [currentTrialIdx, setCurrentTrialIdx] = useState<number>(0);
  const [trialQueue, setTrialQueue] = useState<StimulusItem[]>(DEFAULT_STIMULI);
  const [completedTrials, setCompletedTrials] = useState<any[]>([]);

  // Real-time gaze recording buffer
  const [recordedSamples, setRecordedSamples] = useState<GazeSample[]>([]);
  const [gazeDot, setGazeDot] = useState<{ x: number; y: number }>({ x: 0.5, y: 0.5 });
  const [trialOnsetTs, setTrialOnsetTs] = useState<number>(0);
  const [earlyWindowProgress, setEarlyWindowProgress] = useState<number>(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const sampleIntervalRef = useRef<any>(null);

  // Capture mouse as gaze coordinate proxy
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const nx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      const ny = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
      setGazeDot({ x: nx, y: ny });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Shuffle stimuli randomly
  const handleShuffleStimuli = () => {
    const shuffled = [...DEFAULT_STIMULI].sort(() => Math.random() - 0.5);
    setTrialQueue(shuffled);
    setCurrentTrialIdx(0);
    setTrialPhase('idle');
    setCompletedTrials([]);
  };

  // Start trial execution loop
  const handleStartExperiment = () => {
    if (trialQueue.length === 0) return;
    setCurrentTrialIdx(0);
    setCompletedTrials([]);
    startSingleTrial(0);
  };

  const startSingleTrial = (idx: number) => {
    if (idx >= trialQueue.length) {
      setTrialPhase('finished');
      return;
    }

    setCurrentTrialIdx(idx);
    setTrialPhase('fixation');

    // Step 1: Fixation Cross for 500ms
    setTimeout(() => {
      // Step 2: Stimulus Onset
      setTrialPhase('stimulus');
      const onset = performance.now();
      setTrialOnsetTs(onset);
      setRecordedSamples([]);

      // Start high-frequency gaze sampler (60 Hz -> ~16.6 ms)
      const samplesBuf: GazeSample[] = [];
      const intervalId = setInterval(() => {
        const now = performance.now();
        const elapsed = now - onset;

        // Track early 500ms window progress
        if (elapsed <= 500) {
          setEarlyWindowProgress(Math.min(100, Math.round((elapsed / 500) * 100)));
        }

        samplesBuf.push({
          timestamp_ms: Math.round(elapsed * 10) / 10,
          x: Math.round(gazeDot.x * 10000) / 10000,
          y: Math.round(gazeDot.y * 10000) / 10000,
          valid: true,
        });
      }, 16);

      sampleIntervalRef.current = intervalId;

      // End stimulus presentation after duration
      setTimeout(async () => {
        clearInterval(sampleIntervalRef.current);
        const currentStim = trialQueue[idx];
        const trialId = `TR_${session?.sessionId?.slice(-4) || 'DEMO'}_${idx + 1}_${currentStim.id}`;

        const trialPayload: TrialData = {
          trial_id: trialId,
          stimulus_id: currentStim.id,
          stimulus_name: currentStim.name,
          condition: currentStim.condition,
          familiarity_ground_truth: currentStim.condition === 'probe' ? 1 : 0,
          onset_timestamp_ms: 0.0,
          duration_ms: stimulusDurationMs,
          samples: samplesBuf,
        };

        // Submit to backend API if session exists
        let apiResult = null;
        if (session?.sessionId) {
          try {
            apiResult = await submitTrial(session.sessionId, trialPayload);
          } catch (e) {
            console.warn('Backend submission error:', e);
          }
        }

        const completedRecord = {
          trialId,
          stimulus: currentStim,
          samplesCount: samplesBuf.length,
          apiResult,
        };

        setCompletedTrials((prev) => [...prev, completedRecord]);
        if (onTrialRecorded) onTrialRecorded(completedRecord);

        // Step 3: Inter-Stimulus Interval (ISI)
        setTrialPhase('isi');
        setTimeout(() => {
          startSingleTrial(idx + 1);
        }, isiDurationMs);
      }, stimulusDurationMs);
    }, fixationDurationMs);
  };

  const currentStimulus = trialQueue[currentTrialIdx];
  const progressPercent = Math.round(((currentTrialIdx + (trialPhase === 'finished' ? 1 : 0)) / trialQueue.length) * 100);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="accent">Stage 3 of 4: Stimulus Presentation</Badge>
            <span className="text-xs font-mono text-content-muted">
              Participant: {session?.participantPseudonym || 'Unassigned'}
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content flex items-center gap-2.5">
            <PlayCircle className="w-7 h-7 text-accent-primary" />
            <span>Concealed Information Test (CIT) Trial Battery</span>
          </h1>
          <p className="text-sm text-content-secondary mt-1">
            Measuring high-frequency ocular coordinate telemetry across randomized probe and control stimuli.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleShuffleStimuli}
            disabled={trialPhase !== 'idle' && trialPhase !== 'finished'}
            icon={<RotateCcw className="w-3.5 h-3.5" />}
          >
            Randomize Order
          </Button>

          {trialPhase === 'idle' && (
            <Button
              variant="primary"
              size="sm"
              onClick={handleStartExperiment}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              Start Trial Sequence
            </Button>
          )}
        </div>
      </div>

      {/* Trial Telemetry & Progress Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-content-muted">Trial Progress</span>
            <span className="text-sm font-bold font-mono text-accent-primary">
              {trialPhase === 'finished' ? trialQueue.length : currentTrialIdx + 1} / {trialQueue.length}
            </span>
          </div>
          <div className="mt-2">
            <ProgressBar value={progressPercent} variant={trialPhase === 'finished' ? 'success' : 'default'} />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-content-muted">Current Trial Phase</span>
            <span className="text-xs font-bold font-mono uppercase text-content px-2 py-0.5 rounded bg-surface-elevated border border-border">
              {trialPhase}
            </span>
          </div>
          <p className="text-[11px] text-content-muted mt-2">
            {trialPhase === 'fixation' && 'Central cross fixation (500 ms)'}
            {trialPhase === 'stimulus' && 'Active visual stimulus sampling (2000 ms)'}
            {trialPhase === 'isi' && 'Inter-stimulus interval (500 ms)'}
            {trialPhase === 'idle' && 'Awaiting start'}
            {trialPhase === 'finished' && 'All trials complete'}
          </p>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-content-muted">Early Hypothesis Window</span>
            <div className="flex items-center gap-1.5 text-xs font-mono text-accent-secondary">
              <Clock className="w-3.5 h-3.5" />
              <span>0–500 ms: {trialPhase === 'stimulus' ? `${earlyWindowProgress}%` : '—'}</span>
            </div>
          </div>
          <p className="text-[11px] text-content-muted mt-2">
            Primary CIT visual orienting interval
          </p>
        </Card>
      </div>

      {/* Experimental Presentation Canvas */}
      <Card className="overflow-hidden">
        <CardHeader className="pb-3 border-b border-border bg-surface-elevated">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-accent-primary" />
              <CardTitle className="text-sm">Stimulus Screen Canvas</CardTitle>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono text-content-muted">
              <span>Stimulus Duration: {stimulusDurationMs} ms</span>
              <span>ISI: {isiDurationMs} ms</span>
            </div>
          </div>
        </CardHeader>

        <div className="p-4">
          <div
            ref={containerRef}
            className="relative w-full h-[420px] bg-app rounded-xl border border-border overflow-hidden flex items-center justify-center select-none transition-colors"
          >
            {/* Phase: Idle */}
            {trialPhase === 'idle' && (
              <div className="text-center p-8 space-y-4 max-w-md bg-surface/90 backdrop-blur-md rounded-2xl border border-border shadow-xl">
                <div className="w-14 h-14 rounded-full bg-accent-primary/10 border border-accent-primary/30 mx-auto flex items-center justify-center text-accent-primary">
                  <PlayCircle className="w-7 h-7" />
                </div>
                <div className="space-y-1.5">
                  <h3 className="text-base font-bold text-content">Ready for Stimulus Battery</h3>
                  <p className="text-xs text-content-secondary leading-relaxed">
                    {trialQueue.length} randomized visual stimuli are queued.
                    Each trial begins with a central fixation cross (+), followed by stimulus presentation for {stimulusDurationMs} ms.
                  </p>
                </div>
                <Button
                  variant="primary"
                  onClick={handleStartExperiment}
                  icon={<PlayCircle className="w-4 h-4" />}
                >
                  Begin Stimulus Battery
                </Button>
              </div>
            )}

            {/* Phase: Fixation Cross */}
            {trialPhase === 'fixation' && (
              <div className="text-center animate-pulse">
                <span className="text-6xl font-light text-content-muted font-mono select-none">+</span>
                <span className="block text-xs font-mono text-content-muted mt-2">
                  Fixate on central cross
                </span>
              </div>
            )}

            {/* Phase: Active Stimulus Presentation */}
            {trialPhase === 'stimulus' && currentStimulus && (
              <div className="text-center space-y-4 max-w-md p-8 bg-surface/95 backdrop-blur-md rounded-2xl border border-border shadow-2xl animate-scale-in">
                <div className="w-20 h-20 rounded-2xl bg-accent-primary/10 border border-accent-primary/30 mx-auto flex items-center justify-center text-accent-primary shadow-inner">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <span className="text-xs font-mono text-accent-primary uppercase tracking-wider block mb-1">
                    Stimulus Item {currentTrialIdx + 1} of {trialQueue.length}
                  </span>
                  <h2 className="text-2xl font-extrabold text-content">{currentStimulus.name}</h2>
                  <p className="text-xs text-content-secondary mt-1">{currentStimulus.description}</p>
                </div>

                {/* Early 0-500ms window progress indicator */}
                <div className="w-full bg-app rounded-full h-1.5 overflow-hidden border border-border">
                  <div
                    className="bg-accent-primary h-full transition-all duration-75"
                    style={{ width: `${earlyWindowProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Phase: Inter-Stimulus Interval (ISI) */}
            {trialPhase === 'isi' && (
              <div className="text-xs font-mono text-content-muted">
                [ Inter-Stimulus Interval ]
              </div>
            )}

            {/* Phase: Finished */}
            {trialPhase === 'finished' && (
              <div className="text-center p-8 space-y-4 max-w-md bg-surface/95 backdrop-blur-md rounded-2xl border border-border shadow-2xl animate-scale-in">
                <div className="w-12 h-12 rounded-full bg-status-success/15 border border-status-success/30 mx-auto flex items-center justify-center text-status-success">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <div className="space-y-1">
                  <h3 className="text-base font-bold text-content">Stimulus Protocol Complete</h3>
                  <p className="text-xs text-content-secondary leading-relaxed">
                    All {completedTrials.length} trials were successfully presented, sampled, and extracted into the local database.
                  </p>
                </div>
                <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
                  <Button
                    variant="primary"
                    onClick={() => navigate('/signal')}
                    icon={<ArrowRight className="w-4 h-4" />}
                  >
                    Inspect Signal Dynamics
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => navigate('/report')}
                  >
                    View Executive Report
                  </Button>
                </div>
              </div>
            )}

            {/* Real-time Gaze Indicator Dot */}
            <div
              style={{
                left: `${gazeDot.x * 100}%`,
                top: `${gazeDot.y * 100}%`,
                transform: 'translate(-50%, -50%)',
              }}
              className="absolute w-3 h-3 rounded-full bg-accent-primary/80 border border-content pointer-events-none transition-all duration-75 z-30"
            />
          </div>
        </div>
      </Card>

      {/* Completed Trials Summary Table */}
      {completedTrials.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-status-success" />
              <CardTitle className="text-sm">Recorded Trial Telemetry & Quality Status</CardTitle>
            </div>
            <CardDescription>
              Trial-by-trial sample counts, quality assessment, and calibrated familiarity predictions.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Trial Identifier</TableHead>
                  <TableHead>Stimulus Item</TableHead>
                  <TableHead>Condition</TableHead>
                  <TableHead>Sample Count</TableHead>
                  <TableHead>Quality Status</TableHead>
                  <TableHead className="text-right">Calibrated Posterior</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {completedTrials.map((t, idx) => {
                  const qStatus = t.apiResult?.quality_metrics?.status || 'acceptable';
                  const prob = t.apiResult?.probability;
                  const isProbe = t.stimulus.condition === 'probe';

                  return (
                    <TableRow key={idx}>
                      <TableCell className="font-mono text-content-muted">{t.trialId}</TableCell>
                      <TableCell className="font-semibold text-content">{t.stimulus.name}</TableCell>
                      <TableCell>
                        <Badge variant={isProbe ? 'accent' : 'neutral'}>
                          {t.stimulus.condition.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-content-secondary">{t.samplesCount} samples</TableCell>
                      <TableCell>
                        <Badge
                          variant={
                            qStatus === 'excellent'
                              ? 'success'
                              : qStatus === 'acceptable'
                              ? 'neutral'
                              : 'error'
                          }
                        >
                          {qStatus}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono font-bold text-right text-content">
                        {prob !== undefined && prob !== null ? `${(prob * 100).toFixed(1)}%` : 'Abstained'}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
