import React from 'react';

export default function EmptyState({ icon: Icon, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-surface border border-gray-100 rounded-xl shadow-sm">
      <div className="w-12 h-12 rounded-full bg-gray-50 flex items-center justify-center mb-4">
        {Icon && <Icon className="w-6 h-6 text-gray-400" />}
      </div>
      <h3 className="text-sm font-medium text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-500 max-w-sm">{description}</p>
    </div>
  );
}
