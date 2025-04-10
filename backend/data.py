import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import logging
import pickle
import os

logger = logging.getLogger(__name__)

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def load_cache(ticker, start_date="2020-01-01", end_date="2025-04-09"):
    """Load cached stock data from disk."""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start_date}_{end_date}.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            logger.info(f"Loaded cached data for {ticker} from {cache_file}")
            return pickle.load(f)
    return None

def save_cache(ticker, data, start_date="2020-01-01", end_date="2025-04-09"):
    """Save stock data to disk cache."""
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start_date}_{end_date}.pkl")
    with open(cache_file, 'wb') as f:
        pickle.dump(data, f)
    logger.info(f"Saved data for {ticker} to {cache_file}")

def fetch_stock_data(ticker, start_date="2020-01-01", end_date="2025-04-09"):
    """Fetch stock data from Yahoo Finance with persistent caching."""
    cached_data = load_cache(ticker, start_date, end_date)
    if cached_data is not None:
        return cached_data

    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if stock_data.empty:
            logger.error(f"No data returned for {ticker}")
            return pd.DataFrame()
        # Ensure daily frequency
        stock_data = stock_data.asfreq('D', method='ffill')
        logger.info(f"Fetched {len(stock_data)} rows for {ticker}")
        save_cache(ticker, stock_data[['Close']], start_date, end_date)
        return stock_data[['Close']]
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        raise

def preprocess_data(closing_prices, seq_length=10):
    """Preprocess data for ARIMA and LSTM."""
    try:
        if len(closing_prices) < seq_length + 1:
            raise ValueError(f"Data length {len(closing_prices)} is less than required {seq_length + 1}")
        
        # Differencing for ARIMA (stationarity), preserve index
        data_diff = closing_prices['Close'].diff().dropna()
        
        # Scaling for LSTM
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(closing_prices['Close'].values.reshape(-1, 1))
        
        # Create sequences for LSTM
        X, y = [], []
        for i in range(len(scaled_data) - seq_length):
            X.append(scaled_data[i:i + seq_length])
            y.append(scaled_data[i + seq_length])
        logger.info(f"Preprocessed data: {len(X)} sequences created")
        return np.array(X), np.array(y), scaler, data_diff
    except Exception as e:
        logger.error(f"Error in preprocessing: {e}")
        raise