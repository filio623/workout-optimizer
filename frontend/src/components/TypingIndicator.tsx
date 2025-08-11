import React from 'react';
import { Bot } from 'lucide-react';
import { Theme } from './ThemeSelector';

interface TypingIndicatorProps {
  currentTheme: Theme;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ currentTheme }) => {
  return (
    <div className="flex gap-3 items-start">
      <div className={`w-8 h-8 bg-gradient-to-br ${currentTheme.primary} rounded-xl flex items-center justify-center flex-shrink-0`}>
        <Bot className="w-4 h-4 text-white" />
      </div>
      
      <div className={`${currentTheme.surface} border border-slate-200 rounded-2xl px-4 py-3 shadow-sm`}>
        <div className="flex items-center gap-1">
          <div className="flex gap-1">
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-slate-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
          <span className="text-sm text-slate-500 ml-2">AI is thinking...</span>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;