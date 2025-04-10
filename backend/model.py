from statsmodels.tsa.arima.model import ARIMA
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import numpy as np
from data import preprocess_data  # Import preprocess_data from data.py

class StockPredictor:
    def __init__(self, seq_length=10):
        self.seq_length = seq_length
        self.arima_model = None
        self.lstm_model = None
        self.scaler = None

    def train_arima(self, data_diff, order=(5, 1, 0)):
        """Train ARIMA model."""
        self.arima_model = ARIMA(data_diff, order=order).fit()

    def train_lstm(self, X_train, y_train, epochs=20):
        """Train LSTM model."""
        self.lstm_model = Sequential()
        self.lstm_model.add(LSTM(50, return_sequences=True, input_shape=(self.seq_length, 1)))
        self.lstm_model.add(LSTM(50))
        self.lstm_model.add(Dense(1))
        self.lstm_model.compile(optimizer='adam', loss='mse')
        self.lstm_model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=1)

    def predict(self, closing_prices, days=10):
        """Hybrid prediction using ARIMA and LSTM."""
        # Preprocess data
        X, _, self.scaler, data_diff = preprocess_data(closing_prices, self.seq_length)
        
        # Train models if not already trained
        if not self.arima_model:
            self.train_arima(closing_prices, order=(5, 1, 0))
        if not self.lstm_model:
            self.train_lstm(X, X[:, -1, :])  # Simplified training on full data
        
        # ARIMA forecast
        arima_pred = self.arima_model.forecast(steps=days)
        
        # LSTM forecast
        last_sequence = self.scaler.transform(closing_prices[-self.seq_length:].values.reshape(-1, 1))
        lstm_input = last_sequence.reshape(1, self.seq_length, 1)
        lstm_pred = []
        for _ in range(days):
            pred = self.lstm_model.predict(lstm_input, verbose=0)
            lstm_pred.append(pred[0, 0])
            lstm_input = np.roll(lstm_input, -1, axis=1)
            lstm_input[0, -1, 0] = pred[0, 0]
        lstm_pred = self.scaler.inverse_transform(np.array(lstm_pred).reshape(-1, 1))
        
        # Hybrid prediction (simple average)
        hybrid_pred = (arima_pred + lstm_pred.flatten()) / 2
        return hybrid_pred