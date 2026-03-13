import os
import random
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from newsapi import NewsApiClient
from fredapi import Fred
from dotenv import load_dotenv
from models import MarketData, Asset, AssetType

# Load environment variables
load_dotenv()

class IngestionService:
    def __init__(self):
        self.assets = {
            "^NSEI": Asset("^NSEI", AssetType.EQUITY, "Nifty 50 Index"),
            "RELIANCE.NS": Asset("RELIANCE.NS", AssetType.EQUITY, "Reliance Industries Ltd"),
            "TCS.NS": Asset("TCS.NS", AssetType.EQUITY, "Tata Consultancy Services Ltd"),
            "HDFCBANK.NS": Asset("HDFCBANK.NS", AssetType.EQUITY, "HDFC Bank Ltd"),
            "GOLDBEES.NS": Asset("GOLDBEES.NS", AssetType.COMMODITY, "Nippon India ETF Gold BeES"),
        }
        
        # Initialize APIs
        self.news_api_key = os.getenv("NEWSAPI_KEY")
        self.fred_api_key = os.getenv("FRED_API_KEY")
        
        self.newsapi = NewsApiClient(api_key=self.news_api_key) if self.news_api_key else None
        self.fred = Fred(api_key=self.fred_api_key) if self.fred_api_key else None

    def get_assets(self) -> List[Asset]:
        return list(self.assets.values())

    def fetch_market_data(self, symbols: List[str]) -> List[MarketData]:
        """Fetches real-time market data using yfinance."""
        data = []
        # Ensure BTC is mapped to BTC-USD for yfinance
        yf_symbols = ["BTC-USD" if s == "BTC" else s for s in symbols]
        
        try:
            tickers = yf.Tickers(" ".join(yf_symbols))
            for sym, yf_sym in zip(symbols, yf_symbols):
                ticker = tickers.tickers[yf_sym]
                info = ticker.fast_info
                
                price = info.get('last_price')
                if price is None:
                    # Fallback to history if fast_info fails
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        price = hist['Close'].iloc[-1]
                
                if price is not None:
                    md = MarketData(
                        symbol=sym,
                        timestamp=datetime.now(),
                        price=float(price),
                        volume=float(info.get('last_volume', 0))
                    )
                    data.append(md)
        except Exception as e:
            print(f"Error fetching market data: {e}")
            # Fallback to empty list or handled error
        return data

    def get_economic_indicators(self) -> Dict[str, float]:
        """Fetches key macroeconomic indicators from FRED."""
        indicators = {
            "GDP_Growth": 0.0,
            "CPI_Inflation": 0.0,
            "Interest_Rate": 0.0,
            "Unemployment_Rate": 0.0
        }
        
        if not self.fred:
            print("FRED API key not configured. Returning 0.0 for indicators.")
            return indicators

        try:
            # Series IDs: 
            # GDPC1 (Real GDP), CPIAUCSL (CPI), FEDFUNDS (Effective Fed Funds Rate), UNRATE (Unemployment Rate)
            # Fetching last available values
            indicators["GDP_Growth"] = float(self.fred.get_series("A191RL1Q225SBEA").iloc[-1]) # Real GDP % change
            indicators["CPI_Inflation"] = float(self.fred.get_series("FPCPITOTLZGUSA").iloc[-1]) if "FPCPITOTLZGUSA" else 3.0 # Fallback example
            # Better series for CPI: CPIAUCSL (monthly)
            cpi_series = self.fred.get_series("CPIAUCSL")
            if len(cpi_series) > 12:
                indicators["CPI_Inflation"] = ((cpi_series.iloc[-1] / cpi_series.iloc[-13]) - 1) * 100
                
            indicators["Interest_Rate"] = float(self.fred.get_series("FEDFUNDS").iloc[-1])
            indicators["Unemployment_Rate"] = float(self.fred.get_series("UNRATE").iloc[-1])
        except Exception as e:
            print(f"Error fetching FRED indicators: {e}")
            
        return indicators

    def get_geopolitical_news(self) -> List[Dict[str, str]]:
        """Fetches geopolitical news from NewsAPI."""
        news_list = []
        if not self.newsapi:
            print("NewsAPI key not configured. Returning empty news list.")
            return [{"headline": "Check .env for NewsAPI Key", "sentiment": "neutral", "impact_score": 0.0}]

        try:
            # Search for geopolitical keywords
            queries = "geopolitics OR trade war OR sanctions OR conflict"
            top_headlines = self.newsapi.get_everything(q=queries, language='en', sort_by='relevancy', page_size=5)
            
            for article in top_headlines.get('articles', []):
                # Simple heuristic for sentiment/impact since we don't have a LLM/NLP here
                # In a real app, we'd pipe this through a sentiment analyzer
                headline = article['title']
                sentiment = "neutral"
                impact_score = 0.5
                
                lower_headline = headline.lower()
                if any(word in lower_headline for word in ['escalates', 'threatens', 'sanctions', 'war', 'plunges']):
                    sentiment = "negative"
                    impact_score = 0.8
                elif any(word in lower_headline for word in ['agreement', 'growth', 'peace', 'summit', 'resolve']):
                    sentiment = "positive"
                    impact_score = 0.6
                
                news_list.append({
                    "headline": headline,
                    "sentiment": sentiment,
                    "impact_score": impact_score,
                    "url": article['url']
                })
        except Exception as e:
            print(f"Error fetching NewsAPI data: {e}")
            
        return news_list

    def fetch_historical_data(self, symbols: List[str], days: int = 30) -> Dict[str, List[float]]:
        """Fetches historical price data using yfinance."""
        historical_data = {}
        interval = "1d"
        period = f"{days}d"
        
        yf_symbols = ["BTC-USD" if s == "BTC" else s for s in symbols]
        
        try:
            data = yf.download(yf_symbols, period=period, interval=interval, group_by='ticker', progress=False)
            for sym, yf_sym in zip(symbols, yf_symbols):
                if len(yf_symbols) > 1:
                    df = data[yf_sym]
                else:
                    df = data
                
                if not df.empty:
                    historical_data[sym] = df['Close'].tolist()
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            
        return historical_data

    def get_asset_classes(self) -> Dict[str, str]:
        """Returns mapping of symbols to asset types."""
        return {symbol: asset.asset_type.value for symbol, asset in self.assets.items()}
