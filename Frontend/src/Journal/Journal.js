import React, { useState, useEffect, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import GradientChartExample  from "./GradientChartExample"
import Navbar2 from "../Components/Footer&Navbar/Navbar2"
import Footer from "../Components/Footer&Navbar/Footer"
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

// Register chart.js components
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

function DashboardPage() {
  const API_HOST = process.env.REACT_APP_API_HOST
  const API_PORT = process.env.REACT_APP_API_PORT
  const BASE_URL = `http://${API_HOST}:${API_PORT}`
  const token = localStorage.getItem("access_token");

  const [activeTab, setActiveTab] = useState('active');

  // Placeholder data for tables
  const signals = {
    active: [
      { id: 'T1234', type: 'Long', entry: 20000, tp: 21000, sl: 19500, status: 'active' },
      { id: 'T1235', type: 'Short', entry: 20500, tp: 20000, sl: 21000, status: 'active' },
    ],
    closed: [
      { id: 'T1001', type: 'Long', entry: 18000, tp: 19000, sl: 17500, status: 'takeprofit' },
      { id: 'T1002', type: 'Short', entry: 21000, tp: 20000, sl: 21500, status: 'stoploss' },
    ],
    cancelled: [
      { id: 'T2001', type: 'Long', entry: 22000, tp: 22500, sl: 21500, status: 'cancelled' }
    ],
  };

  // Chart configuration
  const chartRef = useRef(null);

  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Portfolio Growth',
        data: [0, 5, 10, 6, 15, 20, 18],
        fill: true,
        borderColor: '#60a5fa', // blue-400
        pointBackgroundColor: '#60a5fa',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#D1D5DB' },
      },
      title: {
        display: true,
        text: 'Performance Over Time',
        color: '#D1D5DB',
        font: { size: 16 },
      },
      tooltip: {
        titleColor: '#FFFFFF',
        bodyColor: '#FFFFFF',
        backgroundColor: '#1F2937',
        borderColor: '#374151',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: '#D1D5DB' },
        grid: { color: '#374151' },
      },
      y: {
        ticks: { color: '#D1D5DB' },
        grid: { color: '#374151' },
      },
    },
  };

  useEffect(() => {
    if (chartRef.current) {
      const chart = chartRef.current.$context.chart;
      const gradient = chart.ctx.createLinearGradient(0, 0, 0, chart.height);
      gradient.addColorStop(0, 'rgba(159, 122, 234, 0.5)'); // purple-400 with opacity
      gradient.addColorStop(1, 'rgba(96, 165, 250, 0.1)'); // blue-400 with lighter opacity
      chart.data.datasets[0].backgroundColor = gradient;
      chart.update();
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
          <div className="flex-none">
                <Navbar2 />
            </div>
      <div className="max-w-7xl mx-auto px-6 py-8">

        {/* Page Header */}
        <div className="mb-10">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            Trading Signals Dashboard
          </h1>
          <p className="text-gray-300 mt-2 text-sm sm:text-base">
            A comprehensive overview of your trading signals, performance metrics, and ongoing activities.
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Total Signals</p>
            <p className="text-3xl font-bold mt-2">345</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Signals Closed in Profit</p>
            <p className="text-3xl font-bold mt-2 text-green-400">210</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Signals Closed in Loss</p>
            <p className="text-3xl font-bold mt-2 text-red-400">80</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Current Running Signals</p>
            <p className="text-3xl font-bold mt-2">12</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Cancelled Signals</p>
            <p className="text-3xl font-bold mt-2">43</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Avg Profit (%)</p>
            <p className="text-3xl font-bold mt-2 text-green-400">+3.5%</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Avg Loss (%)</p>
            <p className="text-3xl font-bold mt-2 text-red-400">-1.2%</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Win Rate</p>
            <p className="text-3xl font-bold mt-2 text-green-400">64%</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Balance</p>
            <p className="text-3xl font-bold mt-2">$23,452.00</p>
          </div>
          {/* We remove the placeholder chart here since we have a dedicated tab for the chart now */}
          <div className="bg-gray-800 rounded-lg p-4 text-center flex flex-col items-center justify-center">
            <p className="text-gray-300 text-sm mb-2">Additional Metrics / Placeholder</p>
            <div className="w-full h-40 bg-gray-700 rounded-lg flex items-center justify-center">
              <span className="text-gray-400 italic text-sm">[Additional Data Placeholder]</span>
            </div>
          </div>
        </div>

        {/* Tabs for Signals and Chart */}
        <div className="mb-4 border-b border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('active')}
              className={`py-3 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'active' 
                  ? 'border-blue-500 text-blue-400' 
                  : 'border-transparent text-gray-300 hover:text-gray-100 hover:border-gray-500'
              } focus:outline-none`}
            >
              Active
            </button>
            <button
              onClick={() => setActiveTab('closed')}
              className={`py-3 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'closed'
                  ? 'border-blue-500 text-blue-400' 
                  : 'border-transparent text-gray-300 hover:text-gray-100 hover:border-gray-500'
              } focus:outline-none`}
            >
              Closed
            </button>
            <button
              onClick={() => setActiveTab('cancelled')}
              className={`py-3 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'cancelled'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-300 hover:text-gray-100 hover:border-gray-500'
              } focus:outline-none`}
            >
              Cancelled
            </button>
            <button
              onClick={() => setActiveTab('chart')}
              className={`py-3 px-2 border-b-2 font-medium text-sm ${
                activeTab === 'chart'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-300 hover:text-gray-100 hover:border-gray-500'
              } focus:outline-none`}
            >
              Chart
            </button>
          </nav>
        </div>

        {/* Conditional Rendering for Tabs */}
        {activeTab !== 'chart' && (
          <div className="bg-gray-800 rounded-lg p-4 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-700">
                <tr>
                  <th className="py-3 px-4 text-gray-300 font-medium">Trade ID</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Type</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Entry Point</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Take Profit</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Stop Loss</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {signals[activeTab].map((signal) => (
                  <tr key={signal.id} className="border-b border-gray-700 hover:bg-gray-700 transition">
                    <td className="py-3 px-4 text-white">{signal.id}</td>
                    <td className="py-3 px-4 text-white">{signal.type}</td>
                    <td className="py-3 px-4 text-white">{signal.entry}</td>
                    <td className="py-3 px-4 text-white">{signal.tp}</td>
                    <td className="py-3 px-4 text-white">{signal.sl}</td>
                    <td className="py-3 px-4 text-white capitalize">
                      {signal.status === 'active' && <span className="text-blue-400">Active</span>}
                      {signal.status === 'takeprofit' && <span className="text-green-400">Take Profit</span>}
                      {signal.status === 'stoploss' && <span className="text-red-400">Stop Loss</span>}
                      {/* {signal.status === 'cancelled' && <span className="text-yellow-400">Cancelled</span>} */}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {signals[activeTab].length === 0 && (
              <div className="text-gray-400 text-sm py-4 italic text-center">
                No {activeTab} signals found.
              </div>
            )}
          </div>
        )}

        {activeTab === 'chart' && (
          <GradientChartExample />
        )}
      </div>
      <div className="flex-none">
                <Footer />
            </div>
    </div>
  );
}

export default DashboardPage;
