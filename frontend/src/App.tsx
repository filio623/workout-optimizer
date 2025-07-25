import Header from './components/layout/header';
import ChatInterface from './components/chat/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="App bg-gray-100 min-h-screen">
      <Header />
      <main className="p-4">
        <h2 className="text-2xl font-bold text-gray-800">Welcome to Workout Optimizer!</h2>
        <p className="text-gray-600">Your AI Powered fitness companion</p>
        <ChatInterface />
      </main>
    </div>
  );
}

export default App;
