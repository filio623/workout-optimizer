import React from 'react';

const Header: React.FC = () => {
    return (
        <header className="bg-blue-600 text-white p-4">
            <h1 className="text-2xl font-bold">Workout Optimizer</h1>
            <p className="text-sm">AI Powered Fitness Analysis and routine Creation</p>
        </header>
    );
};

export default Header;