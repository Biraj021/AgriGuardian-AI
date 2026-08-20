import React, { useEffect, useState } from 'react';
import { getAnalyticsApi } from '../api/client';
import { dashboardMockData } from '../services/mockData';
import SensorTrendsChart from '../components/charts/SensorTrendsChart';
import Skeleton from '../components/common/Skeleton';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [isDemo, setIsDemo] = useState(true);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const res = await getAnalyticsApi();
        if (res && res.series) {
          setAnalytics({
            labels: res.series.labels.map((label) => new Date(label).toLocaleString()),
            soilMoisture: res.series.soil_moisture,
            temperature: res.series.temperature,
          });
          setIsDemo(false);
        } else {
          throw new Error('Invalid response');
        }
      } catch (err) {
        setAnalytics(dashboardMockData.analytics);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    }
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto space-y-4">
        <Skeleton className="h-8 w-40 rounded-lg" />
        <Skeleton className="h-[400px] w-full rounded-2xl" />
      </div>
    );
  }

  // Calculate some simple stats for the summary cards
  const currentTemp = analytics?.temperature?.[analytics.temperature.length - 1] || '--';
  const currentMoisture = analytics?.soilMoisture?.[analytics.soilMoisture.length - 1] || '--';
  
  const maxTemp = analytics?.temperature ? Math.max(...analytics.temperature) : '--';
  const minMoisture = analytics?.soilMoisture ? Math.min(...analytics.soilMoisture) : '--';

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        {isDemo && (
          <span className="text-xs font-bold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
            Demo Data
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Latest Temperature</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{currentTemp}°C</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Latest Moisture</p>
          <p className="text-2xl font-bold text-emerald-600 mt-2">{currentMoisture}%</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">7-Day Max Temp</p>
          <p className="text-2xl font-bold text-amber-600 mt-2">{maxTemp}°C</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
          <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">7-Day Min Moisture</p>
          <p className="text-2xl font-bold text-red-500 mt-2">{minMoisture}%</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
        <div className="p-2">
          {/* We'll reuse the SensorTrendsChart, but wrap it to give it more height */}
          <SensorTrendsChart analytics={analytics} />
        </div>
      </div>
    </div>
  );
}
