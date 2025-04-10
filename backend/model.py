from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Input
import numpy as np
from data import preprocess_data
import pandas as pd
import logging
import os
import pickle

logger = logging.getLogger(__name__)

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

class StockPredictor:
    def __init__(self, seq_length=10):
        self.seq_length = seq_length
        self.arima_model = None
        self.lstm_model = None
        self.scaler = None
        # Use consistent file extensions and paths
        self.arima_file = os.path.join(MODEL_DIR, "arima_model_{}.pkl")
        self.lstm_file = os.path.join(MODEL_DIR, "lstm_model_{}.h5")
        self.scaler_file = os.path.join(MODEL_DIR, "scaler_{}.pkl")

    def load_models(self, ticker):
        """Load trained models from disk if available."""
        arima_path = self.arima_file.format(ticker)
        lstm_path = self.lstm_file.format(ticker)
        scaler_path = self.scaler_file.format(ticker)
        
        if os.path.exists(arima_path):
            with open(arima_path, 'rb') as f:
                self.arima_model = pickle.load(f)
            logger.info(f"Loaded ARIMA model for {ticker}")
        
        if os.path.exists(lstm_path) and os.path.exists(scaler_path):
            self.lstm_model = load_model(lstm_path, compile=False)  # Load without compiling
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"Loaded LSTM model and scaler for {ticker}")

    def save_models(self, ticker):
        """Save trained models to disk."""
        arima_path = self.arima_file.format(ticker)
        lstm_path = self.lstm_file.format(ticker)
        scaler_path = self.scaler_file.format(ticker)
        
        if self.arima_model:
            with open(arima_path, 'wb') as f:
                pickle.dump(self.arima_model, f)
            logger.info(f"Saved ARIMA model for {ticker}")
        
        if self.lstm_model and self.scaler:
            # Use legacy HDF5 format explicitly
            self.lstm_model.save(lstm_path, save_format='h5')
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            logger.info(f"Saved LSTM model and scaler for {ticker}")

    def train_arima(self, data, order=(2, 1, 2)):
        """Train ARIMA model."""
        try:
            self.arima_model = ARIMA(data, order=order).fit()
            logger.info("ARIMA model trained")
        except Exception as e:
            logger.error(f"Error training ARIMA: {e}")
            raise

    def train_lstm(self, X_train, y_train, epochs=20):
        """Train LSTM model with improved architecture."""
        try:
            self.lstm_model = Sequential([
                Input(shape=(self.seq_length, 1)),
                LSTM(100, return_sequences=True),
                LSTM(50),
                Dense(25, activation='relu'),
                Dense(1)
            ])
            self.lstm_model.compile(optimizer='adam', loss='mse')
            self.lstm_model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=1)
            logger.info("LSTM model trained")
        except Exception as e:
            logger.error(f"Error training LSTM: {e}")
            raise

    def predict(self, closing_prices, days=10, ticker="unknown"):
        """Hybrid prediction using ARIMA and LSTM."""
        try:
            # Load existing models if available
            self.load_models(ticker)
            
            # Preprocess data
            X, _, self.scaler, data_diff = preprocess_data(closing_prices, self.seq_length)
            
            # Train models if not loaded
            if not self.arima_model:
                self.train_arima(closing_prices['Close'])
                self.save_models(ticker)
            if not self.lstm_model:
                self.train_lstm(X, X[:, -1, :])
                self.save_models(ticker)
            
            # ARIMA forecast
            arima_pred = self.arima_model.forecast(steps=days)
            logger.info(f"ARIMA predicted {len(arima_pred)} steps")
            
            # LSTM forecast
            last_sequence = self.scaler.transform(closing_prices['Close'][-self.seq_length:].values.reshape(-1, 1))
            lstm_input = last_sequence.reshape(1, self.seq_length, 1)
            lstm_pred = []
            for _ in range(days):
                pred = self.lstm_model.predict(lstm_input, verbose=0)
                lstm_pred.append(pred[0, 0])
                lstm_input = np.roll(lstm_input, -1, axis=1)
                lstm_input[0, -1, 0] = pred[0, 0]
            lstm_pred = self.scaler.inverse_transform(np.array(lstm_pred).reshape(-1, 1))
            logger.info(f"LSTM predicted {len(lstm_pred)} steps")
            
            # Hybrid prediction (weighted average: 40% ARIMA, 60% LSTM)
            hybrid_pred = 0.4 * arima_pred + 0.6 * lstm_pred.flatten()
            
            # Generate future dates
            last_date = closing_prices.index[-1]
            future_dates = pd.date_range(start=last_date, periods=days + 1, freq='D')[1:]
            
            return hybrid_pred, future_dates
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise