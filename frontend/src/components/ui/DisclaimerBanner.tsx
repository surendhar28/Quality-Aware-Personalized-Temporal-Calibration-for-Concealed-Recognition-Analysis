import React from 'react';
import { ShieldAlert, AlertTriangle, Info } from 'lucide-react';

export interface DisclaimerBannerProps {
  variant?: 'ethical' | 'warning' | 'info';
  title?: string;
  message?: string;
  className?: string;
  compact?: boolean;
}

export const DisclaimerBanner: React.FC<DisclaimerBannerProps> = ({
  variant = 'ethical',
  title,
  message,
  className = '',
  compact = false,
}) => {
  const isEthical = variant === 'ethical';

  const defaultTitle = isEthical
    ? 'Mandatory Research Ethics & Forensic Boundary Notice'
    : variant === 'warning'
    ? 'Experimental Protocol Warning'
    : 'Scientific Information';

  const defaultMessage = isEthical
    ? 'GazeGuard AI is a research instrument designed strictly to analyze physiological fixation duration and visual attention patterns under controlled Concealed Information Test (CIT) paradigms. This model estimates experimental visual familiarity only. It must NEVER be used to label any individual as a liar, guilty, deceptive, dishonest, or untruthful. Eye movements alone do not constitute forensic evidence.'
    : message || '';

  const borderStyles = isEthical
    ? 'border-rose-500/30 bg-rose-500/5 text-content-primary'
    : variant === 'warning'
    ? 'border-amber-500/30 bg-amber-500/5 text-content-primary'
    : 'border-blue-500/30 bg-blue-500/5 text-content-primary';

  const icon = isEthical ? (
    <ShieldAlert className="w-5 h-5 text-status-error shrink-0" />
  ) : variant === 'warning' ? (
    <AlertTriangle className="w-5 h-5 text-status-warning shrink-0" />
  ) : (
    <Info className="w-5 h-5 text-status-info shrink-0" />
  );

  return (
    <div
      role="alert"
      className={`rounded-lg border p-4 ${borderStyles} ${compact ? 'py-3' : 'p-4 sm:p-5'} ${className}`}
    >
      <div className="flex items-start gap-3">
        {icon}
        <div>
          <h4 className="text-sm font-semibold text-content-primary tracking-tight">
            {title || defaultTitle}
          </h4>
          <p className="text-xs text-content-secondary mt-1 leading-relaxed">
            {message || defaultMessage}
          </p>
        </div>
      </div>
    </div>
  );
};
