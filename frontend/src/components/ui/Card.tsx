import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'subtle' | 'outline';
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  variant = 'default',
  hoverable = false,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-surface border border-border shadow-card',
    elevated: 'bg-surface-elevated border border-border shadow-elevated',
    subtle: 'bg-surface/50 border border-border-subtle',
    outline: 'bg-transparent border border-border',
  }[variant];

  const hoverStyle = hoverable ? 'transition-all duration-150 hover:border-accent-primary hover:shadow-elevated hover:-translate-y-0.5' : '';

  return (
    <div
      className={`rounded-lg ${variantStyles} ${hoverStyle} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={`p-4 sm:p-5 border-b border-border flex items-center justify-between gap-4 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <h3 className={`text-base font-semibold text-content-primary tracking-tight ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <p className={`text-xs text-content-muted mt-0.5 ${className}`} {...props}>
    {children}
  </p>
);

export const CardBody: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={`p-4 sm:p-5 ${className}`} {...props}>
    {children}
  </div>
);

export const CardContent = CardBody;

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <div className={`p-3.5 sm:p-4 bg-surface-elevated/40 border-t border-border rounded-b-lg flex items-center justify-between text-xs text-content-muted ${className}`} {...props}>
    {children}
  </div>
);
