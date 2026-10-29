import React from 'react';

export interface PageHeaderProps {
  title: string;
  subtitle?: string;
  category?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  metadata?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  subtitle,
  category,
  badge,
  actions,
  metadata,
  className = '',
}) => {
  return (
    <div className={`mb-6 sm:mb-8 pb-5 border-b border-border ${className}`}>
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          {(category || badge) && (
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              {category && (
                <span className="px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-accent-primary/10 text-accent-primary border border-accent-primary/20">
                  {category}
                </span>
              )}
              {badge}
            </div>
          )}
          <h1 className="text-2xl sm:text-3xl font-extrabold text-content-primary tracking-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-content-secondary max-w-3xl mt-1.5 leading-relaxed">
              {subtitle}
            </p>
          )}
          {metadata && (
            <div className="mt-3 flex items-center gap-4 text-xs font-mono text-content-muted flex-wrap">
              {metadata}
            </div>
          )}
        </div>

        {actions && (
          <div className="flex items-center gap-2.5 shrink-0 self-start md:self-center flex-wrap">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};
