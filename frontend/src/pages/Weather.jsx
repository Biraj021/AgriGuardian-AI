import React, { useEffect, useState } from 'react';
import { getWeatherApi } from '../api/client';
import WeatherForecast from '../components/cards/WeatherForecast';
import { dashboardMockData } from '../services/mockData';
import Skeleton from '../components/common/Skeleton';

const MOCK_WEATHER = dashboardMockData.environmentalIntel.weather;

function normalizeWeatherResponse(apiRes) {
  // The backend /weather/current returns a flat demo object.
  // Normalize it into the shape WeatherForecast.jsx expects.
  if (!apiRes) return null;

  // If it already has the full forecast shape, use it directly
  if (apiRes.forecast && Array.isArray(apiRes.forecast)) return apiRes;

  // Otherwise, build a compatible shape from the flat API response
  return {
    currentTemp: apiRes.temperature ?? MOCK_WEATHER.currentTemp,
    condition: apiRes.condition ?? MOCK_WEATHER.condition,
    feelsLike: apiRes.feelsLike ?? MOCK_WEATHER.feelsLike,
    humidity: apiRes.humidity ?? MOCK_WEATHER.humidity,
    wind: apiRes.wind ?? MOCK_WEATHER.wind,
    forecast: MOCK_WEATHER.forecast, // use mock forecast since API doesn't provide it yet
  };
}

export default function WeatherPage() {
  const [loading, setLoading] = useState(true);
  const [weatherData, setWeatherData] = useState(null);
  const [isDemo, setIsDemo] = useState(true);
  const [apiMessage, setApiMessage] = useState('');

  useEffect(() => {
    async function fetchWeather() {
      try {
        const res = await getWeatherApi();
        const normalized = normalizeWeatherResponse(res);
        setWeatherData(normalized);
        setIsDemo(res.source === 'demo' || !res.is_live);
        if (res.message) setApiMessage(res.message);
      } catch {
        setWeatherData(MOCK_WEATHER);
        setIsDemo(true);
        setApiMessage('Live weather unavailable. Showing fallback demo data.');
      } finally {
        setLoading(false);
      }
    }
    fetchWeather();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-2xl mx-auto space-y-4">
        <Skeleton className="h-8 w-40 rounded-lg" />
        <Skeleton className="h-64 w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Weather</h1>
        {isDemo && (
          <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
            Demo Data
          </span>
        )}
      </div>

      {isDemo && apiMessage && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm p-4 rounded-xl">
          {apiMessage}
        </div>
      )}

      <WeatherForecast
        weather={weatherData || MOCK_WEATHER}
        location="Pune, Maharashtra"
        isDemo={isDemo}
      />
    </div>
  );
}
