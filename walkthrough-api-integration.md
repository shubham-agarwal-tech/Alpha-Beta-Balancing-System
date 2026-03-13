# API Integration Walkthrough

I have successfully integrated real-world data sources into the Alpha-Beta Balancing System. The system now uses live financial data, geopolitical news, and macroeconomic indicators.

## Changes Made

### 1. Ingestion Service Refactoring
- **[ingestion.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py)**: Replaced `MockIngestionService` with [IngestionService](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py#15-161).
- **Yahoo Finance**: Integrated `yfinance` to fetch real-time and historical market data for Indian assets like ^NSEI (Nifty 50), RELIANCE.NS, and TCS.NS.
- **NewsAPI**: Integrated `newsapi-python` to fetch current geopolitical news based on keywords (e.g., "geopolitics", "trade war", "sanctions").
- **FRED API**: Integrated `fredapi` to fetch macroeconomic indicators like GDP Growth, CPI Inflation, Interest Rates, and Unemployment Rate.
- **Environment Management**: Added `python-dotenv` support to securely manage API keys.

### 2. Dependency Management
- **[.env.example](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/.env.example)**: Created a template for necessary API keys (NewsAPI, FRED).
- **requirements.txt**: Updated with new libraries (`yfinance`, `newsapi-python`, `fredapi`, `python-dotenv`).

### 3. Application Updates
- Updated **[main.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/main.py)** and **[app.py](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/app.py)** to use the new [IngestionService](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/ingestion.py#15-161).

## Verification Results

### Market Data Fetching
Successfully fetched live prices for major assets.
- **^NSEI**: Nifty 50 index price fetched as benchmark.
- **Indian Equities**: RELIANCE.NS, TCS.NS, etc., fetched for Alpha strategy.

### Sentiment Analysis (Simplified)
Implemented a keyword-based heuristic to assign sentiment and impact scores to real news headlines, ensuring the existing ML optimization logic continues to function with real data.

### Macroeconomic Indicators fallback
The system is designed to gracefully handle missing API keys by providing informative logs and neutral fallbacks (0.0), allowing the system to run even if the user hasn't set up all keys yet.

## How to use
1. Duplicate [.env.example](file:///c:/Users/Pc/Desktop/Shubham/13.03.2026/alpha_beta_system%20-phase-4/.env.example) as `.env`.
2. Add your `NEWSAPI_KEY` and `FRED_API_KEY`.
3. Run the demo: `python main.py` or start the API with `python app.py`.
