import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  MdMenu, MdNotifications, MdSearch, MdKeyboardArrowDown,
  MdPerson, MdSettings, MdLogout, MdClose, MdCheckCircle,
  MdWarning, MdInfo
} from 'react-icons/md';

// System-generated notifications based on actual context
const SYSTEM_NOTIFICATIONS = [
  {
    id: 1,
    icon: MdWarning,
    iconColor: 'text-amber-500',
    bgColor: 'bg-amber-50',
    title: 'Low Soil Moisture Alert',
    body: 'Soil moisture at 25% — below optimal range. Consider irrigation today.',
    time: 'Just now',
    unread: true,
  },
  {
    id: 2,
    icon: MdInfo,
    iconColor: 'text-blue-500',
    bgColor: 'bg-blue-50',
    title: 'Heatwave Warning',
    body: 'High temperatures (35°C+) expected Aug 08–10 in your region.',
    time: '2h ago',
    unread: true,
  },
  {
    id: 3,
    icon: MdCheckCircle,
    iconColor: 'text-green-500',
    bgColor: 'bg-green-50',
    title: 'AI Model Ready',
    body: 'XGBoost irrigation model loaded successfully. Click "Get AI Recommendation".',
    time: '5h ago',
    unread: true,
  },
];

export default function Navbar({ toggleSidebar }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [notifications, setNotifications] = useState(SYSTEM_NOTIFICATIONS);

  const notifRef = useRef(null);
  const profileRef = useRef(null);

  const unreadCount = notifications.filter((n) => n.unread).length;

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClick(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) setNotifOpen(false);
      if (profileRef.current && !profileRef.current.contains(e.target)) setProfileOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  function markAllRead() {
    setNotifications((prev) => prev.map((n) => ({ ...n, unread: false })));
  }

  function dismissNotification(id) {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }

  const initials = user?.email
    ? user.email.slice(0, 2).toUpperCase()
    : 'RP';

  const displayName = user?.name || user?.email?.split('@')[0] || 'Ramesh Patil';

  return (
    <header className="h-16 bg-surface border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 shrink-0 gap-3 relative z-30">
      {/* Left: Hamburger + Search */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <button
          onClick={toggleSidebar}
          className="md:hidden text-gray-500 hover:text-gray-700 p-2 -ml-2 rounded-lg hover:bg-gray-50 transition-colors shrink-0"
        >
          <MdMenu size={22} />
        </button>

        <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2 max-w-md w-full text-sm text-gray-400 cursor-pointer hover:border-gray-300 transition-colors">
          <MdSearch size={18} className="shrink-0" />
          <span className="flex-1 text-gray-400">Search anything...</span>
          <kbd className="hidden sm:inline text-[10px] font-semibold bg-gray-100 border border-gray-200 text-gray-500 px-1.5 py-0.5 rounded-md">
            Ctrl + K
          </kbd>
        </div>
      </div>

      {/* Right: Notifications + User */}
      <div className="flex items-center gap-2 shrink-0">

        {/* ── Notifications ── */}
        <div ref={notifRef} className="relative">
          <button
            onClick={() => { setNotifOpen((o) => !o); setProfileOpen(false); }}
            className="relative p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-full hover:bg-gray-50"
            aria-label="Notifications"
          >
            <MdNotifications size={22} />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 min-w-[16px] h-4 bg-red-500 rounded-full text-[9px] text-white font-bold flex items-center justify-center px-0.5">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notification dropdown */}
          {notifOpen && (
            <div className="absolute right-0 top-12 w-80 bg-white rounded-2xl border border-gray-100 shadow-xl overflow-hidden z-50">
              <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                <div>
                  <p className="text-sm font-bold text-gray-800">Notifications</p>
                  <p className="text-[10px] text-gray-400">{unreadCount} unread</p>
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    className="text-[11px] text-primary-600 font-semibold hover:text-primary-700"
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-72 overflow-y-auto divide-y divide-gray-50">
                {notifications.length === 0 && (
                  <div className="py-8 text-center text-sm text-gray-400">
                    No notifications
                  </div>
                )}
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`flex gap-3 px-4 py-3 hover:bg-gray-50 transition-colors ${n.unread ? 'bg-blue-50/30' : ''}`}
                  >
                    <div className={`w-8 h-8 rounded-full ${n.bgColor} flex items-center justify-center shrink-0 mt-0.5`}>
                      <n.icon size={16} className={n.iconColor} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-bold text-gray-800 leading-tight">{n.title}</p>
                      <p className="text-[11px] text-gray-500 mt-0.5 leading-snug">{n.body}</p>
                      <p className="text-[10px] text-gray-400 mt-1 font-medium">{n.time}</p>
                    </div>
                    <button
                      onClick={() => dismissNotification(n.id)}
                      className="text-gray-300 hover:text-gray-500 mt-0.5 shrink-0"
                    >
                      <MdClose size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* ── User Profile ── */}
        <div ref={profileRef} className="relative">
          <button
            onClick={() => { setProfileOpen((o) => !o); setNotifOpen(false); }}
            className="flex items-center gap-2.5 cursor-pointer hover:bg-gray-50 rounded-xl px-2 py-1.5 transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-bold text-sm shrink-0">
              {initials}
            </div>
            <div className="hidden sm:flex flex-col text-left">
              <span className="text-sm font-semibold text-gray-800 leading-tight">{displayName}</span>
              <span className="text-[10px] text-gray-400 font-medium capitalize">{user?.role || 'Farmer'}</span>
            </div>
            <MdKeyboardArrowDown
              size={18}
              className={`text-gray-400 hidden sm:block transition-transform ${profileOpen ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Profile dropdown */}
          {profileOpen && (
            <div className="absolute right-0 top-12 w-52 bg-white rounded-2xl border border-gray-100 shadow-xl overflow-hidden z-50">
              <div className="px-4 py-3 border-b border-gray-50">
                <p className="text-xs font-bold text-gray-800 truncate">{displayName}</p>
                <p className="text-[11px] text-gray-400 truncate">{user?.email}</p>
              </div>
              <div className="py-1">
                <button
                  onClick={() => { navigate('/profile'); setProfileOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <MdPerson size={16} className="text-gray-400" />
                  My Profile
                </button>
                <button
                  onClick={() => { navigate('/profile'); setProfileOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <MdSettings size={16} className="text-gray-400" />
                  Settings
                </button>
              </div>
              <div className="border-t border-gray-50 py-1">
                <button
                  onClick={() => { logout(); navigate('/login'); setProfileOpen(false); }}
                  className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                >
                  <MdLogout size={16} />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
