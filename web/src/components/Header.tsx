import React from 'react';
import { Menu, User, Settings, Bell } from 'lucide-react';
import ThemeSelector, { Theme, themes } from './ThemeSelector';

interface HeaderProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  currentTheme: Theme;
  onThemeChange: (theme: Theme) => void;
}

const Header: React.FC<HeaderProps> = ({ sidebarOpen, setSidebarOpen, currentTheme, onThemeChange }) => {
  const [themeMenuOpen, setThemeMenuOpen] = React.useState(false);

  return (
    <header className={`${currentTheme.surface} backdrop-blur-md border-b border-slate-200 px-6 py-4 flex items-center justify-between relative z-40`}>
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 rounded-xl hover:bg-slate-100 transition-colors"
        >
          <Menu className="w-6 h-6 text-slate-700" />
        </button>
        
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 bg-gradient-to-br ${currentTheme.primary} rounded-xl flex items-center justify-center`}>
            <span className="text-white font-bold text-lg">F</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">FitBot AI</h1>
            <p className="text-sm text-slate-500">Your Personal Workout Analyst</p>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="p-2 rounded-xl hover:bg-slate-100 transition-colors relative">
          <Bell className="w-5 h-5 text-slate-600" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
        </button>
        
        <ThemeSelector 
          currentTheme={currentTheme}
          onThemeChange={onThemeChange}
          isOpen={themeMenuOpen}
          onToggle={() => setThemeMenuOpen(!themeMenuOpen)}
        />
        
        <button className="p-2 rounded-xl hover:bg-slate-100 transition-colors">
          <Settings className="w-5 h-5 text-slate-600" />
        </button>
        
        <div className="flex items-center gap-3 ml-4 pl-4 border-l border-slate-200">
          <div className={`w-8 h-8 bg-gradient-to-br ${currentTheme.accent} rounded-full flex items-center justify-center`}>
            <User className="w-4 h-4 text-white" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-slate-900">Alex Johnson</p>
            <p className="text-xs text-slate-500">Premium Member</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;