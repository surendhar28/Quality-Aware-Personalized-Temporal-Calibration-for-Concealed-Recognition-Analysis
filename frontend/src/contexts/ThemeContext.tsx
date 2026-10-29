import React, { createContext, useContext, useState, useEffect } from 'react';

export type ThemeName = 'midnight' | 'clinical' | 'graphite' | 'indigo';

export interface ThemeColors {
  primary: string;
  secondary: string;
  probe: string;
  irrelevant: string;
  grid: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  bgSurface: string;
  textPrimary: string;
  textSecondary: string;
  borderDefault: string;
}

export interface ChartThemeColors {
  primary: string;
  secondary: string;
  probe: string;
  irrelevant: string;
  grid: string;
  text: string;
  tooltipBg: string;
  tooltipBorder: string;
  success: string;
  warning: string;
  error: string;
}

const THEME_PALETTES: Record<ThemeName, ThemeColors> = {
  midnight: {
    primary: '#38BDF8',
    secondary: '#818CF8',
    probe: '#38BDF8',
    irrelevant: '#818CF8',
    grid: 'rgba(255, 255, 255, 0.08)',
    success: '#34D399',
    warning: '#FBBF24',
    error: '#FB7185',
    info: '#60A5FA',
    bgSurface: '#111C2E',
    textPrimary: '#E5EDF7',
    textSecondary: '#A5B4C7',
    borderDefault: '#24344B',
  },
  clinical: {
    primary: '#2563EB',
    secondary: '#6366F1',
    probe: '#2563EB',
    irrelevant: '#6366F1',
    grid: 'rgba(0, 0, 0, 0.08)',
    success: '#047857',
    warning: '#B45309',
    error: '#BE123C',
    info: '#1D4ED8',
    bgSurface: '#FFFFFF',
    textPrimary: '#172033',
    textSecondary: '#475569',
    borderDefault: '#D9E2EC',
  },
  graphite: {
    primary: '#34D399',
    secondary: '#6EE7B7',
    probe: '#34D399',
    irrelevant: '#6EE7B7',
    grid: 'rgba(255, 255, 255, 0.07)',
    success: '#34D399',
    warning: '#FBBF24',
    error: '#FB7185',
    info: '#38BDF8',
    bgSurface: '#1A1F21',
    textPrimary: '#E8EFEC',
    textSecondary: '#AAB8B2',
    borderDefault: '#343C3C',
  },
  indigo: {
    primary: '#A78BFA',
    secondary: '#818CF8',
    probe: '#A78BFA',
    irrelevant: '#818CF8',
    grid: 'rgba(255, 255, 255, 0.08)',
    success: '#34D399',
    warning: '#FBBF24',
    error: '#FB7185',
    info: '#60A5FA',
    bgSurface: '#1B1B35',
    textPrimary: '#F0EEFF',
    textSecondary: '#B8B5D4',
    borderDefault: '#343453',
  },
};

interface ThemeContextType {
  theme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  colors: ThemeColors;
  chartColors: ChartThemeColors;
  isDark: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeName>(() => {
    const saved = localStorage.getItem('gazeguard_theme') as ThemeName;
    if (saved && (saved in THEME_PALETTES)) {
      return saved;
    }
    return 'midnight';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('gazeguard_theme', theme);
  }, [theme]);

  const setTheme = (newTheme: ThemeName) => {
    setThemeState(newTheme);
  };

  const isDark = theme !== 'clinical';
  const colors = THEME_PALETTES[theme];

  const chartColors: ChartThemeColors = {
    primary: colors.primary,
    secondary: colors.secondary,
    probe: colors.probe,
    irrelevant: colors.irrelevant,
    grid: colors.grid,
    text: colors.textSecondary,
    tooltipBg: colors.bgSurface,
    tooltipBorder: colors.borderDefault,
    success: colors.success,
    warning: colors.warning,
    error: colors.error,
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, colors, chartColors, isDark }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
