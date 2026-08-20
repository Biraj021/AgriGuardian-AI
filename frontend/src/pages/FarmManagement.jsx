import React, { useEffect, useState } from 'react';
import { getFarmsApi } from '../api/client';
import { dashboardMockData } from '../services/mockData';
import Skeleton from '../components/common/Skeleton';
import { MdAdd, MdLocationOn, MdGrass } from 'react-icons/md';

export default function FarmManagement() {
  const [loading, setLoading] = useState(true);
  const [farms, setFarms] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchFarms() {
      try {
        const res = await getFarmsApi();
        if (res.farms && res.farms.length > 0) {
          setFarms(res.farms);
        } else {
          // If no farms returned, we can show a mock one for demonstration
          setFarms([{
            id: 'mock-1',
            name: dashboardMockData.farmName,
            primary_crop: 'Wheat',
            location_lat: 18.5204,
            location_lon: 73.8567,
            is_active: true
          }]);
        }
      } catch (err) {
        setError('Failed to fetch farm data. Showing offline mock data.');
        setFarms([{
          id: 'mock-1',
          name: dashboardMockData.farmName,
          primary_crop: 'Wheat',
          location_lat: 18.5204,
          location_lon: 73.8567,
          is_active: true
        }]);
      } finally {
        setLoading(false);
      }
    }
    fetchFarms();
  }, []);

  if (loading) {
    return (
      <div className="p-6 max-w-5xl mx-auto space-y-4">
        <Skeleton className="h-8 w-48 rounded-lg" />
        <Skeleton className="h-32 w-full rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Farm Management</h1>
          <p className="text-sm text-gray-500 mt-1">Manage your connected farms and fields</p>
        </div>
        <button className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-xl text-sm font-semibold transition-colors shadow-sm">
          <MdAdd size={20} /> Add New Farm
        </button>
      </div>

      {error && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 text-sm p-4 rounded-xl">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {farms.map((farm) => (
          <div key={farm.id} className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden flex flex-col transition-all hover:shadow-md">
            <div className="h-24 bg-gradient-to-br from-primary-100 to-emerald-50 p-4 flex items-end">
              <div className="flex justify-between items-center w-full">
                <span className={`px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full ${farm.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                  {farm.is_active ? 'Active' : 'Inactive'}
                </span>
                <span className="text-xs font-mono text-gray-400 bg-white/50 px-2 rounded-md">ID: {farm.id.slice(0, 8)}</span>
              </div>
            </div>
            
            <div className="p-5 flex-1 flex flex-col">
              <h2 className="text-lg font-bold text-gray-900 mb-1">{farm.name}</h2>
              
              <div className="space-y-3 mt-4 flex-1">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center shrink-0">
                    <MdLocationOn className="text-gray-400" size={18} />
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold text-gray-400 uppercase">Coordinates</p>
                    <p className="font-medium text-gray-700">{farm.location_lat?.toFixed(4)}, {farm.location_lon?.toFixed(4)}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center shrink-0">
                    <MdGrass className="text-emerald-500" size={18} />
                  </div>
                  <div>
                    <p className="text-[10px] font-semibold text-gray-400 uppercase">Primary Crop</p>
                    <p className="font-medium text-gray-700">{farm.primary_crop || 'Not specified'}</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-4 border-t border-gray-50 flex gap-2">
                <button className="flex-1 bg-gray-50 hover:bg-gray-100 text-gray-700 py-2 rounded-xl text-sm font-semibold transition-colors">
                  Edit Details
                </button>
                <button className="flex-1 bg-primary-50 hover:bg-primary-100 text-primary-700 py-2 rounded-xl text-sm font-semibold transition-colors">
                  View Map
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
