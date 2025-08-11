import React, { useState, useEffect } from 'react';
import { Send, Mic, Paperclip, MoreVertical } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { Theme } from './ThemeSelector';
import { sendChatMessage } from '../services/api';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'ai' | 'error';
  timestamp: Date;
}

interface ChatAreaProps {
  currentTheme: Theme;
}

const ChatArea: React.FC<ChatAreaProps> = ({ currentTheme }) => {
  const STORAGE_KEY = 'workout-optimizer-messages';

  const saveMessagesToStorage = (messages: Message[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
      console.error('Failed to save messages to local storage:', error);
    }
  };

  const loadMessagesFromStorage = (): Message[] => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const messages = JSON.parse(stored);
        // Convert timestamp strings to Date objects
        return messages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
      }
    } catch (error) {
      console.error('Failed to load messages from local storage:', error);
    }
    return [];
  };

  const scrollToBottom = () => {
    const messageContainer = document.querySelector('.overflow-y-auto');
    if (messageContainer) {
      messageContainer.scrollTop = messageContainer.scrollHeight;
    }
  };

  const getErrorMessage = (error: any): string => {
    // Network connection errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return "Can't connect to server. Check your internet connection and make sure the backend is running.";
    }

    // Timeout errors
    if (error.name === 'AbortError' && error.message.includes('timeout')) {
      return "Request timed out. The AI is busy, please try again in a moment.";
    }

    // HTTP Status errors
    if (error.status) {
      switch (error.status) {
        case 500:
          return "Server error. The AI might be temporarily unavailable.";
        case 429:
          return "Too many requests. Please wait a moment before trying again.";
        case 401:
          return "Authentication error. Please check your API keys.";
        case 404:
          return "Service not found. Please check if the backend is running.";
        default:
          return `Server returned error ${error.status}. Please try again.`;
      }
    }

    // Default fallback
    return "Something went wrong please try again.";
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>(loadMessagesFromStorage());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    saveMessagesToStorage(messages);
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message if no messages exist
  const displayMessages = messages.length === 0 ? [
    {
      id: 'welcome',
      text: "Hi! I'm your FitBot AI assistant. I can help analyze your workout data and provide personalized recommendations. What would you like to know about your fitness progress?",
      type: 'ai' as const,
      timestamp: new Date(),
    }
  ] : messages;

  const handleSend = async () => {
    if (message.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now().toString(),
        text: message,
        type: 'user',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      const userText = message;
      setMessage('');
      setIsLoading(true);

      try {
        const response = await sendChatMessage(userText);
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response,
          type: 'ai',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } catch (error) {
        console.error('Chat error:', error); // For debugging
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: getErrorMessage(error),
          type: 'error',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gradient-to-b from-transparent to-white/30">
      {/* Chat Header */}
      <div className={`${currentTheme.surface} backdrop-blur-md border-b border-slate-200 px-6 py-4`}>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">Workout Analysis Chat</h2>
            <p className="text-sm text-slate-500">AI-powered fitness insights</p>
          </div>
          <button className="p-2 rounded-xl hover:bg-slate-100 transition-colors">
            <MoreVertical className="w-5 h-5 text-slate-600" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {displayMessages.map((msg) => (
          <MessageBubble key={msg.id} message={{
            id: typeof msg.id === 'string' ? parseInt(msg.id) || 0 : msg.id,
            content: msg.text,
            sender: msg.type === 'user' ? 'user' : 'bot',
            timestamp: formatTime(msg.timestamp)
          }} currentTheme={currentTheme} />
        ))}

        {isLoading && <TypingIndicator currentTheme={currentTheme} />}

        {/* Welcome suggestions */}
        <div className="flex flex-wrap gap-2 mt-8">
          {[
            "Analyze my weekly progress",
            "Suggest workout improvements",
            "Compare this month vs last month",
            "What exercises should I focus on?"
          ].map((suggestion, index) => (
            <button
              key={index}
              className={`${currentTheme.surface} backdrop-blur-sm border border-slate-200 rounded-full px-4 py-2 text-sm text-slate-700 hover:shadow-md transition-all duration-200`}
              onClick={() => setMessage(suggestion)}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className={`${currentTheme.surface} backdrop-blur-md border-t border-slate-200 px-6 py-4`}>
        <div className="flex items-center gap-3">
          <button className="p-3 rounded-xl hover:bg-slate-100 transition-colors">
            <Paperclip className="w-5 h-5 text-slate-600" />
          </button>

          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your workouts..."
              className="w-full bg-slate-100 rounded-2xl px-6 py-3 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all duration-200"
            />
          </div>

          <button className="p-3 rounded-xl hover:bg-slate-100 transition-colors">
            <Mic className="w-5 h-5 text-slate-600" />
          </button>

          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className={`p-3 bg-gradient-to-r ${currentTheme.primary} text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatArea;