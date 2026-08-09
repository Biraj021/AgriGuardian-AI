import React from 'react';
import { MdArrowForward } from 'react-icons/md';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: {
      position: 'top',
      align: 'end',
      labels: {
        boxWidth: 10,
        boxHeight: 10,
        borderRadius: 5,
        useBorderRadius: true,
        font: { size: 11, family: 'Inter' },
        color: '#6B7280',
        padding: 16
      }
    },
    tooltip: {
      backgroundColor: 'white',
      borderColor: '#E5E7EB',
      borderWidth: 1,
      titleColor: '#111827',
      bodyColor: '#6B7280',
      titleFont: { size: 12, weight: 'bold', family: 'Inter' },
      bodyFont: { size: 11, family: 'Inter' },
      padding: 12,
      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: { font: { size: 11, family: 'Inter' }, color: '#9CA3AF' }
    },
    y: {
      position: 'left',
      grid: { color: '#F3F4F6' },
      ticks: { font: { size: 11, family: 'Inter' }, color: '#9CA3AF' },
      title: { display: true, text: '%', color: '#9CA3AF', font: { size: 10 } }
    },
    y1: {
      position: 'right',
      grid: { drawOnChartArea: false },
      ticks: { font: { size: 11, family: 'Inter' }, color: '#9CA3AF' },
      title: { display: true, text: '°C', color: '#9CA3AF', font: { size: 10 } }
    }
  }
};

export default function SensorTrendsChart({ analytics }) {
  const { labels, soilMoisture, temperature } = analytics;

  const data = {
    labels,
    datasets: [
      {
        label: 'Soil Moisture (%)',
        data: soilMoisture,
        borderColor: '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#10B981',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        yAxisID: 'y',
      },
      {
        label: 'Temperature (°C)',
        data: temperature,
        borderColor: '#EF4444',
        backgroundColor: 'rgba(239, 68, 68, 0.05)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#EF4444',
        pointBorderColor: 'white',
        pointBorderWidth: 2,
        yAxisID: 'y1',
      }
    ]
  };

  return (
    <div className="bg-surface rounded-xl border border-gray-100 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-gray-800">Sensor Trends (7 Days)</h3>
        <button className="text-xs text-primary-600 font-semibold flex items-center gap-1 hover:gap-2 transition-all">
          View Analytics <MdArrowForward size={14} />
        </button>
      </div>
      <div style={{ height: '220px' }}>
        <Line options={options} data={data} />
      </div>
    </div>
  );
}
