import React from 'react';

export default function NotImplementedPage({ title }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
      <div className="text-6xl mb-4">🚧</div>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
      <p className="text-gray-500 max-w-md">
        This feature is not fully implemented in the current MVP. 
        Please check back in a future release!
      </p>
    </div>
  );
}
