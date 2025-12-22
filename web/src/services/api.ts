const API_BASE_URL = '/api';

export interface Workout {
    id: string;
    title: string;
    date: string;
    duration_minutes: number;
    total_sets: number;
    source: string;
}

export interface ChatSession {
    id: string;
    session_name: string;
    created_at: string;
    last_activity: string;
}

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

interface ApiError extends Error {
    status?: number;
}

export const fetchChatHistory = async (): Promise<ChatSession[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/history`, {
            method: 'GET',
            headers: { 'accept': 'application/json' }
        });
        if (!response.ok) throw new Error('Failed to fetch chat history');
        return await response.json();
    } catch (error) {
        console.error('Error fetching chat history:', error);
        throw error;
    }
};

export const fetchSessionMessages = async (sessionId: string): Promise<ChatMessage[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/${sessionId}`, {
            method: 'GET',
            headers: { 'accept': 'application/json' }
        });
        if (!response.ok) throw new Error('Failed to fetch messages');
        return await response.json();
    } catch (error) {
        console.error('Error fetching messages:', error);
        throw error;
    }
};

export const deleteChatSession = async (sessionId: string): Promise<void> => {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/${sessionId}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete session');
    } catch (error) {
        console.error('Error deleting session:', error);
        throw error;
    }
};

export const sendStreamingChatMessage = async (message: string, sessionId: string | null = null) => {
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
            const error = new Error('Failed to start streaming chat message') as ApiError;
            error.status = response.status;
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

export const syncWorkouts = async (): Promise<void> => {
    try {
        await fetch(`${API_BASE_URL}/workouts/sync`, {
            method: 'POST',
        });
    } catch (error) {
        console.error('Background sync failed:', error);
        // Don't throw, just log. We don't want to break the UI if sync fails.
    }
};

export const getRecentWorkouts = async (): Promise<Workout[]> => {
    try {
        const response = await fetch(`${API_BASE_URL}/workouts/cached?limit=3`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        if (!response.ok) {
            const error = new Error('Failed to fetch recent workouts') as ApiError;
            error.status = response.status;
            throw error;
        }

        const data = await response.json();
        return data.workouts; // Backend returns { workouts: [...] }

    } catch (error) {
        console.error('Error fetching recent workouts:', error);
        throw error;
    }

}

export interface DashboardStats {
    weeklyProgress: { day: string; value: number; raw_date: string }[];
    muscleGroups: { name: string; percentage: number; color: string }[];
    performance: { volumeTrend: number; consistency: string };
    heatmap: number[];
    quickStats: {
        weeklyGoals: string;
        streak: string;
        avgDuration: string;
        progress: string;
    };
}

export const fetchDashboardStats = async (): Promise<DashboardStats> => {
    try {
        const response = await fetch(`${API_BASE_URL}/dashboard/stats`, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
            }
        });
        if (!response.ok) {
            const error = new Error('Failed to fetch dashboard stats') as ApiError;
            error.status = response.status;
            throw error;
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        throw error;
    }
};

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
            const error = new Error('Failed to send message') as ApiError;
            error.status = response.status;
            throw error;
        }

        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error sending chat message:', error);
        throw error;
    }
};

export const uploadFile = async (file: File): Promise<unknown> => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        let endpoint = '/nutrition/upload'; // Default to nutrition (Excel/CSV)

        // Routing logic based on file type/name
        if (file.name.endsWith('.json') || file.name.includes('apple_health')) {
             // Apple Health JSON export
             endpoint = '/apple-health/upload'; 
        } else if (file.name.endsWith('.xml') || file.name.includes('export.xml')) {
             // Apple Health XML export (if supported in future, currently json is main focus)
             // Note: Current backend apple_health.py supports JSON. 
             // If we had an XML parser, we'd route it there. 
             // For now, if user uploads XML, we might fail or need a different route.
             // But based on current apple_health.py, it expects JSON.
             endpoint = '/apple-health/upload'; 
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = new Error('Failed to upload file') as ApiError;
            error.status = response.status;
            // Try to get error details from response
            try {
                const errData = await response.json();
                error.message = errData.detail || 'Failed to upload file';
            } catch {
                // ignore
            }
            throw error;
        }

        return await response.json();
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
};