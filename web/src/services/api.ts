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

export interface DashboardStats {
    weeklyProgress: { day: string; value: number; raw_date: string }[];
    muscleGroups: { name: string; percentage: number; color: string }[];
    performance: { volumeTrend: number; consistency: string };
    heatmap: number[];
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
            const error = new Error('Failed to fetch dashboard stats');
            (error as any).status = response.status;
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

export const uploadFile = async (file: File): Promise<any> => {
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
            const error = new Error('Failed to upload file');
            (error as any).status = response.status;
            // Try to get error details from response
            try {
                const errData = await response.json();
                error.message = errData.detail || 'Failed to upload file';
            } catch (e) {
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