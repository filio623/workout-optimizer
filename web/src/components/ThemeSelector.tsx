import React from 'react';
import { Palette } from 'lucide-react';
import { Theme, themes } from '../data/themes';

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