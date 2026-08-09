import React, { useState } from 'react';
import { getIrrigationRecommendationApi } from '../api/client';
import HeroRecommendationCard from '../components/cards/HeroRecommendationCard';

export default function Recommendations() {
  const [soilMoisture, setSoilMoisture] = useState(25.0);
  const [temperature, setTemperature] = useState(32.0);
  const [humidity, setHumidity] = useState(45.0);
  const [rainfall, setRainfall] = useState(0.0);
  
  const [status, setStatus] = useState('initial'); // 'initial', 'loading', 'success', 'error'
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleRunAi = async () => {
    setStatus('loading');
    setErrorMsg('');
    try {
      const res = await getIrrigationRecommendationApi({
        soil_moisture: parseFloat(soilMoisture),
        temperature: parseFloat(temperature),
        humidity: parseFloat(humidity),
        rainfall_prev_day: parseFloat(rainfall),
      });
      setResult(res);
      setStatus('success');
    } catch (err) {
      setErrorMsg(err.message || 'AI prediction failed');
      setStatus('error');
    }
  };

  const recommendationPayload = result ? {
    decision: result.recommendation,
    confidence: result.confidence,
    reasoning: [
      result.reason,
      `Model prediction: ${result.prediction === 1 ? 'Irrigate' : 'Skip'}`,
      `Inputs — Soil: ${soilMoisture}%, Temp: ${temperature}°C, Humidity: ${humidity}%, Rain: ${rainfall} mm`,
    ],
    recommendedTime: result.prediction === 1 ? '5:30 AM (Early Morning)' : 'N/A (Adequate Moisture)',
    estWater: result.prediction === 1 ? '1,200 Liters / Acre' : '0 Liters',
  } : null;

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
        <p className="text-sm text-gray-500">Live XGBoost AI Recommendation Engine</p>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Soil Moisture: <span className="text-emerald-500">{soilMoisture}%</span>
            </label>
            <input type="range" min="5" max="90" value={soilMoisture} onChange={(e) => setSoilMoisture(e.target.value)} className="w-full accent-emerald-500" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Temperature: <span className="text-amber-500">{temperature}°C</span>
            </label>
            <input type="range" min="10" max="45" value={temperature} onChange={(e) => setTemperature(e.target.value)} className="w-full accent-amber-500" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Humidity: <span className="text-cyan-500">{humidity}%</span>
            </label>
            <input type="range" min="10" max="95" value={humidity} onChange={(e) => setHumidity(e.target.value)} className="w-full accent-cyan-500" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Rainfall (prev day): <span className="text-blue-500">{rainfall} mm</span>
            </label>
            <input type="range" min="0" max="50" value={rainfall} onChange={(e) => setRainfall(e.target.value)} className="w-full accent-blue-500" />
          </div>
        </div>

        <button 
          onClick={handleRunAi}
          disabled={status === 'loading'}
          className="w-full md:w-auto px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-xl disabled:opacity-50 transition-colors"
        >
          {status === 'loading' ? 'Analyzing conditions...' : 'Get AI Recommendation'}
        </button>
      </div>

      {status === 'initial' && (
        <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl text-blue-800 text-center font-medium">
          Enter agricultural conditions and get an AI recommendation.
        </div>
      )}

      {status === 'error' && (
        <div className="bg-red-50 border border-red-100 p-6 rounded-xl text-red-800 text-center">
          <p className="font-bold mb-2">Error generating recommendation</p>
          <p className="text-sm">{errorMsg}</p>
          <button onClick={handleRunAi} className="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 font-bold rounded-lg text-sm transition-colors">Try Again</button>
        </div>
      )}

      {status === 'success' && recommendationPayload && (
        <HeroRecommendationCard recommendation={recommendationPayload} />
      )}
    </div>
  );
}
