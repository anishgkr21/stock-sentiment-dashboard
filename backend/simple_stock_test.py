import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from database import SessionLocal, StockPrice, Base, engine

# Load environment variables
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

def fetch_and_store_stock(symbol):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    print(f"API Response for {symbol}:", data)
    
    if "Global Quote" in data:
        quote = data["Global Quote"]
        
        # Store in database
        db = SessionLocal()
        try:
            stock_price = StockPrice(
                symbol=symbol,
                price=float(quote["05. price"]),
                volume=int(quote["06. volume"]),
                timestamp=datetime.now()
            )
            db.add(stock_price)
            db.commit()
            print(f"✅ Stored {symbol}: ${quote['05. price']}")
        except Exception as e:
            print(f"❌ Database error: {e}")
        finally:
            db.close()
    else:
        print(f"❌ No data received for {symbol}")

# Test with one stock first
fetch_and_store_stock("AAPL")
