import React, { useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Title,
  Filler,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Title,
  Filler,
  Legend
);

// Custom plugin for line shadow
const lineShadowPlugin = {
  id: 'lineShadow',
  afterDraw: (chart) => {
    const { ctx, chartArea } = chart;
    const chartMeta = chart.getDatasetMeta(0);
    if (!chartMeta || !chartMeta.data || chartMeta.data.length < 2) return;

    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.6)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 4;

    // Draw the line again for the shadow
    const { dataset } = chartMeta;
    ctx.beginPath();
    dataset.draw(ctx, chartArea);
    ctx.closePath();
    ctx.restore();
  },
};

ChartJS.register(lineShadowPlugin);

function RefinedGradientChart() {
  const chartRef = useRef(null);

  // Sample data - adjust as needed
  const dataValues = [0, 5, 10, 6, 15, 20, 18];
  const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];

  // Find max and min to highlight points
  const maxValue = Math.max(...dataValues);
  const minValue = Math.min(...dataValues);

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Portfolio Growth',
        data: dataValues,
        fill: true,
        borderColor: '#7C3AED', // Purple accent
        borderWidth: 3,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        // Assign colors based on min/max
        pointBackgroundColor: dataValues.map((val) => {
          if (val === maxValue) return '#10B981'; // highlight max in green
          if (val === minValue) return '#EF4444'; // highlight min in red
          return '#7C3AED'; // default purple
        }),
        pointBorderColor: '#7C3AED',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1200,
      easing: 'easeOutQuart',
    },
    plugins: {
      legend: {
        labels: { 
          color: '#D1D5DB', 
          font: { size: 12 }
        },
      },
      title: {
        display: true,
        text: 'Performance Over Time',
        color: '#D1D5DB',
        font: { size: 18, weight: 'bold' },
        padding: { bottom: 20 },
      },
      tooltip: {
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        backgroundColor: '#1F2937',
        borderColor: '#374151',
        borderWidth: 1,
        displayColors: false,
        padding: 10,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Month',
          color: '#D1D5DB',
          font: { size: 14 },
          padding: 10,
        },
        ticks: { color: '#D1D5DB', font: { size: 12 } },
        grid: { color: '#2D3748' },
      },
      y: {
        title: {
          display: true,
          text: 'Value',
          color: '#D1D5DB',
          font: { size: 14 },
          padding: 10,
        },
        ticks: { color: '#D1D5DB', font: { size: 12 } },
        grid: { color: '#2D3748' },
      },
    },
  };

  useEffect(() => {
    if (!chartRef.current) return;
    const chart = chartRef.current.$context.chart;
    const { ctx, chartArea } = chart;
    if (!chartArea) return;

    // Create a subtle vertical gradient
    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
    gradient.addColorStop(0, 'rgba(124,58,237,0.5)'); // Purple at top
    gradient.addColorStop(1, 'rgba(96,165,250,0.1)'); // Blue at bottom

    chart.data.datasets[0].backgroundColor = gradient;
    chart.update();
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg p-4 relative h-96">
      <Line ref={chartRef} data={chartData} options={chartOptions} />
    </div>
  );
}

export default RefinedGradientChart;
