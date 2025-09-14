import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

interface StockData {
  symbol: string;
  price: number;
  volume: number;
  timestamp: string;
}

interface SentimentData {
  symbol: string;
  average_sentiment: number;
  sentiment_count: number;
  latest_sentiments: Array<{
    score: number;
    text: string;
    timestamp: string;
  }>;
}

interface PredictionData {
  symbol: string;
  prediction: string;
  confidence: number;
  timestamp: string;
}

function App() {
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);

  const API_BASE = 'http://localhost:8000';

  const fetchData = async (symbol: string) => {
    setLoading(true);
    try {
      const [stockResponse, sentimentResponse, predictionResponse] = await Promise.all([
        axios.get(`${API_BASE}/stocks/${symbol}/price`),
        axios.get(`${API_BASE}/stocks/${symbol}/sentiment`),
        axios.get(`${API_BASE}/stocks/${symbol}/prediction`)
      ]);

      setStockData(stockResponse.data);
      setSentimentData(sentimentResponse.data);
      setPredictionData(predictionResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(selectedSymbol);
  }, [selectedSymbol]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Sentiment Dashboard</h1>
        
        <div className="symbol-selector">
          <select 
            value={selectedSymbol} 
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="symbol-select"
          >
            <option value="AAPL">Apple (AAPL)</option>
            <option value="GOOGL">Google (GOOGL)</option>
            <option value="MSFT">Microsoft (MSFT)</option>
          </select>
          <button onClick={() => fetchData(selectedSymbol)} disabled={loading}>
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        <div className="dashboard-grid">
          {/* Stock Price Card */}
          <div className="card">
            <h3>Current Price</h3>
            {stockData ? (
              <div>
                <div className="price">${stockData.price}</div>
                <div className="volume">Volume: {stockData.volume.toLocaleString()}</div>
                <div className="timestamp">
                  Updated: {new Date(stockData.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ) : (
              <div>Loading...</div>
            )}
          </div>

          {/* Sentiment Card */}
          <div className="card">
            <h3>Sentiment Analysis</h3>
            {sentimentData ? (
              <div>
                <div className={`sentiment-score ${sentimentData.average_sentiment > 0 ? 'positive' : 'negative'}`}>
                  {sentimentData.average_sentiment > 0 ? '📈' : '📉'} 
                  {sentimentData.average_sentiment.toFixed(3)}
                </div>
                <div className="sentiment-count">
                  Based on {sentimentData.sentiment_count} data points
                </div>
              </div>
            ) : (
              <div>Loading...</div>
            )}
          </div>

          {/* ML Prediction Card */}
          <div className="card">
            <h3>ML Prediction</h3>
            {predictionData ? (
              <div>
                <div className={`prediction ${predictionData.prediction.toLowerCase()}`}>
                  {predictionData.prediction === 'UP' ? '🚀' : '📉'} {predictionData.prediction}
                </div>
                <div className="confidence">
                  Confidence: {(predictionData.confidence * 100).toFixed(1)}%
                </div>
                <div className="timestamp">
                  Generated: {new Date(predictionData.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ) : (
              <div>Loading...</div>
            )}
          </div>
        </div>

        {/* Recent Sentiment Timeline */}
        {sentimentData && sentimentData.latest_sentiments && (
          <div className="card full-width">
            <h3>Recent Sentiment Timeline</h3>
            <div className="sentiment-list">
              {sentimentData.latest_sentiments.map((sentiment, index) => (
                <div key={index} className="sentiment-item">
                  <span className={`score ${sentiment.score > 0 ? 'positive' : 'negative'}`}>
                    {sentiment.score.toFixed(3)}
                  </span>
                  <span className="text">{sentiment.text}</span>
                  <span className="time">{new Date(sentiment.timestamp).toLocaleTimeString()}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
