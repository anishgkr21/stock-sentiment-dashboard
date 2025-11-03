#!/usr/bin/env python3
"""
Quick integration test for Twitter and enhanced stock collection
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test SQLite database connection"""
    try:
        conn = sqlite3.connect('stockdb.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        print("✅ Database connection successful")
        print(f"   Existing tables: {[table[0] for table in tables]}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_twitter_api():
    """Test Twitter API connection"""
    try:
        from data_collectors.twitter_collector import TwitterCollector
        
        collector = TwitterCollector()
        print("✅ Twitter collector initialized")
        
        # Test building query
        query = collector.build_search_query()
        print(f"   Query: {query[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Twitter API error: {e}")
        print("   Make sure TWITTER_BEARER_TOKEN is set in your environment")
        return False

def test_stock_collector():
    """Test enhanced stock collector"""
    try:
        from data_collectors.stock_collector import EnhancedStockCollector
        
        collector = EnhancedStockCollector()
        print("✅ Enhanced stock collector initialized")
        
        # Test collecting one stock
        test_data = collector.collect_stock_price('AAPL')
        if test_data:
            print(f"   Sample data: AAPL @ ${test_data['price']}")
        else:
            print("   No stock data retrieved (check API keys)")
        
        return True
    except Exception as e:
        print(f"❌ Stock collector error: {e}")
        return False

def test_sentiment_analysis():
    """Test sentiment analysis"""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        
        analyzer = SentimentIntensityAnalyzer()
        test_text = "Apple stock is doing great today! $AAPL to the moon!"
        
        scores = analyzer.polarity_scores(test_text)
        print("✅ Sentiment analysis working")
        print(f"   Test text: '{test_text}'")
        print(f"   Sentiment score: {scores['compound']:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Sentiment analysis error: {e}")
        return False

def show_recent_data():
    """Show recent data from database"""
    try:
        conn = sqlite3.connect('stockdb.db')
        cursor = conn.cursor()
        
        # Check stock prices
        cursor.execute("""
            SELECT symbol, price, timestamp 
            FROM stock_prices 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        stock_data = cursor.fetchall()
        if stock_data:
            print("\n📈 Recent stock prices:")
            for row in stock_data:
                symbol, price, timestamp = row
                print(f"   {symbol}: ${price} at {timestamp}")
        else:
            print("\n📈 No stock price data found")
        
        # Check sentiment data (if table exists)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sentiment_queue'
        """)
        
        if cursor.fetchone():
            cursor.execute("""
                SELECT symbol, sentiment_score, timestamp 
                FROM sentiment_queue 
                ORDER BY timestamp DESC 
                LIMIT 5
            """)
            
            sentiment_data = cursor.fetchall()
            if sentiment_data:
                print("\n💭 Recent sentiment data:")
                for row in sentiment_data:
                    symbol, score, timestamp = row
                    print(f"   {symbol}: {score:.3f} at {timestamp}")
            else:
                print("\n💭 No sentiment data found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error showing data: {e}")

def main():
    """Run all integration tests"""
    print("🚀 Running Stock Sentiment Dashboard Integration Tests")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_sentiment_analysis,
        test_stock_collector,
        test_twitter_api
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your system is ready.")
    else:
        print("⚠️  Some tests failed. Check your environment variables and API keys.")
    
    print("\n" + "=" * 60)
    show_recent_data()

if __name__ == "__main__":
    main()