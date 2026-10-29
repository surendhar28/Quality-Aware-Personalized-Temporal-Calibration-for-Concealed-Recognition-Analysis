import React from 'react';

export interface PageTransitionProps {
  children: React.ReactNode;
  className?: string;
}

export const PageTransition: React.FC<PageTransitionProps> = ({ children, className = '' }) => {
  return (
    <div className={`animate-slide-up w-full ${className}`}>
      {children}
    </div>
  );
};
