import React from 'react';

export interface ProgressBarProps {
  value: number; // 0 to 100
  max?: number;
  label?: string;
  showPercentage?: boolean;
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'default';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showPercentage = true,
  variant = 'primary',
  size = 'md',
  className = '',
}) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const effectiveVariant = variant === 'default' ? 'primary' : variant;

  const variantBar = {
    primary: 'bg-accent-primary',
    success: 'bg-status-success',
    warning: 'bg-status-warning',
    error: 'bg-status-error',
  }[effectiveVariant];

  const heightClass = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  }[size];

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex items-center justify-between text-xs font-mono text-content-secondary mb-1.5">
          {label && <span>{label}</span>}
          {showPercentage && <span className="font-semibold text-content-primary">{Math.round(percentage)}%</span>}
        </div>
      )}
      <div className={`w-full bg-surface-elevated rounded-full overflow-hidden border border-border-subtle ${heightClass}`}>
        <div
          className={`h-full transition-all duration-300 ease-out rounded-full ${variantBar}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
