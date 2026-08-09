import React from 'react';

export default function StatCard({ title, value, unit, icon: Icon, trend }) {
  // Simple trend logic for visual cues
  const isUp = trend === 'up';
  const isFlat = trend === 'flat';
  
  return (
    <div className="bg-surface p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <div className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center text-gray-400">
          <Icon size={20} />
        </div>
      </div>
      
      <div className="flex items-baseline gap-1">
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <span className="text-sm font-medium text-gray-500">{unit}</span>
      </div>
      
      {trend && (
        <div className="mt-2 flex items-center text-xs font-medium">
          {isUp ? (
            <span className="text-primary-600 bg-primary-50 px-2 py-0.5 rounded-md">↑ Increasing</span>
          ) : isFlat ? (
            <span className="text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">→ Stable</span>
          ) : (
            <span className="text-secondary-600 bg-secondary-50 px-2 py-0.5 rounded-md">↓ Decreasing</span>
          )}
        </div>
      )}
    </div>
  );
}
