import React, { useEffect, useState } from 'react';
import { getMarketApi } from '../api/client';
import MarketPrices from '../components/cards/MarketPrices';
import { dashboardMockData } from '../services/mockData';
import Skeleton from '../components/common/Skeleton';

const MOCK_MARKETS = dashboardMockData.marketIntel;

function normalizeMarketResponse(apiRes) {
  // Backend /market/prices returns { prices: [{crop, price, unit, trend}] }
  // MarketPrices.jsx expects [{crop, currentPrice, unit, change, trend, sparkline}]
  if (!apiRes) return MOCK_MARKETS;

  const raw = apiRes.prices || apiRes.markets;
  if (!raw || !Array.isArray(raw)) return MOCK_MARKETS;

  return raw.map((item, i) => {
    // Check if it already has the expected shape
    if (item.currentPrice) return item;

    // Normalize from flat API shape
    const price = item.price ?? 0;
    const mockItem = MOCK_MARKETS[i];
    return {
      crop: item.crop,
      currentPrice: `₹${price.toLocaleString('en-IN')}`,
      unit: item.unit?.replace('₹/', '') || 'Quintal',
      change: item.change ?? (item.trend === 'up' ? '+1.2%' : '-0.8%'),
      trend: item.trend ?? 'up',
      sparkline: mockItem?.sparkline ?? [price * 0.95, price * 0.97, price * 0.99, price, price * 1.01],
    };
  });
}

export default function MarketPage() {
  const [loading, setLoading] = useState(true);
  const [markets, setMarkets] = useState(null);
  const [isDemo, setIsDemo] = useState(true);
  const [apiMessage, setApiMessage] = useState('');

  useEffect(() => {
    async function fetchMarket() {
      try {
        const res = await getMarketApi();
        const normalized = normalizeMarketResponse(res);
        setMarkets(normalized);
        setIsDemo(res.source === 'demo' || !res.is_live);
        if (res.message) setApiMessage(res.message);
      } catch {
        setMarkets(MOCK_MARKETS);
        setIsDemo(true);
        setApiMessage('Live market prices unavailable. Showing fallback demo data.');
      } finally {
        setLoading(false);
      }
    }
    fetchMarket();
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
        <h1 className="text-2xl font-bold text-gray-900">Market Prices</h1>
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

      <MarketPrices markets={markets || MOCK_MARKETS} isDemo={isDemo} />
    </div>
  );
}
