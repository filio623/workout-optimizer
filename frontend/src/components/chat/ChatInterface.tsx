const ChatInterface = () => {
    return (
        <div className="bg-white rounded-lg shadow-md p-4 h-96 flex flex-col">
            <div className="flex-1 bg-gray-50 rounded p-3 mb-4 overflow-y-auto">
                <div className="text-gray-500 text-center">Start chatting with your AI fitness assistant</div>
            </div>
            <div className="flex gap-2">
                <input
                    type="text"
                    placeholder="Ask about your workouts"
                    className="flex-1 border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;