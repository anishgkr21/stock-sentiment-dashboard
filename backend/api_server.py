# C:\Users\anish\stock-sentiment-dashboard\backend\api_server.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from database import SessionLocal, StockPrice, SentimentData, Correlation
from ml_predictor import StockPredictor
# ADDED:
from typing import Dict, Any 
# REMOVED uvicorn import from the top, moved to the bottom __main__ block
import uvicorn 

app = FastAPI(title="Stock Sentiment Dashboard API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = StockPredictor()

@app.get("/")
def root():
    return {"message": "Stock Sentiment Dashboard API"}

@app.get("/stocks/{symbol}/price")
def get_stock_price(symbol: str):
    db = SessionLocal()
    latest_stock = db.query(StockPrice).filter(
        StockPrice.symbol == symbol.upper()
    ).order_by(StockPrice.timestamp.desc()).first()
    
    db.close()
    
    if not latest_stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {
        "symbol": latest_stock.symbol,
        "price": latest_stock.price,
        "volume": latest_stock.volume,
        "timestamp": latest_stock.timestamp
    }

@app.get("/stocks/{symbol}/sentiment")
def get_sentiment(symbol: str):
    db = SessionLocal()
    sentiments = db.query(SentimentData).filter(
        SentimentData.symbol == symbol.upper()
    ).order_by(SentimentData.timestamp.desc()).limit(10).all()
    
    db.close()
    
    if not sentiments:
        raise HTTPException(status_code=404, detail="No sentiment data found")
    
    avg_sentiment = sum(s.sentiment_score for s in sentiments) / len(sentiments)
    
    return {
        "symbol": symbol.upper(),
        "average_sentiment": avg_sentiment,
        "sentiment_count": len(sentiments),
        "latest_sentiments": [
            {
                "score": s.sentiment_score,
                "text": s.text[:100],
                "timestamp": s.timestamp
            } for s in sentiments[:5]
        ]
    }

# --- NEW FUNCTION FOR REAL-TIME TWITTER API INTEGRATION ---
def fetch_and_analyze_live_sentiment(symbol: str) -> Dict[str, Any]:
    """
    *** YOU MUST REPLACE THIS FUNCTION WITH YOUR ACTUAL TWITTER API AND SENTIMENT LOGIC ***
    """
    # Returning Simulated Data as a placeholder for the live endpoint:
    import random
    score = random.uniform(-0.5, 0.5)
    count = random.randint(50, 200)
    
    return {
        "symbol": symbol.upper(),
        "score": score,
        "count": count,
        "source": "Twitter/X Realtime API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stocks/{symbol}/live_sentiment")
def get_live_sentiment(symbol: str):
    """Fetches real-time sentiment from a live source (e.g., Twitter)."""
    try:
        live_data = fetch_and_analyze_live_sentiment(symbol.upper())
        return live_data
    except Exception as e:
        print(f"ERROR fetching live sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch live sentiment data.")

# --- END NEW FUNCTION ---

@app.get("/stocks/{symbol}/prediction")
def get_prediction(symbol: str):
    # Train model if not already trained
    if not predictor.train_model(symbol.upper()):
        raise HTTPException(status_code=400, detail="Insufficient data for prediction")
    
    result = predictor.predict_direction(symbol.upper())
    
    if not result:
        raise HTTPException(status_code=400, detail="Could not generate prediction")
    
    return {
        "symbol": symbol.upper(),
        "prediction": result['direction'],
        "confidence": result['confidence'],
        "timestamp": datetime.now()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)