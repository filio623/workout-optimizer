import { useState } from 'react';
import { sendChatMessage } from '../../services/api';

const ChatInterface: React.FC = () => {
    const [message, setMessage] = useState('');
    const [messages, setMessages] = useState<string[]>([]);

    const handleSend = async () => {
        if (message.trim()) {
            setMessages([...messages, message]);
            const userMessage = message;
            setMessage('');

            try {
                const response = await sendChatMessage(userMessage);
                setMessages(prev => [...prev, response]);
            } catch (error) {
                setMessages(prev => [...prev, 'Error: could not send a message']);
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
          <div className="flex-1 bg-gray-50 rounded p-3 mb-4 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-gray-500 text-center">Start chatting with your AI fitness assistant!</div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className="bg-blue-100 p-2 rounded mb-2">
                  {msg}
                </div>
              ))
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