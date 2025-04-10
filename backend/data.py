import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

def fetch_stock_data(ticker, start_date="2020-01-01", end_date="2025-04-09"):
    """Fetch stock data from Yahoo Finance."""
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data['Close']

def preprocess_data(closing_prices, seq_length=10):
    """Preprocess data for ARIMA and LSTM."""
    # Differencing for ARIMA (stationarity)
    data_diff = closing_prices.diff().dropna()
    
    # Scaling for LSTM
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices.values.reshape(-1, 1))
    
    # Create sequences for LSTM
    X, y = [], []
    for i in range(len(scaled_data) - seq_length):
        X.append(scaled_data[i:i + seq_length])
        y.append(scaled_data[i + seq_length])
    return np.array(X), np.array(y), scaler, data_diff