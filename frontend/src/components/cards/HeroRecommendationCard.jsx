import React from 'react';
import { MdWaterDrop, MdAccessTime, MdCheckCircle } from 'react-icons/md';

export default function HeroRecommendationCard({ recommendation }) {
  const { decision, confidence, reasoning, recommendedTime, estWater } = recommendation;
  const lower = decision.toLowerCase();
  const isIrrigate =
    lower.includes('irrigate now') ||
    lower.includes('irrigate today') ||
    lower === 'irrigate';

  const hasConfidence = confidence != null && !Number.isNaN(confidence);

  return (
    <div className={`relative overflow-hidden rounded-2xl shadow-md ${isIrrigate ? 'bg-gradient-to-br from-green-600 via-green-700 to-emerald-800' : 'bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800'}`}>
      <div className="absolute top-0 right-0 w-72 h-72 rounded-full opacity-10 bg-white -translate-y-1/3 translate-x-1/4 pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 w-48 h-48 rounded-full opacity-10 bg-white translate-y-1/3 pointer-events-none" />

      <div className="relative z-10 p-6 flex flex-col sm:flex-row gap-6">
        <div className="flex-1 min-w-0">
          <div className="inline-flex items-center gap-1.5 bg-white/20 text-white text-[10px] font-bold uppercase tracking-widest px-3 py-1 rounded-full mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></span>
            AI RECOMMENDATION
          </div>

          <div className="flex items-start gap-4 mb-4">
            <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center text-5xl shrink-0 shadow-inner">
              🌱
            </div>
            <div>
              <h2 className="text-4xl font-bold text-white tracking-tight leading-tight flex items-center gap-2">
                {decision}
                {isIrrigate && <MdWaterDrop className="text-blue-200 w-8 h-8" />}
              </h2>
              <div className="flex flex-wrap items-center gap-4 mt-2 text-white/80 text-sm">
                <span className="flex items-center gap-1.5">
                  <MdAccessTime size={15} />
                  Recommended Time: <strong className="text-white">{recommendedTime}</strong>
                </span>
                <span className="flex items-center gap-1.5">
                  <MdWaterDrop size={15} />
                  Est. Water Required: <strong className="text-white">{estWater}</strong>
                </span>
              </div>
            </div>
          </div>

          <div className="mb-5">
            <p className="text-white/80 text-xs font-semibold uppercase tracking-wider mb-2">AI Reasoning</p>
            <ul className="space-y-1.5">
              {reasoning.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-white/90">
                  <MdCheckCircle className="text-white/70 w-4 h-4 mt-0.5 shrink-0" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 bg-white text-green-700 font-bold text-sm px-5 py-2.5 rounded-xl hover:bg-green-50 transition-colors shadow-md active:scale-95">
              <MdWaterDrop size={18} />
              {isIrrigate ? 'Irrigate Now' : 'Acknowledge'}
            </button>
            <button className="flex items-center gap-2 text-white text-sm font-semibold px-5 py-2.5 rounded-xl border border-white/30 hover:bg-white/10 transition-colors">
              View Details
              <span className="text-white/60">→</span>
            </button>
          </div>
        </div>

        <div className="flex flex-col items-center justify-center bg-white/15 rounded-2xl px-8 py-5 shrink-0 text-center border border-white/20 min-w-[140px]">
          {hasConfidence ? (
            <>
              <div className="text-5xl font-black text-white leading-none">
                {Math.round(confidence * 100)}%
              </div>
              <div className="text-white/70 text-xs font-semibold uppercase tracking-widest mt-1">
                Confidence
              </div>
              <div className="relative mt-3 w-16 h-16">
                <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
                  <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth="5" />
                  <circle
                    cx="32" cy="32" r="28"
                    fill="none"
                    stroke="white"
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray={`${2 * Math.PI * 28}`}
                    strokeDashoffset={`${2 * Math.PI * 28 * (1 - confidence)}`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-white text-lg">✓</div>
              </div>
            </>
          ) : (
            <>
              <div className="text-2xl font-bold text-white leading-none">N/A</div>
              <div className="text-white/70 text-xs font-semibold uppercase tracking-widest mt-2">
                Confidence
              </div>
              <p className="text-white/60 text-[10px] mt-2 max-w-[120px]">
                Model does not expose probability scores
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
