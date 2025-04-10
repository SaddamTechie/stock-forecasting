from fastapi import FastAPI, HTTPException
import uvicorn
from data import fetch_stock_data
from model import StockPredictor
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
predictor = StockPredictor(seq_length=10)

# Optional MongoDB connection
client = MongoClient("mongodb+srv://techspa254:bFywDX77eB3U3nrr@cluster0.dbubt.mongodb.net/stock-forecast?retryWrites=true&w=majority&appName=Cluster0")
db = client["stock_db"]
collection = db["predictions"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/predict/{ticker}")
async def predict_stock(ticker: str, days: int = 10):
    """Predict stock prices for a given ticker."""
    try:
        # Fetch data
        closing_prices = fetch_stock_data(ticker)
        if closing_prices.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        # Generate predictions
        predictions = predictor.predict(closing_prices, days)
        
        # Store in MongoDB (optional)
        collection.insert_one({
            "ticker": ticker,
            "predictions": predictions.tolist(),
            "date": "2025-04-09"
        })
        
        return {"ticker": ticker, "predictions": predictions.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting stock prices: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)