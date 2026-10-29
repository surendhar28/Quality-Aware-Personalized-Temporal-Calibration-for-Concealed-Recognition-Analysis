import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCheck2,
  Shield,
  Camera,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Trash2,
  ArrowRight,
  Info,
  Lock,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { createSession } from '../services/api';
import { SessionState } from '../types';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
  Badge,
  Button,
  DisclaimerBanner,
} from '../components/ui';
import { TiltCard } from '../components/motion';

interface ConsentPageProps {
  onSessionCreated: (session: SessionState) => void;
  activeSession?: SessionState;
  onClearSession: () => void;
}

export const ConsentPage: React.FC<ConsentPageProps> = ({
  onSessionCreated,
  activeSession,
  onClearSession,
}) => {
  const navigate = useNavigate();

  const [pseudonym, setPseudonym] = useState<string>(
    activeSession?.participantPseudonym || `SUB_${Math.floor(1000 + Math.random() * 9000)}`
  );
  const [readInfo, setReadInfo] = useState<boolean>(activeSession?.hasConsented || false);
  const [agreeTracking, setAgreeTracking] = useState<boolean>(activeSession?.hasConsented || false);
  const [agreeRetention, setAgreeRetention] = useState<boolean>(activeSession?.hasConsented || false);

  const [cameraStatus, setCameraStatus] = useState<'idle' | 'testing' | 'granted' | 'denied' | 'simulated'>(
    activeSession?.cameraPermitted ? 'granted' : 'idle'
  );
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Test Camera Permissions
  const handleTestCamera = async () => {
    setCameraStatus('testing');
    setCameraError(null);
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error('Camera MediaDevices API is not supported in this browser environment.');
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      // Immediately stop stream after verification
      stream.getTracks().forEach((track) => track.stop());
      setCameraStatus('granted');
    } catch (err: any) {
      setCameraStatus('denied');
      setCameraError(err.message || 'Camera permission denied or camera device unavailable.');
    }
  };

  const handleUseSimulatedTracker = () => {
    setCameraStatus('simulated');
    setCameraError(null);
  };

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!readInfo || !agreeTracking || !agreeRetention) {
      setErrorMsg('All three mandatory ethical consent confirmations must be acknowledged prior to proceeding.');
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    try {
      const res = await createSession({
        participant_pseudonym: pseudonym,
        has_read_information_sheet: readInfo,
        agreed_to_eye_tracking: agreeTracking,
        agreed_to_data_retention: agreeRetention,
        camera_permitted: cameraStatus === 'granted',
      });

      const sessionObj: SessionState = {
        sessionId: res.session_id,
        participantPseudonym: pseudonym,
        hasConsented: true,
        cameraPermitted: cameraStatus === 'granted',
        calibrationCompleted: false,
      };

      onSessionCreated(sessionObj);
      navigate('/calibration');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to initialize session.');
    } finally {
      setSubmitting(false);
    }
  };

  const allConsentsChecked = readInfo && agreeTracking && agreeRetention;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-border">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="accent">Stage 1 of 4: Onboarding</Badge>
            {activeSession && <Badge variant="success">Active Session Enrolled</Badge>}
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-content flex items-center gap-2.5">
            <FileCheck2 className="w-7 h-7 text-accent-primary" />
            <span>Participant Informed Consent & Onboarding</span>
          </h1>
          <p className="text-sm text-content-secondary mt-1">
            Review experimental protocols, data governance policies, and confirm ethical consent declarations.
          </p>
        </div>

        {activeSession && (
          <Button
            variant="outline"
            size="sm"
            onClick={onClearSession}
            icon={<Trash2 className="w-3.5 h-3.5 text-status-error" />}
          >
            Clear Active Session
          </Button>
        )}
      </div>

      {/* Mandatory Ethical Notice */}
      <DisclaimerBanner />

      {/* Protocol Information & Privacy Policy */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <TiltCard className="rounded-lg">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2 text-accent-primary mb-1">
                <Info className="w-4 h-4" />
                <span className="text-xs font-mono uppercase tracking-wider font-semibold">Protocol Overview</span>
              </div>
              <CardTitle>Research Objectives & Procedures</CardTitle>
              <CardDescription>
                Evaluation of Quality-Aware Personalized Temporal Calibration (QPTC).
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs leading-relaxed text-content-secondary">
              <p>
                <strong className="text-content">Scientific Objective:</strong> This investigation evaluates whether
                participant-specific spatial calibration and early temporal windowing (0–500 ms) improve familiarity-related
                fixation pattern classification in the presence of noise.
              </p>
              <p>
                <strong className="text-content">Experimental Routine:</strong> Participants complete a 9-point spatial calibration
                pattern followed by a randomized presentation of 6 visual stimuli (probe and control items) at 2000 ms per trial.
              </p>
              <p>
                <strong className="text-content">Voluntary Participation:</strong> You reserve the unconditional right to pause
                or withdraw from this protocol at any time without penalty or loss of data rights.
              </p>
            </CardContent>
          </Card>
        </TiltCard>

        <TiltCard className="rounded-lg">
          <Card className="h-full">
            <CardHeader>
              <div className="flex items-center gap-2 text-accent-secondary mb-1">
                <Lock className="w-4 h-4" />
                <span className="text-xs font-mono uppercase tracking-wider font-semibold">Privacy Safeguards</span>
              </div>
              <CardTitle>Video Privacy & Retention Policy</CardTitle>
              <CardDescription>
                Strict client-side processing architecture with no video streaming.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3 text-xs leading-relaxed text-content-secondary">
              <div className="p-3 rounded-lg bg-surface-elevated border border-border">
                <span className="font-semibold text-content block mb-1">Zero Raw Video Transmission</span>
                Webcam video frames are transformed entirely in local memory to extract coordinate coordinates [X, Y]. Raw video is
                never recorded, stored on disk, or streamed to any external server.
              </div>
              <p>
                <strong className="text-content">Pseudonymization:</strong> All extracted fixation metrics and derived features are
                keyed solely to an anonymous participant code with zero identifiable demographic links.
              </p>
              <p>
                <strong className="text-content">Storage Retention:</strong> Local database records persist for 30 days under research audit
                guidelines and can be wiped instantly via the "Clear Session" control.
              </p>
            </CardContent>
          </Card>
        </TiltCard>
      </div>

      {/* Main Consent Form & Camera Verification */}
      <form onSubmit={handleStartSession} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Participant Setup & Verification</CardTitle>
            <CardDescription>Configure session identifier and confirm optical tracking modality.</CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Participant Identifier Field */}
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-content uppercase tracking-wider font-mono">
                Pseudonymous Participant Identifier:
              </label>
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                <input
                  type="text"
                  value={pseudonym}
                  onChange={(e) => setPseudonym(e.target.value)}
                  className="bg-app border border-border rounded-lg px-3.5 py-2 text-sm text-content font-mono focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary sm:w-72 transition-colors"
                  placeholder="e.g. SUB_1042"
                  required
                />
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setPseudonym(`SUB_${Math.floor(1000 + Math.random() * 9000)}`)}
                  icon={<RefreshCw className="w-3.5 h-3.5" />}
                >
                  Regenerate Random ID
                </Button>
              </div>
              <p className="text-xs text-content-muted">
                System-generated pseudonyms preserve complete anonymity under human-subject research protocols.
              </p>
            </div>

            {/* Tracking Modality & Camera Verification */}
            <div className="p-4 rounded-xl bg-surface-elevated border border-border space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Camera className="w-4 h-4 text-accent-primary" />
                  <span className="text-sm font-semibold text-content">Optical Gaze Sensor Verification</span>
                </div>

                <div className="flex items-center gap-2">
                  {cameraStatus === 'granted' && (
                    <Badge variant="success" icon={<CheckCircle2 className="w-3 h-3" />}>
                      Optical Camera Verified
                    </Badge>
                  )}
                  {cameraStatus === 'denied' && (
                    <Badge variant="error" icon={<XCircle className="w-3 h-3" />}>
                      Hardware Access Blocked
                    </Badge>
                  )}
                  {cameraStatus === 'simulated' && (
                    <Badge variant="accent" icon={<Shield className="w-3 h-3" />}>
                      Simulated Fixture Mode Active
                    </Badge>
                  )}
                  {cameraStatus === 'idle' && (
                    <Badge variant="neutral">Verification Pending</Badge>
                  )}
                </div>
              </div>

              <p className="text-xs text-content-secondary leading-relaxed">
                Connect your browser's webcam for live ocular tracking. If your system does not possess an optical camera
                or browser permissions are restricted, switch to Simulated Fixture Mode to evaluate using synthetic physiological signals.
              </p>

              <div className="flex flex-wrap items-center gap-3 pt-1">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={handleTestCamera}
                  disabled={cameraStatus === 'testing'}
                  icon={<Camera className="w-3.5 h-3.5" />}
                >
                  {cameraStatus === 'testing' ? 'Querying MediaDevices...' : 'Verify Camera Stream'}
                </Button>

                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={handleUseSimulatedTracker}
                  icon={<Sparkles className="w-3.5 h-3.5 text-accent-primary" />}
                >
                  Switch to Simulated Fixture Mode
                </Button>
              </div>

              {cameraError && (
                <div className="p-3 rounded-lg bg-status-error/10 border border-status-error/30 text-status-error text-xs font-mono flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>Hardware error: {cameraError}. (You can continue seamlessly using Simulated Fixture Mode).</span>
                </div>
              )}
            </div>

            {/* Mandatory Ethical Consent Declarations */}
            <div className="space-y-3 pt-2">
              <span className="text-xs font-bold text-content uppercase tracking-wider font-mono block">
                Mandatory Informed Consent Declarations:
              </span>

              <label
                className={`flex items-start gap-3 p-3.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                  readInfo
                    ? 'bg-accent-primary/10 border-accent-primary shadow-xs ring-1 ring-accent-primary/40'
                    : 'bg-surface hover:bg-surface-elevated border-border'
                }`}
              >
                <input
                  type="checkbox"
                  checked={readInfo}
                  onChange={(e) => setReadInfo(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-border bg-app text-accent-primary focus:ring-accent-primary cursor-pointer transition-transform active:scale-95"
                />
                <span className="text-xs text-content leading-relaxed">
                  I confirm that I have reviewed and understand the participant information sheet explaining the scientific
                  objectives, experimental procedures, and ethical limitations of GazeGuard AI.
                </span>
              </label>

              <label
                className={`flex items-start gap-3 p-3.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                  agreeTracking
                    ? 'bg-accent-primary/10 border-accent-primary shadow-xs ring-1 ring-accent-primary/40'
                    : 'bg-surface hover:bg-surface-elevated border-border'
                }`}
              >
                <input
                  type="checkbox"
                  checked={agreeTracking}
                  onChange={(e) => setAgreeTracking(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-border bg-app text-accent-primary focus:ring-accent-primary cursor-pointer transition-transform active:scale-95"
                />
                <span className="text-xs text-content leading-relaxed">
                  I voluntarily agree to participate in eye-tracking spatial calibration and visual stimulus recording.
                </span>
              </label>

              <label
                className={`flex items-start gap-3 p-3.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                  agreeRetention
                    ? 'bg-accent-primary/10 border-accent-primary shadow-xs ring-1 ring-accent-primary/40'
                    : 'bg-surface hover:bg-surface-elevated border-border'
                }`}
              >
                <input
                  type="checkbox"
                  checked={agreeRetention}
                  onChange={(e) => setAgreeRetention(e.target.checked)}
                  className="mt-0.5 h-4 w-4 rounded border-border bg-app text-accent-primary focus:ring-accent-primary cursor-pointer transition-transform active:scale-95"
                />
                <span className="text-xs text-content leading-relaxed">
                  I consent to the retention of pseudonymous derived fixation metrics under the strict non-accusatory research protocol.
                </span>
              </label>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-lg bg-status-error/10 border border-status-error/30 text-status-error text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
            <span className="text-xs text-content-muted">
              {allConsentsChecked
                ? 'All ethical declarations acknowledged. Ready to initialize.'
                : 'All 3 declarations must be checked to enable session registration.'}
            </span>

            <Button
              type="submit"
              variant="primary"
              disabled={submitting || !allConsentsChecked}
              icon={<ArrowRight className="w-4 h-4" />}
            >
              {submitting ? 'Registering Participant...' : 'Confirm Consent & Proceed to Calibration'}
            </Button>
          </CardFooter>
        </Card>
      </form>
    </div>
  );
};
