const API_BASE_URL = 'http://localhost:8000';

export const sendChatMessage = async (message: string, sessionId: string = 'default_user') => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            const error = new Error('Failed to send message');
            (error as any).status = response.status;
            throw error;
        }
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error sending chat message:', error);
        throw error;
    }
};