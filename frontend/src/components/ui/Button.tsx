import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const variantStyles = {
    primary:
      'bg-accent-primary hover:bg-accent-primary-hover text-white shadow-sm border border-transparent focus-visible:ring-2 focus-visible:ring-accent-primary/50',
    secondary:
      'bg-surface-elevated hover:bg-surface border border-border text-content-primary hover:border-border-strong focus-visible:ring-2 focus-visible:ring-border-strong',
    outline:
      'bg-transparent hover:bg-surface-elevated/40 border border-border text-content-primary hover:border-accent-primary hover:text-accent-primary focus-visible:ring-2 focus-visible:ring-accent-primary/50',
    ghost:
      'bg-transparent hover:bg-surface-elevated/60 text-content-secondary hover:text-content-primary border border-transparent',
    danger:
      'bg-rose-500 hover:bg-rose-600 text-white shadow-sm border border-transparent focus-visible:ring-2 focus-visible:ring-rose-500/50',
  }[variant];

  const sizeStyles = {
    sm: 'px-2.5 py-1.5 text-xs rounded-md gap-1.5',
    md: 'px-3.5 py-2 text-sm rounded-md gap-2',
    lg: 'px-5 py-2.5 text-base rounded-lg gap-2.5',
  }[size];

  return (
    <button
      className={`inline-flex items-center justify-center font-medium transition-all duration-150 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none cursor-pointer ${variantStyles} ${sizeStyles} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin shrink-0" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
};
