import time
from datetime import datetime, timedelta
from simple_stock_test import fetch_and_store_stock
from sentiment_analyzer import SentimentAnalyzer

def generate_sample_data():
    analyzer = SentimentAnalyzer()
    
    # Generate more stock data points (simulate different times)
    print("Generating stock data...")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        fetch_and_store_stock(symbol)
        time.sleep(1)  # Small delay to avoid API rate limits
    
    # Generate more sentiment data
    print("Generating sentiment data...")
    sentiment_samples = [
        ("AAPL", "Apple's new iPhone features are incredible and innovative!"),
        ("AAPL", "Concerned about Apple's supply chain issues affecting production."),
        ("GOOGL", "Google's search algorithm updates are performing excellently."),
        ("GOOGL", "Worried about Google's declining ad revenue this quarter."),
        ("MSFT", "Microsoft's cloud services are dominating the enterprise market."),
        ("MSFT", "Microsoft's recent security vulnerabilities are concerning investors.")
    ]
    
    for symbol, text in sentiment_samples:
        analyzer.analyze_text(text, symbol)
    
    print("Test data generation complete!")

if __name__ == "__main__":
    generate_sample_data()