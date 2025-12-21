import React, { useState, useEffect } from 'react';
import { X, BarChart3, Calendar, Trophy, Target, TrendingUp, Clock, Dumbbell } from 'lucide-react';
import ChartsSection from './ChartsSection';
import { Theme } from './ThemeSelector';
import { getRecentWorkouts, fetchDashboardStats, syncWorkouts, Workout, DashboardStats } from '../services/api';

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  currentTheme: Theme;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen, currentTheme }) => {

  const [workoutHistory, setWorkoutHistory] = useState<Workout[]>([]);
  const [dashboardData, setDashboardData] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = async (isRefresh = false) => {
    if (!isRefresh) setLoading(true);
    
    // Fetch workouts
    try {
      const workouts = await getRecentWorkouts();
      setWorkoutHistory(workouts || []);
    } catch (error) {
      console.error('Error fetching workouts:', error);
      if (!isRefresh) setWorkoutHistory([]);
    }

    // Fetch stats
    try {
      const stats = await fetchDashboardStats();
      setDashboardData(stats);
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
    
    if (!isRefresh) setLoading(false);
  };

  useEffect(() => {
    // 1. Initial load from cache (fast)
    loadData();

    // 2. Background sync (slower) -> then reload
    const performSync = async () => {
      await syncWorkouts();
      // Reload data after sync to show latest
      loadData(true); 
    };

    performSync();
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
    { 
      label: 'Weekly Goals', 
      value: dashboardData?.quickStats.weeklyGoals || '0/5', 
      icon: Target, 
      color: 'text-blue-600' 
    },
    { 
      label: 'Streak', 
      value: dashboardData?.quickStats.streak || '0 active days', 
      icon: Trophy, 
      color: 'text-yellow-600' 
    },
    { 
      label: 'Avg Duration', 
      value: dashboardData?.quickStats.avgDuration || '0 min', 
      icon: Clock, 
      color: 'text-green-600' 
    },
    { 
      label: 'Progress', 
      value: dashboardData?.quickStats.progress || '0%', 
      icon: TrendingUp, 
      color: 'text-purple-600' 
    },
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
        <div className="p-6 h-full flex flex-col overflow-y-auto custom-scrollbar">
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
            <div className="space-y-3">
              {loading ? (
                <div className="text-slate-500 text-sm animate-pulse">Loading workouts...</div>
              ) : workoutHistory.length === 0 ? (
                <div className="text-slate-500 text-sm italic">No recent workouts found.</div>
              ) : (
                workoutHistory.map((workout) => (
                  <div
                    key={workout.id}
                    className={`${currentTheme.surface} backdrop-blur-sm rounded-xl p-4 border border-slate-100 hover:shadow-md transition-all duration-200 cursor-pointer group`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 bg-gradient-to-r ${currentTheme.primary} rounded-full`}></div>
                        <h4 className="font-medium text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-1">
                          {workout.title || 'Untitled Workout'}
                        </h4>
                      </div>
                      <span className="text-xs text-slate-500 whitespace-nowrap">{getRelativeTime(workout.date)}</span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-slate-600">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>{workout.duration_minutes || 0} min</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Dumbbell className="w-3 h-3" />
                        <span>{workout.total_sets || 0} sets</span>
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
          <div className="mt-6 space-y-3 pb-6">
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