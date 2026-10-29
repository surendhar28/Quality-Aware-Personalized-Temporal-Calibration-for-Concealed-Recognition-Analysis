import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '../contexts/ThemeContext';
import { AppLayout } from '../components/Layout/AppLayout';
import { Dashboard } from '../pages/Dashboard';
import { ConsentPage } from '../pages/ConsentPage';
import { CalibrationPage } from '../pages/CalibrationPage';
import { ExperimentPage } from '../pages/ExperimentPage';
import { SignalAnalysisPage } from '../pages/SignalAnalysisPage';
import { ModelComparisonPage } from '../pages/ModelComparisonPage';
import { ReportPage } from '../pages/ReportPage';
import { ResearchPage } from '../pages/ResearchPage';
import { SettingsPage } from '../pages/SettingsPage';
import { SessionState } from '../types';
import { fetchHealth } from '../services/api';

export const App: React.FC = () => {
  const [activeSession, setActiveSession] = useState<SessionState | undefined>(() => {
    const saved = localStorage.getItem('gazeguard_session');
    return saved ? JSON.parse(saved) : undefined;
  });

  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(true);

  useEffect(() => {
    async function checkBackend() {
      try {
        await fetchHealth();
        setIsBackendOnline(true);
      } catch {
        setIsBackendOnline(false);
      }
    }
    checkBackend();
    const timer = setInterval(checkBackend, 15000);
    return () => clearInterval(timer);
  }, []);

  const handleSessionCreated = (session: SessionState) => {
    setActiveSession(session);
    localStorage.setItem('gazeguard_session', JSON.stringify(session));
  };

  const handleClearSession = () => {
    setActiveSession(undefined);
    localStorage.removeItem('gazeguard_session');
  };

  const handleCalibrationComplete = (quality: string) => {
    if (!activeSession) return;
    const updated = {
      ...activeSession,
      calibrationCompleted: true,
      calibrationQuality: quality as any,
    };
    setActiveSession(updated);
    localStorage.setItem('gazeguard_session', JSON.stringify(updated));
  };

  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppLayout
          activeSession={activeSession}
          isBackendOnline={isBackendOnline}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route
              path="/consent"
              element={
                <ConsentPage
                  onSessionCreated={handleSessionCreated}
                  activeSession={activeSession}
                  onClearSession={handleClearSession}
                />
              }
            />
            <Route
              path="/calibration"
              element={
                <CalibrationPage
                  session={activeSession}
                  onCalibrationComplete={handleCalibrationComplete}
                />
              }
            />
            <Route
              path="/experiment"
              element={<ExperimentPage session={activeSession} />}
            />
            <Route path="/signal" element={<SignalAnalysisPage />} />
            <Route path="/models" element={<ModelComparisonPage />} />
            <Route path="/report" element={<ReportPage session={activeSession} />} />
            <Route path="/research" element={<ResearchPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </BrowserRouter>
    </ThemeProvider>
  );
};
