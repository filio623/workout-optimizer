import React, { useState, useEffect, useRef } from 'react';
import { Send, Mic, Paperclip, MoreVertical } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { Theme } from './ThemeSelector';
import { sendStreamingChatMessage, uploadFile, fetchSessionMessages, ChatMessage } from '../services/api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot' | 'error';
  timestamp: Date;
}

interface ChatInterfaceProps {
  currentTheme: Theme;
  sessionId: string | null;
  onNewSessionId: (id: string) => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ currentTheme, sessionId, onNewSessionId }) => {
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  const getErrorMessage = (error: any): string => {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return "Can't connect to server. Check your internet connection and make sure the backend is running.";
    }
    if (error.name === 'AbortError' && error.message.includes('timeout')) {
      return "Request timed out. The AI is busy, please try again in a moment.";
    }
    if (error.status) {
      switch (error.status) {
        case 500: return "Server error. The AI might be temporarily unavailable.";
        case 429: return "Too many requests. Please wait a moment before trying again.";
        case 401: return "Authentication error. Please check your API keys.";
        case 404: return "Service not found. Please check if the backend is running.";
        default: return `Server returned error ${error.status}. Please try again.`
      }
    }
    return "Something went wrong please try again.";
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  // Load messages when sessionId changes
  useEffect(() => {
    const loadHistory = async () => {
      if (!sessionId) {
        // New chat -> Show welcome message
        const welcomeMessage: Message = {
            id: 'welcome',
            content: "Hi! I'm your FitBot AI assistant. I can help analyze your workout data and provide personalized recommendations. What would you like to know about your fitness progress?",
            sender: 'bot',
            timestamp: new Date(),
          };
          setMessages([welcomeMessage]);
        return;
      }

      try {
        const history = await fetchSessionMessages(sessionId);
        const mappedMessages: Message[] = history.map(msg => ({
          id: msg.id,
          content: msg.content,
          sender: msg.role === 'assistant' ? 'bot' : 'user',
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(mappedMessages);
        setTimeout(scrollToBottom, 100);
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    };

    loadHistory();
  }, [sessionId]);

  useEffect(() => {
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 100);
    return () => clearTimeout(timer);
  }, [messages, isStreaming]);

  const handleSend = async () => {
    if (inputMessage.trim() && !isStreaming) {
      const userMessage: Message = {
        id: Date.now().toString(),
        content: inputMessage,
        sender: 'user',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, userMessage]);
      const userText = inputMessage;
      setInputMessage('');
      setIsStreaming(true);

      const aiMessageId = (Date.now() + 1).toString();
      // Add a placeholder AI message
      setMessages(prev => [...prev, { id: aiMessageId, content: '', sender: 'bot', timestamp: new Date() }]);

      try {
        const reader = await sendStreamingChatMessage(userText, sessionId);
        let receivedContent = '';
        let isFirstChunk = true;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          let chunk = new TextDecoder().decode(value);

          // Check for Session ID in first chunk
          if (isFirstChunk) {
            // Chunk might be "SESSION_ID:xyz\nActual content..."
            const match = chunk.match(/^SESSION_ID:(.*?)\n/);
            if (match) {
               const newSessionId = match[1].trim();
               if (!sessionId) {
                   onNewSessionId(newSessionId);
               }
               // Remove the session ID line from content
               chunk = chunk.substring(match[0].length);
            }
            isFirstChunk = false;
          }

          receivedContent += chunk;

          // Update the content of the AI message as chunks arrive
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId ? { ...msg, content: receivedContent } : msg
            )
          );
        }
      } catch (error) {
        console.error('Chat streaming error:', error);
        setMessages(prev =>
          prev.map(msg =>
            msg.id === aiMessageId ? { ...msg, content: getErrorMessage(error), sender: 'error' } : msg
          )
        );
      } finally {
        setIsStreaming(false);
      }
    }
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Add a user message indicating file upload
    const userMessage: Message = {
      id: Date.now().toString(),
      content: `Uploading file: ${file.name}...`,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);

    try {
      const response = await uploadFile(file);
      
      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `✅ Successfully uploaded **${file.name}**.\n\nParsed ${response.new_records || response.records_synced || 'some'} new records. I can now analyze this data for you.`, 
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Upload failed:', error);
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `❌ Failed to upload file: ${getErrorMessage(error)}`,
        sender: 'error',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsStreaming(false);
      // Reset input so same file can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
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
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={{
            id: typeof msg.id === 'string' ? parseInt(msg.id) || 0 : parseInt(msg.id), // Ensure ID is number for MessageBubble
            content: msg.content,
            sender: msg.sender === 'error' ? 'bot' : msg.sender, // Render error messages as bot messages
            timestamp: formatTime(msg.timestamp)
          }} currentTheme={currentTheme} />
        ))}

        {isStreaming && <TypingIndicator currentTheme={currentTheme} />}

        {/* Welcome suggestions */}
        {messages.length <= 1 && (
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
              onClick={() => setInputMessage(suggestion)} // Update inputMessage, not send directly
            >
              {suggestion}
            </button>
          ))}
        </div>
        )}
      </div>

      {/* Input Area */}
      <div className={`${currentTheme.surface} backdrop-blur-md border-t border-slate-200 px-6 py-4`}>
        <div className="flex items-center gap-3">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="hidden" 
            accept=".csv,.xls,.xlsx,.xml,application/json" 
          />
          <button 
            onClick={handleFileClick}
            className="p-3 rounded-xl hover:bg-slate-100 transition-colors"
            title="Upload Nutrition (Excel) or Health (JSON/XML) file"
          >
            <Paperclip className="w-5 h-5 text-slate-600" />
          </button>

          <div className="flex-1 relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your workouts..."
              className="w-full bg-slate-100 rounded-2xl px-6 py-3 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all duration-200"
              disabled={isStreaming}
            />
          </div>

          <button className="p-3 rounded-xl hover:bg-slate-100 transition-colors">
            <Mic className="w-5 h-5 text-slate-600" />
          </button>

          <button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isStreaming}
            className={`p-3 bg-gradient-to-r ${currentTheme.primary} text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
