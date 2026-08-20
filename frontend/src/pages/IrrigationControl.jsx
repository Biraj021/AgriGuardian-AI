import React, { useEffect, useState } from 'react';
import { getDevicesApi, controlDeviceApi, getRecommendationHistoryApi } from '../api/client';
import RecommendationHistory from '../components/cards/RecommendationHistory';
import Skeleton from '../components/common/Skeleton';
import { MdWaterDrop, MdPowerSettingsNew, MdTimer } from 'react-icons/md';

export default function IrrigationControl() {
  const [loading, setLoading] = useState(true);
  const [devices, setDevices] = useState([]);
  const [history, setHistory] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [duration, setDuration] = useState(60);
  const [actionStatus, setActionStatus] = useState({ type: '', message: '' });
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [deviceRes, historyRes] = await Promise.all([
          getDevicesApi(),
          getRecommendationHistoryApi()
        ]);
        
        if (deviceRes.devices) {
          setDevices(deviceRes.devices);
          if (deviceRes.devices.length > 0) {
            setSelectedDevice(deviceRes.devices[0].id);
          }
        }
        
        if (historyRes.recommendations) {
          setHistory(historyRes.recommendations.map((item) => ({
            date: item.created_at ? new Date(item.created_at).toLocaleString() : 'Unknown',
            decision: item.decision,
            confidence: item.confidence != null ? `${Math.round(item.confidence * 100)}%` : 'N/A',
            reason: item.reason || 'No reason recorded',
          })));
        }
      } catch (err) {
        setActionStatus({ type: 'error', message: 'Failed to load data.' });
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handlePumpCommand = async (command) => {
    if (!selectedDevice) return;
    
    setActionLoading(true);
    setActionStatus({ type: '', message: '' });
    
    try {
      const dur = command === 'PUMP_ON' ? parseInt(duration, 10) : null;
      await controlDeviceApi(selectedDevice, command, dur);
      setActionStatus({ 
        type: 'success', 
        message: `Command ${command} sent successfully${dur ? ` for ${dur} seconds` : ''}.` 
      });
    } catch (err) {
      setActionStatus({ type: 'error', message: err.message || 'Failed to send command.' });
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-4">
        <Skeleton className="h-8 w-48 rounded-lg" />
        <Skeleton className="h-[200px] w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Irrigation Control</h1>
        <p className="text-sm text-gray-500 mt-1">Manual override and history of AI-driven irrigation decisions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center gap-2 mb-6">
              <MdWaterDrop className="text-blue-500" size={24} />
              <h2 className="text-lg font-bold text-gray-900">Manual Override</h2>
            </div>

            {actionStatus.message && (
              <div className={`p-3 rounded-xl mb-4 text-sm font-medium ${
                actionStatus.type === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'
              }`}>
                {actionStatus.message}
              </div>
            )}

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Select Target Device</label>
                <select 
                  value={selectedDevice}
                  onChange={(e) => setSelectedDevice(e.target.value)}
                  className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-xl p-3 focus:ring-blue-500 focus:border-blue-500 font-medium"
                >
                  <option value="" disabled>Select a device...</option>
                  {devices.map(d => (
                    <option key={d.id} value={d.id}>{d.mac_address} ({d.status})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-2">Duration (Seconds)</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MdTimer className="text-gray-400" size={18} />
                  </div>
                  <input 
                    type="number" 
                    min="1" 
                    max="300"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full bg-gray-50 border border-gray-200 text-gray-900 text-sm rounded-xl pl-10 p-3 focus:ring-blue-500 focus:border-blue-500 font-medium"
                  />
                </div>
                <p className="text-[10px] text-gray-400 mt-1 font-medium">Max 300 seconds per burst for safety.</p>
              </div>

              <div className="pt-4 flex gap-3">
                <button 
                  onClick={() => handlePumpCommand('PUMP_ON')}
                  disabled={!selectedDevice || actionLoading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                >
                  <MdWaterDrop size={20} /> Turn ON
                </button>
                <button 
                  onClick={() => handlePumpCommand('PUMP_OFF')}
                  disabled={!selectedDevice || actionLoading}
                  className="flex-1 bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white font-bold py-3 rounded-xl transition-all shadow-sm flex items-center justify-center gap-2"
                >
                  <MdPowerSettingsNew size={20} /> Turn OFF
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          <RecommendationHistory history={history} />
        </div>
      </div>
    </div>
  );
}
