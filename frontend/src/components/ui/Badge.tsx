import React from 'react';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'error' | 'info' | 'neutral' | 'primary' | 'accent';
  size?: 'sm' | 'md';
  dot?: boolean;
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  icon,
  className = '',
  ...props
}) => {
  const effectiveVariant = variant === 'accent' ? 'primary' : variant;

  const variantStyles = {
    success: 'bg-emerald-500/10 text-status-success border-emerald-500/25',
    warning: 'bg-amber-500/10 text-status-warning border-amber-500/25',
    error: 'bg-rose-500/10 text-status-error border-rose-500/25',
    info: 'bg-blue-500/10 text-status-info border-blue-500/25',
    primary: 'bg-accent-primary/10 text-accent-primary border-accent-primary/30',
    neutral: 'bg-surface-elevated text-content-secondary border-border',
  }[effectiveVariant];

  const dotColors = {
    success: 'bg-status-success',
    warning: 'bg-status-warning',
    error: 'bg-status-error',
    info: 'bg-status-info',
    primary: 'bg-accent-primary',
    neutral: 'bg-content-muted',
  }[effectiveVariant];

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[11px]',
    md: 'px-2.5 py-1 text-xs',
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${variantStyles} ${sizeStyles} ${className}`}
      {...props}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors}`} />}
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  );
};
