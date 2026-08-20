import React, { useEffect, useState } from 'react';
import { getDevicesApi } from '../api/client';
import Skeleton from '../components/common/Skeleton';
import { MdRouter, MdCheckCircle, MdError, MdRefresh } from 'react-icons/md';

export default function DeviceStatus() {
  const [loading, setLoading] = useState(true);
  const [devices, setDevices] = useState([]);
  const [error, setError] = useState(null);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const res = await getDevicesApi();
      if (res.devices) {
        setDevices(res.devices);
      } else {
        setDevices([]);
      }
    } catch (err) {
      setError('Failed to fetch devices. Check your backend connection.');
      setDevices([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  if (loading && devices.length === 0) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-4">
        <Skeleton className="h-8 w-48 rounded-lg" />
        <Skeleton className="h-[400px] w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Device Status</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor all connected IoT gateways and sensor nodes</p>
        </div>
        <button 
          onClick={fetchDevices}
          className="flex items-center gap-2 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm"
        >
          <MdRefresh size={18} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {error && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm p-4 rounded-xl">
          {error}
        </div>
      )}

      <div className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-600">
            <thead className="bg-gray-50/50 text-gray-500 text-xs uppercase font-semibold border-b border-gray-100">
              <tr>
                <th className="px-6 py-4">Device Info</th>
                <th className="px-6 py-4">MAC Address</th>
                <th className="px-6 py-4">Farm ID</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {devices.length === 0 && !loading && (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                    <MdRouter size={48} className="mx-auto text-gray-300 mb-3" />
                    <p className="font-semibold text-gray-700">No devices found</p>
                    <p className="text-xs mt-1">Connect an ESP32 device to see it listed here.</p>
                  </td>
                </tr>
              )}
              {devices.map((device) => {
                const isOnline = device.status?.toLowerCase() === 'online';
                return (
                  <tr key={device.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${isOnline ? 'bg-green-50 text-green-600' : 'bg-gray-50 text-gray-400'}`}>
                          <MdRouter size={20} />
                        </div>
                        <div>
                          <p className="font-bold text-gray-900">Sensor Node</p>
                          <p className="text-[10px] text-gray-400 font-mono mt-0.5">ID: {device.id.slice(0, 8)}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-gray-600 bg-gray-50/30 rounded">
                      {device.mac_address}
                    </td>
                    <td className="px-6 py-4 text-xs font-mono text-gray-500">
                      {device.farm_id.slice(0, 8)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-1.5">
                        {isOnline ? (
                          <MdCheckCircle className="text-green-500" size={16} />
                        ) : (
                          <MdError className="text-gray-400" size={16} />
                        )}
                        <span className={`text-xs font-bold uppercase tracking-wider ${isOnline ? 'text-green-700' : 'text-gray-500'}`}>
                          {device.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      {device.last_seen_at ? (
                        <div className="text-xs">
                          <p className="font-semibold text-gray-700">{new Date(device.last_seen_at).toLocaleDateString()}</p>
                          <p className="text-gray-400">{new Date(device.last_seen_at).toLocaleTimeString()}</p>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-xs italic">Never</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
