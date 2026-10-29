import React from 'react';
import { Card } from './Card';

export interface MetricCardProps {
  label: string;
  value: React.ReactNode;
  unit?: string;
  subtitle?: string;
  description?: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  provenanceTag?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    direction?: 'up' | 'down' | 'neutral';
  };
  className?: string;
  onClick?: () => void;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  unit,
  subtitle,
  description,
  icon,
  badge,
  provenanceTag,
  trend,
  className = '',
  onClick,
}) => {
  const displaySubtitle = subtitle || description;
  const trendColor = trend
    ? trend.direction === 'up' || trend.isPositive
      ? 'text-status-success'
      : trend.direction === 'down'
      ? 'text-status-error'
      : 'text-content-muted'
    : '';

  return (
    <Card
      hoverable={!!onClick}
      onClick={onClick}
      className={`p-4 sm:p-5 flex flex-col justify-between ${onClick ? 'cursor-pointer' : ''} ${className}`}
    >
      <div>
        <div className="flex items-center justify-between text-content-secondary mb-2">
          <span className="text-xs font-mono uppercase tracking-wider text-content-muted">
            {label}
          </span>
          {icon && <div className="text-accent-primary shrink-0">{icon}</div>}
        </div>

        <div className="flex items-baseline gap-1.5 mt-1">
          <span className="text-2xl sm:text-3xl font-extrabold font-mono text-content-primary tracking-tight">
            {value}
          </span>
          {unit && (
            <span className="text-xs font-mono text-content-muted font-normal">
              {unit}
            </span>
          )}
        </div>

        {(displaySubtitle || trend || badge) && (
          <div className="flex items-center gap-2 mt-2 flex-wrap">
            {badge && <div>{badge}</div>}
            {trend && (
              <span className={`text-xs font-mono font-medium ${trendColor}`}>
                {trend.value}
              </span>
            )}
            {displaySubtitle && (
              <span className="text-xs text-content-muted">
                {displaySubtitle}
              </span>
            )}
          </div>
        )}
      </div>

      {provenanceTag && (
        <div className="mt-3.5 pt-2.5 border-t border-border-subtle flex items-center justify-between text-[11px] font-mono text-content-muted">
          <span>{provenanceTag}</span>
        </div>
      )}
    </Card>
  );
};
