import React, { useState, useEffect } from 'react';
import { X, BarChart3, Calendar, Trophy, Target, TrendingUp, Clock, Dumbbell } from 'lucide-react';
import ChartsSection from './ChartsSection';
import { Theme } from './ThemeSelector';
import { getRecentWorkouts, Workout } from '../services/api';

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  currentTheme: Theme;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen, currentTheme }) => {

  const [workoutHistory, setWorkoutHistory] = useState<Workout[]>([]);
  useEffect(() => {
    const fetchWorkoutHistory = async () => {
      try {
        const workouts = await getRecentWorkouts();
        setWorkoutHistory(workouts);
      } catch (error) {
        console.error('Error fetching workouts:', error);
      }
    };

    fetchWorkoutHistory();
  }, []);

  const getRelativeTime = (dateString: string): string => {
    const workoutDate = new Date(dateString);
    const today = new Date();

    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const workoutStart = new Date(workoutDate.getFullYear(), workoutDate.getMonth(), workoutDate.getDate());

    const diffTime = todayStart.getTime() - workoutStart.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    else if (diffDays === 1) return 'Yesterday';
    else if (diffDays <= 7) return `${diffDays} days ago`;
    else return workoutDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }


  const stats = [
    { label: 'Weekly Goals', value: '4/5', icon: Target, color: 'text-blue-600' },
    { label: 'Streak', value: '7 days', icon: Trophy, color: 'text-yellow-600' },
    { label: 'Avg Duration', value: '42 min', icon: Clock, color: 'text-green-600' },
    { label: 'Progress', value: '+12%', icon: TrendingUp, color: 'text-purple-600' },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:relative lg:translate-x-0 z-30 
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        transition-transform duration-300 ease-in-out
        w-80 h-full ${currentTheme.surface} backdrop-blur-md border-r border-slate-200
      `}>
        <div className="p-6 h-full flex flex-col">
          {/* Close button for mobile */}
          <div className="flex items-center justify-between mb-6 lg:hidden">
            <h2 className="text-lg font-semibold text-slate-900">Workout Data</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-xl hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5 text-slate-600" />
            </button>
          </div>

          {/* Quick Stats */}
          <div className="space-y-4 mb-8">
            <h3 className="text-sm font-medium text-slate-700 uppercase tracking-wider">Quick Stats</h3>
            <div className="grid grid-cols-2 gap-3">
              {stats.map((stat, index) => {
                const Icon = stat.icon;
                return (
                  <div key={index} className={`${currentTheme.surface} backdrop-blur-sm rounded-xl p-4 border border-slate-100 hover:shadow-md transition-all duration-200`}>
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className={`w-4 h-4 ${stat.color}`} />
                      <span className="text-xs text-slate-600">{stat.label}</span>
                    </div>
                    <p className="text-lg font-bold text-slate-900">{stat.value}</p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Workouts */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-slate-700 uppercase tracking-wider mb-4">Recent Workouts</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {workoutHistory.length === 0 ? (
                <div className="text-slate-500 text-sm">Loading workouts...</div>
              ) : (
                workoutHistory.map((workout) => (
                  <div
                    key={workout.id}
                    className={`${currentTheme.surface} backdrop-blur-sm rounded-xl p-4 border border-slate-100 hover:shadow-md transition-all duration-200 cursor-pointer group`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 bg-gradient-to-r ${currentTheme.primary} rounded-full`}></div>
                        <h4 className="font-medium text-slate-900 group-hover:text-blue-600 transition-colors">
                          {workout.title}
                        </h4>
                      </div>
                      <span className="text-xs text-slate-500">{getRelativeTime(workout.date)}</span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{workout.duration}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Dumbbell className="w-3 h-3" />
                        <span>Total sets {workout.sets}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Charts and Analytics Section */}
          <div className="mt-6">
            <ChartsSection />
          </div>

          {/* Action Buttons */}
          <div className="mt-6 space-y-3">
            <button className={`w-full bg-gradient-to-r ${currentTheme.primary} text-white rounded-xl py-3 px-4 font-medium hover:opacity-90 transition-all duration-200 flex items-center justify-center gap-2`}>
              <BarChart3 className="w-4 h-4" />
              View Full Analytics
            </button>
            <button className="w-full bg-slate-100 text-slate-700 rounded-xl py-3 px-4 font-medium hover:bg-slate-200 transition-colors flex items-center justify-center gap-2">
              <Calendar className="w-4 h-4" />
              Schedule Workout
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;