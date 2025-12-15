const API_BASE_URL = '/api';

export interface Workout {
    id: string;
    title: string;
    date: string;
    duration: string;
    sets: number;
}

export const sendStreamingChatMessage = async (message: string, sessionId: string = 'default_user') => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
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
            const error = new Error('Failed to start streaming chat message');
            (error as any).status = response.status;
            throw error;
        }

        if (!response.body) {
            throw new Error('Response body is null, cannot stream.');
        }

        return response.body.getReader();

    } catch (error) {
        console.error('Error starting streaming chat message:', error);
        throw error;
    }
};

export const getRecentWorkouts = async (): Promise<Workout[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/workout-history`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        if (!response.ok) {
            const error = new Error('Failed to fetch recent workouts');
            (error as any).status = response.status;
            throw error;
        }

        const data = await response.json();
        return data;

    } catch (error) {
        console.error('Error fetching recent workouts:', error);
        throw error;
    }

}

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