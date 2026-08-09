import React, { useState, useEffect } from 'react';
import { MdArrowForward, MdAccessTime } from 'react-icons/md';
import { useNavigate } from 'react-router-dom';

const CONDITION_ICONS = {
  Sunny: '☀️', Cloudy: '⛅', Rain: '🌧️', Windy: '🌬️', Snow: '❄️', Storm: '⛈️',
  'Partly Cloudy': '⛅',
};

// Generate real upcoming day labels from today
function getUpcomingDays() {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const today = new Date();
  return Array.from({ length: 5 }, (_, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    return i === 0 ? 'Today' : days[d.getDay()];
  });
}

export default function WeatherForecast({ weather, location, isDemo = false }) {
  const navigate = useNavigate();
  const { currentTemp, condition, feelsLike, humidity, wind, forecast } = weather;

  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000); // update every minute
    return () => clearInterval(timer);
  }, []);

  const dayLabels = getUpcomingDays();

  const currentDateStr = now.toLocaleDateString('en-IN', {
    weekday: 'long', day: '2-digit', month: 'short', year: 'numeric',
  });
  const currentTimeStr = now.toLocaleTimeString('en-IN', {
    hour: '2-digit', minute: '2-digit', hour12: true,
  });

  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5 h-full">
      <div className="flex items-center justify-between mb-1">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-gray-800">Weather Forecast</h3>
            {isDemo && (
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                Demo Data
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 font-medium mt-0.5">{location}</p>
        </div>
        <button
          onClick={() => navigate('/weather')}
          className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all"
        >
          View Full <MdArrowForward size={14} />
        </button>
      </div>

      {/* Live date & time */}
      <div className="flex items-center gap-1.5 text-[10px] text-gray-400 font-medium mb-4">
        <MdAccessTime size={12} />
        <span>{currentDateStr} • {currentTimeStr}</span>
      </div>

      <div className="flex items-center gap-4 mb-5">
        <span className="text-5xl">{CONDITION_ICONS[condition] || '☀️'}</span>
        <div>
          <p className="text-4xl font-bold text-gray-900">{currentTemp}°C</p>
          <p className="text-sm font-medium text-gray-500">{condition}</p>
        </div>
        <div className="ml-auto text-xs text-gray-500 space-y-1 text-right font-medium">
          <p className="flex items-center gap-1 justify-end">
            <span>🌡️</span> Feels like {feelsLike}°C
          </p>
          <p className="flex items-center gap-1 justify-end">
            <span>💧</span> Humidity {humidity}%
          </p>
          <p className="flex items-center gap-1 justify-end">
            <span>💨</span> Wind {wind} km/h
          </p>
        </div>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {forecast.map((day, i) => (
          <div
            key={i}
            className={`flex flex-col items-center gap-1.5 px-3 py-2 rounded-xl flex-1 min-w-[52px] text-center ${i === 0 ? 'bg-primary-50 border border-primary-100' : 'bg-gray-50'}`}
          >
            <p className={`text-[10px] font-bold ${i === 0 ? 'text-primary-700' : 'text-gray-400'}`}>
              {dayLabels[i]}
            </p>
            <span className="text-xl">{CONDITION_ICONS[day.condition] || '☀️'}</span>
            <p className="text-[10px] font-semibold text-gray-600">{day.temp}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
