import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { FaChartLine, FaSpinner, FaExclamationTriangle, FaSync, FaHistory } from 'react-icons/fa';
import { toast, Toaster } from 'sonner';
import { motion } from 'framer-motion';
import './App.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

// Sample ticker list for recommendations (expandable)
const availableTickers = [
  'AAPL', 'AMZN', 'AMD', 'AAL', 'ABNB', 
  'NVDA', 'NFLX', 'NKE', 'NOW', 'NTNX',
  'GOOGL', 'GOOG', 'GME', 'GS', 'GM',
  'MSFT', 'META', 'MCD', 'MRNA', 'MU',
  'TSLA', 'T', 'TM', 'TSM', 'TWTR'
].sort();

function App() {
  const [ticker, setTicker] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState('Fetching data...');
  const [lastUpdated, setLastUpdated] = useState(null);

  const majorTickers = [
    { symbol: 'AAPL', color: '#3b82f6' }, // Blue
    { symbol: 'NVDA', color: '#10b981' }, // Green
    { symbol: 'GOOGL', color: '#f97316' }, // Orange
    { symbol: 'MSFT', color: '#8b5cf6' }, // Purple
    { symbol: 'TSLA', color: '#ef4444' }, // Red
    { symbol: 'AMZN', color: '#facc15' }, // Yellow
  ];

  // Fetch initial data for AAPL
  useEffect(() => {
    fetchStockData('AAPL');
  }, []);

  // Load search history from localStorage
  useEffect(() => {
    const savedHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    setSearchHistory(savedHistory);
  }, [])

  const fetchStockData = async (tickerToFetch) => {
    setLoading(true);
    setError(null);
    const messages = [
      'Fetching data...',
      'Training models...',
      'Generating predictions...',
      'Almost ready...',
    ];
    let msgIndex = 0;
    const interval = setInterval(() => {
      setLoadingMessage(messages[msgIndex]);
      msgIndex = (msgIndex + 1) % messages.length;
    }, 1000);

    try {
      const response = await axios.get(`http://localhost:8000/predict/${tickerToFetch}`);
      setData(response.data);
      setLastUpdated(new Date().toLocaleTimeString());
      toast.success(`Data loaded for ${tickerToFetch}`);
      // Update search history
      const newHistory = [...new Set([tickerToFetch, ...searchHistory.slice(0, 4)])]; // Keep top 5 unique
      setSearchHistory(newHistory);
      localStorage.setItem('searchHistory', JSON.stringify(newHistory));
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to fetch data.';
      setError(errorMsg);
      toast.error(errorMsg);
      setData(null);
    } finally {
      clearInterval(interval);
      setLoading(false);
      setLoadingMessage('Fetching data...');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ticker.trim()) {
      fetchStockData(ticker);
    } else {
      toast.warning('Enter a valid ticker!');
    }
  };


  const handleInputChange = (e) => {
    const value = e.target.value.toUpperCase();
    setTicker(value);
    if (value) {
      const filtered = availableTickers.filter(t => t.startsWith(value)).slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setTicker(suggestion);
    fetchStockData(suggestion);
    setShowSuggestions(false);
  };

  const handleRefresh = () => {
    if (data) {
      fetchStockData(data.ticker);
    }
  };

  const chartData = data
    ? {
        labels: [...data.historical.map(item => item.date), ...data.predictions.map(item => item.date)],
        datasets: [
          {
            label: 'Historical Prices',
            data: data.historical.map(item => item.price),
            borderColor: majorTickers.find(t => t.symbol === data.ticker)?.color || '#3b82f6',
            fill: false,
          },
          {
            label: 'Predicted Prices',
            data: [
              ...Array(data.historical.length).fill(null),
              ...data.predictions.map(item => item.price),
            ],
            borderColor: majorTickers.find(t => t.symbol === data.ticker)?.color || '#f97316',
            borderDash: [5, 5],
            fill: false,
          },
        ],
      }
    : null;

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: `${data?.stock_name || 'Stock'} Price Forecast` },
    },
    scales: {
      x: { title: { display: true, text: 'Date' } },
      y: { title: { display: true, text: 'Price ($)' } },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 p-6">
      <Toaster position="top-right" richColors />
      
      <div className="max-w-5xl mx-auto">
        <motion.h1
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-4xl font-bold text-blue-600 mb-6 flex items-center justify-center"
        >
          <FaChartLine className="mr-2" /> Stock Price Predictor
        </motion.h1>

        <form onSubmit={handleSubmit} className="flex gap-4 mb-8 justify-center items-center">
        <div className='relative'>
          <input
            type="text"
            value={ticker}
            onChange={handleInputChange}
            placeholder="Enter stock ticker (e.g., AAPL)"
            className="p-3 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {showSuggestions && suggestions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute z-10 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-40 overflow-y-auto"
              >
                {suggestions.map((sug, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleSuggestionClick(sug)}
                    className="p-2 hover:bg-gray-100 cursor-pointer text-gray-800"
                  >
                    {sug}
                  </div>
                ))}
              </motion.div>
            )}
        </div>
          <button
            type="submit"
            disabled={loading}
            className="p-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
          >
            {loading ? <FaSpinner className="animate-spin mr-2" /> : null}
            {loading ? loadingMessage : 'Predict'}
          </button>
          {data && (
            <button
              type="button"
              onClick={handleRefresh}
              className="p-3 bg-gray-600 text-white rounded-lg shadow-md hover:bg-gray-700 flex items-center"
            >
              <FaSync className="mr-2" /> Refresh
            </button>
          )}
        </form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-wrap gap-4 mb-8 justify-center"
        >
          {majorTickers.map(t => (
            <motion.button
              key={t.symbol}
              onClick={() => fetchStockData(t.symbol)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 text-white rounded-lg shadow-md"
              style={{ backgroundColor: t.color }}
            >
              {t.symbol}
            </motion.button>
          ))}
        </motion.div>

        {/* {searchHistory.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-2 flex items-center justify-center sm:justify-start">
              <FaHistory className="mr-2" /> Recent Searches
            </h3>
            <div className="flex flex-wrap gap-2 sm:gap-4 justify-center sm:justify-start">
              {searchHistory.map((hist, idx) => (
                <motion.button
                  key={idx}
                  onClick={() => fetchStockData(hist)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 bg-gray-200 text-gray-800 rounded-lg shadow-md hover:bg-gray-300 text-sm sm:text-base"
                >
                  {hist}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )} */}

        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg flex items-center"
          >
            <FaExclamationTriangle className="mr-2" />
            {error}
          </motion.div>
        )}

        {data && (
          <div className="space-y-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                {data.stock_name} ({data.ticker})
              </h2>
              <p className="text-gray-600">
                Last Closing Price: <span className="font-bold text-green-600">${data.last_price.toFixed(2)}</span>
              </p>
              {lastUpdated && (
                <p className="text-sm text-gray-500 mt-2">Last Updated: {lastUpdated}</p>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white p-6 rounded-lg shadow-lg"
            >
              <Line data={chartData} options={chartOptions} />
            </motion.div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Predicted Prices</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {data.predictions.map((pred, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: idx * 0.1 }}
                    className="p-4 text-white rounded-lg shadow-md hover:scale-105 transition-transform"
                    style={{ backgroundColor: majorTickers.find(t => t.symbol === data.ticker)?.color || '#f97316' }}
                  >
                    <p className="text-sm">{pred.date}</p>
                    <p className="text-lg font-bold">${pred.price.toFixed(2)}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;