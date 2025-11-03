A real-time, full-stack dashboard for analyzing stock market sentiment and predicting short-term price movements using machine learning.

This project integrates market data acquisition, sentiment analysis (both historical and real-time social media), and an ML model to provide actionable insights for a diversified portfolio.

Key Features

Full-Stack Architecture: Separates concerns using a modern stack:

Frontend: React (Create React App) for a responsive and dynamic user interface.

Backend: FastAPI (Python) for rapid, high-performance API endpoints.

Database: SQLite (using SQLAlchemy) for storing historical data and model results.

Expanded Portfolio: Tracks and analyzes 12 major stock tickers (AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, etc.) to simulate a diverse investment portfolio.

Dual Sentiment Analysis:

Historical Sentiment: Stores and analyzes historical news headlines and simulates long-term sentiment trends.

Live Social Media Sentiment (Twitter/X Integration): Includes an API structure to integrate with the Twitter/X API for real-time sentiment scoring of recent posts, providing immediate market reaction data.

Machine Learning Prediction: Uses a classification model (e.g., Random Forest Classifier) trained on historical price and sentiment data to predict short-term stock price movement (UP or DOWN) with a calculated Confidence Score.

Tech Stack

Component

Technology

Role

Frontend

React, Axios

User Interface, API Consumption

Backend

Python, FastAPI

High-speed API and core business logic

Data/ML

SQLAlchemy, Scikit-learn, NumPy, Pandas

Data Storage, ML Model Training

Data Sources

Alpha Vantage

Historical Price Data

Getting Started

This application requires two servers to run concurrently: the FastAPI backend (API) and the React frontend (Web App).

Prerequisites

Python 3.8+

Node.js (LTS recommended)

A free Alpha Vantage API Key for historical data generation.

1. Setup and Installation

Clone the repository and install dependencies for both the backend and frontend.

Clone the repository:
git clone https://github.com/anishgkr21/stock-sentiment-dashboard.git
cd stock-sentiment-dashboard

Install Python Dependencies (Backend):
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate

Install Node Dependencies (Frontend):
cd ..
cd frontend-app
npm install

2. Configuration (.env file)

For the application to fetch unique data, you must set up your API key securely.

Obtain a free Alpha Vantage API Key.

Create a file named .env inside the backend folder.


3. Generate Historical Data (One-Time Setup)

The machine learning model requires historical data to train. This script will populate the stockdb.db file with the necessary data.

cd backend
.\venv\Scripts\activate
python historical_data_generator.py
deactivate

4. Running the Application

Open two separate terminal windows and execute the commands below.

Terminal 1: Start the Backend (API Server)

cd stock-sentiment-dashboard\backend
.\venv\Scripts\activate
uvicorn api_server:app --reload

Terminal 2: Start the Frontend (Web App)

cd stock-sentiment-dashboard\frontend-app
npm run start

The application will open in your browser, typically at http://localhost:3000. Keep both terminals running to use the dashboard.
