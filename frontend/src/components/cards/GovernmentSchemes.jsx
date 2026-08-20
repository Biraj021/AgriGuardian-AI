import React from 'react';
import { useNavigate } from 'react-router-dom';
import { MdArrowForward } from 'react-icons/md';

const STATUS_STYLE = {
  Eligible: 'bg-green-100 text-green-700',
  'Action Required': 'bg-amber-100 text-amber-700',
  Pending: 'bg-blue-100 text-blue-700',
};

const SCHEME_ICONS = ['🏛', '💳', '🌱', '🚜', '☀️'];

export default function GovernmentSchemes({ schemes }) {
  const navigate = useNavigate();

  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-gray-800">Government Schemes</h3>
        <button
          onClick={() => navigate('/schemes')}
          className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all cursor-pointer"
        >
          View All <MdArrowForward size={14} />
        </button>
      </div>

      <div className="space-y-3">
        {schemes.map((scheme, i) => (
          <div
            key={i}
            onClick={() => navigate('/schemes')}
            className="flex items-start gap-3 p-3.5 bg-gray-50 rounded-xl border border-gray-100 hover:border-primary-100 hover:bg-primary-50/30 transition-all cursor-pointer"
          >
            {/* Scheme icon */}
            <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-xl shrink-0">
              {SCHEME_ICONS[i] || '🏛'}
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-gray-800 leading-tight">{scheme.title}</p>
              <p className="text-xs text-gray-500 mt-0.5 leading-relaxed line-clamp-2">{scheme.description}</p>
              <p className="text-[10px] text-gray-400 font-medium mt-1">{scheme.details}</p>
            </div>

            <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full shrink-0 ${STATUS_STYLE[scheme.status] || 'bg-gray-100 text-gray-600'}`}>
              {scheme.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
