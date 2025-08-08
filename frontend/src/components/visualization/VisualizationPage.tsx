import React from 'react';
import WorkoutFrequencyChart from './WorkoutFrequencyChart';
import TopExerciseChart from './TopExerciseChart';

const VisualizationPage: React.FC = () => {
    return (
        <div className='p-6'>
            <h1 className='text-3xl font-bold text-gray-800 mb-6'>Workout Data Visualization</h1>
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
                <WorkoutFrequencyChart />
                <TopExerciseChart />
            </div>
        </div>
    );
};

export default VisualizationPage;
