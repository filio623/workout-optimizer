import React, { useState } from 'react';
import { Menu, X, Activity, BarChart3, Calendar, User, Settings, Send, Mic } from 'lucide-react';
import ChatInterface from './ChatInterface';
import Sidebar from './Sidebar';
import Header from './Header';
import { Theme, themes } from './ThemeSelector';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>(themes[0]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  return (
    <div className={`h-screen ${currentTheme.background} flex flex-col`}>
      <Header 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        currentTheme={currentTheme}
        onThemeChange={setCurrentTheme}
      />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar 
          sidebarOpen={sidebarOpen} 
          setSidebarOpen={setSidebarOpen}
          currentTheme={currentTheme}
          currentSessionId={currentSessionId}
          onSelectSession={setCurrentSessionId}
          onNewChat={() => setCurrentSessionId(null)}
        />
        <ChatInterface 
          currentTheme={currentTheme}
          sessionId={currentSessionId}
          onNewSessionId={setCurrentSessionId}
        />
      </div>
    </div>
  );
};

export default Layout;