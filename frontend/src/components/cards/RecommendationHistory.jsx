import React from 'react';
import { MdArrowForward } from 'react-icons/md';

const DECISION_STYLES = {
  'Irrigate Today': 'bg-green-100 text-green-700 border border-green-200',
  'Irrigate': 'bg-green-100 text-green-700 border border-green-200',
  'Do Not Irrigate': 'bg-amber-100 text-amber-700 border border-amber-200',
};

export default function RecommendationHistory({ history }) {
  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-gray-800">Recommendation History</h3>
        <button className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all">
          View All <MdArrowForward size={14} />
        </button>
      </div>

      <div className="overflow-x-auto -mx-5 px-5">
        <table className="w-full min-w-[560px]">
          <thead>
            <tr className="border-b border-gray-100">
              {['Date', 'Recommendation', 'Confidence', 'Primary Driver'].map(h => (
                <th key={h} className="text-left pb-3 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {history.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                <td className="py-3 pr-4 text-xs font-semibold text-gray-600 whitespace-nowrap">
                  {row.date}
                </td>
                <td className="py-3 pr-4">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full whitespace-nowrap ${DECISION_STYLES[row.decision] || 'bg-gray-100 text-gray-600 border border-gray-200'}`}>
                    {row.decision}
                  </span>
                </td>
                <td className="py-3 pr-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-500 rounded-full"
                        style={{ width: row.confidence }}
                      />
                    </div>
                    <span className="text-xs font-bold text-gray-700">{row.confidence}</span>
                  </div>
                </td>
                <td className="py-3 text-xs text-gray-500 font-medium">
                  {row.reason}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
