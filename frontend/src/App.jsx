import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [error, setError] = useState(null);

  const fetchPredictions = async () => {
    try {
      setError(null);
      const response = await axios.get(`http://localhost:8000/predict/${ticker}`);
      setPredictions(response.data.predictions);
    } catch (err) {
      setError('Error fetching predictions. Please check the ticker or server.');
    }
  };

  return (
    <div className="App">
      <h1>Stock Price Predictor</h1>
      <div>
        <input
          type="text"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          placeholder="Enter stock ticker (e.g., AAPL)"
        />
        <button onClick={fetchPredictions}>Predict</button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {predictions.length > 0 && (
        <div>
          <h2>Predictions for {ticker}</h2>
          <ul>
            {predictions.map((pred, idx) => (
              <li key={idx}>Day {idx + 1}: ${pred.toFixed(2)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;