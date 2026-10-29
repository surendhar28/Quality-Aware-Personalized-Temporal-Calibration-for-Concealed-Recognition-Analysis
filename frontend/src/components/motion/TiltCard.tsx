import React, { useRef, useState, useCallback, useEffect } from 'react';

export interface TiltCardProps extends React.HTMLAttributes<HTMLDivElement> {
  maxRotation?: number; // Maximum rotation in degrees (default: 3deg)
  maxTilt?: number; // Ergonomic alias for maxRotation
  perspective?: number; // Perspective distance in px (default: 1000)
  glareEffect?: boolean; // Subtle radial glare overlay
  scaleOnHover?: number; // Scale on hover (default: 1.01)
  scale?: number; // Ergonomic alias for scaleOnHover
  disabled?: boolean;
}

export const TiltCard: React.FC<TiltCardProps> = ({
  children,
  maxRotation = 3,
  maxTilt,
  perspective = 1000,
  glareEffect = true,
  scaleOnHover = 1.01,
  scale,
  disabled = false,
  className = '',
  style,
  ...props
}) => {
  const effectiveRotation = maxTilt ?? maxRotation;
  const effectiveScale = scale ?? scaleOnHover;
  const cardRef = useRef<HTMLDivElement>(null);
  const [transformStyle, setTransformStyle] = useState<string>('');
  const [glareStyle, setGlareStyle] = useState<React.CSSProperties>({ opacity: 0 });
  const [isTouch, setIsTouch] = useState<boolean>(false);
  const [reducedMotion, setReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    // Detect touch-only devices or reduced-motion preference
    if (typeof window !== 'undefined') {
      const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      setIsTouch(hasTouch);

      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      setReducedMotion(mediaQuery.matches);

      const handleChange = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, []);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (disabled || isTouch || reducedMotion || !cardRef.current) return;

      const rect = cardRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left; // x position within card
      const y = e.clientY - rect.top; // y position within card

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      // Calculate tilt angles within restrained bounds (-effectiveRotation to +effectiveRotation)
      const rotateX = (((y - centerY) / centerY) * -effectiveRotation).toFixed(2);
      const rotateY = (((x - centerX) / centerX) * effectiveRotation).toFixed(2);

      setTransformStyle(
        `perspective(${perspective}px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${effectiveScale}, ${effectiveScale}, 1)`
      );

      if (glareEffect) {
        const glareX = ((x / rect.width) * 100).toFixed(1);
        const glareY = ((y / rect.height) * 100).toFixed(1);
        setGlareStyle({
          opacity: 0.12,
          background: `radial-gradient(circle 240px at ${glareX}% ${glareY}%, rgba(56, 189, 248, 0.4), transparent 70%)`,
        });
      }
    },
    [disabled, isTouch, reducedMotion, maxRotation, perspective, scaleOnHover, glareEffect]
  );

  const handleMouseLeave = useCallback(() => {
    if (disabled || isTouch || reducedMotion) return;
    setTransformStyle(`perspective(${perspective}px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`);
    if (glareEffect) {
      setGlareStyle({ opacity: 0 });
    }
  }, [disabled, isTouch, reducedMotion, perspective, glareEffect]);

  const isDisabled = disabled || isTouch || reducedMotion;

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: isDisabled ? undefined : transformStyle,
        transition: transformStyle ? 'transform 0.18s cubic-bezier(0.16, 1, 0.3, 1)' : 'transform 0.35s ease',
        transformStyle: 'preserve-3d',
        ...style,
      }}
      className={`relative overflow-hidden will-change-transform ${className}`}
      {...props}
    >
      {glareEffect && !isDisabled && (
        <div
          className="pointer-events-none absolute inset-0 z-30 transition-opacity duration-300 ease-out rounded-inherit"
          style={glareStyle}
        />
      )}
      <div className="relative z-10">{children}</div>
    </div>
  );
};
