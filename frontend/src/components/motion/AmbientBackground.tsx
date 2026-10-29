import React from 'react';
import { useTheme } from '../../contexts/ThemeContext';

export const AmbientBackground: React.FC = () => {
  const { isDark } = useTheme();

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none"
    >
      {/* Subtle scientific coordinate grid pattern */}
      <div className="absolute inset-0 scientific-grid-bg opacity-35" />

      {/* Atmospheric lighting orbs tailored for dark scientific visualization */}
      {isDark ? (
        <>
          {/* Top-right soft cyan orb */}
          <div
            className="absolute -top-32 -right-32 w-[550px] h-[550px] rounded-full blur-[120px] opacity-15"
            style={{
              background: 'radial-gradient(circle, var(--color-primary) 0%, transparent 70%)',
            }}
          />

          {/* Center-left soft indigo ambient light */}
          <div
            className="absolute top-1/3 -left-40 w-[600px] h-[600px] rounded-full blur-[140px] opacity-10"
            style={{
              background: 'radial-gradient(circle, var(--color-secondary) 0%, transparent 70%)',
            }}
          />

          {/* Bottom-right faint emerald glow */}
          <div
            className="absolute -bottom-40 right-1/4 w-[500px] h-[500px] rounded-full blur-[130px] opacity-10"
            style={{
              background: 'radial-gradient(circle, var(--color-success) 0%, transparent 70%)',
            }}
          />
        </>
      ) : (
        /* Clinical Light theme subtle ambient tone */
        <div
          className="absolute -top-24 right-0 w-[600px] h-[600px] rounded-full blur-[120px] opacity-10"
          style={{
            background: 'radial-gradient(circle, #2563EB 0%, transparent 70%)',
          }}
        />
      )}
    </div>
  );
};
