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
import { FaChartLine, FaSpinner, FaExclamationTriangle } from 'react-icons/fa';
import { toast, Toaster } from 'sonner';
import './App.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function App() {
  const [ticker, setTicker] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch initial data for AAPL on load
  useEffect(() => {
    fetchStockData('AAPL');
  }, []);

  const fetchStockData = async (tickerToFetch) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`http://localhost:8000/predict/${tickerToFetch}`);
      setData(response.data);
      toast.success(`Successfully fetched data for ${tickerToFetch}`);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Error fetching data. Please try again.';
      setError(errorMsg);
      toast.error(errorMsg);
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (ticker.trim()) {
      fetchStockData(ticker);
    } else {
      toast.warning('Please enter a valid ticker');
    }
  };

  // Chart data
  const chartData = data
    ? {
        labels: [...data.historical.map(item => item.date), ...data.predictions.map(item => item.date)],
        datasets: [
          {
            label: 'Historical Prices',
            data: data.historical.map(item => item.price),
            borderColor: '#3b82f6',
            fill: false,
          },
          {
            label: 'Predicted Prices',
            data: [
              ...Array(data.historical.length).fill(null),
              ...data.predictions.map(item => item.price),
            ],
            borderColor: '#f97316',
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
        <h1 className="text-4xl font-bold text-blue-600 mb-6 flex items-center justify-center">
          <FaChartLine className="mr-2" /> Stock Price Predictor
        </h1>

        <form onSubmit={handleSubmit} className="flex gap-4 mb-8 justify-center">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder="Enter stock ticker (e.g., AAPL)"
            className="p-3 rounded-lg border border-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="p-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 disabled:bg-gray-400 flex items-center"
          >
            {loading ? <FaSpinner className="animate-spin mr-2" /> : null}
            {loading ? 'Predicting...' : 'Predict'}
          </button>
        </form>

        {error && (
          <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg flex items-center">
            <FaExclamationTriangle className="mr-2" />
            {error}
          </div>
        )}

        {data && (
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                {data.stock_name} ({data.ticker})
              </h2>
              <p className="text-gray-600">
                Last Closing Price: <span className="font-bold text-green-600">${data.last_price.toFixed(2)}</span>
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-lg">
              <Line data={chartData} options={chartOptions} />
            </div>

            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Predicted Prices</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {data.predictions.map((pred, idx) => (
                  <div
                    key={idx}
                    className="bg-orange-500 text-white p-4 rounded-lg shadow-md hover:scale-105 transition-transform"
                  >
                    <p className="text-sm">{pred.date}</p>
                    <p className="text-lg font-bold">${pred.price.toFixed(2)}</p>
                  </div>
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