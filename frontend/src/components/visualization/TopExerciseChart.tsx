import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const TopExerciseChart: React.FC = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);


    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/top-exercises');
                const result = await response.json();

                console.log('Top exercises API response:', result);
                console.log('Top exercises data:', result.data);
                setData(result.data);
                setLoading(false);
            } catch (err) {
                setError('Failed to load exercise data');
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold mb-4">Top Exercises</h3>
                <p>Loading...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold mb-4">Top Exercises</h3>
                <p className="text-red-500">{error}</p>
            </div>
        );
    }

    return (
        <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4">Top Exercises</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="exerciseName" width={150} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#10B981" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TopExerciseChart;
