from fastapi import FastAPI
import uvicorn
from data import fetch_stock_data
from model import StockPredictor
from pymongo import MongoClient

app = FastAPI()
predictor = StockPredictor(seq_length=10)

# Optional MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["stock_db"]
collection = db["predictions"]

@app.get("/predict/{ticker}")
async def predict_stock(ticker: str, days: int = 10):
    """Predict stock prices for a given ticker."""
    # Fetch data
    closing_prices = fetch_stock_data(ticker)
    
    # Generate predictions
    predictions = predictor.predict(closing_prices, days)
    
    # Store in MongoDB (optional)
    collection.insert_one({
        "ticker": ticker,
        "predictions": predictions.tolist(),
        "date": "2025-04-09"
    })
    
    return {"ticker": ticker, "predictions": predictions.tolist()}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)