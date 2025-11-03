# C:\Users\anish\stock-sentiment-dashboard\backend\historical_data_generator.py

import time
import random
from datetime import datetime, timedelta
from database import SessionLocal, StockPrice, SentimentData, Base, engine
import requests
import os
from dotenv import load_dotenv

load_dotenv()
Base.metadata.create_all(bind=engine)

def generate_historical_stock_data(symbol, days_back=30):
    """Generate simulated historical stock data"""
    db = SessionLocal()
    
    # Get current price as baseline
    api_key = os.getenv("K9TPQLF8F5D8MRCN", "demo")
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "Global Quote" not in data:
        print(f"Could not get current price for {symbol}")
        return
    
    current_price = float(data["Global Quote"]["05. price"])
    current_volume = int(data["Global Quote"]["06. volume"])
    
    # Generate historical data points
    for i in range(days_back, 0, -1):
        # Simulate price variation (±5% from current)
        price_variation = random.uniform(0.95, 1.05)
        simulated_price = current_price * price_variation
        
        # Simulate volume variation
        volume_variation = random.uniform(0.8, 1.2)
        simulated_volume = int(current_volume * volume_variation)
        
        # Create timestamp
        timestamp = datetime.now() - timedelta(days=i, hours=random.randint(0, 23))
        
        stock_price = StockPrice(
            symbol=symbol,
            price=simulated_price,
            volume=simulated_volume,
            timestamp=timestamp
        )
        
        db.add(stock_price)
        print(f"Added historical data for {symbol}: ${simulated_price:.2f} on {timestamp.date()}")
    
    db.commit()
    db.close()

def generate_historical_sentiment_data(symbol, count=20):
    """Generate simulated historical sentiment data"""
    db = SessionLocal()
    
    positive_texts = [
        f"{symbol} showing strong growth potential",
        f"Bullish outlook for {symbol} this quarter",
        f"{symbol} exceeding market expectations",
        f"Strong buy recommendation for {symbol}",
        f"{symbol} innovation driving stock higher"
    ]
    
    negative_texts = [
        f"Concerns about {symbol} market position",
        f"{symbol} facing regulatory challenges",
        f"Bearish sentiment around {symbol}",
        f"{symbol} disappointing earnings report",
        f"Market volatility affecting {symbol}"
    ]
    
    for i in range(count):
        # Random sentiment (60% positive, 40% negative for variation)
        if random.random() < 0.6:
            text = random.choice(positive_texts)
            sentiment_score = random.uniform(0.2, 0.8)
        else:
            text = random.choice(negative_texts)
            sentiment_score = random.uniform(-0.8, -0.2)
        
        timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
        
        sentiment_data = SentimentData(
            symbol=symbol,
            text=text,
            sentiment_score=sentiment_score,
            source="historical_sim",
            timestamp=timestamp
        )
        
        db.add(sentiment_data)
        print(f"Added sentiment for {symbol}: {sentiment_score:.3f}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    # --- MODIFIED: Expanded list to include 12 tickers ---
    symbols = [
        "AAPL", "GOOGL", "MSFT", 
        "AMZN", "TSLA", "NVDA", 
        "AMD", "NFLX", "BABA", 
        "JPM", "WMT", "V"
    ]
    # --- END MODIFICATION ---
    
    # You MUST delete stockdb.db before running this to clear old data!
    
    for symbol in symbols:
        print(f"Generating historical data for {symbol}...")
        generate_historical_stock_data(symbol, days_back=30)
        generate_historical_sentiment_data(symbol, count=15)
        time.sleep(2)  # Rate limiting
        print("---")
    
    print("Historical data generation complete!")

