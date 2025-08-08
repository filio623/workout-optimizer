import { useState } from 'react';
import Header from './components/layout/header';
import ChatInterface from './components/chat/ChatInterface';
import VisualizationPage from './components/visualization/VisualizationPage';

type ActiveView = 'chat' | 'visualization';

function App() {
  const [activeView, setActiveView] = useState<ActiveView>('chat');

  return (
    <div className="bg-gray-100 min-h-screen p-10">
      <Header />
      <nav className="mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveView('chat')}
            className={`px-4 py-2 rounded-md font-medium ${activeView === 'chat'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
          >
            Chat
          </button>
          <button
            onClick={() => setActiveView('visualization')}
            className={`px-4 py-2 rounded-md font-medium ${activeView === 'visualization'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
          >
            Visualization
          </button>
        </div>
      </nav>
      <main className="p-4">
        {activeView === 'chat' && (
          <>
            <h2 className="text-2xl font-bold text-gray-800">Welcome to Workout Optimizer!</h2>
            <p className="text-gray-600">Your AI Powered fitness companion</p>
            <ChatInterface />
          </>
        )}
        {activeView === 'visualization' && <VisualizationPage />}
      </main>
    </div>
  );
}

export default App;
