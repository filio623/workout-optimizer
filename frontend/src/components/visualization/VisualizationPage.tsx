import React from 'react';

const VisualizationPage: React.FC = () => {
    return (
        <div className='p-6'>
            <h1 className='text-3xl font-bold text-gray-800 mb-6'>Workout Data Visualization</h1>
            <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
                <div className='bg-white p-6 rounded-lg shadow-md'>
                    <h2 className='text-xl font-semibold mb-4'>Workout Frequency</h2>
                    <p className='text-gray-600'>Chart showing workout frequency over the last 8 weeks will appear here.</p>
                </div>
                <div className='bg-white p-6 rounded-lg shadow-md'>
                    <h2 className='text-xl font-semibold mb-4'>Top Exercises</h2>
                    <p className='text-gray-600'>Chart showing most performed exercises from the last 3 months will appear here.</p>
                </div>
            </div>
        </div>
    );
};

export default VisualizationPage;