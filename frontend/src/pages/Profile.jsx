import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function ProfilePage() {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4 sm:p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Profile</h1>
        <p className="text-sm text-gray-500">Manage your account information and preferences.</p>
      </div>

      <div className="p-6 space-y-6 bg-white shadow-sm border border-gray-100 rounded-xl">
        <div className="flex items-center space-x-4 border-b border-gray-100 pb-6">
          <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-2xl">
            {user?.name ? user.name.charAt(0).toUpperCase() : (user?.email ? user.email.charAt(0).toUpperCase() : 'F')}
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{user?.name || 'Farmer User'}</h2>
            <p className="text-sm text-gray-500">{user?.email || 'N/A'}</p>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 mt-2">
              {user?.role || 'Farmer'} Account
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">User ID</label>
            <p className="text-sm font-mono text-gray-800 bg-gray-50 p-2.5 rounded border border-gray-200">{user?.id || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Email Address</label>
            <p className="text-sm text-gray-800 bg-gray-50 p-2.5 rounded border border-gray-200">{user?.email || 'N/A'}</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Account Status</label>
            <p className="text-sm text-emerald-600 font-medium bg-emerald-50 p-2.5 rounded border border-emerald-200">Active & Verified</p>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Role</label>
            <p className="text-sm text-gray-800 bg-gray-50 p-2.5 rounded border border-gray-200 capitalize">{user?.role || 'farmer'}</p>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end">
          <button 
            onClick={logout}
            className="px-4 py-2 text-sm font-medium rounded-lg text-red-600 bg-red-50 border border-red-200 hover:bg-red-100 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}
