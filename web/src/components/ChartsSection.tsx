import React from 'react';
import { BarChart3, TrendingUp, Activity, Calendar, Target, Zap } from 'lucide-react';

const ChartsSection: React.FC = () => {
  // Mock data for visualization previews
  const weeklyProgress = [
    { day: 'Mon', value: 85 },
    { day: 'Tue', value: 92 },
    { day: 'Wed', value: 78 },
    { day: 'Thu', value: 96 },
    { day: 'Fri', value: 88 },
    { day: 'Sat', value: 94 },
    { day: 'Sun', value: 82 },
  ];

  const muscleGroups = [
    { name: 'Chest', percentage: 85, color: 'bg-blue-500' },
    { name: 'Back', percentage: 92, color: 'bg-green-500' },
    { name: 'Legs', percentage: 78, color: 'bg-purple-500' },
    { name: 'Arms', percentage: 88, color: 'bg-orange-500' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-slate-700" />
        <h3 className="text-sm font-medium text-slate-700 uppercase tracking-wider">Analytics Dashboard</h3>
      </div>

      {/* Weekly Progress Chart */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-slate-100">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-slate-900">Weekly Progress</h4>
          <TrendingUp className="w-4 h-4 text-green-500" />
        </div>
        <div className="flex items-end justify-between h-20 gap-1">
          {weeklyProgress.map((day, index) => (
            <div key={index} className="flex flex-col items-center flex-1">
              <div 
                className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-t-sm transition-all duration-300 hover:from-blue-600 hover:to-blue-500"
                style={{ height: `${day.value}%` }}
              ></div>
              <span className="text-xs text-slate-500 mt-1">{day.day}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Muscle Group Progress */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-slate-100">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-slate-900">Muscle Groups</h4>
          <Target className="w-4 h-4 text-purple-500" />
        </div>
        <div className="space-y-3">
          {muscleGroups.map((group, index) => (
            <div key={index}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">{group.name}</span>
                <span className="text-slate-500">{group.percentage}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div 
                  className={`${group.color} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${group.percentage}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-slate-100">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-slate-900">Performance</h4>
          <Zap className="w-4 h-4 text-yellow-500" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">+12%</div>
            <div className="text-xs text-slate-500">Strength</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">+8%</div>
            <div className="text-xs text-slate-500">Endurance</div>
          </div>
        </div>
      </div>

      {/* Workout Intensity Heatmap Preview */}
      <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 border border-slate-100">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-slate-900">Intensity Heatmap</h4>
          <Activity className="w-4 h-4 text-red-500" />
        </div>
        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: 28 }, (_, i) => {
            const intensity = Math.random();
            return (
              <div
                key={i}
                className={`aspect-square rounded-sm ${
                  intensity > 0.7 ? 'bg-green-500' :
                  intensity > 0.4 ? 'bg-green-300' :
                  intensity > 0.2 ? 'bg-green-100' :
                  'bg-slate-100'
                }`}
                title={`Day ${i + 1}: ${Math.round(intensity * 100)}% intensity`}
              ></div>
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-slate-500 mt-2">
          <span>4 weeks ago</span>
          <span>Today</span>
        </div>
      </div>

      {/* Quick Action for Full Dashboard */}
      <button className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl py-3 px-4 font-medium hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 flex items-center justify-center gap-2">
        <Calendar className="w-4 h-4" />
        Open Full Dashboard
      </button>
    </div>
  );
};

export default ChartsSection;