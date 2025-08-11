import React from 'react';
import { Bot, User } from 'lucide-react';
import { Theme } from './ThemeSelector';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: number;
  content: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

interface MessageBubbleProps {
  message: Message;
  currentTheme: Theme;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, currentTheme }) => {
  const isBot = message.sender === 'bot';

  return (
    <div className={`flex gap-3 ${isBot ? 'items-start' : 'items-start justify-end'}`}>
      {isBot && (
        <div className={`w-8 h-8 bg-gradient-to-br ${currentTheme.primary} rounded-xl flex items-center justify-center flex-shrink-0 mt-1`}>
          <Bot className="w-4 h-4 text-white" />
        </div>
      )}
      
      <div className={`max-w-[70%] ${isBot ? 'order-2' : 'order-1'}`}>
        <div
          className={`
            relative rounded-2xl px-4 py-3 shadow-sm
            ${isBot
              ? `${currentTheme.surface} border border-slate-200 text-slate-900`
              : `bg-gradient-to-r ${currentTheme.primary} text-white`
            }
          `}
        >
          {/* Message content with ReactMarkdown for AI responses */}
          {isBot ? (
            <div className="prose prose-sm max-w-none prose-slate prose-headings:text-slate-900 prose-p:text-slate-900 prose-strong:text-slate-900 prose-ul:text-slate-900 prose-ol:text-slate-900 prose-li:text-slate-900">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          ) : (
            <div className="whitespace-pre-wrap">{message.content}</div>
          )}
        </div>
        
        <div className={`text-xs text-slate-500 mt-1 ${isBot ? 'text-left' : 'text-right'}`}>
          {message.timestamp}
        </div>
      </div>
      
      {!isBot && (
        <div className={`w-8 h-8 bg-gradient-to-br ${currentTheme.accent} rounded-xl flex items-center justify-center flex-shrink-0 mt-1 order-2`}>
          <User className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;