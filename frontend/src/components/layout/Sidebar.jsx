import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { dashboardMockData } from '../../services/mockData';
import { 
  MdDashboard, 
  MdPsychology, 
  MdWbSunny, 
  MdStorefront, 
  MdWarning, 
  MdPolicy, 
  MdAnalytics,
  MdLandscape,
  MdShower,
  MdRouter,
  MdSettings,
  MdKeyboardArrowDown
} from 'react-icons/md';

const navItems = [
  { path: '/', label: 'Dashboard', icon: MdDashboard },
  { path: '/recommendations', label: 'AI Recommendations', icon: MdPsychology },
  { path: '/weather', label: 'Weather', icon: MdWbSunny },
  { path: '/market', label: 'Market Prices', icon: MdStorefront },
  { path: '/alerts', label: 'Disaster Alerts', icon: MdWarning },
  { path: '/schemes', label: 'Government Schemes', icon: MdPolicy },
  { path: '/analytics', label: 'Analytics', icon: MdAnalytics },
  { path: '/farm-management', label: 'Farm Management', icon: MdLandscape },
  { path: '/irrigation', label: 'Irrigation Control', icon: MdShower },
  { path: '/device-status', label: 'Device Status', icon: MdRouter },
  { path: '/profile', label: 'Profile & Settings', icon: MdSettings },
];

export default function Sidebar({ isOpen, setIsOpen }) {
  const { user } = useAuth();

  // Live clock
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const dateString = now.toLocaleDateString('en-IN', {
    weekday: 'long', day: '2-digit', month: 'short', year: 'numeric',
  });
  const timeString = now.toLocaleTimeString('en-IN', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
  });


  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900/50 md:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar container */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        w-64 bg-surface border-r border-gray-200 
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        flex flex-col h-full overflow-hidden shrink-0
      `}>
        {/* Header Branding */}
        <div className="h-20 flex items-center gap-3 px-6 border-b border-gray-100 shrink-0">
          <span className="w-9 h-9 rounded-xl bg-primary-50 text-xl flex items-center justify-center border border-primary-100 flex-shrink-0">
            🌱
          </span>
          <div className="flex flex-col">
            <span className="text-[17px] font-bold text-primary-600 tracking-tight leading-tight">
              AgriGuardian AI
            </span>
            <span className="text-[10px] text-gray-400 font-medium tracking-wide">
              Smart Farming. Better Tomorrow.
            </span>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 py-4 px-3 space-y-0.5 overflow-y-auto min-h-0">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all
                ${isActive 
                  ? 'bg-primary-600 text-white shadow-sm font-semibold' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}
              `}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Bottom selector and weather widgets */}
        <div className="p-4 border-t border-gray-100 space-y-3 bg-gray-50 shrink-0">
          {/* Farm selector dropdown */}
          <div className="bg-surface p-3 rounded-xl border border-gray-200 shadow-sm flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-2">
              <span className="text-xl">🏡</span>
              <div className="overflow-hidden">
                <p className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">Selected Farm</p>
                <p className="text-[12px] font-semibold text-gray-800 truncate">{dashboardMockData.farmName}</p>
                <p className="text-[10px] text-gray-500">{dashboardMockData.farmSize}</p>
              </div>
            </div>
            <MdKeyboardArrowDown className="text-gray-400 w-5 h-5" />
          </div>

          {/* Mini Weather widget */}
          <div className="bg-surface p-3 rounded-xl border border-gray-200 shadow-sm flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">☀️</span>
                <div>
                  <p className="text-lg font-bold text-gray-800 leading-none">32°C</p>
                  <p className="text-[10px] text-gray-400 font-medium mt-0.5">Sunny</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-[11px] font-semibold text-gray-700">{dashboardMockData.location.split(',')[0]}</p>
                <p className="text-[9px] text-gray-400">{dashboardMockData.location.split(',')[1].trim()}</p>
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-[10px] text-gray-500 font-medium">
              <span>{dateString}</span>
              <span className="font-mono">{timeString}</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
