from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
import numpy as np
from data import preprocess_data
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class StockPredictor:
    def __init__(self, seq_length=10):
        self.seq_length = seq_length
        self.arima_model = None
        self.lstm_model = None
        self.scaler = None

    def train_arima(self, data, order=(5, 1, 0)):
        """Train ARIMA model."""
        try:
            self.arima_model = ARIMA(data, order=order).fit()
            logger.info("ARIMA model trained")
        except Exception as e:
            logger.error(f"Error training ARIMA: {e}")
            raise

    def train_lstm(self, X_train, y_train, epochs=20):
        """Train LSTM model."""
        try:
            self.lstm_model = Sequential([
                Input(shape=(self.seq_length, 1)),
                LSTM(50, return_sequences=True),
                LSTM(50),
                Dense(1)
            ])
            self.lstm_model.compile(optimizer='adam', loss='mse')
            self.lstm_model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=1)
            logger.info("LSTM model trained")
        except Exception as e:
            logger.error(f"Error training LSTM: {e}")
            raise

    def predict(self, closing_prices, days=10):
        """Hybrid prediction using ARIMA and LSTM."""
        try:
            # Preprocess data
            X, _, self.scaler, data_diff = preprocess_data(closing_prices, self.seq_length)
            
            # Train models if not already trained
            if not self.arima_model:
                self.train_arima(closing_prices['Close'], order=(5, 1, 0))
            if not self.lstm_model:
                self.train_lstm(X, X[:, -1, :])
            
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
            
            # Hybrid prediction (simple average)
            hybrid_pred = (arima_pred + lstm_pred.flatten()) / 2
            
            # Generate future dates
            last_date = closing_prices.index[-1]
            future_dates = pd.date_range(start=last_date, periods=days + 1, freq='D')[1:]
            
            return hybrid_pred, future_dates
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise