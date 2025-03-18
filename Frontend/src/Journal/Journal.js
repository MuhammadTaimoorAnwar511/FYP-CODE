import React, { useState, useEffect, useRef } from 'react';
import GradientChartExample from "./GradientChartExample";
import Navbar2 from "../Components/Footer&Navbar/Navbar2";
import Footer from "../Components/Footer&Navbar/Footer";
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

// Register ChartJS components
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

// A small helper function to handle the PEPE symbol variations
function normalizeSymbol(symbol) {
  if (symbol === "1000PEPEUSDT") {
    return "PEPEUSDT";
  }
  return symbol;
}

// Map each symbol to an icon URL (replace these paths with your actual icon paths or URLs)
const coinIcons = {
  BTCUSDT: "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/svg/color/btc.svg",
  ETHUSDT: "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/svg/color/eth.svg",
  BNBUSDT: "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/svg/color/bnb.svg",
  SOLUSDT: "https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/svg/color/sol.svg",
  PEPEUSDT: "https://cryptologos.cc/logos/pepe-pepe-logo.png", 
  // ^ Example placeholder for PEPE. Replace with your actual PEPE icon if you have one.
};

function getCoinIcon(symbol) {
  const normalized = normalizeSymbol(symbol);
  return coinIcons[normalized] || "https://via.placeholder.com/24";
}

function DashboardPage() {
  const API_HOST = process.env.REACT_APP_API_HOST;
  const API_PORT = process.env.REACT_APP_API_PORT;
  const BASE_URL = `http://${API_HOST}:${API_PORT}`;

  const [activeTab, setActiveTab] = useState('active');
  const [journal, setJournal] = useState(null);
  const [user, setUser] = useState(null);
  const [openTrades, setOpenTrades] = useState([]);
  const [closedTrades, setClosedTrades] = useState([]);

  const chartRef = useRef(null);

  const chartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Portfolio Growth',
        data: [0, 5, 10, 6, 15, 20, 18],
        fill: true,
        borderColor: '#60a5fa',
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
      gradient.addColorStop(0, 'rgba(159, 122, 234, 0.5)');
      gradient.addColorStop(1, 'rgba(96, 165, 250, 0.1)');
      chart.data.datasets[0].backgroundColor = gradient;
      chart.update();
    }
  }, [activeTab]);

  // Fetch journal/user data
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    fetch(`${BASE_URL}/journal/data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setJournal(data.journal);
          setUser(data.user);
        }
      })
      .catch(error => console.error("Error fetching journal data:", error));
  }, [BASE_URL]);

  // Fetch open trades
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    fetch(`${BASE_URL}/journal/opentrades`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setOpenTrades(data.open_trades);
        }
      })
      .catch(error => console.error("Error fetching open trades:", error));
  }, [BASE_URL]);

  // Fetch closed trades
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    fetch(`${BASE_URL}/journal/closetrades`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          setClosedTrades(data.closed_trades);
        }
      })
      .catch(error => console.error("Error fetching closed trades:", error));
  }, [BASE_URL]);

  // Sort open trades by entry_time descending
  const sortedOpenTrades = [...openTrades].sort(
    (a, b) => new Date(b.entry_time) - new Date(a.entry_time)
  );

  // Sort closed trades by exit_time descending
  const sortedClosedTrades = [...closedTrades].sort(
    (a, b) => new Date(b.exit_time) - new Date(a.exit_time)
  );

  // Compute additional stats
  const cancelledSignals = journal
    ? journal.total_signals -
      (journal.signals_closed_in_profit +
        journal.signals_closed_in_loss +
        journal.current_running_signals)
    : 0;

  const winRate =
    journal && (journal.signals_closed_in_profit + journal.signals_closed_in_loss > 0)
      ? Math.round(
          (journal.signals_closed_in_profit /
            (journal.signals_closed_in_profit + journal.signals_closed_in_loss)) *
            100
        )
      : 0;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Inline style for custom scrollbar */}
      <style>{`
        /* Custom scrollbar for WebKit-based browsers */
        ::-webkit-scrollbar {
          width: 8px;
        }
        ::-webkit-scrollbar-track {
          background-color: #1F2937; /* matches bg-gray-800 */
        }
        ::-webkit-scrollbar-thumb {
          background-color: #4B5563; /* a darker shade to match theme */
          border-radius: 4px;
        }
      `}</style>

      {/* Navbar */}
      <div className="flex-none">
        <Navbar2 />
      </div>

      {/* Main Container */}
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
            <p className="text-3xl font-bold mt-2">
              {journal ? journal.total_signals : 0}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Signals Closed in Profit</p>
            <p className="text-3xl font-bold mt-2 text-green-400">
              {journal ? journal.signals_closed_in_profit : 0}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Signals Closed in Loss</p>
            <p className="text-3xl font-bold mt-2 text-red-400">
              {journal ? journal.signals_closed_in_loss : 0}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Current Running Signals</p>
            <p className="text-3xl font-bold mt-2">
              {journal ? journal.current_running_signals : 0}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Cancelled Signals</p>
            <p className="text-3xl font-bold mt-2">
              {journal ? cancelledSignals : 0}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Avg Profit (USDT)</p>
            <p className="text-3xl font-bold mt-2 text-green-400">
              {journal ? `${journal.average_profit_usdt}` : "0"}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Avg Loss (USDT)</p>
            <p className="text-3xl font-bold mt-2 text-red-400">
              {journal ? `${journal.average_loss_usdt}` : "0"}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Win Rate</p>
            <p className="text-3xl font-bold mt-2 text-green-400">
              {winRate}%
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-4 text-center hover:shadow-lg transition-transform transform hover:-translate-y-1">
            <p className="text-gray-300 text-sm">Realized Balance</p>
            <p className="text-3xl font-bold mt-2">
              {user ? `$${user.current_balance.toFixed(2)}` : "$0.00"}
            </p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 text-center flex flex-col items-center justify-center">
            <p className="text-gray-300 text-sm mb-2">Additional Metrics / Placeholder</p>
            <div className="w-full h-40 bg-gray-700 rounded-lg flex items-center justify-center">
              <span className="text-gray-400 italic text-sm">[Additional Data Placeholder]</span>
            </div>
          </div>
        </div>

        {/* Tabs */}
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

        {/* Active (Open Trades) */}
        {activeTab === 'active' && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg max-h-96 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="py-3 px-4 text-gray-300 font-medium">Symbol</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Direction</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Entry Time</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Entry Price</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Stop Loss</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Take Profit</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Initial Margin</th>
                </tr>
              </thead>
              <tbody>
                {sortedOpenTrades.length > 0 ? (
                  sortedOpenTrades.map((trade) => (
                    <tr
                      key={trade._id}
                      className="border-b border-gray-700 hover:bg-gray-700 transition"
                    >
                      <td className="py-3 px-4 text-white">
                        <div className="flex items-center">
                          <img
                            src={getCoinIcon(trade.symbol)}
                            alt={trade.symbol}
                            className="w-5 h-5 mr-2"
                          />
                          {trade.symbol}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-white">{trade.direction}</td>
                      <td className="py-3 px-4 text-white">{trade.entry_time}</td>
                      <td className="py-3 px-4 text-white">{trade.entry_price}</td>
                      <td className="py-3 px-4 text-white">{trade.stop_loss}</td>
                      <td className="py-3 px-4 text-white">{trade.take_profit}</td>
                      <td className="py-3 px-4 text-white">{trade.initial_margin}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="py-4 text-center text-gray-400">
                      No open trades found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Closed Trades */}
        {activeTab === 'closed' && (
          <div className="bg-gray-800 rounded-lg p-4 shadow-lg max-h-96 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-700 sticky top-0">
                <tr>
                  <th className="py-3 px-4 text-gray-300 font-medium">Symbol</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Direction</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Entry Time</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Entry Price</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Stop Loss</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Take Profit</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Initial Margin</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">Status</th>
                  <th className="py-3 px-4 text-gray-300 font-medium">PNL</th>
                </tr>
              </thead>
              <tbody>
                {sortedClosedTrades.length > 0 ? (
                  sortedClosedTrades.map((trade) => (
                    <tr
                      key={trade._id}
                      className="border-b border-gray-700 hover:bg-gray-700 transition"
                    >
                      <td className="py-3 px-4 text-white">
                        <div className="flex items-center">
                          <img
                            src={getCoinIcon(trade.symbol)}
                            alt={trade.symbol}
                            className="w-5 h-5 mr-2"
                          />
                          {trade.symbol}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-white">{trade.direction}</td>
                      <td className="py-3 px-4 text-white">{trade.entry_time}</td>
                      <td className="py-3 px-4 text-white">{trade.entry_price}</td>
                      <td className="py-3 px-4 text-white">{trade.stop_loss}</td>
                      <td className="py-3 px-4 text-white">{trade.take_profit}</td>
                      <td className="py-3 px-4 text-white">{trade.initial_margin}</td>
                      <td className="py-3 px-4 text-white">{trade.status}</td>
                      <td className="py-3 px-4 text-white">{trade.PNL}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="9" className="py-4 text-center text-gray-400">
                      No closed trades found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Cancelled Tab */}
        {activeTab === 'cancelled' && (
          <div className="bg-gray-800 rounded-lg p-4 text-gray-400 italic">
            <p>No cancelled trades are displayed yet.</p>
          </div>
        )}

        {/* Chart Tab */}
        {activeTab === 'chart' && (
          <div className="bg-gray-800 rounded-lg p-4 h-96">
            <GradientChartExample />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex-none">
        <Footer />
      </div>
    </div>
  );
}

export default DashboardPage;
