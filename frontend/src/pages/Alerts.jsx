import React, { useEffect, useState } from 'react';
import { getAlertsApi } from '../api/client';
import DisasterAlerts from '../components/cards/DisasterAlerts';
import { dashboardMockData } from '../services/mockData';
import Skeleton from '../components/common/Skeleton';

const MOCK_ALERTS = dashboardMockData.environmentalIntel.alerts;

function normalizeAlertsResponse(apiRes) {
  if (!apiRes || !apiRes.alerts || !Array.isArray(apiRes.alerts)) {
    return MOCK_ALERTS;
  }

  return apiRes.alerts.map((a) => {
    // If it already looks like the frontend shape, return as-is
    if (a.type && a.dateRange) return a;

    return {
      type: a.title || 'Unknown Alert',
      description: a.description || 'No description provided.',
      dateRange: a.issued_at ? new Date(a.issued_at).toLocaleDateString() : 'N/A',
      status: a.severity === 'high' ? 'High Risk' : a.severity === 'medium' ? 'Moderate Risk' : 'Low Risk',
      severity: a.severity === 'high' ? 'danger' : a.severity === 'medium' ? 'warning' : 'safe',
    };
  });
}

export default function AlertsPage() {
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState(null);
  const [isDemo, setIsDemo] = useState(true);
  const [apiMessage, setApiMessage] = useState('');

  useEffect(() => {
    async function fetchAlerts() {
      try {
        const res = await getAlertsApi();
        const normalized = normalizeAlertsResponse(res);
        setAlerts(normalized);
        setIsDemo(res.source === 'demo' || !res.is_live);
        if (res.message) setApiMessage(res.message);
      } catch {
        setAlerts(MOCK_ALERTS);
        setIsDemo(true);
        setApiMessage('Live alerts unavailable. Showing fallback demo data.');
      } finally {
        setLoading(false);
      }
    }
    fetchAlerts();
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
        <h1 className="text-2xl font-bold text-gray-900">Disaster Alerts</h1>
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

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-2">
        <DisasterAlerts alerts={alerts || MOCK_ALERTS} />
      </div>
    </div>
  );
}
