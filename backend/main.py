from fastapi import FastAPI, HTTPException
import uvicorn
from data import fetch_stock_data
from model import StockPredictor
import yfinance as yf
import logging
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

predictor = StockPredictor(seq_length=10)

# Simple in-memory cache
data_cache = {}

@lru_cache(maxsize=100)
def get_stock_info(ticker):
    """Fetch stock info with LRU caching."""
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {e}")
        raise

@app.get("/predict/{ticker}")
async def predict_stock(ticker: str, days: int = 10):
    """Predict stock prices and return historical data."""
    try:
        # Fetch data with caching
        logger.info(f"Fetching data for ticker: {ticker}")
        closing_prices = fetch_stock_data(ticker, cache=data_cache)
        if closing_prices.empty or len(closing_prices) < predictor.seq_length + 1:
            logger.error(f"Insufficient data for {ticker}: {len(closing_prices)} rows")
            raise HTTPException(status_code=400, detail=f"Insufficient data for {ticker}. Need at least {predictor.seq_length + 1} days.")

        # Validate DataFrame structure
        if 'Close' not in closing_prices.columns:
            logger.error(f"DataFrame for {ticker} missing 'Close' column: {closing_prices.columns}")
            raise HTTPException(status_code=500, detail=f"Invalid data format for {ticker}: missing 'Close' column")

        # Fetch stock info with caching
        logger.info(f"Fetching stock info for {ticker}")
        info = get_stock_info(ticker)
        stock_name = info.get("longName", ticker)
        
        # Access last price safely
        last_price = closing_prices['Close'].iloc[-1]  # Already scalar due to iloc
        
        # Generate predictions with dates
        logger.info(f"Generating predictions for {ticker}")
        predictions, future_dates = predictor.predict(closing_prices, days)
        
        # Historical data (last 30 days for chart)
        historical_data = closing_prices.tail(30)
        if historical_data.empty:
            logger.error(f"No historical data available for {ticker} after tail(30)")
            raise HTTPException(status_code=500, detail=f"No historical data available for {ticker}")

        logger.info(f"Successfully processed {ticker}")
        return {
            "ticker": ticker,
            "stock_name": stock_name,
            "last_price": float(last_price),  # last_price is already a scalar
            "historical": [
                {"date": str(date), "price": float(price)}
                for date, price in zip(historical_data.index, historical_data['Close'].values)
            ],
            "predictions": [
                {"date": str(date), "price": float(price)}
                for date, price in zip(future_dates, predictions)
            ]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error predicting stock prices for {ticker}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error predicting stock prices for {ticker}: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)