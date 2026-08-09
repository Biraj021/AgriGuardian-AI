import React from 'react';
import { MdArrowForward, MdTrendingUp, MdTrendingDown, MdRefresh } from 'react-icons/md';
import { useNavigate } from 'react-router-dom';
import Sparkline from '../charts/Sparkline';

const CROP_ICONS = {
  Wheat: '🌾', Rice: '🍚', Maize: '🌽', Cotton: '🌿', Soybean: '🫘',
};

export default function MarketPrices({ markets, isDemo = false, fetchedAt = null, onRefresh = null }) {
  const navigate = useNavigate();

  // Format fetchedAt timestamp to local time
  const lastUpdated = fetchedAt
    ? new Date(fetchedAt).toLocaleTimeString('en-IN', {
        hour: '2-digit', minute: '2-digit', hour12: true,
      })
    : null;

  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-sm font-bold text-gray-800">Market Prices</h3>
          {isDemo ? (
            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
              Demo Data
            </span>
          ) : (
            <span className="text-[10px] font-bold uppercase tracking-wider text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full">
              Live Prices
            </span>
          )}
          {lastUpdated && (
            <span className="text-[10px] text-gray-400 font-medium">
              Updated {lastUpdated}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
              title="Refresh prices"
            >
              <MdRefresh size={16} />
            </button>
          )}
          <button
            onClick={() => navigate('/market')}
            className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all"
          >
            View Market <MdArrowForward size={14} />
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {markets.map((m, i) => {
          const startLabel = m.sparkline_labels?.start || '02 Aug';
          const endLabel = m.sparkline_labels?.end || '09 Aug';
          return (
            <div key={i} className="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
              <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-xl shrink-0 border border-amber-100">
                {CROP_ICONS[m.crop] || '🌱'}
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-gray-800">{m.crop}</p>
                <p className="text-xl font-black text-gray-900 leading-tight">{m.currentPrice}</p>
                <p className="text-[10px] text-gray-400 font-medium">/ {m.unit}</p>
                <div className={`flex items-center gap-1 text-xs font-bold mt-0.5 ${m.trend === 'up' ? 'text-green-600' : 'text-red-500'}`}>
                  {m.trend === 'up' ? <MdTrendingUp size={14} /> : <MdTrendingDown size={14} />}
                  {m.change} vs yesterday
                </div>
              </div>

              <div className="shrink-0">
                <Sparkline
                  data={m.sparkline}
                  color={m.trend === 'up' ? '#10B981' : '#EF4444'}
                  height={44}
                  width={90}
                />
                <div className="flex justify-between text-[9px] text-gray-300 font-medium mt-0.5">
                  <span>{startLabel}</span>
                  <span>{endLabel}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
