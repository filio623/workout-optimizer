import React, { useState } from 'react';
import { Menu, X, Activity, BarChart3, Calendar, User, Settings, Send, Mic } from 'lucide-react';
import ChatInterface from './ChatInterface'; // Updated import
import Sidebar from './Sidebar';
import Header from './Header';
import { Theme, themes } from './ThemeSelector';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentTheme, setCurrentTheme] = useState<Theme>(themes[0]); // Default to Ocean Blue

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
        />
        <ChatInterface currentTheme={currentTheme} /> {/* Updated component usage */}
      </div>
    </div>
  );
};

export default Layout;