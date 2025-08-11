import React from 'react';
import { Palette } from 'lucide-react';

export interface Theme {
  name: string;
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  description: string;
}

export const themes: Theme[] = [
  {
    name: 'Ocean Blue',
    primary: 'from-blue-500 to-blue-600',
    secondary: 'from-slate-50 to-blue-50',
    accent: 'from-green-400 to-green-500',
    background: 'bg-gradient-to-br from-slate-50 to-blue-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Cool and professional with ocean-inspired blues'
  },
  {
    name: 'Sunset Orange',
    primary: 'from-orange-500 to-red-500',
    secondary: 'from-orange-50 to-red-50',
    accent: 'from-yellow-400 to-orange-400',
    background: 'bg-gradient-to-br from-orange-50 to-red-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Energetic and motivating with warm sunset colors'
  },
  {
    name: 'Forest Green',
    primary: 'from-green-600 to-emerald-600',
    secondary: 'from-green-50 to-emerald-50',
    accent: 'from-lime-400 to-green-400',
    background: 'bg-gradient-to-br from-green-50 to-emerald-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Natural and calming with forest-inspired greens'
  },
  {
    name: 'Purple Gradient',
    primary: 'from-purple-500 to-indigo-600',
    secondary: 'from-purple-50 to-indigo-50',
    accent: 'from-pink-400 to-purple-400',
    background: 'bg-gradient-to-br from-purple-50 to-indigo-50',
    surface: 'bg-white/80',
    text: 'text-slate-900',
    description: 'Modern and creative with purple gradients'
  },
  {
    name: 'Dark Mode',
    primary: 'from-blue-400 to-blue-500',
    secondary: 'from-slate-900 to-slate-800',
    accent: 'from-green-400 to-emerald-400',
    background: 'bg-gradient-to-br from-slate-900 to-slate-800',
    surface: 'bg-slate-800/80',
    text: 'text-white',
    description: 'Sleek dark theme for low-light environments'
  }
];

interface ThemeSelectorProps {
  currentTheme: Theme;
  onThemeChange: (theme: Theme) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ 
  currentTheme, 
  onThemeChange, 
  isOpen, 
  onToggle 
}) => {
  return (
    <div className="relative">
      <button
        onClick={onToggle}
        className="p-2 rounded-xl hover:bg-slate-100 transition-colors"
      >
        <Palette className="w-5 h-5 text-slate-600" />
      </button>
      
      {isOpen && (
        <div className="absolute right-0 top-12 w-80 bg-white rounded-xl shadow-xl border border-slate-200 p-4 z-50 shadow-2xl">
          <h3 className="font-semibold text-slate-900 mb-4">Choose Theme</h3>
          <div className="space-y-3">
            {themes.map((theme) => (
              <button
                key={theme.name}
                onClick={() => {
                  onThemeChange(theme);
                  onToggle();
                }}
                className={`w-full p-3 rounded-lg border-2 transition-all text-left ${
                  currentTheme.name === theme.name
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-6 h-6 rounded-full bg-gradient-to-r ${theme.primary}`}></div>
                  <span className="font-medium text-slate-900">{theme.name}</span>
                </div>
                <p className="text-sm text-slate-600">{theme.description}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ThemeSelector;