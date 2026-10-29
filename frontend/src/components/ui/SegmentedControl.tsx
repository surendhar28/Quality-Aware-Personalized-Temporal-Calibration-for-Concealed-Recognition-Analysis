import React from 'react';

export interface SegmentedOption<T extends string> {
  value?: T;
  id?: T;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

export interface SegmentedControlProps<T extends string> {
  options: SegmentedOption<T>[];
  value: T;
  onChange: (value: T) => void;
  size?: 'sm' | 'md';
  className?: string;
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  size = 'md',
  className = '',
}: SegmentedControlProps<T>) {
  const sizeClasses = {
    sm: 'p-0.5 text-xs',
    md: 'p-1 text-sm',
  }[size];

  const itemSizeClasses = {
    sm: 'px-2.5 py-1',
    md: 'px-3.5 py-1.5',
  }[size];

  return (
    <div
      role="tablist"
      className={`inline-flex items-center bg-surface-elevated border border-border rounded-lg ${sizeClasses} ${className}`}
    >
      {options.map((opt) => {
        const optVal = (opt.value ?? opt.id) as T;
        const isActive = optVal === value;
        return (
          <button
            key={optVal}
            role="tab"
            aria-selected={isActive}
            type="button"
            onClick={() => onChange(optVal)}
            className={`flex items-center gap-1.5 font-medium rounded-md transition-all duration-150 cursor-pointer ${itemSizeClasses} ${
              isActive
                ? 'bg-surface text-content-primary shadow-sm border border-border'
                : 'text-content-secondary hover:text-content-primary border border-transparent'
            }`}
          >
            {opt.icon && <span className="shrink-0">{opt.icon}</span>}
            <span>{opt.label}</span>
            {opt.badge !== undefined && (
              <span
                className={`ml-1 text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                  isActive
                    ? 'bg-accent-primary/20 text-accent-primary'
                    : 'bg-surface text-content-muted'
                }`}
              >
                {opt.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
