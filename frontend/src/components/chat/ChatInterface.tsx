import { useState, useEffect } from 'react';
import { sendChatMessage } from '../../services/api';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'ai' | 'error';
  timestamp: Date;
}


const ChatInterface: React.FC = () => {

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
        //convert timestamp strings to Date objects
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

  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>(loadMessagesFromStorage());
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    saveMessagesToStorage(messages);
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getErrorMessage = (error: any): string => {
    // network connection errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return "Can't connect to server. Check your internet connection and make sure the backend is running.";
    }
    // Timeout errors
    if (error.name === 'AbortError' && error.message.includes('timeout')) {
      return "Request timed out. The AI is busy, please try again in a moment.";
    }
    //HTTP Status errors
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

    //Default fallback
    return "Something went wrong please try again.";
  }


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
        console.error('Chat error:', error); //for debugging
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
    if (e.key == 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-96 flex flex-col">
      <div className="flex-1 bg-gray-50 rounded p-3 mb-4 overflow-y-auto flex flex-col">
        {messages.length === 0 ? (
          <div className="text-gray-500 text-center">Start chatting with your AI fitness assistant!</div>
        ) : (
          messages.map((msg, index) => {
            const messageClasses = `p-2 rounded mb-2 max-w-xs ${msg.type === 'user'
              ? 'bg-blue-500 text-white ml-auto'
              : msg.type === 'error'
                ? 'bg-red-100 text-red-800 mr-auto'
                : 'bg-gray-200 text-gray-800 mr-auto'
              }`;

            return (
              <div key={index} className={`${messageClasses} message-container`}>
                <div>
                  {msg.type === 'ai' ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{msg.text}</ReactMarkdown>
                    </div>
                  ) : (
                    <div>{msg.text}</div>
                  )}
                </div>
                <div className={`timestamp ${
                  msg.type === 'user' 
                    ? 'text-white' 
                    : msg.type === 'error'
                    ? 'text-red-800'
                    : 'text-gray-800'
                      }`}>
                  {formatTime(msg.timestamp)}
                </div>
              </div>
            );
          })
        )}
        {isLoading && (
          <div className="p-2 rounded mb-2 max-w-xs bg-gray-200 text-gray-800 mr-auto">
            <div className="flex items-center">
              <div className="text-sm">AI is thinking...</div>
              <div className="ml-2 flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask about your workouts..."
          className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;