import React from 'react';
import { MdArrowForward, MdWarning, MdCheckCircle } from 'react-icons/md';

const SEVERITY_STYLES = {
  danger: {
    card: 'bg-red-50 border-red-200',
    badge: 'bg-red-100 text-red-700',
    icon: '⚠️',
  },
  warning: {
    card: 'bg-amber-50 border-amber-200',
    badge: 'bg-amber-100 text-amber-700',
    icon: '🌬️',
  },
  safe: {
    card: 'bg-gray-50 border-gray-100',
    badge: 'bg-green-100 text-green-700',
    icon: '✅',
  },
};

export default function DisasterAlerts({ alerts }) {
  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-gray-800">Disaster Alerts</h3>
        <button className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all">
          View All <MdArrowForward size={14} />
        </button>
      </div>

      <div className="space-y-3">
        {alerts.map((alert, i) => {
          const style = SEVERITY_STYLES[alert.severity] || SEVERITY_STYLES.safe;
          return (
            <div key={i} className={`rounded-xl border p-3.5 ${style.card}`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5 flex-1">
                  <span className="text-lg shrink-0 mt-0.5">{style.icon}</span>
                  <div>
                    <p className="text-sm font-bold text-gray-800 leading-tight">{alert.type}</p>
                    <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{alert.description}</p>
                    {alert.severity === 'danger' && (
                      <p className="text-[10px] text-red-600 font-medium mt-1">{alert.dateRange}</p>
                    )}
                  </div>
                </div>
                <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full whitespace-nowrap shrink-0 ${style.badge}`}>
                  {alert.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
