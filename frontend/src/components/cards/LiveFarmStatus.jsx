import React from 'react';
import Sparkline from '../charts/Sparkline';

const SENSOR_CONFIG = {
  soilMoisture: { label: 'Soil Moisture', icon: '💧', sparkColor: '#3B82F6' },
  temperature:   { label: 'Temperature',   icon: '🌡️', sparkColor: '#EF4444' },
  humidity:      { label: 'Humidity',      icon: '💦', sparkColor: '#10B981' },
  rainfall:      { label: 'Rainfall',      icon: '🌧️', sparkColor: '#F59E0B' },
  waterLevel:    { label: 'Water Level',   icon: '🪣', sparkColor: '#3B82F6' },
};

const STATUS_STYLES = {
  Low:     'text-red-600 bg-red-50',
  High:    'text-red-600 bg-red-50',
  Normal:  'text-green-600 bg-green-50',
  Good:    'text-green-600 bg-green-50',
  'No Rain': 'text-amber-600 bg-amber-50',
};

export default function LiveFarmStatus({ liveStatus }) {
  const sensors = Object.entries(liveStatus);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4">
      {sensors.map(([key, data]) => {
        const config = SENSOR_CONFIG[key];
        const statusStyle = STATUS_STYLES[data.status] || 'text-gray-600 bg-gray-50';
        return (
          <div key={key} className="bg-surface rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium text-gray-500">{config.label}</p>
              <span className="text-lg">{config.icon}</span>
            </div>

            {/* Big value */}
            <div className="flex items-baseline gap-1 mb-1">
              <span className="text-2xl font-bold text-gray-900">{data.value}</span>
              <span className="text-sm text-gray-400 font-medium">{data.unit}</span>
            </div>

            {/* Status badge */}
            <span className={`self-start text-[10px] font-bold px-2 py-0.5 rounded-full mb-3 ${statusStyle}`}>
              {data.status}
            </span>

            {/* Sparkline */}
            <Sparkline data={data.sparkline} color={config.sparkColor} height={36} width={110} />

            {/* Range */}
            <p className="text-[10px] text-gray-400 font-medium mt-2">Range: {data.range}</p>
          </div>
        );
      })}
    </div>
  );
}
