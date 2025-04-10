Below is a well-structured and informative README for your stock price prediction project. It covers the project overview, features, setup instructions, usage, file structure, and contribution guidelines, tailored to what we’ve built so far.

---

# Stock Price Predictor

A web application that fetches historical stock data and predicts future prices using a hybrid ARIMA-LSTM model. Built with a FastAPI backend and a React frontend, this project offers an intuitive UI with real-time predictions, ticker recommendations, and search history.

## Features

- **Stock Price Prediction**: Uses a hybrid ARIMA and LSTM model to forecast stock prices for the next 10 days.
- **Historical Data**: Displays the last 30 days of closing prices in a clear chart.
- **Persistent Caching**: Stores stock data in `pickle` files to reduce API calls across restarts.
- **Model Persistence**: Saves trained ARIMA and LSTM models to disk for faster subsequent predictions.
- **Ticker-Specific Colors**: Assigns unique colors to major tickers (e.g., AAPL: Blue, NVDA: Green) for charts and UI elements.
- **Search History**: Tracks up to 5 recent ticker searches, stored in `localStorage`, with clickable buttons to re-fetch.
- **Ticker Recommendations**: Suggests tickers as you type (e.g., "A" → `AAPL`, `AMZN`; "NV" → `NVDA`) in a dropdown.
- **Dynamic Loading Messages**: Cycles through informative messages ("Fetching data...", "Training models...") during requests.
- **Refresh Functionality**: Re-fetch data for the current ticker with a dedicated button.
- **Animations**: Smooth transitions and hover effects using Framer Motion.

## Prerequisites

- **Python 3.8+**: For the backend.
- **Node.js 16+**: For the frontend.
- **Git**: To clone the repository.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/SaddamTechie/stock-price-predict.git
cd stock-price-predictor
```

### 2. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the backend**:
   ```bash
   python main.py
   ```
   - The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Run the frontend**:
   ```bash
   npm start
   ```
   - The app will open at `http://localhost:5173`.

### 4. Verify

- Open your browser to `http://localhost:5173`.
- The app should load with `AAPL` data by default. Try typing "NV" for suggestions or clicking major ticker buttons (e.g., `NVDA`, `GOOGL`).

## Usage

1. **Enter a Ticker**: Type a stock ticker (e.g., `AAPL`) in the input field and click "Predict".
2. **Major Tickers**: Click buttons like `AAPL`, `NVDA`, or `TSLA` to fetch data instantly.
3. **Search History**: View and click recent searches below the major tickers.
4. **Ticker Recommendations**: Start typing (e.g., "A" or "NV") to see a dropdown of matching tickers; click one to fetch.
5. **Refresh**: Click the "Refresh" button to update the current ticker’s data.
6. **View Results**: See the stock name, last closing price, a chart with historical and predicted prices, and a list of future predictions.

## Project Structure

```
stock-price-predictor/
├── backend/
│   ├── cache/              # Persistent stock data cache (auto-generated)
│   ├── models/             # Saved ARIMA/LSTM models (auto-generated)
│   ├── data.py             # Data fetching and preprocessing
│   ├── main.py             # FastAPI app and API endpoints
│   ├── model.py            # ARIMA-LSTM hybrid model logic
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles for the app
│   │   └── index.js        # React entry point
│   ├── package.json        # Frontend dependencies
│   └── public/             # Static assets
└── README.md               # Project documentation
```

## Dependencies

### Backend

- FastAPI, Uvicorn, yfinance, pandas, numpy, statsmodels, tensorflow, scikit-learn

### Frontend

- React, axios, chart.js, react-chartjs-2, framer-motion, react-icons, sonner, tailwindcss

(See `backend/requirements.txt` and `frontend/package.json` for full lists.)

## Notes

- **Chart Size**: Fixed at 400px height for consistent visibility. Adjust in `App.css` if needed.
- **Ticker Recommendations**: Based on a static list in `App.js`. Expand `availableTickers` or integrate an API for more options.
- **Prediction Accuracy**: The hybrid model uses 40% ARIMA and 60% LSTM weighting. Fine-tune in `model.py` if predictions need adjustment.
