import React, { useState, useEffect, useCallback } from 'react';
import { dashboardMockData } from '../../services/mockData';
import { useAuth } from '../../context/AuthContext';
import {
  getDashboardApi,
  getIrrigationRecommendationApi,
  getWeatherApi,
  getMarketApi,
  getAnalyticsApi,
  getRecommendationHistoryApi,
} from '../../api/client';
import Skeleton from '../../components/common/Skeleton';
import HeroRecommendationCard from '../../components/cards/HeroRecommendationCard';
import LiveFarmStatus from '../../components/cards/LiveFarmStatus';
import WeatherForecast from '../../components/cards/WeatherForecast';
import DisasterAlerts from '../../components/cards/DisasterAlerts';
import MarketPrices from '../../components/cards/MarketPrices';
import GovernmentSchemes from '../../components/cards/GovernmentSchemes';
import SensorTrendsChart from '../../components/charts/SensorTrendsChart';
import RecommendationHistory from '../../components/cards/RecommendationHistory';

function DashboardSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="mb-4">
        <Skeleton className="h-6 w-40 mb-1.5" />
        <Skeleton className="h-3.5 w-28" />
      </div>
      <Skeleton className="h-52 w-full rounded-2xl" />
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-36 rounded-xl" />)}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [farm, setFarm] = useState(null);
  const [dbRecommendation, setDbRecommendation] = useState(null);
  const [device, setDevice] = useState(null);
  const [latestSensor, setLatestSensor] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [backendError, setBackendError] = useState(null);
  const [weatherIsDemo, setWeatherIsDemo] = useState(true);
  const [marketIsDemo, setMarketIsDemo] = useState(true);

  const [soilMoisture, setSoilMoisture] = useState(25.0);
  const [temperature, setTemperature] = useState(32.0);
  const [humidity, setHumidity] = useState(45.0);
  const [rainfall, setRainfall] = useState(0.0);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState(null);
  const [aiError, setAiError] = useState(null);

  useEffect(() => {
    async function loadData() {
      setBackendError(null);
      try {
        const dashboardRes = await getDashboardApi();
        if (dashboardRes.farm) {
          setFarm(dashboardRes.farm);
        }
        if (dashboardRes.latest_recommendation) {
          setDbRecommendation(dashboardRes.latest_recommendation);
        }
        setDevice(dashboardRes.device || null);
        if (dashboardRes.latest_sensor) {
          const s = dashboardRes.latest_sensor;
          setLatestSensor(s);
          if (s.soil_moisture != null) setSoilMoisture(s.soil_moisture);
          if (s.temperature != null) setTemperature(s.temperature);
          if (s.humidity != null) setHumidity(s.humidity);
        }
        const [analyticsRes, historyRes] = await Promise.all([
          getAnalyticsApi(), getRecommendationHistoryApi(),
        ]);
        setAnalytics(analyticsRes);
        setHistory(historyRes.recommendations || []);
      } catch (e) {
        console.warn('Dashboard API unavailable:', e);
        setBackendError(e.message);
      }

      try {
        const weatherRes = await getWeatherApi();
        setWeatherIsDemo(weatherRes.source === 'demo' || !weatherRes.is_live);
      } catch {
        setWeatherIsDemo(true);
      }

      try {
        const marketRes = await getMarketApi();
        setMarketIsDemo(marketRes.source === 'demo' || !marketRes.is_live);
      } catch {
        setMarketIsDemo(true);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleRunAi = useCallback(async () => {
    setAiLoading(true);
    setAiError(null);
    try {
      const res = await getIrrigationRecommendationApi({
        soil_moisture: parseFloat(soilMoisture),
        temperature: parseFloat(temperature),
        humidity: parseFloat(humidity),
        rainfall_prev_day: parseFloat(rainfall),
      });
      setAiResult(res);
      const historyRes = await getRecommendationHistoryApi();
      setHistory(historyRes.recommendations || []);
    } catch (err) {
      setAiError(err.message || 'AI prediction failed');
      setAiResult(null);
    } finally {
      setAiLoading(false);
    }
  }, [soilMoisture, temperature, humidity, rainfall]);

  if (loading) return <DashboardSkeleton />;

  const farmName = farm?.name || 'No active farm';
  const cropName = farm?.primary_crop || 'No crop configured';

  const heroRecommendation = aiResult
    ? {
        decision: aiResult.recommendation,
        confidence: aiResult.confidence,
        reasoning: [
          aiResult.reason,
          `Model prediction: ${aiResult.prediction === 1 ? 'Irrigate' : 'Skip'}`,
          `Inputs — Soil: ${soilMoisture}%, Temp: ${temperature}°C, Humidity: ${humidity}%, Rain: ${rainfall} mm`,
        ],
        recommendedTime: aiResult.prediction === 1 ? '5:30 AM (Early Morning)' : 'N/A (Adequate Moisture)',
        estWater: aiResult.prediction === 1 ? '1,200 Liters / Acre' : '0 Liters',
      }
    : dbRecommendation
    ? {
        decision: dbRecommendation.decision,
        confidence: dbRecommendation.confidence,
        reasoning: [dbRecommendation.reason],
        recommendedTime: 'Check live status',
        estWater: 'Check live status',
      }
    : null;

  const historyRows = history.map((item) => ({
    date: item.created_at ? new Date(item.created_at).toLocaleString() : 'Unknown',
    decision: item.decision,
    confidence: item.confidence != null ? `${Math.round(item.confidence * 100)}%` : 'N/A',
    reason: item.reason || 'No reason recorded',
  }));

  const chartAnalytics = analytics ? {
    labels: analytics.series.labels.map((label) => new Date(label).toLocaleString()),
    soilMoisture: analytics.series.soil_moisture,
    temperature: analytics.series.temperature,
  } : null;

  return (
    <div className="space-y-4 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">Dashboard</h1>
          <p className="text-xs text-gray-400 font-medium mt-0.5">
            {farmName} ({cropName}) • {user?.email || 'Guest'} •{' '}
            <span className="text-emerald-600 font-semibold">
              {backendError ? 'Offline Mode' : 'SQLite + FastAPI Live'}
            </span>
          </p>
        </div>
        <span className={`hidden sm:flex items-center gap-1.5 text-[10px] font-bold px-3 py-1.5 rounded-full border ${
          backendError
            ? 'text-amber-700 bg-amber-50 border-amber-100'
            : 'text-green-600 bg-green-50 border-green-100'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${backendError ? 'bg-amber-500' : 'bg-green-500'}`} />
          {backendError ? 'Backend Unavailable' : 'Live AI Backend'}
        </span>
      </div>

      {backendError && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm p-3.5 rounded-xl">
          {backendError}. Core farm data is unavailable; no farm data is being substituted.
        </div>
      )}

      {dbRecommendation && !aiResult && (
        <div className="bg-blue-50 border border-blue-100 text-blue-800 text-xs p-3 rounded-xl">
          Last saved recommendation from database: <strong>{dbRecommendation.decision}</strong>{dbRecommendation.created_at ? ` (${new Date(dbRecommendation.created_at).toLocaleString()})` : ''}
        </div>
      )}

      <section className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
        <div className="bg-white border border-gray-100 rounded-xl p-4"><p className="text-xs text-gray-400">Farm</p><p className="font-semibold text-gray-800">{farm?.name || 'No active farm'}</p></div>
        <div className="bg-white border border-gray-100 rounded-xl p-4"><p className="text-xs text-gray-400">Device</p><p className="font-semibold text-gray-800">{device ? `${device.mac_address} · ${device.status}` : 'No active device'}</p></div>
        <div className="bg-white border border-gray-100 rounded-xl p-4"><p className="text-xs text-gray-400">Latest sensor reading</p><p className="font-semibold text-gray-800">{latestSensor?.recorded_at ? new Date(latestSensor.recorded_at).toLocaleString() : 'No readings'}</p></div>
      </section>

      {/* AI Recommendation Engine */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 p-5 rounded-2xl text-white shadow-lg border border-slate-700">
        <div className="flex items-center justify-between mb-3 flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <div>
              <h2 className="text-sm font-bold tracking-tight">Live XGBoost AI Recommendation Engine</h2>
              <p className="text-xs text-slate-400">Adjust field conditions and get a real model.joblib prediction</p>
            </div>
          </div>
          <button
            onClick={handleRunAi}
            disabled={aiLoading}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 active:scale-95 disabled:opacity-60 text-white font-bold text-xs rounded-xl shadow-md transition-all flex items-center gap-2"
          >
            {aiLoading ? (
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              '⚡ Get AI Recommendation'
            )}
          </button>
        </div>

        {aiError && (
          <div className="mb-3 bg-red-500/20 border border-red-400/40 text-red-100 text-xs p-3 rounded-lg">
            {aiError}
          </div>
        )}

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-800/80 p-3 rounded-xl border border-slate-700/60">
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Soil Moisture: <span className="text-emerald-400 font-bold">{soilMoisture}%</span>
            </label>
            <input type="range" min="5" max="90" value={soilMoisture}
              onChange={(e) => setSoilMoisture(e.target.value)}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500" />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Temperature: <span className="text-amber-400 font-bold">{temperature}°C</span>
            </label>
            <input type="range" min="10" max="45" value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500" />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Humidity: <span className="text-cyan-400 font-bold">{humidity}%</span>
            </label>
            <input type="range" min="10" max="95" value={humidity}
              onChange={(e) => setHumidity(e.target.value)}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-500" />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Rainfall: <span className="text-blue-400 font-bold">{rainfall} mm</span>
            </label>
            <input type="range" min="0" max="50" value={rainfall}
              onChange={(e) => setRainfall(e.target.value)}
              className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500" />
          </div>
        </div>
      </div>

      {heroRecommendation ? <HeroRecommendationCard recommendation={heroRecommendation} /> : (
        <div className="bg-white border border-gray-100 rounded-xl p-5 text-sm text-gray-500">No saved recommendation yet. Run the irrigation analysis to create one.</div>
      )}

      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold text-gray-800">Live Farm Status</h2>
          <span className="text-xs text-amber-600 font-semibold">Current values: database reading or user input</span>
        </div>
        <LiveFarmStatus liveStatus={{
          soilMoisture: {
            value: parseFloat(soilMoisture), unit: '%',
            status: parseFloat(soilMoisture) < 30 ? 'Low' : 'Normal',
            range: '25% - 60%', color: 'text-blue-500',
            sparkline: [35, 32, 30, parseFloat(soilMoisture) - 2, parseFloat(soilMoisture)],
          },
          temperature: {
            value: parseFloat(temperature), unit: '°C',
            status: parseFloat(temperature) > 35 ? 'High' : 'Normal',
            range: '18°C - 35°C', color: 'text-red-500',
            sparkline: [28, 29, 30, parseFloat(temperature) - 1, parseFloat(temperature)],
          },
          humidity: {
            value: parseFloat(humidity), unit: '%',
            status: 'Normal', range: '40% - 70%', color: 'text-green-500',
            sparkline: [50, 48, 47, parseFloat(humidity), parseFloat(humidity)],
          },
          rainfall: {
            value: parseFloat(rainfall), unit: 'mm',
            status: parseFloat(rainfall) > 0 ? 'Normal' : 'No Rain',
            range: 'Next 24h', color: 'text-amber-500',
            sparkline: [0, 0, 0, parseFloat(rainfall), parseFloat(rainfall)],
          },
        }} />
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <WeatherForecast
          weather={dashboardMockData.environmentalIntel.weather}
          location="Punjab, India"
          isDemo={weatherIsDemo}
        />
        <div>
          <p className="mb-2 text-xs font-semibold text-amber-700">Demo Data — live alerts are not implemented in MVP.</p>
          <DisasterAlerts alerts={dashboardMockData.environmentalIntel.alerts} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold text-amber-700">Demo Data — schemes are not implemented in MVP.</p>
          <GovernmentSchemes schemes={dashboardMockData.governmentSupport} />
        </div>
        <div className="lg:col-span-2">
          {chartAnalytics ? <SensorTrendsChart analytics={chartAnalytics} /> : <div className="bg-white border border-gray-100 rounded-xl p-5 text-sm text-gray-500">No sensor trend data available.</div>}
        </div>
      </div>

      <div>
        <p className="mb-2 text-xs font-semibold text-amber-700">Demo Data — dashboard market cards await live API binding. Visit Market for the API-backed view.</p>
        <MarketPrices markets={dashboardMockData.marketIntel} isDemo={marketIsDemo} />
      </div>

      <RecommendationHistory history={historyRows} />

      <footer className="pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-gray-400 font-medium">
        <span>© 2026 AgriGuardian AI. All rights reserved.</span>
        <span className="flex items-center gap-1">
          v1.0.0 • Powered by <strong className="text-emerald-600">FastAPI + XGBoost AI</strong>
        </span>
      </footer>
    </div>
  );
}
